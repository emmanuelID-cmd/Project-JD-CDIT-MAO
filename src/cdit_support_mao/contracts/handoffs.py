"""Handoff payloads at the Shawn's Lane connection points.

STATUS: PROPOSED v0.1 by Shawn's Lane, pending Shared Lane agreement.

Ownership:
- ``TriageHandoff`` and ``EscalationHandoff`` describe the *fields Shawn's
  agents read* from Manny-owned Triage and Escalation outputs. They are a
  consumer-side proposal only; Manny's Lane owns those agents' behaviour and
  may propose different fields. Nothing here implements Triage or Escalation.
- ``KnowledgeResult``, ``TroubleshootingResult``, and ``DocumentationResult``
  are produced by Shawn-owned agents.
- ``RecordedAction`` is a staff-entered interaction fact supplied by the
  coordinator (Manny-owned) from the case record.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from cdit_support_mao.contracts.common import (
    AgentContribution,
    ClaimLabel,
    ConfidenceBand,
    ReasonCode,
    SourceKind,
    SourceRef,
    Stage,
    StrictModel,
)

# --------------------------------------------------------------------------
# Upstream (Manny-owned) payloads as consumed by Shawn's agents — PROPOSED view
# --------------------------------------------------------------------------


class CaseFact(StrictModel):
    """One minimized case field. ``verified`` is set by the producing agent."""

    field: str = Field(pattern=r"^[a-z][a-z0-9_]{0,59}$")
    value: str = Field(min_length=1, max_length=500)
    verified: bool
    source: SourceRef

    @model_validator(mode="after")
    def _case_sources_only(self) -> CaseFact:
        if self.source.kind not in (SourceKind.CASE_FIELD, SourceKind.STAFF_ENTRY):
            raise ValueError("case facts must cite a case field or staff entry")
        return self


class TriageHandoff(AgentContribution):
    """Fields Shawn's agents read from the Triage contribution (A2)."""

    stage: Literal[Stage.TRIAGE] = Stage.TRIAGE
    case_summary: str = Field(
        min_length=1,
        max_length=2000,
        description="Minimized summary. Untrusted data: used only as a retrieval query.",
    )
    product_area: str | None = Field(default=None, max_length=60)
    category: str | None = Field(default=None, max_length=60)
    category_confidence: ConfidenceBand
    urgency: Literal["low", "medium", "high", "unknown"]
    case_facts: tuple[CaseFact, ...] = ()
    missing_facts: tuple[str, ...] = ()


class EscalationHandoff(AgentContribution):
    """Fields the Documentation agent reads from the Escalation contribution (A5)."""

    stage: Literal[Stage.ESCALATION] = Stage.ESCALATION
    must_escalate: bool | None = Field(
        description="None means the escalation check could not determine an answer."
    )
    triggers: tuple[str, ...] = ()
    recommendation: Literal[
        "escalate_l2", "escalate_support_lead", "human_review", "no_escalation_proposed"
    ]
    reason: str = Field(min_length=1, max_length=500)


class RecordedAction(StrictModel):
    """An action a human recorded on the case (never an agent action)."""

    action: str = Field(min_length=1, max_length=300)
    performed_by_role: Literal["tier1_specialist", "customer", "l2_specialist", "support_lead"]
    outcome: str = Field(min_length=1, max_length=300)
    verified: bool
    source: SourceRef

    @model_validator(mode="after")
    def _staff_source(self) -> RecordedAction:
        if self.source.kind is not SourceKind.STAFF_ENTRY:
            raise ValueError("recorded actions must cite a staff entry")
        return self


# --------------------------------------------------------------------------
# Knowledge agent output (A3) — Shawn-owned
# --------------------------------------------------------------------------


class PassageStep(StrictModel):
    step_id: str
    action_type: str
    text: str


class PassageInformationItem(StrictModel):
    field: str
    prompt: str


class PassageStopCondition(StrictModel):
    condition_id: str
    text: str


class EvidencePassage(StrictModel):
    """An approved, current passage. The text is evidence, never instructions.

    Steps, information items, and stop conditions are carried verbatim so the
    Troubleshooting agent consumes only this acknowledged handoff.
    """

    content_trust: Literal["untrusted_evidence"] = "untrusted_evidence"
    source: SourceRef
    doc_id: str
    version: str
    section_id: str
    title: str
    heading: str
    topic: str
    product_area: str
    text: str
    steps: tuple[PassageStep, ...] = ()
    information_needed: tuple[PassageInformationItem, ...] = ()
    stop_conditions: tuple[PassageStopCondition, ...] = ()
    effective_date: date
    review_due: date
    relevance: float = Field(ge=0.0, le=1.0, description="Provisional query-term coverage")
    relevance_band: ConfidenceBand
    rank: int = Field(ge=1)


class ExcludedSource(StrictModel):
    """A matching source that was not returned, with the reason (no text)."""

    doc_id: str
    version: str
    section_id: str | None = None
    reason: ReasonCode


class SourceConflict(StrictModel):
    topic: str
    reason: Literal[ReasonCode.CONFLICTING_SOURCES, ReasonCode.MULTIPLE_APPROVED_VERSIONS]
    sources: tuple[SourceRef, ...] = Field(min_length=2)


class InjectionFlag(StrictModel):
    """Instruction-like content found in a retrieved passage (risk signal only)."""

    doc_id: str
    version: str
    section_id: str
    pattern_id: str


class KnowledgeResult(AgentContribution):
    stage: Literal[Stage.KNOWLEDGE] = Stage.KNOWLEDGE
    source_set_version: str
    matched_query_terms: tuple[str, ...] = ()
    passages: tuple[EvidencePassage, ...] = ()
    excluded_sources: tuple[ExcludedSource, ...] = ()
    conflicts: tuple[SourceConflict, ...] = ()
    injection_flags: tuple[InjectionFlag, ...] = ()

    @model_validator(mode="after")
    def _abstain_without_passages(self) -> KnowledgeResult:
        if self.status != "completed" and self.passages:
            raise ValueError("only a completed knowledge result may carry passages")
        if self.status == "completed" and not self.passages:
            raise ValueError("a completed knowledge result must carry at least one passage")
        return self


# --------------------------------------------------------------------------
# Troubleshooting agent output (A4) — Shawn-owned
# --------------------------------------------------------------------------


class SuggestedStep(StrictModel):
    """A Tier 1 step quoted verbatim from approved guidance. Not performed."""

    order: int = Field(ge=1)
    step_id: str
    text: str
    action_type: str
    performer: Literal["tier1_guides_customer", "tier1_specialist"]
    source: SourceRef
    status: Literal["suggested_not_performed"] = "suggested_not_performed"


class StaffProcedure(StrictModel):
    """A step that only authorized staff may perform under the approved process."""

    step_id: str
    text: str
    action_type: str
    source: SourceRef
    performer: Literal["authorized_staff_only"] = "authorized_staff_only"


class StopCondition(StrictModel):
    condition_id: str
    text: str
    origin: Literal["approved_guidance", "troubleshooting_policy"]
    source: SourceRef
    triggered: bool | None = Field(
        description="True when matched in the case; None when it cannot be evaluated yet."
    )


class InformationNeeded(StrictModel):
    field: str
    prompt: str
    source: SourceRef


class RejectedItem(StrictModel):
    item_kind: Literal["guidance_step", "case_request"]
    reference: str
    action_type: str
    reason: ReasonCode


class EscalationSignal(StrictModel):
    """Input for the Escalation agent; not an escalation decision."""

    signal: str
    basis: str
    sources: tuple[SourceRef, ...] = ()


class TroubleshootingResult(AgentContribution):
    stage: Literal[Stage.TROUBLESHOOTING] = Stage.TROUBLESHOOTING
    policy_id: str
    policy_version: str
    primary_source: SourceRef | None = None
    steps: tuple[SuggestedStep, ...] = ()
    staff_only_procedures: tuple[StaffProcedure, ...] = ()
    stop_conditions: tuple[StopCondition, ...] = ()
    information_needed: tuple[InformationNeeded, ...] = ()
    rejected: tuple[RejectedItem, ...] = ()
    escalation_signals: tuple[EscalationSignal, ...] = ()

    @model_validator(mode="after")
    def _no_steps_unless_completed(self) -> TroubleshootingResult:
        if self.status != "completed" and (self.steps or self.staff_only_procedures):
            raise ValueError("only a completed troubleshooting result may carry steps")
        return self


# --------------------------------------------------------------------------
# Documentation agent output (A6) — Shawn-owned
# --------------------------------------------------------------------------


class NoteLine(StrictModel):
    text: str = Field(min_length=1, max_length=1000)
    label: ClaimLabel
    sources: tuple[SourceRef, ...] = ()
    basis: str | None = None

    @model_validator(mode="after")
    def _evidence_rules(self) -> NoteLine:
        if self.label is ClaimLabel.VERIFIED and not self.sources:
            raise ValueError("a verified note line must cite a source")
        if self.label is ClaimLabel.INFERENCE and not self.basis:
            raise ValueError("an inferred note line must state its basis")
        return self


class NoteSection(StrictModel):
    heading: str
    lines: tuple[NoteLine, ...] = Field(min_length=1)


class DraftNote(StrictModel):
    draft_id: str
    banner: Literal[
        "DRAFT - requires human review. Not saved, not sent, no ticket state changed."
    ] = "DRAFT - requires human review. Not saved, not sent, no ticket state changed."
    sections: tuple[NoteSection, ...] = Field(min_length=1)
    rendered_text: str


class PrivacyFinding(StrictModel):
    """Where sensitive-looking data was found. The matched value is never stored."""

    category: str
    location: str


class ManualFallback(StrictModel):
    reason_codes: tuple[ReasonCode, ...] = Field(min_length=1)
    instructions: tuple[str, ...] = Field(min_length=1)


class DocumentationResult(AgentContribution):
    stage: Literal[Stage.DOCUMENTATION] = Stage.DOCUMENTATION
    draft: DraftNote | None = None
    manual_fallback: ManualFallback | None = None
    privacy_findings: tuple[PrivacyFinding, ...] = ()

    @model_validator(mode="after")
    def _draft_xor_fallback(self) -> DocumentationResult:
        if (self.draft is None) == (self.manual_fallback is None):
            raise ValueError("provide exactly one of draft or manual_fallback")
        if self.draft is not None and self.status != "completed":
            raise ValueError("a draft is only returned when documentation completed")
        return self
