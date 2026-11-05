"""Prepare a minimized semantic request from a validated local Triage candidate.

This is a provider-free composition boundary. It excludes ambiguous parent
segmentation and strips run, case, policy, source, and example identifiers.
"""
from __future__ import annotations

from cdit_support_mao.agents.triage.multi_item import MultiItemTriageCandidate
from cdit_support_mao.agents.triage.semantic_contract import (
    TriageModelItemInput,
    TriageSemanticRequest,
)


class TriageSemanticPreparationError(ValueError):
    """Content-free fail-closed error preparing semantic model input."""


def prepare_semantic_request(
    candidate: MultiItemTriageCandidate,
    *,
    allowed_categories: tuple[str, ...],
) -> TriageSemanticRequest:
    """Build a minimized request only when each item has a clear boundary.

    Existing fixture proposals and example references are intentionally not
    sent to the model. They remain separate evidence for later human review.
    """
    if not isinstance(candidate, MultiItemTriageCandidate):
        raise TriageSemanticPreparationError("invalid_triage_candidate")
    if any(item.segmentation != "candidate_boundary" for item in candidate.items):
        raise TriageSemanticPreparationError("ambiguous_segmentation_requires_auditor")
    try:
        return TriageSemanticRequest(
            items=tuple(
                TriageModelItemInput(item_index=item.item_index, text=item.reported_text)
                for item in candidate.items
            ),
            allowed_categories=allowed_categories,
            data_classification="synthetic",
        )
    except (TypeError, ValueError):
        raise TriageSemanticPreparationError("invalid_triage_semantic_request") from None
