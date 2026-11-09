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
- ``LinkedItemRef`` and ``TriageItemScope`` (proposed S-1, 2026-11-05) let one
  linked item of a multi-item case message travel as its own Triage handoff.
  They carry identity, span, eligibility, and by-reference proposal fields only.
  Manny's Lane owns segmentation, classification, attention, and dispatch.
- S-1.1 (approved by Manny, 2026-11-08) moves the item scope to version 0.2: an
  ``attention_check`` status and a content-addressed category taxonomy citation.
  Legacy 0.1 scopes stay accepted under the S-1 rules.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from cdit_support_mao.contracts.common import (
    SHA256_HEX_PATTERN,
    AgentContribution,
    AgentStatus,
    ClaimLabel,
    ConfidenceBand,
    ReasonCode,
    RunContext,
    SourceKind,
    SourceRef,
    Stage,
    StrictModel,
    stable_id,
)

#: Version of the linked-item scope carried on a Triage handoff (S-1.1, Manny Q4).
TRIAGE_ITEM_SCOPE_VERSION = "triage-item-scope-0.2-proposed"
#: Legacy S-1 scope version, still accepted under the S-1 validation rules (Manny Q4).
LEGACY_TRIAGE_ITEM_SCOPE_VERSION = "triage-item-scope-0.1-proposed"
#: Upper bound on linked items per parent message (matches Manny's segmentation limit).
MAX_LINKED_ITEMS = 8
#: Source ID of the pinned synthetic category taxonomy (S-1.1, F-4, Manny Q2).
CATEGORY_TAXONOMY_SOURCE_ID = "SYN-TICKET-CATEGORY-TAXONOMY"
_TAXONOMY_LOCATOR = re.compile(r"category_sha256:([0-9a-f]{64})")

#: What the attention literal check did for one item (S-1.1, F-3, Manny Q1).
AttentionCheck = Literal["potential_attention", "no_configured_match", "check_not_run"]


def is_category_taxonomy_ref(source: SourceRef) -> bool:
    """True for a self-consistent, content-addressed category taxonomy reference.

    Mirrors Triage's own rule (``agents/triage/multi_item.py``): the locator names
    the full taxonomy digest and the version is its first 16 hex characters. This
    checks shape only; Triage's pinned loader decides whether the taxonomy is trusted.
    """
    if source.kind is not SourceKind.POLICY_RULE or source.source_id != CATEGORY_TAXONOMY_SOURCE_ID:
        return False
    match = _TAXONOMY_LOCATOR.fullmatch(source.locator or "")
    return match is not None and source.version == f"sha256-{match.group(1)[:16]}"

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


def item_id_for(
    context: RunContext, parent_digest: str, item_index: int, source_start: int, source_end: int
) -> str:
    """Run-scoped linked-item ID, as approved by Manny (Q-C, 2026-11-05).

    A new run, case version, or segmentation may produce a new ID; the ID is not
    stable across runs and must not be used as a durable ticket identifier.
    """
    return stable_id(
        "ITM", context.run_id, context.case_version, parent_digest, item_index, source_start, source_end
    )


class LinkedItemRef(StrictModel):
    """Identity of one linked item of a parent case message. Never carries text.

    Knowledge echoes this block (``KnowledgeResult.item_scope_ref``) so every
    downstream stage can join results item by item without re-reading case text.
    """

    scope_contract_version: Literal[
        "triage-item-scope-0.1-proposed", "triage-item-scope-0.2-proposed"
    ] = TRIAGE_ITEM_SCOPE_VERSION
    item_id: str = Field(pattern=r"^ITM-[0-9A-F]{16}$")
    item_index: int = Field(strict=True, ge=1, le=MAX_LINKED_ITEMS)
    item_count: int = Field(strict=True, ge=1, le=MAX_LINKED_ITEMS)
    parent_source: SourceRef
    parent_digest: str = Field(pattern=SHA256_HEX_PATTERN, description="SHA-256 of the parent message text")
    source_start: int = Field(strict=True, ge=0, description="Codepoint offset in the parent message")
    source_end: int = Field(strict=True, ge=1, description="Exclusive codepoint offset in the parent message")

    @model_validator(mode="after")
    def _shape(self) -> LinkedItemRef:
        if self.item_index > self.item_count:
            raise ValueError("item_index_exceeds_item_count")
        if self.source_start >= self.source_end:
            raise ValueError("item_span_empty_or_reversed")
        if self.parent_source.kind is not SourceKind.CASE_FIELD or self.parent_source.locator != "message":
            raise ValueError("parent_source_must_be_case_message")
        return self

    def matches_context(self, context: RunContext) -> bool:
        """True when the parent source is this run's case message at this case version."""
        return (
            self.parent_source.source_id == context.case_id
            and self.parent_source.version == str(context.case_version)
        )

    def expected_item_id(self, context: RunContext) -> str:
        return item_id_for(context, self.parent_digest, self.item_index, self.source_start, self.source_end)

    @property
    def is_legacy_scope(self) -> bool:
        """True for a 0.1 scope, which keeps the S-1 validation rules."""
        return self.scope_contract_version == LEGACY_TRIAGE_ITEM_SCOPE_VERSION


class TriageItemScope(StrictModel):
    """Linked-item scope of one Triage handoff (proposed S-1, 2026-11-05).

    Eligibility for Knowledge (Manny, Q-A): a ``candidate_boundary`` item with an
    inferred category may go to Knowledge for read-only retrieval while the
    human Auditor reviews urgency. Later processing (Troubleshooting,
    Documentation) waits until ``auditor_review`` is ``band_and_route_determined``.

    Category, attention, and Auditor fields are carried *by reference* for
    Documentation; Knowledge never reads their values.

    ``attention_check`` (S-1.1, scope 0.2 only) says what the attention literal
    check did for this item. ``no_configured_match`` is never a risk assessment,
    and ``check_not_run`` is information for Staff/Admin, not an extra hold (Q3).
    It is required on every 0.2 scope (Q5, 2026-11-09, once Manny's connector
    always supplied it in ``1c822c8``) and must stay ``None`` on a legacy 0.1 scope.
    """

    identity: LinkedItemRef
    segmentation: Literal["candidate_boundary", "ambiguous_parent"]
    depends_on: tuple[int, ...] = Field(default=(), max_length=MAX_LINKED_ITEMS - 1)
    item_status: Literal["proposal_for_human_review", "abstained_needs_human"]
    category_label: Literal["inference", "unknown"]
    category_basis: str | None = Field(default=None, min_length=1, max_length=500)
    category_sources: tuple[SourceRef, ...] = Field(default=(), max_length=8)
    category_evidence_span: tuple[int, int] | None = Field(
        default=None, description="Codepoint span of the category evidence in the parent message"
    )
    auditor_review: Literal["pending", "band_and_route_determined"] = "pending"
    attention_ref: SourceRef | None = Field(
        default=None, description="Reference to this item's attention flag (Manny, Q-B); never its text"
    )
    parent_attention_flagged: bool = Field(
        default=False, description="True when any item of the parent has an attention flag (parent summary)"
    )
    attention_check: AttentionCheck | None = Field(
        default=None,
        description="S-1.1: what the attention literal check did for this item; required on scope 0.2 (Q5), "
        "None only on a legacy 0.1 scope",
    )

    @model_validator(mode="after")
    def _scope_rules(self) -> TriageItemScope:
        ident = self.identity
        if len(set(self.depends_on)) != len(self.depends_on) or any(
            i < 1 or i > ident.item_count or i == ident.item_index for i in self.depends_on
        ):
            raise ValueError("invalid_item_dependency")
        if self.category_label == "inference" and (not self.category_basis or not self.category_sources):
            raise ValueError("category_inference_requires_basis_and_sources")
        if self.category_label == "unknown" and (self.category_basis or self.category_sources):
            raise ValueError("unknown_category_must_not_include_proposal")
        if self.segmentation == "ambiguous_parent" and (
            self.category_label != "unknown" or self.item_status != "abstained_needs_human"
        ):
            raise ValueError("ambiguous_segmentation_requires_abstention")
        if self.category_evidence_span is not None:
            start, end = self.category_evidence_span
            if not ident.source_start <= start < end <= ident.source_end:
                raise ValueError("category_evidence_outside_item_span")
        if self.attention_ref is not None and not self.parent_attention_flagged:
            raise ValueError("item_attention_requires_parent_summary")
        if self.attention_check is None and not ident.is_legacy_scope:
            raise ValueError("attention_check_required_for_scope_0_2")
        if self.attention_check is not None:
            if ident.is_legacy_scope:
                raise ValueError("attention_check_requires_scope_0_2")
            if (self.attention_check == "potential_attention") != (self.attention_ref is not None):
                raise ValueError("attention_check_ref_mismatch")
            if self.attention_check == "check_not_run" and self.parent_attention_flagged:
                raise ValueError("attention_check_not_run_but_parent_flagged")
        return self


class TriageHandoff(AgentContribution):
    """Fields Shawn's agents read from the Triage contribution (A2).

    ``item_scope`` is ``None`` for a single-case handoff (unchanged behaviour).
    When set, ``case_summary`` is exactly one linked item's text, never the parent.
    """

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
    item_scope: TriageItemScope | None = None

    @model_validator(mode="after")
    def _item_scope_consistent(self) -> TriageHandoff:
        scope = self.item_scope
        if scope is None:
            return self
        ident = scope.identity
        if not ident.matches_context(self.context):
            raise ValueError("item_parent_source_context_mismatch")
        if ident.item_id != ident.expected_item_id(self.context):
            raise ValueError("item_id_mismatch")
        if ident.source_end - ident.source_start != len(self.case_summary):
            raise ValueError("item_span_length_mismatch")
        if (self.status is AgentStatus.COMPLETED) != (scope.item_status == "proposal_for_human_review"):
            raise ValueError("item_status_mismatch")
        if (scope.category_label == "inference") != bool(self.category and self.category.strip()):
            raise ValueError("item_category_label_mismatch")
        if scope.auditor_review == "band_and_route_determined" and self.urgency == "unknown":
            raise ValueError("auditor_determination_requires_urgency_band")
        for source in scope.category_sources:
            if source.kind is SourceKind.CASE_FIELD and (
                source.source_id != self.context.case_id or source.version != str(self.context.case_version)
            ):
                raise ValueError("item_claim_case_source_mismatch")
            if source.kind is not SourceKind.POLICY_RULE:
                continue
            # S-1.1 (scope 0.2): the taxonomy is cited by its own content-addressed
            # version. Every other policy source keeps the run's policy version, and
            # a legacy 0.1 scope keeps the S-1 rule for all policy sources.
            if not ident.is_legacy_scope and source.source_id == CATEGORY_TAXONOMY_SOURCE_ID:
                if not is_category_taxonomy_ref(source):
                    raise ValueError("item_claim_taxonomy_source_mismatch")
            elif source.version != self.context.policy_version:
                raise ValueError("item_claim_policy_version_mismatch")
        return self


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
    item_scope_ref: LinkedItemRef | None = Field(
        default=None, description="Echo of the Triage item identity; None on single-case runs"
    )
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
