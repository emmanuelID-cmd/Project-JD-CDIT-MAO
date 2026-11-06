"""Input-gate helpers shared by Shawn's Lane agents.

These checks implement each receiving agent's own validation (lane gate-work):
an input is usable only when it belongs to the current run context, has been
acknowledged by the coordinator, and was not itself blocked. They do not
change or validate the internal behaviour of Manny-owned agents.
"""

from __future__ import annotations

from collections.abc import Iterable, Set
from datetime import UTC, datetime

from cdit_support_mao.contracts.common import (
    AgentContribution,
    AgentStatus,
    ReasonCode,
    RunContext,
)
from cdit_support_mao.contracts.handoffs import KnowledgeResult, TriageHandoff


def utc_now(now: datetime | None = None) -> datetime:
    """Timestamp source for contributions (UTC, injectable for tests; see D-10)."""
    if now is None:
        return datetime.now(UTC)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    return now


def unique(reasons: Iterable[ReasonCode]) -> tuple[ReasonCode, ...]:
    return tuple(dict.fromkeys(reasons))


def upstream_reasons(
    context: RunContext,
    upstream: Iterable[AgentContribution],
    acknowledged: Set[str],
    *,
    must_be_completed: Iterable[AgentContribution] = (),
) -> tuple[ReasonCode, ...]:
    """Reasons an agent must refuse its inputs; empty when inputs are usable.

    Every upstream contribution must match the current run context (stale case,
    policy, or run versions are rejected) and be acknowledged. A BLOCKED input is
    never usable; inputs listed in ``must_be_completed`` must also have COMPLETED.
    """
    reasons: list[ReasonCode] = []
    for contribution in upstream:
        if contribution.context != context:
            reasons.append(ReasonCode.CONTEXT_MISMATCH)
        if contribution.contribution_id not in acknowledged:
            reasons.append(ReasonCode.UPSTREAM_NOT_ACKNOWLEDGED)
        if contribution.status is AgentStatus.BLOCKED:
            reasons.append(ReasonCode.UPSTREAM_BLOCKED)
    for contribution in must_be_completed:
        if contribution.status is not AgentStatus.COMPLETED:
            reasons.append(ReasonCode.UPSTREAM_BLOCKED)
    return unique(reasons)


def consumed(contribution: AgentContribution, *upstream: AgentContribution) -> bool:
    """True when ``contribution`` consumed exactly these upstream contributions.

    Each upstream must appear in ``input_refs`` by ID *and* by content digest
    (proposed S-2): a ref without a digest, or with a digest of different
    content under the same ID, does not count as consumed.
    """
    refs = {ref.contribution_id: ref for ref in contribution.input_refs}
    for item in upstream:
        ref = refs.get(item.contribution_id)
        if ref is None or ref.content_digest is None or ref.content_digest != item.content_digest():
            return False
    return True


def item_scope_reasons(context: RunContext, triage: TriageHandoff) -> tuple[ReasonCode, ...]:
    """Knowledge's second-line eligibility check for one linked Triage item (K-1).

    Empty for a single-case handoff (no ``item_scope``) or an eligible item. The
    Coordinator connector checks first; this gate re-checks so Knowledge never
    retrieves for an item outside the agreed rule (Manny, Q-A, 2026-11-05): a
    ``candidate_boundary`` item, with no dependencies, whose category is an
    inference and whose status is a proposal for human review. Urgency and the
    Auditor review state are deliberately not checked here: retrieval is
    read-only and may run while the Auditor reviews urgency.
    """
    scope = triage.item_scope
    if scope is None:
        return ()
    ident = scope.identity
    reasons: list[ReasonCode] = []
    if not ident.matches_context(context):
        reasons.append(ReasonCode.CONTEXT_MISMATCH)
    if (
        ident.item_id != ident.expected_item_id(context)
        or ident.source_end - ident.source_start != len(triage.case_summary)
        or not 1 <= ident.item_index <= ident.item_count
    ):
        reasons.append(ReasonCode.UPSTREAM_CHAIN_MISMATCH)
    if (
        scope.segmentation != "candidate_boundary"
        or scope.depends_on
        or scope.item_status != "proposal_for_human_review"
        or scope.category_label != "inference"
    ):
        reasons.append(ReasonCode.UPSTREAM_BLOCKED)
    return unique(reasons)


def item_chain_reasons(triage: TriageHandoff, knowledge: KnowledgeResult) -> tuple[ReasonCode, ...]:
    """Same-item join check for stages after Knowledge (K-4).

    The Knowledge echo must name exactly the Triage item (or both must be
    single-case); otherwise results of different items could be mixed.
    """
    expected = triage.item_scope.identity if triage.item_scope is not None else None
    if knowledge.item_scope_ref != expected:
        return (ReasonCode.UPSTREAM_CHAIN_MISMATCH,)
    return ()


def awaiting_auditor(triage: TriageHandoff) -> bool:
    """True while a linked item still waits for the Auditor's urgency band and route.

    Manny (Q-A, 2026-11-05): hold processing after Knowledge until the Auditor
    determines the band and route. Single-case handoffs are never held here.
    """
    return triage.item_scope is not None and triage.item_scope.auditor_review != "band_and_route_determined"
