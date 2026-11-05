"""Shawn's Lane validation harness — NOT the coordinator.

Runs the Knowledge -> Troubleshooting -> Documentation agents on synthetic case
files so the lane can be validated before Manny's Lane delivers the
Coordinator, Triage, and Escalation agents. Triage and Escalation outputs are
built from clearly labelled *stand-ins* declared in each case file; they are
fixtures, not implementations of Manny-owned behaviour. The harness also plays
the coordinator's acknowledgment role only so the agents' input gates can be
exercised.

Each run also records the wall-clock duration of every lane agent call (PRD-v3
§2d per-run latency). Durations depend on the machine, so they stay out of
``LaneRun.as_json()`` and out of committed evidence; the CLIs print a summary.

Usage (from the repository root)::

    python -m cdit_support_mao.lane_harness synthetic_data/cases
    python -m cdit_support_mao.lane_harness synthetic_data/cases/case-01-golden-report-export.json --json
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Literal

from pydantic import ValidationError

from cdit_support_mao.agents.documentation import DocumentationAgent
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

STAND_IN_VERSION = "fixture-0.1"
LANE_AGENTS = ("knowledge", "troubleshooting", "documentation")


class FactStandIn(StrictModel):
    field: str
    value: str
    verified: bool


class TriageStandIn(StrictModel):
    status: AgentStatus = AgentStatus.COMPLETED
    case_summary: str
    product_area: str | None = None
    category: str | None = None
    category_confidence: ConfidenceBand
    urgency: Literal["low", "medium", "high", "unknown"]
    case_facts: tuple[FactStandIn, ...] = ()
    missing_facts: tuple[str, ...] = ()


class EscalationStandIn(StrictModel):
    status: AgentStatus = AgentStatus.COMPLETED
    must_escalate: bool | None
    triggers: tuple[str, ...] = ()
    recommendation: Literal["escalate_l2", "escalate_support_lead", "human_review", "no_escalation_proposed"]
    reason: str


class ActionStandIn(StrictModel):
    action: str
    performed_by_role: Literal["tier1_specialist", "customer", "l2_specialist", "support_lead"]
    outcome: str
    verified: bool


class ExpectedOutcome(StrictModel):
    """Expected results, written before the case is run (PRD eval-card practice)."""

    knowledge_status: AgentStatus | None = None
    knowledge_reasons: tuple[ReasonCode, ...] = ()
    top_doc_id: str | None = None
    troubleshooting_status: AgentStatus
    troubleshooting_reasons: tuple[ReasonCode, ...] = ()
    min_steps: int = 0
    max_steps: int | None = None
    escalation_signals: tuple[str, ...] = ()
    documentation_status: AgentStatus
    documentation_reasons: tuple[ReasonCode, ...] = ()
    must_not_appear: tuple[str, ...] = ()


class LaneCase(StrictModel):
    case_file_version: Literal["0.1"]
    case_id: str
    title: str
    scenario_ref: str
    as_of: date
    case_version: int = 1
    policy_version: str = "SYN-SUPPORT-POLICY-0.1"
    triage: TriageStandIn
    escalation: EscalationStandIn
    recorded_actions: tuple[ActionStandIn, ...] = ()
    # Optional only for generated calibration cases; lane case files must declare it.
    expected: ExpectedOutcome | None = None


@dataclass(frozen=True)
class LaneRun:
    case: LaneCase
    context: RunContext
    triage: TriageHandoff
    escalation: EscalationHandoff
    knowledge: KnowledgeResult
    troubleshooting: TroubleshootingResult
    documentation: DocumentationResult
    # Wall-clock milliseconds per lane agent call; machine-dependent, so not in as_json().
    durations_ms: Mapping[str, float] = field(default_factory=dict, compare=False)

    def as_json(self) -> dict:
        return {
            "case_id": self.case.case_id,
            "title": self.case.title,
            "stand_ins_are_fixtures": True,
            "triage_stand_in": self.triage.model_dump(mode="json"),
            "escalation_stand_in": self.escalation.model_dump(mode="json"),
            "knowledge": self.knowledge.model_dump(mode="json"),
            "troubleshooting": self.troubleshooting.model_dump(mode="json"),
            "documentation": self.documentation.model_dump(mode="json"),
        }


def load_case(path: Path) -> LaneCase:
    try:
        return LaneCase.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, ValidationError) as error:
        raise ValueError(f"invalid lane case file {path}: {error}") from error


def case_files(target: Path) -> list[Path]:
    return sorted(target.glob("*.json")) if target.is_dir() else [target]


def _stand_in_checkpoint(checkpoint: str, status: AgentStatus) -> CheckpointOutcome:
    passed = status is AgentStatus.COMPLETED
    return CheckpointOutcome(
        checkpoint=checkpoint,
        passed=passed,
        reason_codes=() if passed else (ReasonCode.UPSTREAM_BLOCKED,),
    )


class LaneHarness:
    def __init__(self, corpus: KnowledgeCorpus, policy: TroubleshootingPolicy) -> None:
        self.knowledge_agent = KnowledgeAgent(corpus)
        self.troubleshooting_agent = TroubleshootingAgent(policy)
        self.documentation_agent = DocumentationAgent()

    def run(self, case: LaneCase, *, now: datetime) -> LaneRun:
        context = RunContext(
            run_id=f"RUN-{case.case_id}-{case.case_version}",
            case_id=case.case_id,
            case_version=case.case_version,
            policy_version=case.policy_version,
        )
        stand_in = case.triage
        triage = TriageHandoff(
            contribution_id=stable_id("TRI", context.run_id, STAND_IN_VERSION),
            agent="triage-stand-in (fixture; not Manny's Triage agent)",
            agent_version=STAND_IN_VERSION,
            context=context,
            created_at=now,
            status=stand_in.status,
            checkpoint=_stand_in_checkpoint("A2", stand_in.status),
            confidence=stand_in.category_confidence,
            confidence_rationale="Lane-validation stand-in value from the synthetic case file.",
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
        durations: dict[str, float] = {}

        start = time.perf_counter()
        knowledge = self.knowledge_agent.run(
            context, triage, acknowledged=acknowledged, as_of=case.as_of, now=now
        )
        durations["knowledge"] = _elapsed_ms(start)
        acknowledged.add(knowledge.contribution_id)

        start = time.perf_counter()
        troubleshooting = self.troubleshooting_agent.run(
            context, triage, knowledge, acknowledged=acknowledged, now=now
        )
        durations["troubleshooting"] = _elapsed_ms(start)
        acknowledged.add(troubleshooting.contribution_id)

        esc = case.escalation
        escalation = EscalationHandoff(
            contribution_id=stable_id("ESC", context.run_id, STAND_IN_VERSION),
            agent="escalation-stand-in (fixture; not Manny's Escalation agent)",
            agent_version=STAND_IN_VERSION,
            context=context,
            input_refs=(triage.as_input_ref(),),
            created_at=now,
            status=esc.status,
            checkpoint=_stand_in_checkpoint("A5", esc.status),
            confidence=ConfidenceBand.MEDIUM,
            confidence_rationale="Lane-validation stand-in value from the synthetic case file.",
            must_escalate=esc.must_escalate,
            triggers=esc.triggers,
            recommendation=esc.recommendation,
            reason=esc.reason,
        )
        acknowledged.add(escalation.contribution_id)

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
        start = time.perf_counter()
        documentation = self.documentation_agent.run(
            context,
            triage=triage,
            knowledge=knowledge,
            troubleshooting=troubleshooting,
            escalation=escalation,
            recorded_actions=actions,
            acknowledged=acknowledged,
            now=now,
        )
        durations["documentation"] = _elapsed_ms(start)
        return LaneRun(
            case, context, triage, escalation, knowledge, troubleshooting, documentation, durations
        )


def _elapsed_ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000.0


def _stats(values: Sequence[float]) -> dict[str, float]:
    ordered = sorted(values)
    nearest_rank = max(1, math.ceil(0.95 * len(ordered)))
    return {
        "cases": len(ordered),
        "median_ms": round(statistics.median(ordered), 3),
        "p95_ms": round(ordered[nearest_rank - 1], 3),
        "max_ms": round(ordered[-1], 3),
    }


def duration_summary(runs: Iterable[LaneRun]) -> dict[str, dict[str, float]]:
    """Median, 95th percentile (nearest rank), and maximum milliseconds per lane agent and in total.

    Runs without recorded durations are skipped. "lane_total" is the sum of the three
    lane agents for one case; stand-in construction is not included.
    """
    samples: dict[str, list[float]] = {name: [] for name in (*LANE_AGENTS, "lane_total")}
    for run in runs:
        if not all(name in run.durations_ms for name in LANE_AGENTS):
            continue
        for name in LANE_AGENTS:
            samples[name].append(run.durations_ms[name])
        samples["lane_total"].append(sum(run.durations_ms[name] for name in LANE_AGENTS))
    return {name: _stats(values) for name, values in samples.items() if values}


def format_durations(summary: Mapping[str, Mapping[str, float]]) -> str:
    if not summary:
        return "Per-agent duration: no timed runs."
    lines = ["Per-agent duration in ms (median / p95 / max; machine-dependent; 0 model calls, $0 provider cost):"]
    for name, stats in summary.items():
        lines.append(
            f"  {name:<16} {stats['median_ms']:8.3f} / {stats['p95_ms']:8.3f} / {stats['max_ms']:8.3f}"
            f"  ({stats['cases']} cases)"
        )
    return "\n".join(lines)


def check_expectations(run: LaneRun) -> list[str]:
    """Compare a run with the case file's expected outcome; return mismatch messages."""
    expected = run.case.expected
    if expected is None:
        return ["case declares no expected outcome"]
    problems: list[str] = []

    def status(name: str, actual: AgentStatus, wanted: AgentStatus | None) -> None:
        if wanted is not None and actual is not wanted:
            problems.append(f"{name} status {actual} != expected {wanted}")

    def reasons(name: str, actual: Sequence[ReasonCode], wanted: Sequence[ReasonCode]) -> None:
        missing = [code for code in wanted if code not in actual]
        if missing:
            problems.append(f"{name} missing reason codes {missing}; got {list(actual)}")

    status("knowledge", run.knowledge.status, expected.knowledge_status)
    reasons("knowledge", run.knowledge.checkpoint.reason_codes, expected.knowledge_reasons)
    if expected.top_doc_id is not None:
        top = run.knowledge.passages[0].doc_id if run.knowledge.passages else None
        if top != expected.top_doc_id:
            problems.append(f"top source {top} != expected {expected.top_doc_id}")

    status("troubleshooting", run.troubleshooting.status, expected.troubleshooting_status)
    reasons("troubleshooting", run.troubleshooting.checkpoint.reason_codes, expected.troubleshooting_reasons)
    step_count = len(run.troubleshooting.steps)
    if step_count < expected.min_steps or (expected.max_steps is not None and step_count > expected.max_steps):
        problems.append(
            f"step count {step_count} outside [{expected.min_steps}, {expected.max_steps}]"
        )
    signals = {signal.signal for signal in run.troubleshooting.escalation_signals}
    missing_signals = [s for s in expected.escalation_signals if s not in signals]
    if missing_signals:
        problems.append(f"missing escalation signals {missing_signals}; got {sorted(signals)}")

    status("documentation", run.documentation.status, expected.documentation_status)
    reasons("documentation", run.documentation.checkpoint.reason_codes, expected.documentation_reasons)

    if expected.must_not_appear:
        produced = json.dumps(
            [
                run.knowledge.model_dump(mode="json"),
                run.troubleshooting.model_dump(mode="json"),
                run.documentation.model_dump(mode="json"),
            ]
        )
        for text in expected.must_not_appear:
            if text.lower() in produced.lower():
                problems.append(f"forbidden text appeared in agent output: {text!r}")
    return problems


def default_now() -> datetime:
    return datetime.now(UTC)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Shawn's Lane agents on synthetic case files.")
    parser.add_argument("target", type=Path, help="Case file or directory of case files")
    parser.add_argument("--knowledge-dir", type=Path, default=None)
    parser.add_argument("--policy", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Print full agent outputs as JSON")
    args = parser.parse_args(argv)

    harness = LaneHarness(load_corpus(args.knowledge_dir), load_policy(args.policy))
    now = default_now()
    failures = 0
    outputs = []
    runs: list[LaneRun] = []
    for path in case_files(args.target):
        run = harness.run(load_case(path), now=now)
        runs.append(run)
        problems = check_expectations(run)
        failures += bool(problems)
        if args.json:
            outputs.append({**run.as_json(), "expectation_problems": problems})
            continue
        verdict = "PASS" if not problems else "FAIL"
        print(
            f"{verdict}  {run.case.case_id}  K={run.knowledge.status:<9} "
            f"T={run.troubleshooting.status:<9} D={run.documentation.status:<9} {run.case.title}"
        )
        for problem in problems:
            print(f"      - {problem}")
    if args.json:
        print(json.dumps(outputs if len(outputs) != 1 else outputs[0], indent=2))
    else:
        print(f"\n{len(case_files(args.target)) - failures} passed, {failures} failed")
        print(format_durations(duration_summary(runs)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
