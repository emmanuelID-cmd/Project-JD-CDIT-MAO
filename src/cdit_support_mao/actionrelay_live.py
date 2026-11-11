"""Authenticated synthetic case-to-Claude checkpoint, with durable run evidence."""
from __future__ import annotations

from contextlib import closing
from datetime import UTC, datetime
import json
import os
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from cdit_support_mao.agents.coordinator import (
    Coordinator, FixtureCaseVersions, FixturePolicyVersions, FixtureSession,
    FixtureSessionAuthority,
)
from cdit_support_mao.agents.coordinator.handoff import HandoffRegistry
from cdit_support_mao.agents.triage.anthropic_client import (
    AnthropicClientConfigurationError, create_anthropic_client,
)
from cdit_support_mao.agents.triage.runtime_harness import MannyA0A2Harness
from cdit_support_mao.actionrelay_outcomes import SENSITIVE_INPUT
from cdit_support_mao.database import connect
from cdit_support_mao.web import Actor, get_case, require_roles, stamp

router = APIRouter()
POLICY = "SYN-ACTIONRELAY-V1"
# All provider input remains synthetic, short, and explicitly billable-authorized.
# Requests matching the shared sensitive-input rule stay on the human route.


class RunAuthorization(BaseModel):
    model_config = ConfigDict(extra="forbid")
    authorize_billable_call: bool


class AuditorFeedback(BaseModel):
    model_config = ConfigDict(extra="forbid")
    note: str = Field(default="", max_length=2000)
    flagged: bool = False


def run_triage(case_id: str, message: str, actor: Actor, client, record_attempt) -> dict:
    """Reuse the existing authorized Coordinator and Triage handoff."""
    case_id = case_id.upper()
    owner, sender, receiver = object(), object(), object()
    sessions = FixtureSessionAuthority(provisioning_capability=owner, ttl_seconds=120)
    token = sessions.issue(
        FixtureSession(actor_id="SYN-ACTOR-" + actor.account_id.removeprefix("SYN-"),
                       role=actor.role, active=True,
                       allowed_case_ids=(case_id,)), capability=owner,
    )
    versions = FixtureCaseVersions(provisioning_capability=owner)
    versions.set_version(case_id, 1, expected_version=None, capability=owner)
    policies = FixturePolicyVersions(provisioning_capability=owner, active=frozenset({POLICY}))
    registry = HandoffRegistry(
        sender_capability=sender, receiver_capability=receiver, timeout_seconds=60,
        actor_sessions=sessions, case_versions=versions, policy_versions=policies,
    )
    harness = MannyA0A2Harness(
        Coordinator(sessions, case_versions=versions, policy_versions=policies), registry,
        sender_capability=sender, receiver_capability=receiver,
    )
    failure_codes: list[str] = []
    result = harness.run(
        {"case_id": case_id, "case_version": 1, "policy_version": POLICY,
         "message": message, "data_classification": "synthetic"},
        session_token=token, client=client, billable_call_authorized=True,
        provider_attempt_observer=record_attempt,
        semantic_failure_observer=failure_codes.append,
    )
    triage = result.triage
    semantic = triage.semantic_result if triage else None
    context = result.intake.context
    return {
        "trace_id": result.intake.trace_id,
        "workflow_run_id": context.run_id if context else None,
        "coordinator": result.intake.status.value,
        "triage": triage.status if triage else "not_run",
        "reason": triage.reason if triage else result.intake.reason_code,
        "validated_model_result": semantic is not None,
        "provider_failure": failure_codes[-1] if failure_codes else None,
        "usage": {"model": semantic.model, "input_tokens": semantic.input_tokens,
                  "output_tokens": semantic.output_tokens, "elapsed_ms": semantic.elapsed_ms}
                 if semantic else None,
        "items": [{"index": item.item_index, "category": item.category_label}
                  for item in triage.candidate.items] if triage else [],
        "next_action": "human_review",
    }


def _run_rows(case_id: str) -> list[dict]:
    with closing(connect()) as db:
        rows = db.execute(
            "SELECT run_id, case_version, status, started_at, completed_at, provider_attempts, result_json "
            "FROM actionrelay_runs WHERE case_id = ? ORDER BY started_at DESC", (case_id,),
        ).fetchall()
    return [{**{key: row[key] for key in row.keys() if key != "result_json"},
             "result": json.loads(row["result_json"])} for row in rows]


@router.get("/api/cases/{case_id}/agent-runs")
def read_runs(case_id: str, actor: Actor = Depends(require_roles("user", "staff", "admin"))):
    get_case(case_id, actor)
    triage_runs = _run_rows(case_id)
    with closing(connect()) as db:
        reviews = db.execute(
            "SELECT run_id, case_version, status, started_at, completed_at, result_json "
            "FROM actionrelay_review_runs WHERE case_id = ? ORDER BY started_at DESC", (case_id,),
        ).fetchall()
        outcome = db.execute(
            "SELECT case_version, route, reason, recorded_at FROM actionrelay_ticket_outcomes WHERE case_id = ?",
            (case_id,),
        ).fetchone()
    # Join persisted checkpoints by the exact case version. A human review can
    # therefore continue the Triage run that paused, and the deterministic
    # outcome gate appears on that same case-version timeline.
    grouped: dict[str, dict] = {}
    for row in triage_runs:
        version = row["case_version"]
        result = row["result"]
        stages = []
        if result.get("coordinator"):
            stages.append({"name": "Coordinator", "status": result["coordinator"]})
        if result.get("triage"):
            stages.append({"name": "Claude Triage", "status": result["triage"]})
        grouped[version] = {
            "run_id": row["run_id"], "case_version": version,
            "status": row["status"], "started_at": row["started_at"],
            "completed_at": row["completed_at"], "provider_attempts": row["provider_attempts"],
            "result": {**result, "stages": stages},
        }
    for row in reviews:
        version = row["case_version"]
        review_result = json.loads(row["result_json"])
        workflow = grouped.setdefault(version, {
            "run_id": row["run_id"], "case_version": version,
            "status": row["status"], "started_at": row["started_at"],
            "completed_at": row["completed_at"], "provider_attempts": 0,
            "result": {"stages": []},
        })
        workflow["result"]["stages"].append({
            "name": "Auditor decision", "status": "recorded",
            "decision_id": review_result.get("decision_id"),
            "decision_version": review_result.get("decision_version"),
        })
        workflow["result"]["stages"].extend(review_result.get("stages", []))
        workflow["result"]["decision_id"] = review_result.get("decision_id")
        workflow["review_run_id"] = row["run_id"]
        workflow["status"] = row["status"]
        workflow["completed_at"] = row["completed_at"] or workflow["completed_at"]
        if row["started_at"] < workflow["started_at"]:
            workflow["started_at"] = row["started_at"]
    if outcome:
        workflow = grouped.setdefault(outcome["case_version"], {
            "run_id": "AR-OUTCOME-" + case_id, "case_version": outcome["case_version"],
            "status": "human_review", "started_at": outcome["recorded_at"],
            "completed_at": outcome["recorded_at"], "provider_attempts": 0,
            "result": {"stages": []},
        })
        with closing(connect()) as db:
            current = db.execute("SELECT status FROM synthetic_cases WHERE case_id = ?", (case_id,)).fetchone()
        resource_delivered = outcome["route"] in {"routine_form", "resource_link"}
        resolved = bool(resource_delivered and current and current["status"] in {"resolved", "closed"})
        workflow["result"]["stages"].append({
            "name": "Application outcome",
            "status": "resolved" if resolved else ("delivered_open" if resource_delivered else "human_review"),
        })
        workflow["result"]["outcome_reason"] = outcome["reason"]
        if resolved:
            workflow["status"] = "resolved"
        workflow["completed_at"] = outcome["recorded_at"]
    rows = sorted(grouped.values(), key=lambda row: row["started_at"], reverse=True)
    if actor.role == "user":
        return [{key: row[key] for key in ("run_id", "status", "started_at", "completed_at")}
                for row in rows]
    return rows


@router.post("/api/cases/{case_id}/agent-runs", status_code=201)
def start_run(case_id: str, payload: RunAuthorization,
              actor: Actor = Depends(require_roles("admin"))):
    if not payload.authorize_billable_call:
        raise HTTPException(422, "Confirm authorization for one billable Claude call.")
    if os.environ.get("ACTIONRELAY_ENABLE_LIVE_TRIAGE") != "1":
        raise HTTPException(503, "Live Triage is disabled on this server.")
    case = get_case(case_id, actor)
    if (case["record_kind"] != "user_request" or case["status"] != "submitted"
            or case["is_synthetic"] != 1 or len(case["request_text"]) > 2000):
        raise HTTPException(422, "Live Triage requires a submitted synthetic request of 2,000 characters or fewer.")
    if SENSITIVE_INPUT.search(case["request_text"]):
        raise HTTPException(422, "This request may contain personal or sensitive information. It remains for human review and was not sent to Claude.")
    try:
        client = create_anthropic_client()
    except AnthropicClientConfigurationError:
        raise HTTPException(503, "Claude is not configured on this server.") from None
    with client:
        run_id = "AR-RUN-" + uuid4().hex
        with closing(connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            inserted = db.execute(
                """INSERT OR IGNORE INTO actionrelay_runs
                   (run_id, case_id, case_version, actor_account_id, status, started_at)
                   SELECT ?, case_id, updated_at, ?, 'running', ? FROM synthetic_cases
                   WHERE case_id = ? AND updated_at = ? AND status = 'submitted'
                     AND is_synthetic = 1""",
                (run_id, actor.account_id, stamp(datetime.now(UTC)), case_id, case["updated_at"]),
            ).rowcount
        if not inserted:
            raise HTTPException(409, "This case changed or its current version already has a run.")

        def record_attempt() -> None:
            with closing(connect()) as db, db:
                db.execute("BEGIN IMMEDIATE")
                updated = db.execute(
                    """UPDATE actionrelay_runs SET provider_attempts = 1
                       WHERE run_id = ? AND provider_attempts = 0
                       AND EXISTS (SELECT 1 FROM synthetic_cases
                           WHERE case_id = ? AND updated_at = ? AND status = 'submitted')
                       AND EXISTS (SELECT 1 FROM synthetic_accounts
                           WHERE account_id = ? AND role = 'admin' AND status = 'active')""",
                    (run_id, case_id, case["updated_at"], actor.account_id),
                ).rowcount
                if not updated:
                    raise RuntimeError("live_triage_authority_changed")

        try:
            result = run_triage(case_id, case["request_text"], actor, client, record_attempt)
            status = "human_review" if result["validated_model_result"] else "blocked"
        except Exception:
            # Store a bounded failure reason. SDK exceptions may contain sensitive details.
            result = {"reason": "workflow_execution_failed", "next_action": "human_review"}
            status = "blocked"
        with closing(connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute(
                "SELECT updated_at FROM synthetic_cases WHERE case_id = ?", (case_id,),
            ).fetchone()
            if current is None:
                raise HTTPException(404, "Case no longer exists.")
            if current["updated_at"] != case["updated_at"]:
                status = "stale"
                result = {"reason": "case_changed_during_run", "next_action": "human_review"}
            db.execute(
                "UPDATE actionrelay_runs SET status = ?, completed_at = ?, result_json = ? "
                "WHERE run_id = ?",
                (status, stamp(datetime.now(UTC)), json.dumps(result), run_id),
            )
    return next(row for row in _run_rows(case_id) if row["run_id"] == run_id)


@router.get("/api/auditor/feedback")
def read_feedback(actor: Actor = Depends(require_roles("staff", "admin"))):
    if actor.role != "admin" and not actor.auditor:
        raise HTTPException(403, "Auditor capability required.")
    with closing(connect()) as db:
        return [dict(row) for row in db.execute(
            """SELECT f.*, d.case_id, d.item_id, d.decision_version
               FROM actionrelay_auditor_feedback f
               JOIN synthetic_auditor_decisions d ON d.decision_id = f.decision_id
               WHERE ? = 'admin' OR d.reviewer_account_id = ?
               ORDER BY f.created_at DESC""", (actor.role, actor.account_id),
        )]


@router.post("/api/admin/auditor-decisions/{decision_id}/feedback", status_code=201)
def add_feedback(decision_id: str, payload: AuditorFeedback,
                 actor: Actor = Depends(require_roles("admin"))):
    note = payload.note.strip()
    feedback_id = "AR-FB-" + uuid4().hex
    with closing(connect()) as db, db:
        db.execute("BEGIN IMMEDIATE")
        previous = db.execute(
            "SELECT flagged FROM actionrelay_auditor_feedback WHERE decision_id = ? "
            "ORDER BY created_at DESC LIMIT 1", (decision_id,),
        ).fetchone()
        if not note and bool(previous and previous["flagged"]) == payload.flagged:
            raise HTTPException(422, "Enter a note or change the flag.")
        inserted = db.execute(
            """INSERT INTO actionrelay_auditor_feedback
               (feedback_id, decision_id, author_account_id, note, flagged, created_at)
               SELECT ?, decision_id, ?, ?, ?, ? FROM synthetic_auditor_decisions
               WHERE decision_id = ?""",
            (feedback_id, actor.account_id, note, int(payload.flagged),
             stamp(datetime.now(UTC)), decision_id),
        ).rowcount
        if not inserted:
            raise HTTPException(404, "Decision version not found.")
    return {"feedback_id": feedback_id, "decision_id": decision_id}


@router.get("/api/auditor/accounts")
def read_auditor_accounts(actor: Actor = Depends(require_roles("staff"))):
    if not actor.auditor:
        raise HTTPException(403, "Auditor capability required.")
    with closing(connect()) as db:
        return [dict(row) for row in db.execute(
            "SELECT username, role, status, auditor_access FROM synthetic_accounts ORDER BY username"
        )]
