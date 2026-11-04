"""Troubleshooting agent (Shawn's Lane) — PRD checkpoint A4, troubleshooting boundary.

Proposes only Tier 1 steps quoted verbatim from the top approved passage the
Knowledge agent returned, after validating every step's action type against the
troubleshooting policy. It has no tools and performs no actions. It:

- rejects restricted requests found in the (untrusted) case summary and, for
  blocking rules, suggests nothing and emits escalation signals;
- abstains when Knowledge abstained or when approved guidance contains a step
  outside Tier 1 authority (a guidance governance problem for humans);
- separates steps reserved for authorized staff from Tier 1 suggestions;
- lists stop conditions and information still needed, with provenance.

Escalation signals are inputs for the Manny-owned Escalation agent; this agent
does not make the escalation decision.
"""

from __future__ import annotations

from collections.abc import Set
from datetime import datetime

from cdit_support_mao.agents._gates import consumed, unique, upstream_reasons, utc_now
from cdit_support_mao.agents.troubleshooting.policy import TroubleshootingPolicy
from cdit_support_mao.contracts.common import (
    AgentStatus,
    CheckpointOutcome,
    Claim,
    ClaimLabel,
    ConfidenceBand,
    ReasonCode,
    RunContext,
    SourceKind,
    SourceRef,
    min_band,
    stable_id,
)
from cdit_support_mao.contracts.handoffs import (
    EscalationSignal,
    EvidencePassage,
    InformationNeeded,
    KnowledgeResult,
    RejectedItem,
    StaffProcedure,
    StopCondition,
    SuggestedStep,
    TriageHandoff,
    TroubleshootingResult,
)

AGENT_NAME = "troubleshooting-agent"
AGENT_VERSION = "0.1.0"


def _step_ref(passage: EvidencePassage, step_id: str) -> SourceRef:
    return SourceRef(
        kind=SourceKind.KB_STEP,
        source_id=passage.doc_id,
        version=passage.version,
        locator=f"{passage.section_id}/{step_id}",
    )


class TroubleshootingAgent:
    def __init__(self, policy: TroubleshootingPolicy) -> None:
        self._policy = policy

    def _policy_ref(self, rule_id: str) -> SourceRef:
        return SourceRef(
            kind=SourceKind.POLICY_RULE,
            source_id=self._policy.policy_id,
            version=self._policy.version,
            locator=rule_id,
        )

    def run(
        self,
        context: RunContext,
        triage: TriageHandoff,
        knowledge: KnowledgeResult,
        *,
        acknowledged: Set[str],
        now: datetime | None = None,
    ) -> TroubleshootingResult:
        created_at = utc_now(now)
        contribution_id = stable_id(
            "TRB",
            context.run_id,
            context.case_id,
            context.case_version,
            context.policy_version,
            triage.contribution_id,
            knowledge.contribution_id,
            self._policy.policy_id,
            self._policy.version,
            AGENT_VERSION,
        )
        base = {
            "contribution_id": contribution_id,
            "agent": AGENT_NAME,
            "agent_version": AGENT_VERSION,
            "context": context,
            "input_refs": (triage.as_input_ref(), knowledge.as_input_ref()),
            "created_at": created_at,
            "policy_id": self._policy.policy_id,
            "policy_version": self._policy.version,
        }

        gate = list(upstream_reasons(context, [triage, knowledge], acknowledged, must_be_completed=[triage]))
        if not consumed(knowledge, triage):
            gate.append(ReasonCode.UPSTREAM_CHAIN_MISMATCH)
        if gate:
            return TroubleshootingResult(
                **base,
                status=AgentStatus.BLOCKED,
                checkpoint=CheckpointOutcome(checkpoint="A4", passed=False, reason_codes=unique(gate)),
                claims=(
                    Claim(
                        statement="No troubleshooting was proposed because an upstream handoff was not usable.",
                        label=ClaimLabel.UNKNOWN,
                        confidence=ConfidenceBand.LOW,
                    ),
                ),
                confidence=ConfidenceBand.LOW,
                confidence_rationale="No troubleshooting was attempted.",
                unknowns=("Supported Tier 1 steps for this case are unknown.",),
            )

        summary = triage.case_summary
        reasons: list[ReasonCode] = []
        claims: list[Claim] = []
        rejected: list[RejectedItem] = []
        signals: list[EscalationSignal] = []
        unknowns: list[str] = []

        # 1. Restricted requests in the untrusted case summary.
        blocking = False
        for rule in self._policy.restricted_request_rules:
            if not rule.matches(summary):
                continue
            ref = self._policy_ref(rule.rule_id)
            rejected.append(
                RejectedItem(
                    item_kind="case_request",
                    reference=rule.rule_id,
                    action_type=rule.action_type,
                    reason=ReasonCode.RESTRICTED_ACTION_REQUESTED,
                )
            )
            claims.append(
                Claim(
                    statement=(
                        f"The case text appears to request a restricted action ({rule.action_type}); "
                        "the assistant cannot perform or advise it."
                    ),
                    label=ClaimLabel.INFERENCE,
                    sources=(ref,),
                    basis=f"Deterministic pattern {rule.rule_id} on untrusted case text; risk signal only.",
                    confidence=ConfidenceBand.MEDIUM,
                )
            )
            if rule.effect == "block":
                blocking = True
                signals.append(
                    EscalationSignal(
                        signal=rule.signal,
                        basis=f"Restricted request rule {rule.rule_id} matched the case summary.",
                        sources=(ref,),
                    )
                )
        if blocking:
            reasons.append(ReasonCode.RESTRICTED_ACTION_REQUESTED)

        # 2. Policy stop conditions triggered by the case summary.
        stop_conditions: list[StopCondition] = []
        halted = False
        for condition in self._policy.global_stop_conditions:
            if not condition.matches(summary):
                continue
            halted = halted or condition.halts_routine_steps
            ref = self._policy_ref(condition.condition_id)
            stop_conditions.append(
                StopCondition(
                    condition_id=condition.condition_id,
                    text=condition.text,
                    origin="troubleshooting_policy",
                    source=ref,
                    triggered=True,
                )
            )
            signals.append(
                EscalationSignal(
                    signal=condition.signal,
                    basis=f"Stop condition {condition.condition_id} matched the case summary.",
                    sources=(ref,),
                )
            )
            claims.append(
                Claim(
                    statement=f"Stop condition {condition.condition_id} applies: {condition.text}",
                    label=ClaimLabel.INFERENCE,
                    sources=(ref,),
                    basis="Deterministic pattern on untrusted case text; risk signal only.",
                    confidence=ConfidenceBand.MEDIUM,
                )
            )
        if stop_conditions:
            reasons.append(ReasonCode.POLICY_STOP_CONDITION)

        # 3. Information still needed (triage-reported gaps keep their provenance).
        verified_fields = {fact.field for fact in triage.case_facts if fact.verified}
        triage_ref = SourceRef(
            kind=SourceKind.CONTRIBUTION, source_id=triage.contribution_id, version=triage.contract_version
        )
        information: dict[str, InformationNeeded] = {}
        for index, gap in enumerate(triage.missing_facts, start=1):
            information[f"triage_gap_{index}"] = InformationNeeded(
                field=f"triage_gap_{index}", prompt=gap, source=triage_ref
            )

        # 4. Without usable approved evidence nothing can be suggested.
        if knowledge.status is not AgentStatus.COMPLETED:
            reasons.append(ReasonCode.KNOWLEDGE_ABSTAINED)
            signals.append(
                EscalationSignal(
                    signal="insufficient_approved_evidence",
                    basis="Knowledge agent abstained: "
                    + ", ".join(knowledge.checkpoint.reason_codes),
                    sources=(
                        SourceRef(
                            kind=SourceKind.CONTRIBUTION,
                            source_id=knowledge.contribution_id,
                            version=knowledge.contract_version,
                        ),
                    ),
                )
            )
            unknowns.append("No approved guidance supports Tier 1 steps for this case.")
            return self._abstain(base, reasons, claims, rejected, signals, stop_conditions, information, unknowns)

        primary = knowledge.passages[0]
        base["primary_source"] = primary.source
        for item in primary.information_needed:
            if item.field not in verified_fields:
                information.setdefault(
                    item.field,
                    InformationNeeded(field=item.field, prompt=item.prompt, source=primary.source),
                )
        for condition in primary.stop_conditions:
            stop_conditions.append(
                StopCondition(
                    condition_id=condition.condition_id,
                    text=condition.text,
                    origin="approved_guidance",
                    source=primary.source,
                    triggered=None,
                )
            )

        if blocking or halted:
            unknowns.append(
                "A restricted request or a halting stop condition was found; no Tier 1 steps are suggested."
            )
            return self._abstain(base, reasons, claims, rejected, signals, stop_conditions, information, unknowns)

        # 5. Validate every guidance step against the action-type policy.
        steps: list[SuggestedStep] = []
        staff_only: list[StaffProcedure] = []
        guidance_rejected = False
        for step in primary.steps:
            kind = self._policy.classify(step.action_type)
            ref = _step_ref(primary, step.step_id)
            if kind in ("forbidden", "unknown"):
                guidance_rejected = True
                reason = (
                    ReasonCode.UNSUPPORTED_STEP_REJECTED
                    if kind == "forbidden"
                    else ReasonCode.UNKNOWN_ACTION_TYPE
                )
                reasons.append(reason)
                rejected.append(
                    RejectedItem(
                        item_kind="guidance_step",
                        reference=ref.cite(),
                        action_type=step.action_type,
                        reason=reason,
                    )
                )
                signals.append(
                    EscalationSignal(
                        signal="guidance_step_outside_tier1",
                        basis=f"Approved guidance step {ref.cite()} has action type '{step.action_type}'.",
                        sources=(ref,),
                    )
                )
            elif kind == "staff_only":
                staff_only.append(
                    StaffProcedure(step_id=step.step_id, text=step.text, action_type=step.action_type, source=ref)
                )
            else:
                steps.append(
                    SuggestedStep(
                        order=len(steps) + 1,
                        step_id=step.step_id,
                        text=step.text,
                        action_type=step.action_type,
                        performer=self._policy.tier1_action_types[step.action_type],
                        source=ref,
                    )
                )

        if guidance_rejected:
            unknowns.append(
                "Approved guidance includes a step outside Tier 1 authority; a knowledge owner must review it."
            )
            return self._abstain(base, reasons, claims, rejected, signals, stop_conditions, information, unknowns)

        if staff_only:
            reasons.append(ReasonCode.STAFF_ONLY_PROCEDURE)
            signals.append(
                EscalationSignal(
                    signal="authorized_staff_procedure_required",
                    basis="Approved guidance reserves steps for authorized staff.",
                    sources=tuple(p.source for p in staff_only),
                )
            )

        band = min_band(knowledge.confidence, primary.relevance_band)
        for step in steps:
            claims.append(
                Claim(
                    statement=f"Approved guidance {step.source.cite()} lists this Tier 1 step: {step.text}",
                    label=ClaimLabel.VERIFIED,
                    sources=(step.source,),
                    confidence=band,
                )
            )
        for procedure in staff_only:
            claims.append(
                Claim(
                    statement=(
                        f"Approved guidance {procedure.source.cite()} reserves this step for authorized "
                        f"staff: {procedure.text}"
                    ),
                    label=ClaimLabel.VERIFIED,
                    sources=(procedure.source,),
                    confidence=band,
                )
            )
        if not steps:
            unknowns.append("Approved guidance contains no step a Tier 1 specialist may suggest.")
        if band is ConfidenceBand.MEDIUM:
            unknowns.append("Guidance relevance is tentative (medium band); staff should confirm it fits.")

        result = TroubleshootingResult(
            **base,
            status=AgentStatus.COMPLETED,
            checkpoint=CheckpointOutcome(checkpoint="A4", passed=True, reason_codes=unique(reasons)),
            steps=tuple(steps),
            staff_only_procedures=tuple(staff_only),
            stop_conditions=tuple(stop_conditions),
            information_needed=tuple(information.values()),
            rejected=tuple(rejected),
            escalation_signals=tuple(signals),
            claims=tuple(claims),
            confidence=band,
            confidence_rationale="Never higher than the Knowledge result or the primary passage band.",
            unknowns=tuple(unknowns),
        )
        self._assert_boundary(result)
        return result

    def _assert_boundary(self, result: TroubleshootingResult) -> None:
        """A4 output check: no suggested step may carry a non-Tier 1 action type."""
        for step in result.steps:
            if self._policy.classify(step.action_type) != "tier1":
                raise AssertionError(f"step {step.step_id} escaped the Tier 1 allowlist")
        for procedure in result.staff_only_procedures:
            if self._policy.classify(procedure.action_type) != "staff_only":
                raise AssertionError(f"procedure {procedure.step_id} is not a staff-only action type")

    @staticmethod
    def _abstain(
        base: dict,
        reasons: list[ReasonCode],
        claims: list[Claim],
        rejected: list[RejectedItem],
        signals: list[EscalationSignal],
        stop_conditions: list[StopCondition],
        information: dict[str, InformationNeeded],
        unknowns: list[str],
    ) -> TroubleshootingResult:
        return TroubleshootingResult(
            **base,
            status=AgentStatus.ABSTAINED,
            checkpoint=CheckpointOutcome(checkpoint="A4", passed=False, reason_codes=unique(reasons)),
            stop_conditions=tuple(stop_conditions),
            information_needed=tuple(information.values()),
            rejected=tuple(rejected),
            escalation_signals=tuple(signals),
            claims=(
                Claim(
                    statement="No Tier 1 troubleshooting steps are suggested for this case.",
                    label=ClaimLabel.UNKNOWN,
                    confidence=ConfidenceBand.LOW,
                ),
                *claims,
            ),
            confidence=ConfidenceBand.LOW,
            confidence_rationale="Abstained: evidence missing or request/guidance outside Tier 1 authority.",
            unknowns=tuple(unknowns),
        )
