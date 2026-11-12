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
from cdit_support_mao.agents.coordinator.handoff import (
    HandoffCheckpoint,
    HandoffError,
    HandoffRegistry,
    HandoffState,
)
from cdit_support_mao.contracts.common import (
    AgentContribution,
    AgentStatus,
    CheckpointOutcome,
    Claim,
    ClaimLabel,
    ConfidenceBand,
    RunContext,
    SourceKind,
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
from cdit_support_mao.agents.triage.attention import AttentionSignal

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
        attention_signal: AttentionSignal | None = None,
        attention_checkpoint: HandoffCheckpoint | None = None,
        handoff_registry: HandoffRegistry | None = None,
        receiver_capability: object | None = None,
        now: datetime | None = None,
    ) -> EscalationHandoff:
        created_at = utc_now(now)
        recorded_actions = tuple(actions)
        inputs = tuple(c for c in (triage, knowledge, troubleshooting) if c is not None)
        contribution_id = stable_id(
            "ESC",
            context.run_id,
            context.case_id,
            context.case_version,
            context.policy_version,
            *(c.contribution_id for c in inputs),
            *(action.model_dump_json() for action in recorded_actions),
            *((attention_signal.model_dump_json(),) if attention_signal is not None else ()),
            *((
                attention_checkpoint.trace_id,
                attention_checkpoint.handoff_id,
                str(attention_checkpoint.state_version),
                str(attention_checkpoint.state),
            ) if isinstance(attention_checkpoint, HandoffCheckpoint) else ()),
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

        attention_error = _attention_signal_error(
            attention_signal,
            attention_checkpoint,
            handoff_registry,
            receiver_capability,
            context,
            now=created_at,
        )
        potential_attention = bool(
            attention_error is None
            and attention_signal is not None
            and attention_signal.status == "potential_attention"
        )
        rejected_attention = attention_error is not None

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

        investigation_source = _verified_investigation_source(triage, context)
        investigation_in_progress = investigation_source is not None

        must_escalate: bool | None = None if (potential_attention or rejected_attention) else False
        recommendation: Literal["escalate_l2", "escalate_support_lead", "human_review", "no_escalation_proposed"] = "no_escalation_proposed"
        triggers: list[str] = ["human_investigation_in_progress"] if investigation_in_progress else []
        if potential_attention:
            triggers.append("potential_urgent_attention")
        if rejected_attention:
            triggers.append("attention_signal_validation_failed")
        recommendation = "human_review" if (investigation_in_progress or potential_attention or rejected_attention) else "no_escalation_proposed"
        reason = (
            "Route the existing case to human review; do not change its status."
            if investigation_in_progress
            else "A synthetic attention phrase matched untrusted case text; a human must inspect its context."
            if potential_attention
            else attention_error
            if rejected_attention
            else "Routine Tier 1 troubleshooting applicable with approved guidance."
        )

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

        # Unknown urgency remains unknown and must go to the human Auditor.
        # A potential-urgent attention flag does not establish a verified band.
        elif triage and triage.urgency == "unknown":
            must_escalate = None
            recommendation = "human_review"
            triggers.append("urgency_unknown")
            reason = "Urgency is unknown; route to the human Auditor without assigning a band or treating a risk flag as a verified band."

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

        if investigation_in_progress:
            reason += " No case-status change or outside contact is performed; a human decides any next action."
        if potential_attention:
            reason += " The phrase match is a risk signal only; it does not verify an incident or assign an urgency band."
        if rejected_attention:
            reason += " The supplied signal was excluded; inspect the case using the authorized source."

        # 3. Derive Confidence
        bands = [c.confidence for c in inputs] or [ConfidenceBand.MEDIUM]
        confidence = min_band(*bands)
        if must_escalate is None:
            confidence = ConfidenceBand.LOW

        # 4. Compile Unknowns & Claims
        unknowns_set: list[str] = []
        for c in inputs:
            unknowns_set.extend(c.unknowns)
        if troubleshooting:
            unknowns_set.extend(
                f"Unresolved question: {item.prompt}"
                for item in troubleshooting.information_needed
            )
        if triage and triage.urgency == "unknown":
            unknowns_set.append("Urgency remains unknown pending human Auditor review.")
        if potential_attention:
            unknowns_set.append("Potential attention signal does not determine urgency or verify an incident.")
        if rejected_attention:
            unknowns_set.append("Attention signal was rejected; its match details were not used.")
        if must_escalate is None and (
            (knowledge and knowledge.status is not AgentStatus.COMPLETED)
            or (troubleshooting and troubleshooting.status is not AgentStatus.COMPLETED)
        ):
            unknowns_set.append("Escalation determination uncertain due to incomplete or conflicting upstream evidence")
        if rejected_attention:
            unknowns_set.append("Supplied attention signal was rejected for context or provenance mismatch")

        claim = Claim(
            statement=f"A5 proposes {recommendation}.",
            label=ClaimLabel.INFERENCE if must_escalate is not None else ClaimLabel.UNKNOWN,
            sources=(),
            confidence=confidence,
            basis=f"Evaluated triggers: {', '.join(triggers) if triggers else 'None'}",
        )
        investigation_claims = (
            (
                Claim(
                    statement="The current verified case status is Under Investigation.",
                    label=ClaimLabel.VERIFIED,
                    sources=(investigation_source,),
                    confidence=confidence,
                    basis="Verified Triage case fact for the current case version.",
                ),
            )
            if investigation_source is not None
            else ()
        )
        attention_claims = (
            tuple(
                Claim(
                    statement="A configured synthetic phrase matched untrusted case text; a human must inspect its full context. This does not verify an incident or assign an urgency band.",
                    label=ClaimLabel.INFERENCE,
                    sources=(match.source,),
                    confidence=ConfidenceBand.LOW,
                    basis=(
                        "Fixture-only literal match: "
                        f"pattern_id={match.fixture_pattern_id}, "
                        f"source_start_codepoint={match.start_codepoint}, "
                        f"end_codepoint={match.end_codepoint}. "
                        "This does not establish an incident or urgency band."
                    ),
                )
                for match in attention_signal.matches
            )
            if potential_attention and attention_signal is not None
            else ()
        )

        action_claims = tuple(
            Claim(
                statement=(
                    f"Staff-recorded action ({action.performed_by_role}): "
                    f"{action.action}; outcome: {action.outcome}"
                ),
                # The coordinator is the trusted producer for case-record
                # entries. Refuse to promote a caller's verified flag unless
                # its source is bound to this exact case version.
                label=(
                    ClaimLabel.VERIFIED
                    if action.verified and _action_source_matches_context(action, context)
                    else ClaimLabel.UNKNOWN
                ),
                sources=(action.source,),
                confidence=(
                    confidence
                    if action.verified and _action_source_matches_context(action, context)
                    else ConfidenceBand.LOW
                ),
            )
            for action in recorded_actions
        )
        information_claims = tuple(
            Claim(
                statement=f"Unresolved question: {item.prompt}",
                label=ClaimLabel.UNKNOWN,
                sources=(item.source,),
                confidence=ConfidenceBand.LOW,
            )
            for item in (troubleshooting.information_needed if troubleshooting else ())
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
            claims=(claim, *investigation_claims, *attention_claims, *information_claims, *action_claims),
        )


def _action_source_matches_context(action: RecordedAction, context: RunContext) -> bool:
    """Require a recorded action pointer to belong to this case/version."""
    return (
        action.source.source_id.startswith(f"{context.case_id}.staff_entry.")
        and action.source.version == str(context.case_version)
    )


def _verified_investigation_source(
    triage: TriageHandoff | None, context: RunContext
) -> SourceRef | None:
    """Return only a current, verified case-field status with its provenance."""
    if triage:
        for fact in triage.case_facts:
            if (
                fact.field == "case_status"
                and fact.value == "under_investigation"
                and fact.verified
                and fact.source.kind is SourceKind.CASE_FIELD
                and fact.source.source_id == f"{context.case_id}.case_status"
                and fact.source.version == str(context.case_version)
            ):
                return fact.source
    return None


def _attention_signal_error(
    signal: AttentionSignal | None,
    checkpoint: HandoffCheckpoint | None,
    registry: HandoffRegistry | None,
    receiver_capability: object | None,
    context: RunContext,
    *,
    now: datetime,
) -> str | None:
    """Revalidate the accepted A1 record before using a signal as evidence.

    A5 validates its snapshot for this calculation. The Coordinator must still
    revalidate ownership and active state before any later downstream action.
    """
    if signal is None:
        return None
    if not isinstance(signal, AttentionSignal) or signal.context != context:
        return "Attention signal context does not match the current A5 run and case. Human review is required."
    if signal.status == "not_assessed":
        return None if not signal.matches else "Unassessed attention signal unexpectedly contains matches. Human review is required."
    if signal.status != "potential_attention" or not signal.matches:
        return "Potential attention signal is missing its evidence matches. Human review is required."
    if checkpoint is None:
        return "Potential attention signal has no trusted A1 handoff checkpoint. Human review is required."
    if (
        not isinstance(checkpoint, HandoffCheckpoint)
        or checkpoint.context != context
        or checkpoint.state is not HandoffState.ACCEPTED
    ):
        return "A1 handoff checkpoint does not match the current accepted run and case. Human review is required."
    if not isinstance(registry, HandoffRegistry) or receiver_capability is None:
        return "Potential attention signal cannot be revalidated against the active A1 registry. Human review is required."
    try:
        active_checkpoint = registry.validate_active(
            checkpoint.handoff_id,
            expected_version=checkpoint.state_version,
            capability=receiver_capability,
            context=context,
            now=now,
        )
    except HandoffError:
        return "A1 handoff is stale, unavailable, or no longer authorized. Human review is required."
    if (
        checkpoint.trace_id != active_checkpoint.trace_id
        or checkpoint.handoff_id != active_checkpoint.handoff_id
        or checkpoint.state_version != active_checkpoint.state_version
    ):
        return "A1 checkpoint snapshot does not match the active registry record. Human review is required."
    if (
        signal.trace_id != active_checkpoint.trace_id
        or signal.handoff_id != active_checkpoint.handoff_id
        or signal.handoff_state_version != active_checkpoint.state_version
    ):
        return "Attention signal does not match the current A1 handoff checkpoint. Human review is required."
    if any(
        match.source.kind is not SourceKind.CASE_FIELD
        or match.source.source_id != context.case_id
        or match.source.version != str(context.case_version)
        or match.source.locator != "message"
        for match in signal.matches
    ):
        return "Attention signal evidence does not cite the current case message. Human review is required."
    return None
