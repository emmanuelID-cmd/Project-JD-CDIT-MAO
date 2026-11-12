"""Downstream fixture harness using a stand-in TriageHandoff (A2–A6).

This synthetic test harness runs Knowledge, Troubleshooting, Escalation, and
Documentation from a fixture-created case-level TriageHandoff. It does not run
the Coordinator or semantic Triage and does not establish a full A0–A6 run.
No external writes, notifications, or ticket actions are available here.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, date, datetime
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Literal, Sequence

from cdit_support_mao.agents.documentation import DocumentationAgent
from cdit_support_mao.agents.escalation import EscalationAgent
from cdit_support_mao.agents.knowledge import KnowledgeAgent, KnowledgeCorpus, load_corpus
from cdit_support_mao.agents.troubleshooting import (
    TroubleshootingAgent,
    TroubleshootingPolicy,
    load_policy,
)
from cdit_support_mao.contracts.common import (
    AgentStatus,
    CheckpointOutcome,
    ConfidenceBand,
    ReasonCode,
    RunContext,
    SourceKind,
    SourceRef,
    StrictModel,
    stable_id,
)
from cdit_support_mao.contracts.handoffs import (
    CaseFact,
    DocumentationResult,
    EscalationHandoff,
    KnowledgeResult,
    RecordedAction,
    TriageHandoff,
    TriageItemScope,
    TroubleshootingResult,
)
from cdit_support_mao.lane_harness import LaneCase, case_files, load_case
from cdit_support_mao.agents.triage.anthropic_adapter import AnthropicClient

if TYPE_CHECKING:
    from cdit_support_mao.agents.triage.runtime_harness import MannyA0A2Harness
    from cdit_support_mao.manny_connected_harness import MannyConnectedRun

STAND_IN_VERSION = "fixture-0.1"


@dataclass(frozen=True)
class CombinedRun:
    case: LaneCase
    context: RunContext
    triage: TriageHandoff
    knowledge: KnowledgeResult
    troubleshooting: TroubleshootingResult
    escalation: EscalationHandoff
    documentation: DocumentationResult

    def as_json(self) -> dict:
        return {
            "case_id": self.case.case_id,
            "title": self.case.title,
            "triage": self.triage.model_dump(mode="json"),
            "knowledge": self.knowledge.model_dump(mode="json"),
            "troubleshooting": self.troubleshooting.model_dump(mode="json"),
            "escalation": self.escalation.model_dump(mode="json"),
            "documentation": self.documentation.model_dump(mode="json"),
        }


@dataclass(frozen=True)
class AuditorDispositionFixture:
    """Synthetic human decision input for Shared harness resume tests only.

    This is not a runtime agent, persisted audit record, or product contract.
    The caller supplies an explicit human reviewer ID and urgency band after
    the connected run has stopped at the Auditor boundary.
    """

    item_id: str
    reviewer_id: str
    urgency: Literal["low", "medium", "high"]
    decided_at: datetime

    def __post_init__(self) -> None:
        if not re.fullmatch(r"SYN-AUDITOR-[A-Z0-9]{3,8}", self.reviewer_id):
            raise ValueError("auditor_fixture_requires_synthetic_reviewer_id")
        if self.decided_at.tzinfo is None or self.decided_at.utcoffset() is None:
            raise ValueError("auditor_fixture_timestamp_must_be_timezone_aware")


@dataclass(frozen=True)
class AuditorDispositionEvent:
    """Transient, non-persisted harness event describing a human fixture input."""

    run_id: str
    item_id: str
    actor_id: str
    decision: Literal["band_and_route_determined"]
    category: str
    urgency: Literal["low", "medium", "high"]
    source_digest: str
    created_at: datetime


@dataclass(frozen=True)
class ConnectedItemRun:
    """Result of one item through the connected A0–A6 harness path."""

    item_id: str
    initial_state: str
    state: Literal[
        "awaiting_auditor_review",
        "knowledge_abstained_or_blocked",
        "troubleshooting_abstained_or_blocked",
        "escalation_abstained_or_blocked",
        "documentation_abstained_or_blocked",
        "ready_for_human_review",
        "discarded_stale_result",
    ]
    auditor_event: AuditorDispositionEvent | None = None
    triage: TriageHandoff | None = None
    knowledge: KnowledgeResult | None = None
    troubleshooting: TroubleshootingResult | None = None
    escalation: EscalationHandoff | None = None
    documentation: DocumentationResult | None = None


@dataclass(frozen=True)
class CombinedMannyConnectedRun:
    """Test-only A0–A6 result after supplied human Auditor fixtures.

    It never marks a business ticket complete and has no write/dispatch path.
    """

    context: RunContext
    items: tuple[ConnectedItemRun, ...]
    status: Literal[
        "awaiting_auditor_review",
        "stopped_for_human_review",
        "source_stale",
        "ready_for_human_review",
    ]
    human_review_required: Literal[True] = True
    parent_complete: Literal[False] = False
    ticket_writes: Literal[0] = 0
    external_dispatches: Literal[0] = 0
    customer_notifications: Literal[0] = 0


class CombinedWorkflowHarness:
    """Runs the downstream agents from an explicitly fixture-created A2 input."""

    def __init__(self, corpus: KnowledgeCorpus, policy: TroubleshootingPolicy) -> None:
        self.knowledge_agent = KnowledgeAgent(corpus)
        self.troubleshooting_agent = TroubleshootingAgent(policy)
        self.escalation_agent = EscalationAgent()
        self.documentation_agent = DocumentationAgent()

    def run(self, case: LaneCase, *, now: datetime | None = None) -> CombinedRun:
        run_now = now or datetime.now(UTC)
        context = RunContext(
            run_id=f"RUN-{case.case_id}-{case.case_version}",
            case_id=case.case_id,
            case_version=case.case_version,
            policy_version=case.policy_version,
        )

        # 1. Triage stage (A2)
        stand_in = case.triage
        passed_a2 = stand_in.status is AgentStatus.COMPLETED
        triage = TriageHandoff(
            contribution_id=stable_id("TRI", context.run_id, STAND_IN_VERSION),
            agent="triage-adapter",
            agent_version=STAND_IN_VERSION,
            context=context,
            created_at=run_now,
            status=stand_in.status,
            checkpoint=CheckpointOutcome(
                checkpoint="A2",
                passed=passed_a2,
                reason_codes=() if passed_a2 else (ReasonCode.UPSTREAM_BLOCKED,),
            ),
            confidence=stand_in.category_confidence,
            confidence_rationale="Synthetic triage classification.",
            case_summary=stand_in.case_summary,
            product_area=stand_in.product_area,
            category=stand_in.category,
            category_confidence=stand_in.category_confidence,
            urgency=stand_in.urgency,
            case_facts=tuple(
                CaseFact(
                    field=fact.field,
                    value=fact.value,
                    verified=fact.verified,
                    source=SourceRef(
                        kind=SourceKind.CASE_FIELD,
                        source_id=f"{case.case_id}.{fact.field}",
                        version=str(case.case_version),
                    ),
                )
                for fact in stand_in.case_facts
            ),
            missing_facts=stand_in.missing_facts,
        )
        acknowledged = {triage.contribution_id}

        # 2. Knowledge stage (A3)
        knowledge = self.knowledge_agent.run(
            context, triage, acknowledged=acknowledged, as_of=case.as_of, now=run_now
        )
        acknowledged.add(knowledge.contribution_id)

        # 3. Troubleshooting stage (A4)
        troubleshooting = self.troubleshooting_agent.run(
            context, triage, knowledge, acknowledged=acknowledged, now=run_now
        )
        acknowledged.add(troubleshooting.contribution_id)

        # 4. Escalation stage (A5) - executes actual EscalationAgent
        actions = tuple(
            RecordedAction(
                action=item.action,
                performed_by_role=item.performed_by_role,
                outcome=item.outcome,
                verified=item.verified,
                source=SourceRef(
                    kind=SourceKind.STAFF_ENTRY,
                    source_id=f"{case.case_id}.staff_entry.{index}",
                    version=str(case.case_version),
                ),
            )
            for index, item in enumerate(case.recorded_actions, start=1)
        )
        escalation = self.escalation_agent.run(
            context,
            triage=triage,
            knowledge=knowledge,
            troubleshooting=troubleshooting,
            acknowledged=acknowledged,
            actions=actions,
            now=run_now,
        )
        acknowledged.add(escalation.contribution_id)

        # 5. Documentation stage (A6)
        documentation = self.documentation_agent.run(
            context,
            triage=triage,
            knowledge=knowledge,
            troubleshooting=troubleshooting,
            escalation=escalation,
            recorded_actions=actions,
            acknowledged=acknowledged,
            now=run_now,
        )

        return CombinedRun(
            case=case,
            context=context,
            triage=triage,
            knowledge=knowledge,
            troubleshooting=troubleshooting,
            escalation=escalation,
            documentation=documentation,
        )

    def run_manny_connected(
        self,
        triage_harness: MannyA0A2Harness,
        request: object,
        *,
        session_token: object,
        as_of: date,
        client: AnthropicClient | None = None,
        billable_call_authorized: bool = False,
        now: datetime | None = None,
    ) -> MannyConnectedRun:
        """Run Manny's real synthetic A0–A3 path through this Knowledge receiver.

        The linked-item Triage handoff is used as the receiver input. Unknown
        urgency leaves the item awaiting the human Auditor; this method never
        enters Troubleshooting or Documentation until that decision exists.
        The fixture-based ``run`` path above remains available for regression.
        """
        from cdit_support_mao.manny_connected_harness import MannyConnectedWorkflowHarness

        connected = MannyConnectedWorkflowHarness(
            triage_harness, self.knowledge_agent, as_of=as_of
        )
        return connected.run(
            request,
            session_token=session_token,
            client=client,
            billable_call_authorized=billable_call_authorized,
            now=now,
        )

    def continue_after_auditor(
        self,
        connected_run: MannyConnectedRun,
        triage_harness: MannyA0A2Harness,
        dispositions: Sequence[AuditorDispositionFixture],
        *,
        as_of: date,
        now: datetime | None = None,
    ) -> CombinedMannyConnectedRun:
        """Resume eligible connected items with explicit synthetic human decisions.

        A disposition becomes a new, validated TriageHandoff for the same item.
        Knowledge is rerun against that handoff before A4–A6. This seam is only
        for synthetic harness evaluation; it creates no Auditor runtime agent,
        persisted A7 event, or product UI.
        """
        from cdit_support_mao.agents.triage.runtime_harness import MannyA0A2Harness
        from cdit_support_mao.manny_connected_harness import MannyConnectedRun

        if not isinstance(connected_run, MannyConnectedRun):
            raise TypeError("MannyConnectedRun required")
        if not isinstance(triage_harness, MannyA0A2Harness):
            raise TypeError("MannyA0A2Harness required for source freshness checks")
        if not isinstance(as_of, date):
            raise TypeError("as_of date required")
        context = connected_run.upstream.intake.context
        if context is None:
            raise ValueError("connected_run_has_no_validated_context")

        current_time = now or datetime.now(UTC)
        decisions: dict[str, AuditorDispositionFixture] = {}
        for decision in dispositions:
            if not isinstance(decision, AuditorDispositionFixture):
                raise TypeError("synthetic AuditorDispositionFixture required")
            if decision.item_id in decisions:
                raise ValueError("duplicate_auditor_disposition_for_item")
            decisions[decision.item_id] = decision

        connected_items = {item.dispatch.item_id: item for item in connected_run.items}
        unknown_items = set(decisions) - set(connected_items)
        if unknown_items:
            raise ValueError("auditor_disposition_item_not_in_connected_run")

        def stale_result(item_id: str, initial_state: str, event: AuditorDispositionEvent | None = None):
            return ConnectedItemRun(
                item_id=item_id,
                initial_state=initial_state,
                state="discarded_stale_result",
                auditor_event=event,
            )

        def make_audited_triage(
            handoff: TriageHandoff, decision: AuditorDispositionFixture
        ) -> tuple[TriageHandoff, AuditorDispositionEvent]:
            scope = handoff.item_scope
            if scope is None:
                raise ValueError("auditor_resume_requires_item_scoped_handoff")
            if scope.identity.item_id != decision.item_id:
                raise ValueError("auditor_decision_item_identity_mismatch")
            if scope.auditor_review != "pending" or handoff.urgency != "unknown":
                raise ValueError("auditor_resume_requires_pending_unknown_urgency")
            if scope.category_label != "inference" or not handoff.category:
                raise ValueError("auditor_resume_requires_existing_inferred_category")
            if handoff.status is not AgentStatus.COMPLETED:
                raise ValueError("auditor_resume_requires_completed_triage_proposal")

            event = AuditorDispositionEvent(
                run_id=context.run_id,
                item_id=decision.item_id,
                actor_id=decision.reviewer_id,
                decision="band_and_route_determined",
                category=handoff.category,
                urgency=decision.urgency,
                source_digest=handoff.content_digest(),
                created_at=decision.decided_at,
            )
            scope_payload = scope.model_dump(mode="python")
            scope_payload["auditor_review"] = "band_and_route_determined"
            resolved_scope = TriageItemScope.model_validate(scope_payload)

            payload = handoff.model_dump(mode="python")
            payload.update(
                {
                    "contribution_id": stable_id(
                        "TRI",
                        context.run_id,
                        handoff.contribution_id,
                        event.actor_id,
                        event.decision,
                        event.urgency,
                        event.created_at.isoformat(),
                    ),
                    "agent": "human-auditor-fixture",
                    "agent_version": "harness-0.1",
                    "input_refs": (handoff.as_input_ref(),),
                    "created_at": decision.decided_at,
                    "urgency": decision.urgency,
                    "item_scope": resolved_scope.model_dump(mode="python"),
                }
            )
            return TriageHandoff.model_validate(payload), event

        results: list[ConnectedItemRun] = []
        if connected_run.status == "source_stale" or not triage_harness.source_is_current(
            connected_run.upstream, now=current_time
        ):
            results = [
                stale_result(item.dispatch.item_id, item.state)
                for item in connected_run.items
            ]
            return CombinedMannyConnectedRun(context, tuple(results), "source_stale")

        for connected_item in connected_run.items:
            item_id = connected_item.dispatch.item_id
            original = connected_item.dispatch.handoff
            decision = decisions.get(item_id)

            if connected_item.state == "discarded_stale_result":
                results.append(stale_result(item_id, connected_item.state))
                continue
            if original is None:
                if decision is not None:
                    raise ValueError("auditor_fixture_cannot_release_item_without_eligible_triage_handoff")
                results.append(
                    ConnectedItemRun(
                        item_id=item_id,
                        initial_state=connected_item.state,
                        state="awaiting_auditor_review",
                    )
                )
                continue
            if decision is None:
                results.append(
                    ConnectedItemRun(
                        item_id=item_id,
                        initial_state=connected_item.state,
                        state="awaiting_auditor_review",
                        triage=original,
                        knowledge=connected_item.knowledge,
                    )
                )
                continue

            triage, event = make_audited_triage(original, decision)
            if not triage_harness.source_is_current(connected_run.upstream, now=current_time):
                results.append(stale_result(item_id, connected_item.state, event))
                continue

            knowledge = self.knowledge_agent.run(
                context,
                triage,
                acknowledged=frozenset({triage.contribution_id}),
                as_of=as_of,
                now=current_time,
            )
            if not triage_harness.source_is_current(connected_run.upstream, now=current_time):
                results.append(stale_result(item_id, connected_item.state, event))
                continue
            if knowledge.status is not AgentStatus.COMPLETED:
                results.append(
                    ConnectedItemRun(
                        item_id=item_id,
                        initial_state=connected_item.state,
                        state="knowledge_abstained_or_blocked",
                        auditor_event=event,
                        triage=triage,
                        knowledge=knowledge,
                    )
                )
                continue

            acknowledged = {triage.contribution_id, knowledge.contribution_id}
            troubleshooting = self.troubleshooting_agent.run(
                context, triage, knowledge, acknowledged=acknowledged, now=current_time
            )
            if not triage_harness.source_is_current(connected_run.upstream, now=current_time):
                results.append(stale_result(item_id, connected_item.state, event))
                continue
            if troubleshooting.status is not AgentStatus.COMPLETED:
                results.append(
                    ConnectedItemRun(
                        item_id=item_id,
                        initial_state=connected_item.state,
                        state="troubleshooting_abstained_or_blocked",
                        auditor_event=event,
                        triage=triage,
                        knowledge=knowledge,
                        troubleshooting=troubleshooting,
                    )
                )
                continue

            acknowledged.add(troubleshooting.contribution_id)
            escalation = self.escalation_agent.run(
                context,
                triage=triage,
                knowledge=knowledge,
                troubleshooting=troubleshooting,
                acknowledged=acknowledged,
                now=current_time,
            )
            if not triage_harness.source_is_current(connected_run.upstream, now=current_time):
                results.append(stale_result(item_id, connected_item.state, event))
                continue
            if escalation.status is not AgentStatus.COMPLETED:
                results.append(
                    ConnectedItemRun(
                        item_id=item_id,
                        initial_state=connected_item.state,
                        state="escalation_abstained_or_blocked",
                        auditor_event=event,
                        triage=triage,
                        knowledge=knowledge,
                        troubleshooting=troubleshooting,
                        escalation=escalation,
                    )
                )
                continue

            acknowledged.add(escalation.contribution_id)
            documentation = self.documentation_agent.run(
                context,
                triage=triage,
                knowledge=knowledge,
                troubleshooting=troubleshooting,
                escalation=escalation,
                recorded_actions=(),
                acknowledged=acknowledged,
                now=current_time,
            )
            if not triage_harness.source_is_current(connected_run.upstream, now=current_time):
                results.append(stale_result(item_id, connected_item.state, event))
                continue
            results.append(
                ConnectedItemRun(
                    item_id=item_id,
                    initial_state=connected_item.state,
                    state=(
                        "ready_for_human_review"
                        if documentation.status is AgentStatus.COMPLETED
                        else "documentation_abstained_or_blocked"
                    ),
                    auditor_event=event,
                    triage=triage,
                    knowledge=knowledge,
                    troubleshooting=troubleshooting,
                    escalation=escalation,
                    documentation=documentation,
                )
            )

        states = {item.state for item in results}
        if "discarded_stale_result" in states:
            status: Literal[
                "awaiting_auditor_review", "stopped_for_human_review", "source_stale", "ready_for_human_review"
            ] = "source_stale"
        elif "awaiting_auditor_review" in states:
            status = "awaiting_auditor_review"
        elif states == {"ready_for_human_review"}:
            status = "ready_for_human_review"
        else:
            status = "stopped_for_human_review"
        return CombinedMannyConnectedRun(context, tuple(results), status)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run downstream synthetic agents from a fixture TriageHandoff.")
    parser.add_argument("cases", type=Path, help="Case file or directory of synthetic cases")
    parser.add_argument("--json", action="store_true", help="Output full JSON run results")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[2]
    corpus = load_corpus(root / "synthetic_data" / "knowledge")
    policy = load_policy(root / "synthetic_data" / "policy" / "troubleshooting-policy_v0.1.1.json")
    harness = CombinedWorkflowHarness(corpus, policy)

    files = case_files(args.cases)
    runs = [harness.run(load_case(f)) for f in files]

    if args.json:
        print(json.dumps([r.as_json() for r in runs], indent=2))
    else:
        for r in runs:
            print(
                f"PASS  {r.case.case_id}  "
                f"K={r.knowledge.status.value} "
                f"T={r.troubleshooting.status.value} "
                f"E={r.escalation.recommendation} "
                f"D={r.documentation.status.value} "
                f"{r.case.title}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
