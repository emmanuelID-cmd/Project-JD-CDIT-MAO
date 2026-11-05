"""Local, policy-independent Triage proposal validation for synthetic fixtures.

This verifies source-span identity, not truth, policy entailment, downstream
permissions, or reviewer approval. Model-supplied text remains untrusted.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, ValidationError

from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.segment import extract_request_parts
from cdit_support_mao.contracts.common import RunContext, SourceRef, StrictModel


class UntrustedProposalInput(StrictModel):
    """Strict caller input. Source text, citations and confidence are not caller-settable."""
    item_index: int = Field(strict=True, ge=1, le=8)
    category: Literal["unknown"] = "unknown"
    urgency: Literal["unknown"] = "unknown"
    destination: Literal["unknown"] = "unknown"
    unknowns: tuple[str, ...] = Field(default=(), max_length=16, repr=False)
    conflicts: tuple[str, ...] = Field(default=(), max_length=16, repr=False)


class ProvisionalItemProposal(StrictModel):
    """An untrusted report attribution with no fact/policy/authority validation."""
    trace_id: str
    handoff_id: str
    handoff_state_version: int = Field(strict=True, ge=2)
    context: RunContext
    item_index: int = Field(strict=True, ge=1, le=8)
    item_count: int = Field(strict=True, ge=1, le=8)
    start_codepoint: int = Field(strict=True, ge=0)
    end_codepoint: int = Field(strict=True, ge=1)
    reported_text: str = Field(min_length=1, max_length=2000, repr=False)
    reported_source: SourceRef
    source_check: Literal["exact_case_message_span_only"] = "exact_case_message_span_only"
    report_status: Literal["untrusted_report_not_verified_event"] = "untrusted_report_not_verified_event"
    segmentation_status: Literal["segmented_needs_classification", "needs_auditor"]
    category: Literal["unknown"] = "unknown"
    urgency: Literal["unknown"] = "unknown"
    destination: Literal["unknown"] = "unknown"
    unknowns: tuple[str, ...] = Field(default=(), repr=False)
    conflicts: tuple[str, ...] = Field(default=(), repr=False)
    notes_trust: Literal["untrusted_candidate_data"] = "untrusted_candidate_data"
    status: Literal["abstained_needs_human"] = "abstained_needs_human"
    human_review_required: Literal[True] = True
    downstream_allowed: Literal[False] = False
    dispatched: Literal[False] = False
    parent_complete: Literal[False] = False


def validate_provisional_item(
    registry: HandoffRegistry, *, handoff_id: str, expected_version: int,
    receiver_capability: object, context: RunContext, candidate: object,
    now: datetime | None = None,
) -> ProvisionalItemProposal:
    """Return a scoped, source-bound abstention, never a routed handoff.

    The receiver capability and synthetic caller-supplied clock are trusted
    runtime fixture inputs, not model- or user-supplied authority. No source
    field or span comes from the candidate. The returned snapshot can become
    stale immediately; any later consumer must revalidate authorization,
    ownership and versions before use. No JSON serialization belongs in logs.
    """
    try:
        raw = candidate.model_dump() if isinstance(candidate, UntrustedProposalInput) else candidate
        proposal = UntrustedProposalInput.model_validate(raw)
    except (ValidationError, TypeError, ValueError):
        raise HandoffError("invalid_triage_proposal") from None
    # Bound untrusted notes without reflecting their contents in errors.
    if any(not value.strip() or len(value) > 500 for value in proposal.unknowns + proposal.conflicts):
        raise HandoffError("invalid_triage_proposal")
    parts = extract_request_parts(registry, handoff_id=handoff_id,
        expected_version=expected_version, receiver_capability=receiver_capability,
        context=context, now=now)
    if proposal.item_index > len(parts.items):
        raise HandoffError("invalid_request_item")
    item = parts.items[proposal.item_index - 1]
    result = ProvisionalItemProposal(trace_id=parts.trace_id, handoff_id=parts.handoff_id,
        handoff_state_version=expected_version, context=parts.context, item_index=item.item_index,
        item_count=len(parts.items), start_codepoint=item.start_codepoint, end_codepoint=item.end_codepoint,
        reported_text=item.reported_text, reported_source=item.source, segmentation_status=parts.status,
        unknowns=proposal.unknowns, conflicts=proposal.conflicts)
    registry.validate_active(handoff_id, expected_version=expected_version,
        capability=receiver_capability, context=context, now=now)
    return result
