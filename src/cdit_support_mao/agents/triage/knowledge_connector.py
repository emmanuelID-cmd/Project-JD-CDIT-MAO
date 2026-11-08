"""Manny-owned bridge from validated A2 items to the accepted Knowledge contract.

This module constructs read-only, item-scoped TriageHandoff contributions. It
does not approve category proposals, set urgency, authorize actions, or persist
or dispatch tickets. The caller supplies a live-source preflight and the
Knowledge receiver; contract acceptance remains a separate Shared review gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from typing import Callable, Literal

from cdit_support_mao.agents.coordinator.handoff import HandoffError
from cdit_support_mao.agents.triage.runtime import TriageRuntimeResult
from cdit_support_mao.contracts.common import (
    AgentStatus,
    CheckpointOutcome,
    Claim,
    ClaimLabel,
    ConfidenceBand,
    RunContext,
    SourceKind,
    SourceRef,
    stable_id,
)
from cdit_support_mao.contracts.handoffs import LinkedItemRef, TriageHandoff, TriageItemScope, item_id_for


@dataclass(frozen=True, slots=True)
class ItemKnowledgeDispatch:
    """A dispatchable read-only handoff or an explicit human-review disposition."""

    item_index: int
    item_id: str
    status: Literal["ready_for_knowledge", "auditor_review"]
    handoff: TriageHandoff | None
    reason: str | None


def build_item_knowledge_handoffs(
    result: TriageRuntimeResult,
    *,
    preflight: Callable[[], bool],
    now: datetime | None = None,
) -> tuple[ItemKnowledgeDispatch, ...]:
    """Create item-scoped A2 contributions after revalidating the source.

    Unknown urgency is intentionally allowed to Knowledge when category is an
    evidence-bound inference. Unknown category, ambiguous segmentation,
    dependencies, conflicts, or any failed upstream state remain with the human
    Auditor. A result never authorizes Troubleshooting, writes, or notices.
    """
    if not isinstance(result, TriageRuntimeResult):
        raise HandoffError("invalid_triage_runtime_result")
    if preflight() is not True:
        raise HandoffError("triage_source_stale_before_knowledge_handoff")
    current_time = now or datetime.now(timezone.utc)
    context: RunContext = result.triage_input.context
    parent_text = result.triage_input.reported_message
    candidate = result.candidate
    if (candidate.context != context or candidate.source_text != parent_text
            or candidate.source.source_id != context.case_id
            or candidate.source.version != str(context.case_version)):
        raise HandoffError("triage_candidate_parent_mismatch")

    parent_digest = hashlib.sha256(parent_text.encode("utf-8")).hexdigest()
    attention = result.attention_signal
    if attention is not None and attention.context != context:
        raise HandoffError("triage_attention_context_mismatch")
    parent_flagged = bool(attention and attention.matches)
    output: list[ItemKnowledgeDispatch] = []

    for item in candidate.items:
        identity = LinkedItemRef(
            item_id=item_id_for(
                context, parent_digest, item.item_index, item.source_start, item.source_end
            ),
            item_index=item.item_index,
            item_count=len(candidate.items),
            parent_source=candidate.source,
            parent_digest=parent_digest,
            source_start=item.source_start,
            source_end=item.source_end,
        )
        reason = _ineligible_reason(result, item)
        if reason is not None:
            output.append(ItemKnowledgeDispatch(
                item_index=item.item_index, item_id=identity.item_id,
                status="auditor_review", handoff=None, reason=reason,
            ))
            continue

        assert item.category is not None and item.category_basis is not None
        category_evidence = item.category_evidence_quote
        if not category_evidence:
            output.append(ItemKnowledgeDispatch(
                item_index=item.item_index, item_id=identity.item_id,
                status="auditor_review", handoff=None, reason="category_evidence_missing",
            ))
            continue
        relative_start = item.reported_text.find(category_evidence)
        if relative_start < 0:
            output.append(ItemKnowledgeDispatch(
                item_index=item.item_index, item_id=identity.item_id,
                status="auditor_review", handoff=None, reason="category_evidence_not_in_item",
            ))
            continue

        category_span = (
            item.source_start + relative_start,
            item.source_start + relative_start + len(category_evidence),
        )
        item_attention = None
        if attention is not None:
            for match in attention.matches:
                if match.start_codepoint < item.source_end and item.source_start < match.end_codepoint:
                    item_attention = SourceRef(
                        kind=SourceKind.CASE_FIELD,
                        source_id=context.case_id,
                        version=str(context.case_version),
                        locator=f"attention-flag:{match.start_codepoint}-{match.end_codepoint}",
                    )
                    break

        # Keep the exact sources validated by Triage. In particular, S-1.1
        # recognizes the content-addressed category taxonomy source; replacing
        # it with a policy-version stand-in loses provenance and used to produce
        # an impossible "unavailable" placeholder (F-9).
        category_sources = tuple(item.category_sources)
        attention_check = (
            "check_not_run"
            if attention is None
            else "potential_attention"
            if item_attention is not None
            else "no_configured_match"
        )
        scope = TriageItemScope(
            identity=identity,
            segmentation=item.segmentation,
            depends_on=item.depends_on,
            item_status="proposal_for_human_review",
            category_label="inference",
            category_basis=item.category_basis,
            category_sources=category_sources,
            category_evidence_span=category_span,
            auditor_review="pending",
            attention_ref=item_attention,
            parent_attention_flagged=parent_flagged,
            attention_check=attention_check,
        )
        claim = Claim(
            statement=f"Proposed support category: {item.category}",
            label=ClaimLabel.INFERENCE,
            sources=category_sources,
            basis=item.category_basis,
            confidence=ConfidenceBand.LOW,
        )
        triage_handoff = TriageHandoff(
            contribution_id=stable_id("TRI", context.run_id, identity.item_id, "A2"),
            agent="triage-agent",
            agent_version=(
                f"0.2.0+{result.semantic_result.model}"
                if result.semantic_result is not None else "0.2.0"
            ),
            context=context,
            created_at=current_time,
            status=AgentStatus.COMPLETED,
            checkpoint=CheckpointOutcome(checkpoint="A2", passed=True),
            claims=(claim,),
            confidence=ConfidenceBand.LOW,
            confidence_rationale=(
                "Category is an uncalibrated inference from the item's synthetic text; "
                "human review is required."
            ),
            unknowns=("Urgency and destination remain unknown pending human Auditor review.",),
            case_summary=item.reported_text,
            product_area=None,
            category=item.category,
            category_confidence=ConfidenceBand.LOW,
            urgency="unknown",
            case_facts=(),
            missing_facts=item.missing_facts,
            item_scope=scope,
        )
        if preflight() is not True:
            raise HandoffError("triage_source_stale_during_knowledge_handoff")
        output.append(ItemKnowledgeDispatch(
            item_index=item.item_index, item_id=identity.item_id,
            status="ready_for_knowledge", handoff=triage_handoff, reason=None,
        ))

    return tuple(output)


def _ineligible_reason(result: TriageRuntimeResult, item: object) -> str | None:
    if item.segmentation != "candidate_boundary":
        return "ambiguous_segmentation"
    if result.status != "proposal_for_human_review":
        return "triage_requires_human_review"
    if item.category_label != "inference" or not item.category:
        return "unknown_category"
    if item.status != "proposal_for_human_review":
        return "item_requires_human_review"
    if item.depends_on:
        return "item_dependency_unresolved"
    if item.conflicts_present:
        return "item_conflict_unresolved"
    if item.human_review_required is not True or item.downstream_allowed is not False:
        return "triage_authority_invariant_failed"
    return None
