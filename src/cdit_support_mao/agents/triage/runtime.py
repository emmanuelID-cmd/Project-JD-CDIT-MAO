"""Local runtime-callable entry point for validated synthetic Triage."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import ValidationError, model_validator

from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.anthropic_adapter import AnthropicClient, TriageModelResult
from cdit_support_mao.agents.triage.attention import (
    AttentionSignal,
    FixtureAttentionPatterns,
    inspect_attention_signal,
)
from cdit_support_mao.agents.triage.development_examples import (
    DevelopmentCatalogError,
    DevelopmentCategoryTaxonomy,
    load_project_category_taxonomy,
)
from cdit_support_mao.agents.triage.input import TriageInput, read_acknowledged_input
from cdit_support_mao.agents.triage.multi_item import LinkedTriageItem, MultiItemTriageCandidate
from cdit_support_mao.agents.triage.multi_item_adapter import prepare_multi_item_candidate
from cdit_support_mao.agents.triage.semantic_pipeline import execute_semantic_triage
from cdit_support_mao.contracts.common import RunContext, SourceKind, SourceRef, StrictModel


class TriageRuntimeResult(StrictModel):
    """Ephemeral proposal result; never an action authorization or dispatch."""

    triage_input: TriageInput
    candidate: MultiItemTriageCandidate
    attention_signal: AttentionSignal | None = None
    category_taxonomy: DevelopmentCategoryTaxonomy | None = None
    semantic_result: TriageModelResult | None = None
    status: Literal["proposal_for_human_review", "needs_human_review"]
    reason: Literal["semantic_result_unavailable", "triage_result_validation_failed", "category_taxonomy_unavailable", "handoff_stale"] | None = None
    urgency: Literal["unknown"] = "unknown"
    destination: Literal["unknown"] = "unknown"
    human_review_required: Literal[True] = True
    downstream_allowed: Literal[False] = False
    dispatched: Literal[False] = False

    @model_validator(mode="after")
    def result_matches_evidence(self) -> TriageRuntimeResult:
        if self.attention_signal is not None and (
            self.attention_signal.trace_id != self.triage_input.trace_id
            or self.attention_signal.handoff_id != self.triage_input.handoff_id
            or self.attention_signal.handoff_state_version != self.triage_input.handoff_state_version
            or self.attention_signal.context != self.triage_input.context
        ):
            raise ValueError("triage_runtime_attention_context_mismatch")
        if self.attention_signal is not None:
            for match in self.attention_signal.matches:
                if (match.source != self.triage_input.source
                        or match.end_codepoint > len(self.triage_input.reported_message)):
                    raise ValueError("triage_runtime_attention_evidence_mismatch")
        if self.semantic_result is None:
            if self.status != "needs_human_review" or self.reason is None:
                raise ValueError("triage_runtime_missing_semantic_result")
            if self.reason == "category_taxonomy_unavailable" and self.category_taxonomy is not None:
                raise ValueError("triage_taxonomy_fallback_mismatch")
            return self
        if (self.status != "proposal_for_human_review" or self.reason is not None
                or self.category_taxonomy is None):
            raise ValueError("triage_runtime_proposal_state_mismatch")
        outputs = self.semantic_result.proposal.items
        candidates = {item.item_index: item for item in self.candidate.items}
        if tuple(item.item_index for item in outputs) != tuple(candidates):
            raise ValueError("triage_runtime_item_coverage_mismatch")
        for output in outputs:
            source_item = candidates[output.item_index]
            if (output.category is not None and output.category not in self.category_taxonomy.categories
                    or output.evidence_quote is not None and output.evidence_quote not in source_item.reported_text):
                raise ValueError("triage_runtime_evidence_mismatch")
            if (source_item.category != output.category
                    or source_item.category_label != output.category_label
                    or source_item.category_evidence_quote != output.evidence_quote):
                raise ValueError("triage_runtime_candidate_mismatch")
        return self


def run_triage_runtime(
    registry: HandoffRegistry,
    *,
    handoff_id: str,
    expected_version: int,
    receiver_capability: object,
    context: RunContext,
    category_taxonomy: DevelopmentCategoryTaxonomy | None,
    fixture_patterns: FixtureAttentionPatterns | None = None,
    client: AnthropicClient | None = None,
    billable_call_authorized: bool = False,
    now: datetime | None = None,
) -> TriageRuntimeResult:
    """Run semantic Triage on a current Coordinator-acknowledged synthetic input.

    The caller supplies the client; this function never constructs one or loads
    credentials. A stale/invalid handoff detected before candidate creation
    raises the registry's content-free HandoffError. If the handoff becomes
    stale during the semantic preflight, the semantic pipeline returns no
    result and this wrapper returns a review-required result. The injected
    category taxonomy is loaded from the pinned project source and exposes only
    its versioned category names;
    the 80 example queries, bands, and conditions are not model examples or
    labels. No taxonomy means human review without a provider call.
    Nothing is written or dispatched.
    """
    triage_input = read_acknowledged_input(
        registry,
        handoff_id=handoff_id,
        expected_version=expected_version,
        receiver_capability=receiver_capability,
        context=context,
        now=now,
    )
    candidate = prepare_multi_item_candidate(
        registry,
        handoff_id=handoff_id,
        expected_version=expected_version,
        receiver_capability=receiver_capability,
        context=context,
        catalog=None,
        now=now,
    )
    unbound_candidate = candidate
    attention_signal = None
    if fixture_patterns is not None:
        attention_signal = inspect_attention_signal(
            registry,
            handoff_id=handoff_id,
            expected_version=expected_version,
            receiver_capability=receiver_capability,
            context=context,
            fixture_patterns=fixture_patterns,
            now=now,
        )
    if category_taxonomy is None:
        if not _handoff_is_active(registry, handoff_id, expected_version, receiver_capability, context, now):
            return _stale_handoff_review(triage_input, candidate)
        return TriageRuntimeResult(
            triage_input=triage_input,
            candidate=candidate,
            attention_signal=attention_signal,
            status="needs_human_review",
            reason="category_taxonomy_unavailable",
        )
    if not isinstance(category_taxonomy, DevelopmentCategoryTaxonomy):
        raise HandoffError("invalid_category_taxonomy")
    try:
        category_taxonomy = DevelopmentCategoryTaxonomy.model_validate(category_taxonomy.model_dump())
    except (ValidationError, TypeError, ValueError):
        raise HandoffError("invalid_category_taxonomy") from None
    try:
        trusted_taxonomy = load_project_category_taxonomy()
    except DevelopmentCatalogError:
        if not _handoff_is_active(registry, handoff_id, expected_version, receiver_capability, context, now):
            return _stale_handoff_review(triage_input, candidate)
        return TriageRuntimeResult(
            triage_input=triage_input,
            candidate=candidate,
            attention_signal=attention_signal,
            status="needs_human_review",
            reason="category_taxonomy_unavailable",
        )
    if category_taxonomy != trusted_taxonomy:
        raise HandoffError("invalid_category_taxonomy")
    semantic_result = execute_semantic_triage(
        registry,
        handoff_id=handoff_id,
        expected_version=expected_version,
        receiver_capability=receiver_capability,
        context=context,
        candidate=candidate,
        allowed_categories=category_taxonomy.categories,
        client=client,
        billable_call_authorized=billable_call_authorized,
        now=now,
    )
    if semantic_result is None:
        if not _handoff_is_active(registry, handoff_id, expected_version, receiver_capability, context, now):
            return _stale_handoff_review(triage_input, unbound_candidate)
        return TriageRuntimeResult(
            triage_input=triage_input,
            candidate=candidate,
            attention_signal=attention_signal,
            category_taxonomy=category_taxonomy,
            status="needs_human_review",
            reason="semantic_result_unavailable",
        )
    if not _handoff_is_active(registry, handoff_id, expected_version, receiver_capability, context, now):
        return _stale_handoff_review(triage_input, unbound_candidate)
    try:
        candidate = _bind_category_proposals(candidate, category_taxonomy, semantic_result)
    except HandoffError:
        if not _handoff_is_active(registry, handoff_id, expected_version, receiver_capability, context, now):
            return _stale_handoff_review(triage_input, unbound_candidate)
        return TriageRuntimeResult(
            triage_input=triage_input,
            candidate=unbound_candidate,
            attention_signal=attention_signal,
            category_taxonomy=category_taxonomy,
            status="needs_human_review",
            reason="triage_result_validation_failed",
        )
    if not _handoff_is_active(registry, handoff_id, expected_version, receiver_capability, context, now):
        return _stale_handoff_review(triage_input, unbound_candidate)
    return TriageRuntimeResult(
        triage_input=triage_input,
        candidate=candidate,
        attention_signal=attention_signal,
        category_taxonomy=category_taxonomy,
        semantic_result=semantic_result,
        status="proposal_for_human_review",
        reason=None,
    )


def _handoff_is_active(
    registry: HandoffRegistry,
    handoff_id: str,
    expected_version: int,
    receiver_capability: object,
    context: RunContext,
    now: datetime | None,
) -> bool:
    try:
        registry.validate_active(
            handoff_id,
            expected_version=expected_version,
            capability=receiver_capability,
            context=context,
            now=now,
        )
    except HandoffError:
        return False
    return True


def _stale_handoff_review(triage_input: TriageInput, candidate: MultiItemTriageCandidate) -> TriageRuntimeResult:
    """Return only the original unbound snapshot when state changed mid-run."""
    return TriageRuntimeResult(
        triage_input=triage_input,
        candidate=candidate,
        status="needs_human_review",
        reason="handoff_stale",
    )


def _bind_category_proposals(
    candidate: MultiItemTriageCandidate,
    taxonomy: DevelopmentCategoryTaxonomy,
    semantic_result: TriageModelResult,
) -> MultiItemTriageCandidate:
    """Join model proposals to Manny-local items with both evidence sources."""
    outputs = {item.item_index: item for item in semantic_result.proposal.items}
    if tuple(outputs) != tuple(item.item_index for item in candidate.items):
        raise HandoffError("triage_runtime_item_coverage_mismatch")
    taxonomy_ref = SourceRef(
        kind=SourceKind.POLICY_RULE,
        source_id=taxonomy.source.source_id,
        version=taxonomy.source.version,
        locator=f"category_sha256:{taxonomy.taxonomy_sha256}",
    )
    bound_items: list[LinkedTriageItem] = []
    for item in candidate.items:
        output = outputs[item.item_index]
        if output.category is None:
            update = {
                "category": None,
                "category_label": "unknown",
                "category_sources": (),
                "category_basis": None,
                "category_evidence_quote": None,
                "missing_facts": output.missing_questions,
                "status": "abstained_needs_human",
            }
        else:
            update = {
                "category": output.category,
                "category_label": "inference",
                "category_sources": (item.source, taxonomy_ref),
                "category_basis": output.rationale,
                "category_evidence_quote": output.evidence_quote,
                "missing_facts": output.missing_questions,
                "status": "proposal_for_human_review",
            }
        try:
            bound_items.append(LinkedTriageItem.model_validate(item.model_copy(update=update).model_dump()))
        except (ValidationError, TypeError, ValueError):
            raise HandoffError("triage_runtime_item_validation_failed") from None
    try:
        return MultiItemTriageCandidate.model_validate(
            candidate.model_copy(update={"items": tuple(bound_items)}).model_dump()
        )
    except (ValidationError, TypeError, ValueError):
        raise HandoffError("triage_runtime_candidate_validation_failed") from None
