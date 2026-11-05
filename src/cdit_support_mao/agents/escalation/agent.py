"""Escalation agent (Manny's Lane) — PRD checkpoint A5, escalation decision.

Checks deterministic must-escalate conditions, separates risk signals from
action authority, and prepares the human handoff packet for L2 or Support Lead.
It has no tools and performs no external notifications, state transitions, or writes.
"""
from __future__ import annotations

from collections.abc import Iterable, Set
from datetime import datetime
from typing import Literal

from cdit_support_mao.agents._gates import unique, upstream_reasons, utc_now
from cdit_support_mao.contracts.common import (
    AgentContribution,
    AgentStatus,
    CheckpointOutcome,
    Claim,
    ClaimLabel,
    ConfidenceBand,
    ReasonCode,
    RunContext,
    min_band,
    stable_id,
)
from cdit_support_mao.contracts.handoffs import (
    EscalationHandoff,
    KnowledgeResult,
    RecordedAction,
    TriageHandoff,
    TroubleshootingResult,
)

AGENT_NAME = "escalation-agent"
AGENT_VERSION = "0.1.0"


class EscalationAgent:
    """Evaluates must-escalate conditions and prepares human handoff packets (A5)."""

    def __init__(self, agent_version: str = AGENT_VERSION) -> None:
        self.agent_version = agent_version

    def run(
        self,
        context: RunContext,
        triage: TriageHandoff | None = None,
        knowledge: KnowledgeResult | None = None,
        troubleshooting: TroubleshootingResult | None = None,
        *,
        acknowledged: Set[str],
        actions: Iterable[RecordedAction] = (),
        now: datetime | None = None,
    ) -> EscalationHandoff:
        created_at = utc_now(now)
        inputs = tuple(c for c in (triage, knowledge, troubleshooting) if c is not None)
        contribution_id = stable_id(
            "ESC",
            context.run_id,
            context.case_id,
            context.case_version,
            context.policy_version,
            *(c.contribution_id for c in inputs),
            self.agent_version,
        )
        input_refs = tuple(c.as_input_ref() for c in inputs)

        # 1. Input Gate: Upstream check
        reasons = list(upstream_reasons(context, inputs, acknowledged))
        if reasons:
            return EscalationHandoff(
                contribution_id=contribution_id,
                agent=AGENT_NAME,
                agent_version=self.agent_version,
                context=context,
                input_refs=input_refs,
                created_at=created_at,
                status=AgentStatus.ABSTAINED,
                checkpoint=CheckpointOutcome(checkpoint="A5", passed=False, reason_codes=unique(reasons)),
                must_escalate=None,
                triggers=("upstream_validation_failed",),
                recommendation="human_review",
                reason="Upstream inputs failed validation (unacknowledged or context mismatch); routed to human review.",
                confidence=ConfidenceBand.LOW,
                confidence_rationale="Low confidence due to upstream validation failure.",
                unknowns=("Upstream handoffs not ready or verified",),
                claims=(),
            )

        # 2. Evaluate deterministic must-escalate conditions
        signals: set[str] = set()
        if troubleshooting:
            signals.update(s.signal for s in troubleshooting.escalation_signals)
            for cond in troubleshooting.stop_conditions:
                if cond.triggered:
                    if cond.condition_id == "TS-SC-PRIVACY":
                        signals.add("possible_privacy_incident")
                    elif cond.condition_id == "TS-SC-SECURITY":
                        signals.add("possible_security_incident")
                    elif cond.condition_id == "TS-SC-ACCESS":
                        signals.add("access_or_identity")

        must_escalate: bool | None = False
        recommendation: Literal["escalate_l2", "escalate_support_lead", "human_review", "no_escalation_proposed"] = "no_escalation_proposed"
        triggers: list[str] = []
        reason = "Routine Tier 1 troubleshooting applicable with approved guidance."

        # Rule 1: Privacy incident (highest priority)
        if "possible_privacy_incident" in signals:
            must_escalate = True
            recommendation = "escalate_support_lead"
            triggers.append("possible_privacy_incident")
            reason = "Possible privacy incident detected (e.g. PHI exposure or cross-site data exposure). Immediate escalation to Support Lead required."

        # Rule 2: Security incident
        elif "possible_security_incident" in signals:
            must_escalate = True
            recommendation = "escalate_support_lead"
            triggers.append("possible_security_incident")
            reason = "Possible security incident detected (e.g. compromised account or credentials). Immediate escalation to Support Lead required."

        # Rule 3: High Urgency (P1)
        elif triage and triage.urgency == "high":
            must_escalate = True
            recommendation = "escalate_support_lead"
            triggers.append("high_urgency_p1")
            reason = "High urgency (P1) case requires immediate Support Lead review and SLA monitoring."

        # Rule 4: Out of Tier 1 authority / blocked requests
        elif troubleshooting and any(r.item_kind == "case_request" for r in troubleshooting.rejected):
            must_escalate = True
            recommendation = "escalate_l2"
            triggers.append("out_of_tier1_scope")
            reason = "Requested action is outside Tier 1 authority. Escalation to L2 specialist required."

        # Rule 5: Access or identity change requiring staff action
        elif "access_or_identity" in signals or "authorized_staff_procedure_required" in signals:
            must_escalate = True
            recommendation = "escalate_l2"
            triggers.append("access_or_identity")
            reason = "Case involves access grant, role change, or identity verification requiring authorized staff review."

        # Rule 6: Quoted policy override attempt
        elif "quoted_policy_override_attempt" in signals:
            must_escalate = True
            recommendation = "human_review"
            triggers.append("quoted_policy_override_attempt")
            reason = "Quoted policy-override attempt detected in case text; routes to human review as an escalation signal."

        # Rule 7: Conflicting, stale, or unavailable knowledge evidence
        elif knowledge and knowledge.status is not AgentStatus.COMPLETED:
            must_escalate = None  # Preserve uncertainty
            recommendation = "human_review"
            triggers.append("conflicting_or_stale_evidence")
            reason = "Approved guidance is conflicting, stale, or unavailable. Preserving uncertainty and routing to human review."

        # Rule 8: Incomplete troubleshooting without specific stop signals
        elif troubleshooting and troubleshooting.status is not AgentStatus.COMPLETED:
            must_escalate = None  # Preserve uncertainty
            recommendation = "human_review"
            triggers.append("troubleshooting_incomplete")
            reason = "Troubleshooting could not be completed with Tier 1 guidance. Preserving uncertainty and routing to human review."

        # 3. Derive Confidence
        bands = [c.confidence for c in inputs] or [ConfidenceBand.MEDIUM]
        confidence = min_band(*bands)
        if must_escalate is None:
            confidence = ConfidenceBand.LOW

        # 4. Compile Unknowns & Claims
        unknowns_set: list[str] = []
        for c in inputs:
            unknowns_set.extend(c.unknowns)
        if must_escalate is None:
            unknowns_set.append("Escalation determination uncertain due to incomplete or conflicting upstream evidence")

        claim = Claim(
            statement=reason,
            label=ClaimLabel.INFERENCE if must_escalate is not None else ClaimLabel.UNKNOWN,
            sources=(),
            confidence=confidence,
            basis=f"Evaluated triggers: {', '.join(triggers) if triggers else 'None'}",
        )

        return EscalationHandoff(
            contribution_id=contribution_id,
            agent=AGENT_NAME,
            agent_version=self.agent_version,
            context=context,
            input_refs=input_refs,
            created_at=created_at,
            status=AgentStatus.COMPLETED,
            checkpoint=CheckpointOutcome(checkpoint="A5", passed=True),
            must_escalate=must_escalate,
            triggers=tuple(triggers),
            recommendation=recommendation,
            reason=reason,
            confidence=confidence,
            confidence_rationale=f"Confidence evaluated from upstream contributions and deterministic rules: {confidence}.",
            unknowns=tuple(dict.fromkeys(unknowns_set)),
            claims=(claim,),
        )
