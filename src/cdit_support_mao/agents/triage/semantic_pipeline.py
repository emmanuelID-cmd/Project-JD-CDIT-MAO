"""Prepare a minimized semantic request and execute authorized Triage inference.

This is a provider-isolated composition boundary. It excludes ambiguous parent
segmentation and strips run, case, policy, source, and example identifiers.
Model calls require explicit per-run billable authorization and fail closed to None.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from cdit_support_mao.agents.coordinator.handoff import HandoffRegistry
    from cdit_support_mao.agents.triage.anthropic_adapter import AnthropicClient
    from cdit_support_mao.contracts.common import RunContext

from cdit_support_mao.agents.triage.anthropic_adapter import (
    AnthropicTriageError,
    TriageModelResult,
    classify_synthetic_items,
)
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


def execute_semantic_triage(
    registry: HandoffRegistry,
    *,
    handoff_id: str,
    expected_version: int,
    receiver_capability: object,
    context: RunContext,
    candidate: MultiItemTriageCandidate,
    allowed_categories: tuple[str, ...],
    client: AnthropicClient | None = None,
    billable_call_authorized: bool = False,
    now: datetime | None = None,
    on_failure: Callable[[str], None] | None = None,
    on_provider_attempt: Callable[[], None] | None = None,
) -> TriageModelResult | None:
    """Execute model-backed semantic category proposal only when authorized.

    Fails closed to None on missing authorization, missing client, stale handoff,
    ambiguous segmentation, provider timeout/error, or output contract violation.
    All fallback cases require human Auditor review.
    """
    if client is None or billable_call_authorized is not True:
        if on_failure is not None:
            on_failure("triage_call_not_authorized_or_client_missing")
        return None

    try:
        registry.validate_active(
            handoff_id,
            expected_version=expected_version,
            capability=receiver_capability,
            context=context,
            now=now,
        )
    except Exception:
        if on_failure is not None:
            on_failure("triage_handoff_preflight_failed")
        return None

    try:
        request = prepare_semantic_request(
            candidate,
            allowed_categories=allowed_categories,
        )
    except TriageSemanticPreparationError as exc:
        if on_failure is not None:
            on_failure(str(exc))
        return None

    def handoff_preflight() -> bool:
        try:
            registry.validate_active(
                handoff_id,
                expected_version=expected_version,
                capability=receiver_capability,
                context=context,
                now=now,
            )
            return True
        except Exception:
            return False

    try:
        return classify_synthetic_items(
            request,
            client=client,
            billable_call_authorized=billable_call_authorized,
            handoff_preflight=handoff_preflight,
            on_provider_attempt=on_provider_attempt,
        )
    except AnthropicTriageError as exc:
        if on_failure is not None:
            on_failure(exc.code)
        return None
