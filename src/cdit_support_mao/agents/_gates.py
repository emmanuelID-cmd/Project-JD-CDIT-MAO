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
    """True when ``contribution`` records that it consumed every given upstream id."""
    refs = {ref.contribution_id for ref in contribution.input_refs}
    return all(item.contribution_id in refs for item in upstream)
