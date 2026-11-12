"""Bounded synthetic Phase 2 snapshot of unknown items awaiting human review.

This is a local fixture composition, not an accepted handoff or real review.
It does not classify, use an LLM, route, dispatch, change a ticket or establish
semantic completeness. A downstream consumer must revalidate current scope,
case/policy versions and ownership at the moment of any later use; the final
check here cannot make a returned snapshot permanently fresh.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, ValidationError

from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.auditor import AuditorReviewProposal, prepare_auditor_review
from cdit_support_mao.agents.triage.segment import extract_request_parts
from cdit_support_mao.agents.triage.proposal import (
    ProvisionalItemProposal, UntrustedProposalInput, validate_provisional_item,
)
from cdit_support_mao.contracts.common import RunContext, StrictModel


class UnknownItemsSnapshot(StrictModel):
    """Ephemeral per-run suggestions, not a workflow transition or dispatch."""
    trace_id: str
    handoff_id: str
    handoff_state_version: int = Field(strict=True, ge=2)
    context: RunContext
    segmentation_status: Literal["segmented_needs_classification", "needs_auditor"]
    segmentation_reason: Literal["segmented", "uncertain_segmentation", "too_many_items"]
    proposals: tuple[AuditorReviewProposal, ...] = Field(min_length=1, max_length=8, repr=False)
    triage_proposals: tuple[ProvisionalItemProposal, ...] = Field(default=(), max_length=8, repr=False)
    semantic_completeness: Literal["unknown"] = "unknown"
    human_review_required: Literal[True] = True
    parent_complete: Literal[False] = False
    downstream_allowed: Literal[False] = False
    dispatched: Literal[False] = False


def prepare_unknown_items(registry: HandoffRegistry, *, handoff_id: str, expected_version: int,
                          receiver_capability: object, context: RunContext,
                          now: datetime | None = None,
                          item_candidates: object = None) -> UnknownItemsSnapshot:
    """Prepare exactly one local unknown proposal per conservatively detected item.

    The extractor and proposal builder read through current Coordinator-owned
    fixture gates. Optional per-item candidate notes remain untrusted, and are
    joined only after independent source and context checks. Every item is still
    unknown; no independent item may advance.
    The final check detects stale/cancelled handoffs during construction, not
    changes after return. Real-time access checks and an A2/Auditor handoff do
    not exist here. ``now`` is a fixture clock override, not real-time proof.
    """
    parts = extract_request_parts(registry, handoff_id=handoff_id, expected_version=expected_version,
        receiver_capability=receiver_capability, context=context, now=now)
    proposals = []
    for item in parts.items:
        proposal = prepare_auditor_review(registry, handoff_id=handoff_id,
            expected_version=expected_version, receiver_capability=receiver_capability,
            context=context, item_index=item.item_index, now=now)
        # Revalidate the whole proposal: model_copy can bypass frozen-model validation.
        try:
            if not isinstance(proposal, AuditorReviewProposal):
                raise HandoffError("invalid_unknown_item_proposal")
            proposal = AuditorReviewProposal.model_validate(proposal.model_dump())
        except ValidationError:
            raise HandoffError("invalid_unknown_item_proposal") from None
        # Do not join a proposal that no longer matches the initially read item.
        if (proposal.trace_id != parts.trace_id or proposal.handoff_id != parts.handoff_id
                or proposal.handoff_state_version != expected_version or proposal.context != parts.context
                or proposal.item_index != item.item_index or proposal.item_count != len(parts.items)
                or proposal.source != item.source or proposal.start_codepoint != item.start_codepoint
                or proposal.end_codepoint != item.end_codepoint or proposal.reported_text != item.reported_text
                or proposal.segmentation_status != parts.status or proposal.segmentation_reason != parts.reason_code):
            raise HandoffError("unknown_item_snapshot_mismatch")
        proposals.append(proposal)
    if item_candidates is None:
        item_candidates = ()
    if not isinstance(item_candidates, (tuple, list)) or len(item_candidates) > 8:
        raise HandoffError("invalid_triage_candidates")
    triage_proposals = []
    seen = set()
    for candidate in item_candidates:
        try:
            raw = candidate.model_dump() if isinstance(candidate, UntrustedProposalInput) else candidate
            supplied = UntrustedProposalInput.model_validate(raw)
        except (ValidationError, TypeError, ValueError):
            raise HandoffError("invalid_triage_candidate") from None
        if supplied.item_index in seen:
            raise HandoffError("duplicate_triage_item")
        seen.add(supplied.item_index)
        if supplied.item_index > len(parts.items):
            raise HandoffError("invalid_request_item")
        if any(not note.strip() or len(note) > 500 for note in supplied.unknowns + supplied.conflicts):
            raise HandoffError("invalid_triage_candidate")
        result = validate_provisional_item(registry, handoff_id=handoff_id,
            expected_version=expected_version, receiver_capability=receiver_capability,
            context=context, candidate=supplied, now=now)
        try:
            if not isinstance(result, ProvisionalItemProposal):
                raise HandoffError("invalid_provisional_item")
            result = ProvisionalItemProposal.model_validate(result.model_dump())
        except ValidationError:
            raise HandoffError("invalid_provisional_item") from None
        item = parts.items[supplied.item_index - 1]
        if (result.trace_id != parts.trace_id or result.handoff_id != parts.handoff_id
                or result.handoff_state_version != expected_version or result.context != parts.context
                or result.item_index != item.item_index or result.item_count != len(parts.items)
                or result.reported_source != item.source or result.start_codepoint != item.start_codepoint
                or result.end_codepoint != item.end_codepoint or result.reported_text != item.reported_text
                or result.segmentation_status != parts.status or result.unknowns != supplied.unknowns
                or result.conflicts != supplied.conflicts):
            raise HandoffError("provisional_item_snapshot_mismatch")
        triage_proposals.append(result)
    registry.validate_active(handoff_id, expected_version=expected_version,
        capability=receiver_capability, context=context, now=now)
    return UnknownItemsSnapshot(trace_id=parts.trace_id, handoff_id=parts.handoff_id,
        handoff_state_version=expected_version, context=parts.context,
        segmentation_status=parts.status, segmentation_reason=parts.reason_code,
        proposals=tuple(proposals), triage_proposals=tuple(triage_proposals))
