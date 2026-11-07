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
from typing import TYPE_CHECKING, Literal

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
