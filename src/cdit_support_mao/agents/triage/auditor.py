"""Prepare local, untrusted unknown-item proposals for later human review.

This is not a dispatch, ticket update, authentication check for a reviewer,
or proof that a human has accepted a review. Snapshots require revalidation
by the trusted coordinator before any later use.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, Field, field_validator

from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.segment import extract_request_parts
from cdit_support_mao.contracts.common import RunContext, SourceRef, StrictModel


AUDITOR_QUESTIONS = (
    "What is the request and which system or service is affected?",
    "What is the current impact, affected scope, and timing?",
    "Which approved policy and destination apply?",
)


class AuditorReviewProposal(StrictModel):
    """A provisional item, not an accepted or dispatched human handoff."""

    model_config = ConfigDict(hide_input_in_errors=True)

    trace_id: str
    handoff_id: str
    handoff_state_version: int = Field(strict=True, ge=2)
    context: RunContext
    item_index: int = Field(strict=True, ge=1, le=8)
    item_count: int = Field(strict=True, ge=1, le=8)
    source: SourceRef
    start_codepoint: int = Field(strict=True, ge=0)
    end_codepoint: int = Field(strict=True, ge=1)
    reported_text: str = Field(min_length=1, max_length=2000, repr=False)
    text_trust: Literal["untrusted_case_data"] = "untrusted_case_data"
    segmentation_status: Literal["segmented_needs_classification", "needs_auditor"]
    segmentation_reason: Literal["segmented", "uncertain_segmentation", "too_many_items"]
    category: Literal["unknown"] = "unknown"
    urgency: Literal["unknown"] = "unknown"
    destination: Literal["unknown"] = "unknown"
    status: Literal["abstained_needs_human"] = "abstained_needs_human"
    questions: tuple[str, ...] = Field(default=AUDITOR_QUESTIONS, repr=False)

    @field_validator("questions")
    @classmethod
    def _fixed_questions(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if value != AUDITOR_QUESTIONS:
            raise ValueError("invalid_auditor_questions")
        return value
    human_review_required: Literal[True] = True
    downstream_allowed: Literal[False] = False
    parent_complete: Literal[False] = False
    dispatched: Literal[False] = False


def prepare_auditor_review(
    registry: HandoffRegistry, *, handoff_id: str, expected_version: int,
    receiver_capability: object, context: RunContext, item_index: int,
    now: datetime | None = None,
) -> AuditorReviewProposal:
    """Prepare a scoped snapshot for an unknown item without sending it.

    Only a trusted receiver capability can read the currently acknowledged
    handoff. The item is re-extracted from the source, never supplied by the
    caller. A later review integration must recheck current authorization,
    version and ownership before disclosing or acting on this snapshot.
    """
    parts = extract_request_parts(registry, handoff_id=handoff_id,
        expected_version=expected_version, receiver_capability=receiver_capability,
        context=context, now=now)
    if type(item_index) is not int or not 1 <= item_index <= len(parts.items):
        raise HandoffError("invalid_request_item")
    item = parts.items[item_index - 1]
    proposal = AuditorReviewProposal(trace_id=parts.trace_id, handoff_id=parts.handoff_id,
        handoff_state_version=expected_version, context=parts.context,
        item_index=item.item_index, item_count=len(parts.items), source=item.source,
        start_codepoint=item.start_codepoint, end_codepoint=item.end_codepoint,
        reported_text=item.reported_text, segmentation_status=parts.status,
        segmentation_reason=parts.reason_code)
    registry.validate_active(handoff_id, expected_version=expected_version,
        capability=receiver_capability, context=context, now=now)
    return proposal
