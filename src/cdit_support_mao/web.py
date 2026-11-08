"""Local-only synthetic authentication and protected support API."""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from cdit_support_mao.database import connect, initialize_database


IDLE_TIMEOUT = timedelta(minutes=30)
ABSOLUTE_TIMEOUT = timedelta(hours=8)
COOKIE_NAME = "cdit_session"
COMPONENT_VERSION = "0.1.0"
router = APIRouter()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def stamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def parse_stamp(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


def _hash_password(password: str, *, salt: bytes | None = None) -> str:
    if len(password) < 12 or len(password) > 128:
        raise ValueError("synthetic password must contain 12 to 128 characters")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=64)
    return "scrypt$16384$8$1$" + salt.hex() + "$" + digest.hex()


def _verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        algorithm, n, r, p, salt_hex, digest_hex = stored.split("$")
        if algorithm != "scrypt":
            return False
        actual = hashlib.scrypt(
            password.encode("utf-8"),
            salt=bytes.fromhex(salt_hex),
            n=int(n), r=int(r), p=int(p),
            dklen=len(bytes.fromhex(digest_hex)),
        )
        return hmac.compare_digest(actual.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def provision_synthetic_password(account_id: str, password: str) -> None:
    """Set the password for a seeded local synthetic account; never accepts real account data."""
    hashed = _hash_password(password)
    initialize_database()
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT status FROM synthetic_accounts WHERE account_id = ?", (account_id,)
        ).fetchone()
        if row is None:
            db.rollback()
            raise ValueError("synthetic account does not exist")
        db.execute(
            "UPDATE synthetic_accounts SET password_hash = ?, status = 'active', updated_at = ? WHERE account_id = ?",
            (hashed, stamp(now_utc()), account_id),
        )
        db.commit()


@dataclass(frozen=True)
class Actor:
    account_id: str
    username: str
    role: str


class LoginPayload(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=1, max_length=128)


class SupportRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=160)
    request_text: str = Field(min_length=1, max_length=12000)


class AccountChange(BaseModel):
    role: Literal["user", "staff", "admin"] | None = None
    status: Literal["active", "suspended", "deactivated", "removed"] | None = None


def _record_health(db: sqlite3.Connection, event_type: str, component: str, status: str, error_code: str | None = None) -> None:
    db.execute(
        """INSERT INTO product_health_events
           (event_id, occurred_at, event_type, component, component_version, status_code, error_code)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("PH-" + uuid.uuid4().hex, stamp(now_utc()), event_type, component, COMPONENT_VERSION, status, error_code),
    )


def _session_context(request: Request, *, touch: bool) -> tuple[Actor, dict]:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    token_hash = hashlib.sha256(token.encode("ascii", errors="ignore")).hexdigest()
    initialize_database()
    current = now_utc()
    with connect() as db:
        row = db.execute(
            """SELECT s.session_id, s.issued_at, s.last_activity_at, s.absolute_expires_at,
                      s.warned_15m, s.warned_5m, s.revoked_at,
                      a.account_id, a.username, a.role, a.status
               FROM sessions s JOIN synthetic_accounts a ON a.account_id = s.account_id
               WHERE s.token_hash = ?""",
            (token_hash,),
        ).fetchone()
        if row is None or row["revoked_at"] is not None or row["status"] != "active":
            raise HTTPException(status_code=401, detail="Authentication required")
        idle_deadline = parse_stamp(row["last_activity_at"]) + IDLE_TIMEOUT
        absolute_deadline = parse_stamp(row["absolute_expires_at"])
        deadline = min(idle_deadline, absolute_deadline)
        if current >= deadline:
            db.execute("UPDATE sessions SET revoked_at = ? WHERE session_id = ?", (stamp(current), row["session_id"]))
            db.commit()
            raise HTTPException(status_code=401, detail="Session expired")
        if touch:
            db.execute(
                "UPDATE sessions SET last_activity_at = ? WHERE session_id = ?",
                (stamp(current), row["session_id"]),
            )
            idle_deadline = current + IDLE_TIMEOUT
            deadline = min(idle_deadline, absolute_deadline)
        remaining = deadline - current
        warned15 = bool(row["warned_15m"])
        warned5 = bool(row["warned_5m"])
        if remaining <= timedelta(minutes=15) and not warned15:
            db.execute("UPDATE sessions SET warned_15m = 1 WHERE session_id = ?", (row["session_id"],))
            _record_health(db, "session_warning_15m", "session", "warning")
            warned15 = True
        if remaining <= timedelta(minutes=5) and not warned5:
            db.execute("UPDATE sessions SET warned_5m = 1 WHERE session_id = ?", (row["session_id"],))
            _record_health(db, "session_warning_5m", "session", "warning")
            warned5 = True
        db.commit()
        actor = Actor(row["account_id"], row["username"], row["role"])
        state = {
            "authenticated": True,
            "idle_expires_at": stamp(idle_deadline),
            "absolute_expires_at": stamp(absolute_deadline),
            "expires_at": stamp(deadline),
            "remaining_seconds": max(0, int(remaining.total_seconds())),
            "warning": "5m" if remaining <= timedelta(minutes=5) else ("15m" if remaining <= timedelta(minutes=15) else None),
            "extension_available": False,
        }
        return actor, state


def current_actor(request: Request) -> Actor:
    actor, _ = _session_context(request, touch=True)
    return actor


def require_roles(*roles: str):
    def dependency(actor: Actor = Depends(current_actor)) -> Actor:
        if actor.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return actor
    return dependency


def _set_session_cookie(response: Response, token: str) -> None:
    secure = os.environ.get("CDIT_COOKIE_SECURE", "").lower() in {"1", "true", "yes"}
    response.set_cookie(
        COOKIE_NAME, token, httponly=True, secure=secure, samesite="strict",
        path="/", max_age=int(ABSOLUTE_TIMEOUT.total_seconds()),
    )


@router.post("/auth/login")
def login(payload: LoginPayload, response: Response):
    username = payload.username.strip()
    initialize_database()
    with connect() as db:
        row = db.execute(
            "SELECT account_id, username, role, status, password_hash FROM synthetic_accounts WHERE username = ? COLLATE NOCASE",
            (username,),
        ).fetchone()
        if row is None or row["status"] != "active" or not _verify_password(payload.password, row["password_hash"]):
            _record_health(db, "auth_denied", "auth", "blocked", "invalid_credentials")
            db.commit()
            raise HTTPException(status_code=401, detail="Invalid username or password")
        now = now_utc()
        raw_token = secrets.token_urlsafe(32)
        session_id = "SES-" + uuid.uuid4().hex
        db.execute(
            """INSERT INTO sessions
               (session_id, token_hash, account_id, issued_at, last_activity_at, absolute_expires_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, hashlib.sha256(raw_token.encode("ascii")).hexdigest(), row["account_id"],
             stamp(now), stamp(now), stamp(now + ABSOLUTE_TIMEOUT)),
        )
        db.commit()
    _set_session_cookie(response, raw_token)
    return {"account_id": row["account_id"], "username": row["username"], "role": row["role"]}


@router.post("/auth/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        with connect() as db:
            db.execute(
                "UPDATE sessions SET revoked_at = ? WHERE token_hash = ? AND revoked_at IS NULL",
                (stamp(now_utc()), hashlib.sha256(token.encode("ascii", errors="ignore")).hexdigest()),
            )
            db.commit()
    response.delete_cookie(COOKIE_NAME, path="/", samesite="strict")
    return {"ok": True}


@router.get("/auth/session")
def session_status(request: Request):
    try:
        _actor, state = _session_context(request, touch=False)
        return state
    except HTTPException as exc:
        if exc.status_code == 401:
            return {"authenticated": False}
        raise


@router.get("/auth/me")
def me(actor: Actor = Depends(current_actor)):
    return {"account_id": actor.account_id, "username": actor.username, "role": actor.role}


@router.post("/auth/continue")
def continue_session(request: Request, actor: Actor = Depends(current_actor)):
    # An authenticated user action resets only the idle timer; the absolute deadline remains fixed.
    _actor, state = _session_context(request, touch=True)
    return state


@router.post("/auth/extension-request")
def request_extension(request: Request, actor: Actor = Depends(current_actor)):
    _actor, state = _session_context(request, touch=False)
    with connect() as db:
        existing = db.execute(
            "SELECT alert_id FROM session_extension_alerts WHERE session_id = (SELECT session_id FROM sessions WHERE token_hash = ?) AND review_status = 'new'",
            (hashlib.sha256(request.cookies[COOKIE_NAME].encode("ascii", errors="ignore")).hexdigest(),),
        ).fetchone()
        if existing:
            return {"alert_id": existing["alert_id"], "status": "new", "session_extended": False}
        row = db.execute(
            "SELECT session_id FROM sessions WHERE token_hash = ?",
            (hashlib.sha256(request.cookies[COOKIE_NAME].encode("ascii", errors="ignore")).hexdigest(),),
        ).fetchone()
        alert_id = "EXT-" + uuid.uuid4().hex
        db.execute(
            "INSERT INTO session_extension_alerts(alert_id, session_id, account_id, requested_at) VALUES (?, ?, ?, ?)",
            (alert_id, row["session_id"], actor.account_id, stamp(now_utc())),
        )
        _record_health(db, "session_extension_requested", "session", "warning")
        db.commit()
    return {"alert_id": alert_id, "status": "new", "session_extended": False, "expires_at": state["expires_at"]}


@router.get("/api/cases")
def list_cases(actor: Actor = Depends(require_roles("user", "staff", "admin"))):
    with connect() as db:
        if actor.role == "user":
            rows = db.execute(
                "SELECT case_id, owner_account_id, subject, request_text, status, urgency_band, created_at, updated_at FROM synthetic_cases WHERE owner_account_id = ? ORDER BY updated_at DESC",
                (actor.account_id,),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT case_id, owner_account_id, subject, request_text, status, urgency_band, created_at, updated_at FROM synthetic_cases ORDER BY updated_at DESC"
            ).fetchall()
    return [dict(row) for row in rows]


@router.post("/api/cases", status_code=201)
def submit_case(payload: SupportRequest, actor: Actor = Depends(require_roles("user"))):
    case_id = "SYN-CASE-" + uuid.uuid4().hex
    now = stamp(now_utc())
    subject = payload.subject.strip()
    request_text = payload.request_text.strip()
    if not subject or not request_text:
        raise HTTPException(status_code=422, detail="Subject and request are required")
    with connect() as db:
        db.execute(
            """INSERT INTO synthetic_cases
               (case_id, owner_account_id, subject, request_text, status, urgency_band, is_synthetic, created_at, updated_at)
               VALUES (?, ?, ?, ?, 'submitted', 'unknown', 1, ?, ?)""",
            (case_id, actor.account_id, subject, request_text, now, now),
        )
        db.commit()
    return {"case_id": case_id, "status": "submitted", "urgency_band": "unknown"}


@router.get("/api/cases/{case_id}")
def get_case(case_id: str, actor: Actor = Depends(require_roles("user", "staff", "admin"))):
    with connect() as db:
        if actor.role == "user":
            row = db.execute(
                "SELECT case_id, owner_account_id, subject, request_text, status, urgency_band, created_at, updated_at FROM synthetic_cases WHERE case_id = ? AND owner_account_id = ?",
                (case_id, actor.account_id),
            ).fetchone()
        else:
            row = db.execute(
                "SELECT case_id, owner_account_id, subject, request_text, status, urgency_band, created_at, updated_at FROM synthetic_cases WHERE case_id = ?",
                (case_id,),
            ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return dict(row)


@router.get("/api/admin/accounts")
def list_accounts(actor: Actor = Depends(require_roles("admin"))):
    with connect() as db:
        rows = db.execute(
            "SELECT account_id, username, role, status, created_at, updated_at FROM synthetic_accounts ORDER BY username"
        ).fetchall()
    return [dict(row) for row in rows]


@router.patch("/api/admin/accounts/{account_id}")
def change_account(account_id: str, payload: AccountChange, actor: Actor = Depends(require_roles("admin"))):
    if payload.role is None and payload.status is None:
        raise HTTPException(status_code=422, detail="At least one account field is required")
    now = stamp(now_utc())
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT account_id, role, status, password_hash FROM synthetic_accounts WHERE account_id = ?",
            (account_id,),
        ).fetchone()
        if row is None:
            db.rollback()
            raise HTTPException(status_code=404, detail="Account not found")
        new_role = payload.role or row["role"]
        new_status = payload.status or row["status"]
        if new_status == "active" and not row["password_hash"]:
            db.rollback()
            raise HTTPException(status_code=409, detail="Account requires local credential setup")
        if row["account_id"] == actor.account_id and (new_role != "admin" or new_status != "active"):
            active_admins = db.execute(
                "SELECT COUNT(*) FROM synthetic_accounts WHERE role='admin' AND status='active'"
            ).fetchone()[0]
            if active_admins <= 1:
                db.rollback()
                raise HTTPException(status_code=409, detail="The last active Admin cannot remove their own access")
        if new_role == row["role"] and new_status == row["status"]:
            db.rollback()
            return {"account_id": account_id, "role": row["role"], "status": row["status"], "changed": False}
        role_order = {"user": 0, "staff": 1, "admin": 2}
        if new_role != row["role"]:
            action = "promote" if role_order[new_role] > role_order[row["role"]] else "demote"
        else:
            action = {"suspended": "suspend", "deactivated": "deactivate", "removed": "remove", "active": "reactivate"}.get(new_status, "update_role")
        db.execute(
            "UPDATE synthetic_accounts SET role = ?, status = ?, updated_at = ? WHERE account_id = ?",
            (new_role, new_status, now, account_id),
        )
        db.execute(
            """INSERT INTO account_access_events
               (event_id, actor_account_id, target_account_id, action, before_role, after_role, before_status, after_status, occurred_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("AUD-" + uuid.uuid4().hex, actor.account_id, account_id, action,
             row["role"], new_role, row["status"], new_status, now),
        )
        db.execute(
            "UPDATE sessions SET revoked_at = ? WHERE account_id = ? AND revoked_at IS NULL",
            (now, account_id),
        )
        _record_health(db, "account_access_changed", "access_admin", "ok")
        db.commit()
    return {"account_id": account_id, "role": new_role, "status": new_status, "changed": True}


@router.get("/api/admin/session-extension-alerts")
def list_extension_alerts(actor: Actor = Depends(require_roles("admin"))):
    with connect() as db:
        rows = db.execute(
            """SELECT x.alert_id, x.session_id, x.account_id, a.username, x.requested_at,
                      x.review_status, x.reviewed_at
               FROM session_extension_alerts x JOIN synthetic_accounts a ON a.account_id = x.account_id
               ORDER BY x.requested_at DESC LIMIT 100"""
        ).fetchall()
    return [dict(row) for row in rows]


@router.patch("/api/admin/session-extension-alerts/{alert_id}/review")
def review_extension_alert(alert_id: str, actor: Actor = Depends(require_roles("admin"))):
    with connect() as db:
        cursor = db.execute(
            "UPDATE session_extension_alerts SET review_status = 'reviewed', reviewed_at = ? WHERE alert_id = ? AND review_status = 'new'",
            (stamp(now_utc()), alert_id),
        )
        db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Alert not found or already reviewed")
    return {"alert_id": alert_id, "review_status": "reviewed", "session_extended": False}

@router.get("/api/product-health")
def product_health(actor: Actor = Depends(require_roles("staff", "admin"))):
    with connect() as db:
        events = db.execute(
            """SELECT event_id, occurred_at, event_type, component, component_version,
                      status_code, error_code, duration_ms
               FROM product_health_events ORDER BY occurred_at DESC LIMIT 100"""
        ).fetchall()
        summaries = db.execute(
            """SELECT summary_id, window_started_at, window_ended_at, component,
                      component_version, event_count, failure_count, total_duration_ms
               FROM product_health_summaries ORDER BY window_ended_at DESC LIMIT 100"""
        ).fetchall()
    return {"events": [dict(row) for row in events], "summaries": [dict(row) for row in summaries]}
