"""Synthetic connected A0–A3 harness for Manny's real Triage-to-Knowledge path.

This connects the existing Coordinator/A0–A2 runtime to Shawn's existing
Knowledge receiver through the merged item-scoped contract. It stops at A3:
Troubleshooting and Documentation wait for the human Auditor's band-and-route
decision. This is not a production app endpoint or a ticket action path.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Literal

from cdit_support_mao.agents.knowledge.agent import KnowledgeAgent
from cdit_support_mao.agents.coordinator.handoff import HandoffError
from cdit_support_mao.agents.triage.anthropic_adapter import AnthropicClient
from cdit_support_mao.agents.triage.knowledge_connector import (
    ItemKnowledgeDispatch,
    build_item_knowledge_handoffs,
)
from cdit_support_mao.agents.triage.runtime_harness import MannyA0A2Harness, MannyA0A2Run
from cdit_support_mao.contracts.handoffs import KnowledgeResult


@dataclass(frozen=True, slots=True)
class ConnectedItemResult:
    dispatch: ItemKnowledgeDispatch
    knowledge: KnowledgeResult | None
    state: Literal[
        "auditor_review",
        "knowledge_completed",
        "knowledge_abstained_or_blocked",
        "discarded_stale_result",
    ]


@dataclass(frozen=True, slots=True)
class MannyConnectedRun:
    upstream: MannyA0A2Run
    items: tuple[ConnectedItemResult, ...]
    status: Literal["awaiting_auditor_review", "stopped_for_human_review", "source_stale"]
    human_review_required: Literal[True] = True
    parent_complete: Literal[False] = False
    ticket_writes: Literal[0] = 0
    external_dispatches: Literal[0] = 0
    customer_notifications: Literal[0] = 0


class MannyConnectedWorkflowHarness:
    """Run synthetic Coordinator→Triage→Knowledge, preserving Auditor gates."""

    def __init__(
        self,
        triage_harness: MannyA0A2Harness,
        knowledge_agent: KnowledgeAgent,
        *,
        as_of: date,
    ) -> None:
        if not isinstance(triage_harness, MannyA0A2Harness):
            raise TypeError("Manny A0-A2 harness required")
        if not isinstance(knowledge_agent, KnowledgeAgent):
            raise TypeError("KnowledgeAgent receiver required")
        if not isinstance(as_of, date):
            raise TypeError("as_of date required")
        self._triage_harness = triage_harness
        self._knowledge_agent = knowledge_agent
        self._as_of = as_of

    def run(
        self,
        request: object,
        *,
        session_token: object,
        client: AnthropicClient | None = None,
        billable_call_authorized: bool = False,
        now: datetime | None = None,
    ) -> MannyConnectedRun:
        current_time = now or datetime.now(timezone.utc)
        upstream = self._triage_harness.run(
            request,
            session_token=session_token,
            client=client,
            billable_call_authorized=billable_call_authorized,
            now=current_time,
        )
        if upstream.triage is None or upstream.intake.context is None:
            return MannyConnectedRun(
                upstream=upstream,
                items=(),
                status="stopped_for_human_review",
            )
        if not self._triage_harness.source_is_current(upstream, now=current_time):
            return MannyConnectedRun(upstream=upstream, items=(), status="source_stale")

        try:
            dispatches = build_item_knowledge_handoffs(
                upstream.triage,
                preflight=lambda: self._triage_harness.source_is_current(upstream, now=current_time),
                now=current_time,
            )
        except HandoffError:
            return MannyConnectedRun(upstream=upstream, items=(), status="source_stale")
        results: list[ConnectedItemResult] = []
        for dispatch in dispatches:
            if dispatch.handoff is None:
                results.append(ConnectedItemResult(
                    dispatch=dispatch, knowledge=None, state="auditor_review"
                ))
                continue
            if not self._triage_harness.source_is_current(upstream, now=current_time):
                results.append(ConnectedItemResult(
                    dispatch=dispatch, knowledge=None, state="discarded_stale_result"
                ))
                continue
            knowledge = self._knowledge_agent.run(
                upstream.intake.context,
                dispatch.handoff,
                acknowledged=frozenset({dispatch.handoff.contribution_id}),
                as_of=self._as_of,
                now=current_time,
            )
            if not self._triage_harness.source_is_current(upstream, now=current_time):
                # Do not expose downstream output if the source changed mid-stage.
                results.append(ConnectedItemResult(
                    dispatch=dispatch, knowledge=None, state="discarded_stale_result"
                ))
                continue
            state = (
                "knowledge_completed"
                if knowledge.status.value == "completed"
                else "knowledge_abstained_or_blocked"
            )
            results.append(ConnectedItemResult(dispatch, knowledge, state))

        overall = (
            "awaiting_auditor_review"
            if any(item.state == "knowledge_completed" for item in results)
            or any(item.state == "auditor_review" for item in results)
            else "stopped_for_human_review"
        )
        return MannyConnectedRun(upstream=upstream, items=tuple(results), status=overall)
