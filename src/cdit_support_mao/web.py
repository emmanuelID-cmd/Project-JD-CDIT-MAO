"""Local-only synthetic authentication and protected support API."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import uuid
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    with closing(connect()) as db, db:
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
    auditor: bool = False


class LoginPayload(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=1, max_length=128)


class SupportRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=160)
    request_text: str = Field(min_length=1, max_length=12000)



class CaseEditPayload(BaseModel):
    subject: str | None = Field(default=None, min_length=1, max_length=160)
    request_text: str | None = Field(default=None, min_length=1, max_length=12000)


class CaseAssignmentPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    staff_account_id: str | None = Field(default=None, min_length=3, max_length=64)


class StatusUpdatePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal[
        "submitted", "in_progress", "waiting_on_customer", "under_investigation",
        "escalated", "resolved", "closed",
    ] | None = None
    response: str | None = Field(default=None, min_length=1, max_length=4000)


class AuditorDecisionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_id: str = Field(min_length=1, max_length=128)
    item_index: int = Field(ge=1, le=8)
    item_count: int = Field(ge=1, le=8)
    expected_previous_decision_version: int = Field(default=0, ge=0)
    expected_case_version: str = Field(min_length=1, max_length=64)
    source_id: str = Field(min_length=1, max_length=128)
    source_version: str = Field(min_length=1, max_length=64)
    source_start: int = Field(ge=0)
    source_end: int = Field(gt=0)
    policy_version: str = Field(min_length=1, max_length=64)
    category: str = Field(min_length=1, max_length=120)
    urgency_band: Literal["low", "medium", "high"]
    destination: str = Field(min_length=1, max_length=120)
    rationale: str = Field(min_length=1, max_length=2000)
    evidence: str = Field(min_length=1, max_length=2000)
    admin_override_reason: str | None = Field(default=None, min_length=1, max_length=500)
    conditions: list[str] = Field(default_factory=list, max_length=20)
    exceptions: list[str] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def validate_item_scope(self):
        if self.item_index > self.item_count:
            raise ValueError("item_index must not exceed item_count")
        if self.source_end <= self.source_start:
            raise ValueError("source_end must be after source_start")
        for values in (self.conditions, self.exceptions):
            if any(not item.strip() or len(item) > 240 for item in values):
                raise ValueError("conditions and exceptions must be non-empty and at most 240 characters")
        for field in ("item_id", "source_id", "source_version", "policy_version", "category", "destination", "rationale", "evidence"):
            value = getattr(self, field).strip()
            if not value:
                raise ValueError(f"{field} must not be blank")
            setattr(self, field, value)
        self.conditions = [item.strip() for item in self.conditions]
        self.exceptions = [item.strip() for item in self.exceptions]
        if self.admin_override_reason is not None:
            self.admin_override_reason = self.admin_override_reason.strip() or None
        return self


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
    with closing(connect()) as db, db:
        row = db.execute(
            """SELECT s.session_id, s.issued_at, s.last_activity_at, s.absolute_expires_at,
                      s.warned_15m, s.warned_5m, s.revoked_at,
                      a.account_id, a.username, a.role, a.status, a.auditor_access
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
        actor = Actor(row["account_id"], row["username"], row["role"],
                      row["role"] == "staff" and bool(row["auditor_access"]))
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
    with closing(connect()) as db, db:
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
        with closing(connect()) as db, db:
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
    return {"account_id": actor.account_id, "username": actor.username, "role": actor.role, "auditor": actor.auditor}


@router.post("/auth/continue")
def continue_session(request: Request, actor: Actor = Depends(current_actor)):
    # An authenticated user action resets only the idle timer; the absolute deadline remains fixed.
    _actor, state = _session_context(request, touch=True)
    return state


@router.post("/auth/extension-request")
def request_extension(request: Request, actor: Actor = Depends(current_actor)):
    _actor, state = _session_context(request, touch=False)
    with closing(connect()) as db, db:
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


ALLOWED_STATUS_TRANSITIONS = {
    "submitted": {"in_progress", "closed"},
    "in_progress": {"waiting_on_customer", "under_investigation", "escalated", "resolved", "closed"},
    "waiting_on_customer": {"in_progress", "under_investigation", "escalated", "resolved", "closed"},
    "under_investigation": {"in_progress", "escalated", "resolved", "closed"},
    "escalated": {"in_progress", "under_investigation", "resolved", "closed"},
    "resolved": {"in_progress", "closed"},
    "closed": set(),
}


def _case_change_event(
    db: sqlite3.Connection, *, case_id: str, actor: Actor, action: str,
    before_status: str | None, after_status: str, reason_code: str,
    subject_changed: bool = False, request_text_changed: bool = False,
) -> None:
    db.execute(
        """INSERT INTO synthetic_case_change_events
           (event_id, case_id, actor_account_id, action, before_status, after_status,
            subject_changed, request_text_changed, reason_code, occurred_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("CASE-EVT-" + uuid.uuid4().hex, case_id, actor.account_id, action,
         before_status, after_status, int(subject_changed), int(request_text_changed),
         reason_code, stamp(now_utc())),
    )


def _case_for_role(row: sqlite3.Row, role: str, *, auditor: bool = False) -> dict:
    result = dict(row)
    if result.get("delivery_links_json") is not None:
        try:
            result["reply_links"] = json.loads(result.pop("delivery_links_json") or "[]")
        except (TypeError, json.JSONDecodeError):
            result["reply_links"] = []
    if role == "user":
        result.pop("reply_basis_case_id", None)
        result.pop("assigned_staff_account_id", None)
        result.pop("assigned_staff_username", None)
    result["display_status"] = (
        "in_review" if role == "user" and result["status"] == "in_progress" else result["status"]
    )
    result["can_edit"] = bool(
        role == "user" and result["record_kind"] == "user_request" and result["status"] == "submitted"
    )
    result["can_cancel"] = bool(
        role == "user" and result["record_kind"] == "user_request"
        and result["status"] not in {"resolved", "closed"}
        and not result.get("withdrawal_requested_at")
    )
    classified = result["urgency_band"] != "unknown" and bool(result["category"])
    result["review_flag"] = result["status"] == "resolved"
    result["allowed_next_statuses"] = (
        sorted(status for status in ALLOWED_STATUS_TRANSITIONS[result["status"]]
               if classified or status not in {"resolved", "closed"})
        if role in {"staff", "admin"} else []
    )
    return result


def _attach_case_responses(cases: list[dict]) -> list[dict]:
    """Attach separately stored staff replies without changing request text."""
    for case in cases:
        case["responses"] = []
    case_ids = [case["case_id"] for case in cases]
    for offset in range(0, len(case_ids), 400):
        batch = case_ids[offset:offset + 400]
        if not batch:
            continue
        placeholders = ",".join("?" for _ in batch)
        with closing(connect()) as db:
            rows = db.execute(
                f"""SELECT r.case_id, r.response_id, r.case_version, r.response_text,
                           r.created_at, a.username AS responded_by
                    FROM synthetic_case_responses r
                    JOIN synthetic_accounts a ON a.account_id = r.author_account_id
                    WHERE r.case_id IN ({placeholders})
                    ORDER BY r.created_at, r.response_id""",
                batch,
            ).fetchall()
        grouped: dict[str, list[dict]] = {}
        for row in rows:
            grouped.setdefault(row["case_id"], []).append({key: row[key] for key in row.keys()})
        for case in cases[offset:offset + 400]:
            case["responses"] = grouped.get(case["case_id"], [])
    return cases


@router.get("/api/cases")
def list_cases(actor: Actor = Depends(require_roles("user", "staff", "admin"))):
    query = """SELECT c.case_id, c.owner_account_id, c.subject, c.request_text, c.status,
                      c.urgency_band, c.created_at, c.updated_at, c.record_kind, c.category,
                      c.catalog_id, c.closure_reason, c.withdrawal_requested_at, c.assigned_staff_account_id,
                      assigned.username AS assigned_staff_username,
                      cat.rationale AS catalog_rationale, outcome.route AS reply_route, outcome.reply,
                      outcome.source_url AS reply_url, outcome.reason AS reply_reason,
                      outcome.delivery_links_json, outcome.resolution_basis_case_id AS reply_basis_case_id
               FROM synthetic_cases c
               LEFT JOIN actionrelay_ticket_outcomes outcome ON outcome.case_id = c.case_id
               LEFT JOIN synthetic_case_catalog cat ON cat.catalog_id = c.catalog_id
               LEFT JOIN synthetic_accounts assigned ON assigned.account_id = c.assigned_staff_account_id"""
    with closing(connect()) as db, db:
        if actor.role == "user":
            rows = db.execute(
                query + " WHERE c.owner_account_id = ? AND c.record_kind = 'user_request' ORDER BY c.updated_at DESC",
                (actor.account_id,),
            ).fetchall()
        elif actor.role == "staff" and not actor.auditor:
            rows = db.execute(
                query + " WHERE c.assigned_staff_account_id = ? ORDER BY c.updated_at DESC",
                (actor.account_id,),
            ).fetchall()
        else:
            rows = db.execute(query + " ORDER BY c.updated_at DESC").fetchall()
    return _attach_case_responses([
        _case_for_role(row, actor.role, auditor=actor.auditor) for row in rows
    ])


@router.get("/api/auditor/taxonomy")
def auditor_taxonomy(actor: Actor = Depends(require_roles("staff", "admin"))):
    """Return the approved synthetic category vocabulary used by the local case catalog."""
    with closing(connect()) as db, db:
        rows = db.execute(
            "SELECT DISTINCT category FROM synthetic_case_catalog ORDER BY category COLLATE NOCASE"
        ).fetchall()
    return {"categories": [row["category"] for row in rows]}


@router.get("/api/auditor/decisions")
def list_auditor_decisions(actor: Actor = Depends(require_roles("staff", "admin"))):
    """List decision history visible to the assigned Staff member or Admin."""
    with closing(connect()) as db, db:
        rows = db.execute(
            """SELECT d.decision_id, d.case_id, d.item_id, d.decision_version,
                      d.item_index, d.item_count, d.case_version, d.source_id,
                      d.source_version, d.source_start, d.source_end, d.source_digest_sha256,
                      d.policy_version, d.category, d.urgency_band, d.destination,
                      d.rationale, d.evidence, d.conditions_json, d.exceptions_json,
                      d.reviewer_account_id, d.recorded_at, d.admin_override_reason
               FROM synthetic_auditor_decisions d
               JOIN synthetic_cases c ON c.case_id = d.case_id
               WHERE (? = 'admin' OR c.assigned_staff_account_id = ?)
               ORDER BY d.recorded_at DESC, d.decision_id""",
            (actor.role, actor.account_id),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["conditions"] = json.loads(item.pop("conditions_json"))
        item["exceptions"] = json.loads(item.pop("exceptions_json"))
        result.append(item)
    return result


@router.post("/api/cases/{case_id}/items/auditor-decisions", status_code=201)
def record_auditor_decision(
    case_id: str, payload: AuditorDecisionPayload,
    actor: Actor = Depends(require_roles("staff", "admin")),
):
    """Record a human item-level routing decision without changing the ticket."""
    now = stamp(now_utc())
    if actor.role != "admin" and not actor.auditor:
        raise HTTPException(403, "Auditor capability required.")
    decision_id = "AUD-" + uuid.uuid4().hex
    if actor.role == "admin" and not payload.admin_override_reason:
        raise HTTPException(status_code=422, detail="Admin decisions require an override reason")
    if actor.role == "staff" and payload.admin_override_reason is not None:
        raise HTTPException(status_code=422, detail="Only Admin may record an override reason")
    with closing(connect()) as db, db:
        db.execute("BEGIN IMMEDIATE")
        case = db.execute(
            "SELECT request_text, updated_at, is_synthetic, status, category, urgency_band FROM synthetic_cases WHERE case_id = ? AND (? = 'admin' OR assigned_staff_account_id = ?)",
            (case_id, actor.role, actor.account_id),
        ).fetchone()
        if case is None or case["is_synthetic"] != 1:
            db.rollback()
            raise HTTPException(status_code=404, detail="Synthetic case not found")
        if case["status"] == "closed":
            raise HTTPException(409, "Closed cases are read-only.")
        if case["updated_at"] != payload.expected_case_version:
            db.rollback()
            raise HTTPException(status_code=409, detail="Case changed since this review form was loaded; refresh and review again")
        if payload.source_end > len(case["request_text"]):
            db.rollback()
            raise HTTPException(status_code=422, detail="Source span is outside the current case text")
        item_text = case["request_text"][payload.source_start:payload.source_end]
        if not item_text.strip():
            db.rollback()
            raise HTTPException(status_code=422, detail="Source span must identify non-empty case text")
        category = db.execute(
            "SELECT 1 FROM synthetic_case_catalog WHERE category = ? COLLATE NOCASE LIMIT 1",
            (payload.category,),
        ).fetchone()
        if category is None:
            db.rollback()
            raise HTTPException(status_code=422, detail="Choose a category from the synthetic taxonomy")
        latest = db.execute(
            "SELECT decision_version, reviewer_account_id, admin_override_reason "
            "FROM synthetic_auditor_decisions WHERE case_id = ? AND item_id = ? "
            "ORDER BY decision_version DESC LIMIT 1",
            (case_id, payload.item_id),
        ).fetchone()
        if actor.auditor and latest and (
            latest["reviewer_account_id"] != actor.account_id or latest["admin_override_reason"]
        ):
            raise HTTPException(403, "You can revise only your own current decisions.")
        previous = latest["decision_version"] if latest else 0
        if previous != payload.expected_previous_decision_version:
            db.rollback()
            raise HTTPException(status_code=409, detail="A newer decision exists; refresh the decision history")
        source_digest = hashlib.sha256(case["request_text"].encode("utf-8")).hexdigest()
        classification_changed = (
            case["category"] != payload.category or case["urgency_band"] != payload.urgency_band
        )
        decision_case_version = stamp(now_utc()) if classification_changed else case["updated_at"]
        if classification_changed:
            db.execute(
                "UPDATE synthetic_cases SET category = ?, urgency_band = ?, updated_at = ? WHERE case_id = ? AND updated_at = ?",
                (payload.category, payload.urgency_band, decision_case_version, case_id, case["updated_at"]),
            )
        db.execute(
            """INSERT INTO synthetic_auditor_decisions
               (decision_id, case_id, item_id, decision_version, item_index, item_count,
                case_version, source_id, source_version, source_start, source_end,
                source_digest_sha256, policy_version, category, urgency_band, destination,
                 rationale, evidence, conditions_json, exceptions_json, reviewer_account_id,
                 admin_override_reason, recorded_at, is_synthetic)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                decision_id, case_id, payload.item_id, previous + 1, payload.item_index,
                payload.item_count, decision_case_version, payload.source_id, payload.source_version,
                payload.source_start, payload.source_end, source_digest, payload.policy_version,
                payload.category, payload.urgency_band, payload.destination, payload.rationale,
                payload.evidence, json.dumps(payload.conditions, ensure_ascii=False, separators=(",", ":")),
                json.dumps(payload.exceptions, ensure_ascii=False, separators=(",", ":")),
                actor.account_id, payload.admin_override_reason, now,
            ),
        )
        db.commit()
    return {
        "decision_id": decision_id, "case_id": case_id, "item_id": payload.item_id,
        "decision_version": previous + 1, "reviewer_account_id": actor.account_id,
        "admin_override_reason": payload.admin_override_reason,
        "recorded_at": now, "ticket_changed": classification_changed,
        "classification_changed": classification_changed,
        "category": payload.category, "urgency_band": payload.urgency_band,
    }


@router.post("/api/cases", status_code=201)
def submit_case(payload: SupportRequest, actor: Actor = Depends(require_roles("user"))):
    case_id = "SYN-CASE-" + uuid.uuid4().hex
    now = stamp(now_utc())
    subject = payload.subject.strip()
    request_text = payload.request_text.strip()
    if not subject or not request_text:
        raise HTTPException(status_code=422, detail="Subject and request are required")
    with closing(connect()) as db, db:
        db.execute("BEGIN IMMEDIATE")
        db.execute(
            """INSERT INTO synthetic_cases
               (case_id, owner_account_id, subject, request_text, status, urgency_band,
                is_synthetic, created_at, updated_at, record_kind)
               VALUES (?, ?, ?, ?, 'submitted', 'unknown', 1, ?, ?, 'user_request')""",
            (case_id, actor.account_id, subject, request_text, now, now),
        )
        _case_change_event(
            db, case_id=case_id, actor=actor, action="user_submitted",
            before_status=None, after_status="submitted", reason_code="initial_submission",
        )
        db.commit()
    from cdit_support_mao.actionrelay_outcomes import apply_intake_outcome

    return {"case_id": case_id, **apply_intake_outcome(case_id, now, request_text, actor)}


@router.get("/api/cases/{case_id}")
def get_case(case_id: str, actor: Actor = Depends(require_roles("user", "staff", "admin"))):
    with closing(connect()) as db, db:
        if actor.role == "user":
            row = db.execute(
                """SELECT c.*, cat.rationale AS catalog_rationale FROM synthetic_cases c
                   LEFT JOIN synthetic_case_catalog cat ON cat.catalog_id = c.catalog_id
                   WHERE c.case_id = ? AND c.owner_account_id = ? AND c.record_kind = 'user_request'""",
                (case_id, actor.account_id),
            ).fetchone()
        elif actor.role == "admin" or actor.auditor:
            row = db.execute(
                """SELECT c.*, cat.rationale AS catalog_rationale FROM synthetic_cases c
                   LEFT JOIN synthetic_case_catalog cat ON cat.catalog_id = c.catalog_id
                   WHERE c.case_id = ?""",
                (case_id,),
            ).fetchone()
        else:
            row = db.execute(
                """SELECT c.*, cat.rationale AS catalog_rationale,
                          assigned.username AS assigned_staff_username
                   FROM synthetic_cases c
                   LEFT JOIN synthetic_case_catalog cat ON cat.catalog_id = c.catalog_id
                   LEFT JOIN synthetic_accounts assigned ON assigned.account_id = c.assigned_staff_account_id
                   WHERE c.case_id = ? AND c.assigned_staff_account_id = ?""",
                (case_id, actor.account_id),
            ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return _attach_case_responses([_case_for_role(row, actor.role, auditor=actor.auditor)])[0]


@router.patch("/api/cases/{case_id}")
def edit_case(case_id: str, payload: CaseEditPayload, actor: Actor = Depends(require_roles("user", "staff", "admin"))):
    if actor.role != "user":
        raise HTTPException(403, "Staff, Auditors, and Admin respond to the request; they cannot rewrite it.")
    fields = payload.model_fields_set
    if not fields:
        raise HTTPException(status_code=422, detail="Provide a subject or request description")
    subject_changed = "subject" in fields
    request_changed = "request_text" in fields
    subject = payload.subject.strip() if subject_changed and payload.subject is not None else None
    request_text = payload.request_text.strip() if request_changed and payload.request_text is not None else None
    if subject_changed and not subject or request_changed and not request_text:
        raise HTTPException(status_code=422, detail="Subject and request description cannot be blank")
    with closing(connect()) as db, db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            """SELECT status, record_kind, subject, request_text FROM synthetic_cases
               WHERE case_id = ? AND owner_account_id = ? AND record_kind = 'user_request'""",
            (case_id, actor.account_id),
        ).fetchone()
        if row is None:
            db.rollback()
            raise HTTPException(status_code=404, detail="Case not found")
        if row["status"] == "closed":
            raise HTTPException(409, "Closed cases are read-only.")
        if actor.role == "user" and row["status"] != "submitted":
            db.rollback()
            raise HTTPException(status_code=409, detail="This request is in review and can no longer be edited")
        updates = []
        values = []
        if subject_changed:
            updates.append("subject = ?")
            values.append(subject)
        if request_changed:
            updates.append("request_text = ?")
            values.append(request_text)
        updates.append("updated_at = ?")
        values.extend([stamp(now_utc()), case_id])
        db.execute("UPDATE synthetic_cases SET " + ", ".join(updates) + " WHERE case_id = ?", values)
        action = "user_edited" if actor.role == "user" else actor.role + "_edited"
        _case_change_event(
            db, case_id=case_id, actor=actor, action=action,
            before_status=row["status"], after_status=row["status"],
            reason_code="content_correction", subject_changed=subject_changed,
            request_text_changed=request_changed,
        )
        db.commit()
    return {"case_id": case_id, "updated": True, "status": row["status"]}


@router.post("/api/cases/{case_id}/cancel")
def cancel_case(case_id: str, actor: Actor = Depends(require_roles("user"))):
    with closing(connect()) as db, db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            """SELECT status, withdrawal_requested_at FROM synthetic_cases WHERE case_id = ?
               AND owner_account_id = ? AND record_kind = 'user_request'""",
            (case_id, actor.account_id),
        ).fetchone()
        if row is None:
            db.rollback()
            raise HTTPException(status_code=404, detail="Case not found")
        if row["status"] in {"resolved", "closed"}:
            db.rollback()
            raise HTTPException(status_code=409, detail="This request is already complete and cannot be cancelled")
        if row["withdrawal_requested_at"]:
            return {"case_id": case_id, "status": row["status"], "withdrawal_requested": True}
        now = stamp(now_utc())
        db.execute(
            "UPDATE synthetic_cases SET withdrawal_requested_at = ?, updated_at = ? WHERE case_id = ?",
            (now, now, case_id),
        )
        _case_change_event(
            db, case_id=case_id, actor=actor, action="requester_cancelled",
            before_status=row["status"], after_status=row["status"],
            reason_code="requester_cancellation",
        )
        db.commit()
    return {"case_id": case_id, "status": row["status"], "withdrawal_requested": True}


@router.patch("/api/cases/{case_id}/status")
def update_case_status(
    case_id: str, payload: StatusUpdatePayload,
    actor: Actor = Depends(require_roles("staff", "admin")),
):
    response_text = payload.response.strip() if payload.response is not None else None
    if payload.response is not None and not response_text:
        raise HTTPException(422, "Write a response or leave the response field blank.")
    if payload.status is None and response_text is None:
        raise HTTPException(422, "Provide a response, a status update, or both.")
    with closing(connect()) as db, db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            """SELECT status, category, urgency_band, updated_at FROM synthetic_cases
               WHERE case_id = ? AND (? = 'admin' OR assigned_staff_account_id = ?)""",
            (case_id, actor.role, actor.account_id),
        ).fetchone()
        if row is None:
            db.rollback()
            raise HTTPException(status_code=404, detail="Case not found")
        before = row["status"]
        after = payload.status or before
        changed = after != before
        if changed and not response_text:
            db.rollback()
            raise HTTPException(422, "Include a response whenever you change ticket status.")
        if changed and after not in ALLOWED_STATUS_TRANSITIONS[before]:
            db.rollback()
            raise HTTPException(status_code=409, detail=f"Status transition from {before} to {after} is not allowed")
        if changed and after in {"resolved", "closed"} and (not row["category"] or row["urgency_band"] == "unknown"):
            raise HTTPException(409, "Classify the case before resolving or closing it.")
        response_id = None
        new_version = row["updated_at"]
        if changed:
            new_version = stamp(now_utc())
            db.execute(
                "UPDATE synthetic_cases SET status = ?, closure_reason = ?, updated_at = ? WHERE case_id = ?",
                (after, "staff_closed" if after == "closed" and actor.role == "staff"
                 else "admin_closed" if after == "closed" else None, new_version, case_id),
            )
        if response_text:
            response_id = "CASE-RESPONSE-" + uuid.uuid4().hex
            db.execute(
                """INSERT INTO synthetic_case_responses
                   (response_id, case_id, case_version, author_account_id, response_text, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (response_id, case_id, new_version, actor.account_id, response_text, stamp(now_utc())),
            )
        if not changed:
            return {"case_id": case_id, "status": before, "changed": False,
                    "response_id": response_id}
        action = actor.role + "_status_updated"
        _case_change_event(
            db, case_id=case_id, actor=actor, action=action,
            before_status=before, after_status=after, reason_code="human_status_change",
        )
        db.commit()
    return {"case_id": case_id, "status": after, "changed": changed,
            "response_id": response_id}


@router.patch("/api/admin/cases/{case_id}/assignment")
def assign_case(
    case_id: str, payload: CaseAssignmentPayload,
    actor: Actor = Depends(require_roles("admin")),
):
    """Assign or unassign a synthetic case and append an Admin-attributed event."""
    now = stamp(now_utc())
    event_id = "CASE-ASG-" + uuid.uuid4().hex
    with closing(connect()) as db, db:
        db.execute("BEGIN IMMEDIATE")
        case = db.execute(
            "SELECT assigned_staff_account_id FROM synthetic_cases WHERE case_id = ? AND is_synthetic = 1",
            (case_id,),
        ).fetchone()
        if case is None:
            db.rollback()
            raise HTTPException(status_code=404, detail="Synthetic case not found")
        previous = case["assigned_staff_account_id"]
        new_assignee = payload.staff_account_id
        if new_assignee == previous:
            db.rollback()
            return {"case_id": case_id, "staff_account_id": previous, "changed": False}
        if new_assignee is not None:
            account = db.execute(
                "SELECT role, status FROM synthetic_accounts WHERE account_id = ?",
                (new_assignee,),
            ).fetchone()
            if account is None or account["role"] != "staff" or account["status"] != "active":
                db.rollback()
                raise HTTPException(status_code=422, detail="Choose an active Staff account")
        action = "unassigned" if new_assignee is None else "reassigned" if previous else "assigned"
        db.execute(
            "UPDATE synthetic_cases SET assigned_staff_account_id = ? WHERE case_id = ?",
            (new_assignee, case_id),
        )
        db.execute(
            """INSERT INTO synthetic_case_assignment_events
               (event_id, case_id, actor_account_id, previous_staff_account_id,
                assigned_staff_account_id, action, occurred_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (event_id, case_id, actor.account_id,
             previous, new_assignee, action, now),
        )
        db.commit()
    return {"event_id": event_id, "case_id": case_id, "staff_account_id": new_assignee, "changed": True, "action": action}


@router.get("/api/admin/case-assignment-events")
def list_case_assignment_events(actor: Actor = Depends(require_roles("admin"))):
    with closing(connect()) as db, db:
        rows = db.execute(
            """SELECT e.event_id, e.case_id, e.actor_account_id,
                      actor.username AS actor_username, e.previous_staff_account_id,
                      previous.username AS previous_staff_username,
                      e.assigned_staff_account_id, assigned.username AS assigned_staff_username,
                      e.action, e.occurred_at
               FROM synthetic_case_assignment_events e
               LEFT JOIN synthetic_accounts actor ON actor.account_id = e.actor_account_id
               LEFT JOIN synthetic_accounts previous ON previous.account_id = e.previous_staff_account_id
               LEFT JOIN synthetic_accounts assigned ON assigned.account_id = e.assigned_staff_account_id
               ORDER BY e.occurred_at DESC, e.event_id"""
        ).fetchall()
    return [dict(row) for row in rows]


@router.get("/api/admin/accounts")
def list_accounts(actor: Actor = Depends(require_roles("admin"))):
    with closing(connect()) as db, db:
        rows = db.execute(
            "SELECT account_id, username, role, status, created_at, updated_at FROM synthetic_accounts ORDER BY username"
        ).fetchall()
    return [dict(row) for row in rows]


@router.patch("/api/admin/accounts/{account_id}")
def change_account(account_id: str, payload: AccountChange, actor: Actor = Depends(require_roles("admin"))):
    if payload.role is None and payload.status is None:
        raise HTTPException(status_code=422, detail="At least one account field is required")
    now = stamp(now_utc())
    with closing(connect()) as db, db:
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
    with closing(connect()) as db, db:
        rows = db.execute(
            """SELECT x.alert_id, x.session_id, x.account_id, a.username, x.requested_at,
                      x.review_status, x.reviewed_at
               FROM session_extension_alerts x JOIN synthetic_accounts a ON a.account_id = x.account_id
               ORDER BY x.requested_at DESC LIMIT 100"""
        ).fetchall()
    return [dict(row) for row in rows]


@router.patch("/api/admin/session-extension-alerts/{alert_id}/review")
def review_extension_alert(alert_id: str, actor: Actor = Depends(require_roles("admin"))):
    with closing(connect()) as db, db:
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
    with closing(connect()) as db, db:
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
        workflow_events = db.execute(
            """WITH workflow(event_id, case_id, occurred_at, event_type, component, status_code) AS (
                   SELECT run_id, case_id, completed_at, 'triage_run', 'Claude Triage', status
                   FROM actionrelay_runs WHERE completed_at IS NOT NULL
                   UNION ALL
                   SELECT run_id, case_id, completed_at, 'review_run', 'Downstream review', status
                   FROM actionrelay_review_runs WHERE completed_at IS NOT NULL
                   UNION ALL
                   SELECT 'AR-OUTCOME-' || case_id, case_id, recorded_at, 'intake_outcome',
                          'Application outcome', route FROM actionrelay_ticket_outcomes
               )
               SELECT w.event_id, w.occurred_at, w.event_type, w.component, '1.0' AS component_version,
                      w.status_code, NULL AS error_code, NULL AS duration_ms
               FROM workflow w JOIN synthetic_cases c ON c.case_id = w.case_id
               WHERE w.occurred_at >= ? AND (? OR c.assigned_staff_account_id = ?)
               ORDER BY w.occurred_at DESC LIMIT 100""",
            (stamp(now_utc() - timedelta(days=30)), actor.role == "admin" or actor.auditor, actor.account_id),
        ).fetchall()
    merged = sorted((dict(row) for row in [*events, *workflow_events]),
                    key=lambda row: row["occurred_at"], reverse=True)
    return {"events": merged[:100], "summaries": [dict(row) for row in summaries]}
