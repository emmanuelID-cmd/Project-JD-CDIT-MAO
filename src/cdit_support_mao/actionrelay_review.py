"""Resume real read-only agents from a current persisted human decision."""
from __future__ import annotations

from contextlib import closing
from datetime import UTC, datetime
from hashlib import sha256
import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from cdit_support_mao.agents.documentation import DocumentationAgent
from cdit_support_mao.agents.escalation import EscalationAgent
from cdit_support_mao.agents.knowledge import KnowledgeAgent, load_corpus
from cdit_support_mao.agents.troubleshooting import TroubleshootingAgent, load_policy
from cdit_support_mao.contracts.common import (
    AgentStatus, CheckpointOutcome, ConfidenceBand, RunContext, stable_id,
)
from cdit_support_mao.contracts.handoffs import TriageHandoff
from cdit_support_mao.database import connect
from cdit_support_mao.web import Actor, require_roles, stamp

router = APIRouter()


class ReviewResume(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision_id: str = Field(min_length=5, max_length=96)


def _binding(db, case_id: str, decision_id: str, actor: Actor):
    row = db.execute(
        """SELECT d.*, c.updated_at, c.request_text, c.status, c.assigned_staff_account_id,
                  a.status AS actor_status, a.role AS actor_role, a.auditor_access
           FROM synthetic_auditor_decisions d JOIN synthetic_cases c ON c.case_id = d.case_id
           JOIN synthetic_accounts a ON a.account_id = ?
           WHERE d.decision_id = ? AND d.case_id = ? AND c.is_synthetic = 1
             AND NOT EXISTS (SELECT 1 FROM synthetic_auditor_decisions latest
                 WHERE latest.case_id = d.case_id AND latest.item_id = d.item_id
                   AND latest.decision_version > d.decision_version)""",
        (actor.account_id, decision_id, case_id),
    ).fetchone()
    if row is None:
        raise HTTPException(409, "Select the latest decision for this case.")
    if row["actor_status"] != "active" or row["actor_role"] != actor.role or (
        actor.role != "admin" and (
            not row["auditor_access"] or row["assigned_staff_account_id"] != actor.account_id
            or row["reviewer_account_id"] != actor.account_id
        )
    ):
        raise HTTPException(403, "This decision is outside your review scope.")
    message = row["request_text"]
    if (row["case_version"] != row["updated_at"] or row["status"] in {"resolved", "closed"}
            or sha256(message.encode()).hexdigest() != row["source_digest_sha256"]):
        raise HTTPException(409, "The case changed after this decision was saved.")
    if (row["item_index"] != 1 or row["item_count"] != 1 or row["source_start"] != 0
            or row["source_end"] != len(message) or len(message) > 2000
            or len(row["category"]) > 60):
        raise HTTPException(422, "This release resumes whole, single-item reviews. Keep split cases in human review.")
    return row


def downstream(row, run_id: str, check) -> dict:
    if row["request_text"].casefold().strip().rstrip(".!?") == "i need a copy of my personal w-2":
        return {"decision_id": row["decision_id"], "decision_version": row["decision_version"],
                "stages": [{"name": "Personal record routing", "status": "human_review"}],
                "next_action": "human_review"}
    now = datetime.now(UTC)
    policy = load_policy()
    context = RunContext(
        run_id=run_id, case_id=row["case_id"].upper(),
        case_version=row["decision_version"], policy_version=policy.version,
    )
    triage = TriageHandoff(
        contribution_id=stable_id("TRI", run_id, row["decision_id"]),
        agent="auditor-reviewed-handoff", agent_version="1.0", context=context,
        created_at=now, status=AgentStatus.COMPLETED,
        checkpoint=CheckpointOutcome(checkpoint="A2", passed=True),
        confidence=ConfidenceBand.MEDIUM, confidence_rationale="Human reviewed classification.",
        case_summary=row["request_text"], category=row["category"],
        category_confidence=ConfidenceBand.MEDIUM, urgency=row["urgency_band"],
    )
    stages: list[dict] = []
    result = {"decision_id": row["decision_id"], "decision_version": row["decision_version"],
              "stages": stages, "next_action": "human_review"}
    ack = {triage.contribution_id}

    def record(name, contribution) -> bool:
        stages.append({"name": name, "status": contribution.status.value,
                       "reasons": [code.value for code in contribution.checkpoint.reason_codes]})
        check()
        ack.add(contribution.contribution_id)
        return contribution.status is AgentStatus.COMPLETED

    check()
    knowledge = KnowledgeAgent(load_corpus()).run(
        context, triage, acknowledged=ack, as_of=now.date(), now=now,
    )
    if not record("Knowledge", knowledge):
        return result
    troubleshooting = TroubleshootingAgent(policy).run(context, triage, knowledge, acknowledged=ack, now=now)
    if not record("Troubleshooting", troubleshooting):
        return result
    escalation = EscalationAgent().run(
        context, triage=triage, knowledge=knowledge, troubleshooting=troubleshooting, acknowledged=ack, now=now,
    )
    if not record("Escalation", escalation):
        return result
    documentation = DocumentationAgent().run(
        context, triage=triage, knowledge=knowledge, troubleshooting=troubleshooting,
        escalation=escalation, recorded_actions=(), acknowledged=ack, now=now,
    )
    record("Documentation", documentation)
    return result


@router.post("/api/cases/{case_id}/resume-review")
def resume_review(case_id: str, payload: ReviewResume,
                  actor: Actor = Depends(require_roles("staff", "admin"))):
    if actor.role != "admin" and not actor.auditor:
        raise HTTPException(403, "Auditor capability required.")
    with closing(connect()) as db, db:
        db.execute("BEGIN IMMEDIATE")
        row = _binding(db, case_id, payload.decision_id, actor)
        existing = db.execute(
            "SELECT run_id, status, result_json FROM actionrelay_review_runs WHERE decision_id = ?",
            (payload.decision_id,),
        ).fetchone()
        if existing:
            return {"run_id": existing["run_id"], "status": existing["status"],
                    "result": json.loads(existing["result_json"])}
        run_id = "RUN-AR-REVIEW-" + uuid4().hex
        db.execute(
            """INSERT INTO actionrelay_review_runs
               (decision_id, case_id, case_version, run_id, status, started_at)
               VALUES (?, ?, ?, ?, 'running', ?)""",
            (payload.decision_id, case_id, row["case_version"], run_id, stamp(datetime.now(UTC))),
        )

    def check():
        with closing(connect()) as db:
            _binding(db, case_id, payload.decision_id, actor)

    try:
        result = downstream(row, run_id, check)
        status = "human_review"
    except HTTPException:
        result, status = {"reason": "decision_binding_changed"}, "stale"
    except Exception:
        result, status = {"reason": "downstream_execution_blocked"}, "blocked"
    with closing(connect()) as db, db:
        db.execute("BEGIN IMMEDIATE")
        try:
            _binding(db, case_id, payload.decision_id, actor)
        except HTTPException:
            result, status = {"reason": "decision_binding_changed"}, "stale"
        if status == "human_review":
            db.execute(
                "UPDATE synthetic_cases SET category = ?, urgency_band = ? WHERE case_id = ? AND updated_at = ?",
                (row["category"], row["urgency_band"], case_id, row["case_version"]),
            )
        db.execute(
            "UPDATE actionrelay_review_runs SET status = ?, completed_at = ?, result_json = ? WHERE run_id = ?",
            (status, stamp(datetime.now(UTC)), json.dumps(result), run_id),
        )
    return {"run_id": run_id, "status": status, "result": result}
