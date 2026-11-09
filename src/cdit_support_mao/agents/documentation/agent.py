"""Documentation agent (Shawn's Lane) — PRD checkpoint A6, draft assembly and review.

Builds a Salesforce-style draft case note from labelled upstream content only:
verified case fields, staff-recorded actions, cited approved guidance, and
clearly marked proposals from other agents. It never invents facts, never
states that a step was performed unless staff recorded it, and never changes
ticket state, saves, or sends anything (``save_reviewed_result`` stays disabled).

The draft is suppressed in favour of a manual fallback when a dependency is
missing, an input is stale, unacknowledged, or blocked, or sensitive-looking
data would appear in the note.

For one linked item of a multi-item case message, the draft covers that item
only: it states "Item n of m", shows the category as a Triage inference with its
basis and sources, refers to an attention flag without repeating it, and never
shows another item's text. It is held (``missing_dependency``) until the Auditor
has determined the item's urgency band and route (Manny, Q-A, 2026-11-05).
When the item has no attention flag, one line states what the attention check did
(S-1.1): no match is never a risk assessment, and a check that did not run is
information for Staff/Admin only. It adds no hold (Manny, S-1.1 Q3, 2026-11-08).
"""

from __future__ import annotations

from collections.abc import Iterable, Set
from datetime import datetime

from cdit_support_mao.agents._gates import (
    awaiting_auditor,
    consumed,
    item_chain_reasons,
    unique,
    upstream_reasons,
    utc_now,
)
from cdit_support_mao.agents.documentation.privacy import scan_for_sensitive_data
from cdit_support_mao.contracts.common import (
    AgentContribution,
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
    DocumentationResult,
    DraftNote,
    EscalationHandoff,
    KnowledgeResult,
    LinkedItemRef,
    ManualFallback,
    NoteLine,
    NoteSection,
    PrivacyFinding,
    RecordedAction,
    TriageHandoff,
    TroubleshootingResult,
)

AGENT_NAME = "documentation-agent"
AGENT_VERSION = "0.2.1"

_RECOMMENDATION_TEXT = {
    "escalate_l2": "escalate to L2",
    "escalate_support_lead": "escalate to the Support Lead",
    "human_review": "route to human review",
    "no_escalation_proposed": "no escalation proposed",
}


def _contribution_ref(contribution: AgentContribution) -> SourceRef:
    return SourceRef(
        kind=SourceKind.CONTRIBUTION,
        source_id=contribution.contribution_id,
        version=contribution.contract_version,
    )


def _verified(text: str, *sources: SourceRef) -> NoteLine:
    return NoteLine(text=text, label=ClaimLabel.VERIFIED, sources=tuple(sources))


def _inference(text: str, basis: str, *sources: SourceRef) -> NoteLine:
    return NoteLine(text=text, label=ClaimLabel.INFERENCE, sources=tuple(sources), basis=basis)


def _unknown(text: str, *sources: SourceRef) -> NoteLine:
    return NoteLine(text=text, label=ClaimLabel.UNKNOWN, sources=tuple(sources))


_ATTENTION_CHECK_TEXT = {
    "no_configured_match": (
        "Attention check: no configured phrase matched this item. This is not a risk assessment."
    ),
    "check_not_run": (
        "Attention check: did not run for this item. Information only; "
        "the Auditor's urgency review still applies."
    ),
}


def _attention_check_line(triage: TriageHandoff, triage_ref: SourceRef) -> NoteLine:
    """One Staff/Admin information line for an item without an attention flag (S-1.1).

    It never clears or implies a flag and adds no hold (Manny, S-1.1 Q3). A 0.2 scope
    always states the check (Q5); the unknown line remains for legacy 0.1 scopes.
    """
    check = triage.item_scope.attention_check if triage.item_scope is not None else None
    text = _ATTENTION_CHECK_TEXT.get(check) if check is not None else None
    if text is None:
        return _unknown("Attention check: Triage did not say whether it ran for this item.", triage_ref)
    return _inference(
        text, f"Attention check status recorded in Triage handoff {triage.contribution_id}.", triage_ref
    )


class DocumentationAgent:
    def run(
        self,
        context: RunContext,
        *,
        triage: TriageHandoff | None,
        knowledge: KnowledgeResult | None,
        troubleshooting: TroubleshootingResult | None,
        escalation: EscalationHandoff | None,
        recorded_actions: Iterable[RecordedAction] = (),
        acknowledged: Set[str],
        now: datetime | None = None,
    ) -> DocumentationResult:
        created_at = utc_now(now)
        actions = tuple(recorded_actions)
        inputs: list[AgentContribution] = [
            item for item in (triage, knowledge, troubleshooting, escalation) if item is not None
        ]
        contribution_id = stable_id(
            "DOC",
            context.run_id,
            context.case_id,
            context.case_version,
            context.policy_version,
            *(item.contribution_id for item in inputs),
            *(action.model_dump_json() for action in actions),
            AGENT_VERSION,
        )
        base = {
            "contribution_id": contribution_id,
            "agent": AGENT_NAME,
            "agent_version": AGENT_VERSION,
            "context": context,
            "input_refs": tuple(item.as_input_ref() for item in inputs),
            "created_at": created_at,
        }

        reasons: list[ReasonCode] = []
        if len(inputs) < 4:
            reasons.append(ReasonCode.MISSING_DEPENDENCY)
        reasons += upstream_reasons(
            context, inputs, acknowledged, must_be_completed=[triage] if triage else []
        )
        if knowledge and triage and not consumed(knowledge, triage):
            reasons.append(ReasonCode.UPSTREAM_CHAIN_MISMATCH)
        if troubleshooting and not consumed(troubleshooting, *(x for x in (triage, knowledge) if x)):
            reasons.append(ReasonCode.UPSTREAM_CHAIN_MISMATCH)
        if triage and knowledge:
            reasons += item_chain_reasons(triage, knowledge)
        held = triage is not None and awaiting_auditor(triage)
        if held:
            reasons.append(ReasonCode.MISSING_DEPENDENCY)
        if reasons:
            return self._fallback(base, unique(reasons), held=held)

        assert triage and knowledge and troubleshooting and escalation  # narrowed by the gate above
        sections = self._compose(triage, knowledge, troubleshooting, escalation, actions)

        findings = tuple(
            PrivacyFinding(category=category, location=f"{section.heading} / line {number}")
            for section in sections
            for number, line in enumerate(section.lines, start=1)
            for category in scan_for_sensitive_data(line.text)
        )
        if findings:
            return self._fallback(base, (ReasonCode.SENSITIVE_DATA_DETECTED,), findings)

        draft_id = stable_id("DRAFT", contribution_id)
        draft = DraftNote(
            draft_id=draft_id,
            sections=sections,
            rendered_text=self._render(
                context,
                draft_id,
                created_at,
                sections,
                triage.item_scope.identity if triage.item_scope is not None else None,
            ),
        )
        if scan_for_sensitive_data(draft.rendered_text):  # A6 output check on the final text
            return self._fallback(
                base,
                (ReasonCode.SENSITIVE_DATA_DETECTED,),
                (PrivacyFinding(category="rendered_text", location="draft header"),),
            )

        lines = [line for section in sections for line in section.lines]
        counts = {label: sum(1 for line in lines if line.label is label) for label in ClaimLabel}
        unknowns = list(
            dict.fromkeys(
                [*triage.unknowns, *knowledge.unknowns, *troubleshooting.unknowns, *escalation.unknowns]
            )
        )
        return DocumentationResult(
            **base,
            status=AgentStatus.COMPLETED,
            checkpoint=CheckpointOutcome(checkpoint="A6", passed=True),
            draft=draft,
            claims=(
                Claim(
                    statement=(
                        f"The draft has {counts[ClaimLabel.VERIFIED]} verified, "
                        f"{counts[ClaimLabel.INFERENCE]} inferred, and {counts[ClaimLabel.UNKNOWN]} "
                        "unknown lines; every verified line cites a source."
                    ),
                    label=ClaimLabel.VERIFIED,
                    sources=tuple(_contribution_ref(item) for item in inputs),
                    confidence=ConfidenceBand.HIGH,
                ),
            ),
            confidence=min_band(
                triage.category_confidence,
                knowledge.confidence,
                troubleshooting.confidence,
                escalation.confidence,
            ),
            confidence_rationale="Weakest upstream band; the draft only restates labelled upstream content.",
            unknowns=tuple(unknowns),
        )

    def _compose(
        self,
        triage: TriageHandoff,
        knowledge: KnowledgeResult,
        troubleshooting: TroubleshootingResult,
        escalation: EscalationHandoff,
        actions: tuple[RecordedAction, ...],
    ) -> tuple[NoteSection, ...]:
        triage_ref = _contribution_ref(triage)
        sections: list[NoteSection] = []

        facts = [
            _verified(f"{fact.field}: {fact.value}", fact.source) for fact in triage.case_facts if fact.verified
        ]
        sections.append(
            NoteSection(
                heading="Case facts (verified)",
                lines=tuple(facts) or (_unknown("No verified case facts were supplied."),),
            )
        )

        triage_basis = f"Triage proposal {triage.contribution_id}; not confirmed by staff."
        sections.append(
            NoteSection(
                heading="Triage proposal (pending staff confirmation)",
                lines=self._triage_lines(triage, triage_ref, triage_basis),
            )
        )

        guidance: list[NoteLine] = [
            _verified(f"{passage.title} - {passage.heading}", passage.source) for passage in knowledge.passages
        ]
        guidance += [
            _verified(
                "Conflicting approved sources, not resolved by the assistant: "
                + ", ".join(ref.cite() for ref in conflict.sources),
                *conflict.sources,
            )
            for conflict in knowledge.conflicts
        ]
        if not knowledge.passages:
            guidance.append(
                _unknown(
                    "No approved guidance was used ("
                    + ", ".join(knowledge.checkpoint.reason_codes)
                    + ").",
                    _contribution_ref(knowledge),
                )
            )
        sections.append(NoteSection(heading="Approved guidance consulted", lines=tuple(guidance)))

        steps = [
            _verified(f"{step.order}. {step.text}", step.source) for step in troubleshooting.steps
        ]
        if not steps:
            reason = ", ".join(troubleshooting.checkpoint.reason_codes) or "none in approved guidance"
            steps.append(
                _unknown(f"No Tier 1 steps are suggested ({reason}).", _contribution_ref(troubleshooting))
            )
        sections.append(NoteSection(heading="Suggested Tier 1 steps (not performed)", lines=tuple(steps)))

        if troubleshooting.staff_only_procedures:
            sections.append(
                NoteSection(
                    heading="Steps reserved for authorized staff",
                    lines=tuple(
                        _verified(procedure.text, procedure.source)
                        for procedure in troubleshooting.staff_only_procedures
                    ),
                )
            )

        performed = [
            _verified(
                f"{action.performed_by_role}: {action.action} - outcome: {action.outcome}", action.source
            )
            for action in actions
            if action.verified
        ]
        sections.append(
            NoteSection(
                heading="Actions taken (recorded by staff)",
                lines=tuple(performed)
                or (_unknown("No staff-recorded actions were supplied; do not assume any step was performed."),),
            )
        )

        if troubleshooting.information_needed:
            sections.append(
                NoteSection(
                    heading="Information still needed",
                    lines=tuple(
                        _unknown(f"{item.field}: {item.prompt}", item.source)
                        for item in troubleshooting.information_needed
                    ),
                )
            )

        escalation_ref = _contribution_ref(escalation)
        escalation_lines = [
            _inference(
                f"Escalation proposal: {_RECOMMENDATION_TEXT[escalation.recommendation]}"
                + (f"; triggers: {', '.join(escalation.triggers)}" if escalation.triggers else "")
                + f". Reason: {escalation.reason}",
                f"Escalation proposal {escalation.contribution_id}; a human decides.",
                escalation_ref,
            )
        ]
        escalation_lines += [
            _inference(
                f"Escalation signal for review: {signal.signal}.",
                signal.basis,
                *signal.sources,
            )
            for signal in troubleshooting.escalation_signals
        ]
        for condition in troubleshooting.stop_conditions:
            if condition.triggered:
                escalation_lines.append(
                    _inference(
                        f"Stop condition applies: {condition.text}",
                        "Deterministic pattern on case text; risk signal only.",
                        condition.source,
                    )
                )
            else:
                escalation_lines.append(_verified(f"Stop condition: {condition.text}", condition.source))
        sections.append(NoteSection(heading="Stop conditions and escalation", lines=tuple(escalation_lines)))

        open_items = [
            _unknown(f"Reported, not verified - {fact.field}: {fact.value}", fact.source)
            for fact in triage.case_facts
            if not fact.verified
        ]
        open_items += [
            _unknown(f"Reported action, not verified - {action.action}", action.source)
            for action in actions
            if not action.verified
        ]
        open_items += [
            _unknown(f"Requested action not performed by the assistant: {item.action_type}.")
            for item in troubleshooting.rejected
            if item.item_kind == "case_request"
        ]
        if open_items:
            sections.append(NoteSection(heading="Unverified or unresolved", lines=tuple(open_items)))
        return tuple(sections)

    @staticmethod
    def _triage_lines(triage: TriageHandoff, triage_ref: SourceRef, triage_basis: str) -> tuple[NoteLine, ...]:
        scope = triage.item_scope
        category_text = (
            f"Proposed category: {triage.category or 'undetermined'} (confidence {triage.category_confidence})."
        )
        if scope is None:
            return (
                _inference(category_text, triage_basis, triage_ref),
                _inference(f"Proposed urgency: {triage.urgency}.", triage_basis, triage_ref),
            )
        ident = scope.identity
        lines = [
            _inference(
                f"Item {ident.item_index} of {ident.item_count} (linked to parent case "
                f"{ident.parent_source.source_id}; linked item {ident.item_id}). "
                "This note covers this item only.",
                f"Triage segmentation proposal {triage.contribution_id}; not confirmed by staff.",
                triage_ref,
                ident.parent_source,
            )
        ]
        if scope.category_label == "inference" and scope.category_basis:
            lines.append(
                _inference(
                    category_text,
                    f"{scope.category_basis.rstrip('.')}; {triage_basis}",
                    triage_ref,
                    *scope.category_sources,
                )
            )
        else:
            lines.append(_unknown("Category: unknown; the Auditor reviews this item.", triage_ref))
        if scope.auditor_review == "band_and_route_determined":
            lines.append(
                _inference(
                    f"Urgency band: {triage.urgency} (determined by the Auditor; recorded in the Triage handoff).",
                    f"Auditor determination recorded in Triage handoff {triage.contribution_id}; "
                    "staff confirm it in the case record.",
                    triage_ref,
                )
            )
        else:
            lines.append(_inference(f"Proposed urgency: {triage.urgency}.", triage_basis, triage_ref))
        if scope.attention_ref is not None:
            lines.append(
                _inference(
                    "Attention flag present on this item; see the Triage attention record. "
                    "Only a human may clear it.",
                    f"Triage attention flag {scope.attention_ref.cite()} (by reference).",
                    scope.attention_ref,
                )
            )
        elif scope.parent_attention_flagged:
            lines.append(
                _inference(
                    "Another item of the parent case has an attention flag; review the parent case.",
                    f"Parent-level attention summary in Triage handoff {triage.contribution_id}.",
                    triage_ref,
                )
            )
        if scope.attention_ref is None:
            lines.append(_attention_check_line(triage, triage_ref))
        return tuple(lines)

    @staticmethod
    def _render(
        context: RunContext,
        draft_id: str,
        created_at: datetime,
        sections: tuple[NoteSection, ...],
        item: LinkedItemRef | None = None,
    ) -> str:
        header = (
            f"Case {context.case_id} (version {context.case_version}) | Run {context.run_id} | "
            f"Policy {context.policy_version} | Draft {draft_id}"
        )
        if item is not None:
            header += f" | Item {item.item_index} of {item.item_count} ({item.item_id})"
        out = [
            DraftNote.model_fields["banner"].default,
            header,
            f"Prepared {created_at.isoformat()} by {AGENT_NAME} {AGENT_VERSION}",
        ]
        for section in sections:
            out += ["", section.heading]
            for line in section.lines:
                if line.label is ClaimLabel.VERIFIED:
                    tag = "verified: " + "; ".join(ref.cite() for ref in line.sources)
                elif line.label is ClaimLabel.INFERENCE:
                    tag = f"inference: {line.basis}"
                else:
                    tag = "unknown"
                out.append(f"- {line.text} [{tag}]")
        return "\n".join(out) + "\n"

    @staticmethod
    def _fallback(
        base: dict,
        reasons: tuple[ReasonCode, ...],
        findings: tuple[PrivacyFinding, ...] = (),
        *,
        held: bool = False,
    ) -> DocumentationResult:
        instructions = [
            "Write the case note manually in the approved system from verified case details.",
            "Review the upstream agent results referenced by this contribution before relying on them.",
        ]
        if ReasonCode.SENSITIVE_DATA_DETECTED in reasons:
            instructions.append(
                "Do not copy the flagged content; follow the approved data-handling procedure for sensitive data."
            )
        if ReasonCode.MISSING_DEPENDENCY in reasons:
            instructions.append("Re-run documentation after every required upstream stage has completed.")
        if held:
            instructions.append(
                "This linked item is held until the Auditor determines its urgency band and route."
            )
        return DocumentationResult(
            **base,
            status=AgentStatus.BLOCKED,
            checkpoint=CheckpointOutcome(checkpoint="A6", passed=False, reason_codes=reasons),
            manual_fallback=ManualFallback(reason_codes=reasons, instructions=tuple(instructions)),
            privacy_findings=findings,
            claims=(
                Claim(
                    statement="Draft suppressed: " + ", ".join(reasons) + ".",
                    label=ClaimLabel.UNKNOWN,
                    confidence=ConfidenceBand.LOW,
                ),
            ),
            confidence=ConfidenceBand.LOW,
            confidence_rationale="No draft was released.",
            unknowns=("A reviewed case note does not exist yet.",),
        )
