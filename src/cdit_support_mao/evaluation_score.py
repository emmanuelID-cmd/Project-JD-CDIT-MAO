"""Produce a non-billable, Knowledge-only diagnostic over the 100-case draft.

This runner scores observed Knowledge retrieval behavior against the case file's
current source expectations. It deliberately does not mark the label set
approved and does not claim end-to-end MAO accuracy.

Usage:
    python -m cdit_support_mao.evaluation_score
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any, Sequence

from cdit_support_mao.lane_eval_sources import (
    DEFAULT_CASES,
    DEFAULT_FIXTURES,
    DEFAULT_POLICY,
    SourceCheckRun,
    load_source_map,
    run_source_check,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "docs" / "lanes" / "manny" / "evaluation" / "EVAL-DRAFT-V1-DIAGNOSTIC.md"
DEFAULT_RESULTS = ROOT / "docs" / "lanes" / "manny" / "evaluation" / "eval-draft-v1-diagnostic.results.json"


def summarize(
    run: SourceCheckRun, dataset: dict[str, Any], source_map: Any
) -> dict[str, Any]:
    """Summarize item-level Knowledge outcomes without promoting draft labels."""
    verdicts = Counter(item.verdict for item in run.items)
    citations_by_id = source_map.by_citation()
    citation_cases = 0
    citation_hits = 0
    intended_abstention_cases = 0
    intended_abstention_exact = 0
    stale_cases = 0
    stale_cases_without_answer = 0
    for item in run.items:
        if item.route != "knowledge":
            continue
        entries = [citations_by_id[c] for c in item.expected if c in citations_by_id]
        expected_citations = {
            entry.citation for entry in entries if entry.expected_outcome == "cited"
        }
        expected_abstentions = [
            entry for entry in entries if entry.expected_outcome.startswith("abstain_")
        ]
        if expected_citations:
            citation_cases += 1
            if expected_citations.intersection(item.cited):
                citation_hits += 1
        if expected_abstentions:
            intended_abstention_cases += 1
            if item.verdict == "abstained_as_expected":
                intended_abstention_exact += 1
        if any(entry.expected_outcome == "abstain_stale" for entry in expected_abstentions):
            stale_cases += 1
            if item.knowledge_status != "completed":
                stale_cases_without_answer += 1

    cases = dataset.get("cases", [])
    return {
        "dataset_id": dataset.get("dataset_id"),
        "dataset_status": dataset.get("status", "unknown"),
        "approval": dataset.get("approval", {}),
        "diagnostic_only": True,
        "final_evaluation_score": None,
        "case_count": len(cases),
        "item_count": len(run.items),
        "evaluation_as_of": run.evaluation_as_of.isoformat(),
        "source_set_version": run.source_set_version,
        "knowledge_agent_version": run.knowledge_agent_version,
        "source_map_problem_count": len(run.source_map_problems),
        "source_map_problems": list(run.source_map_problems),
        "item_verdicts": dict(sorted(verdicts.items())),
        "knowledge_metrics": {
            "expected_citation_hits": citation_hits,
            "expected_citation_cases": citation_cases,
            "expected_citation_rate": (
                citation_hits / citation_cases if citation_cases else None
            ),
            "expected_citation_misses": citation_cases - citation_hits,
            "expected_abstention_cases": intended_abstention_cases,
            "expected_reason_abstentions": intended_abstention_exact,
            "stale_source_cases": stale_cases,
            "stale_source_cases_without_an_answer": stale_cases_without_answer,
            "wrong_source_or_missing_expected_abstention": verdicts["cited_other_source"],
            "auditor_held_items": verdicts["held_for_auditor"],
            "no_source_expected_and_abstained": verdicts["no_source_expected_abstained"],
        },
        "not_scored_gates": [
            "semantic triage category accuracy",
            "Auditor band and route accuracy",
            "Coordinator-to-Triage live handoff behavior",
            "Troubleshooting and Documentation accuracy over these 100 cases",
            "end-to-end injection, privacy, and authorization behavior",
            "fallback behavior outside the Knowledge source check",
            "latency, model cost, confidence calibration, and reviewer seeded-error rate",
        ],
        "case_results": [
            {
                "case_id": item.case_id,
                "item_id": item.item_id,
                "scenario": item.scenario,
                "route": item.route,
                "expected_sources": list(item.expected),
                "knowledge_status": item.knowledge_status,
                "reason_codes": list(item.reason_codes),
                "cited_sources": list(item.cited),
                "verdict": item.verdict,
            }
            for item in run.items
        ],
    }


def render_report(result: dict[str, Any]) -> str:
    metrics = result["knowledge_metrics"]
    rate = metrics["expected_citation_rate"]
    rate_text = "N/A" if rate is None else f"{rate:.1%}"
    lines = [
        "# Evaluation draft v1: Knowledge diagnostic",
        "",
        "**Diagnostic only.** This runs the Knowledge agent against every routable item in the synthetic draft. It does not call a model provider, approve labels, or measure full MAO accuracy.",
        "",
        f"- Dataset: {result['dataset_id']}",
        f"- Dataset status: {result['dataset_status']}",
        f"- Label approval: {result['approval'].get('approved', False)}",
        f"- Scoring authorization: {result['approval'].get('scoring_authorized', False)}",
        f"- Cases/items inspected: {result['case_count']} / {result['item_count']}",
        f"- As-of date: {result['evaluation_as_of']}",
        f"- Knowledge source set: {result['source_set_version']}",
        f"- Knowledge agent version: {result['knowledge_agent_version']}",
        "",
        "## Knowledge diagnostic results",
        "",
        f"- Expected-source citation rate: {metrics['expected_citation_hits']}/{metrics['expected_citation_cases']} ({rate_text}); this is an observed diagnostic rate, not a PRD acceptance score.",
        f"- Expected-source citation misses: {metrics['expected_citation_misses']}",
        f"- Expected-reason abstentions: {metrics['expected_reason_abstentions']}/{metrics['expected_abstention_cases']}",
        f"- Stale-source cases without an answer: {metrics['stale_source_cases_without_an_answer']}/{metrics['stale_source_cases']}",
        f"- Wrong-source/missed-abstention items: {metrics['wrong_source_or_missing_expected_abstention']}",
        f"- Items held for Auditor: {metrics['auditor_held_items']}",
        f"- Items with no expected Knowledge source that abstained: {metrics['no_source_expected_and_abstained']}",
        f"- Source-map validation problems: {result['source_map_problem_count']}",
        "",
        "## Verdict counts",
        "",
        "| Verdict | Items |",
        "| :--- | ---: |",
    ]
    lines.extend(
        f"| {verdict} | {count} |"
        for verdict, count in result["item_verdicts"].items()
    )
    lines.extend(["", "## Not scored by this run", ""])
    lines.extend(f"- {gate}" for gate in result["not_scored_gates"])
    lines.extend(["", "## Case and item outcomes", "", "| Case | Item | Scenario | Route | Verdict | Observed source(s) |", "| :--- | :--- | :--- | :--- | :--- | :--- |"])
    for item in result["case_results"]:
        sources = ", ".join(item["cited_sources"]) or "—"
        lines.append(
            f"| {item['case_id']} | {item['item_id']} | {item['scenario']} | "
            f"{item['route']} | {item['verdict']} | {sources} |"
        )
    return "\n".join(lines) + "\n"


def run_diagnostic(
    cases_path: Path,
    fixture_set_dir: Path,
    policy_path: Path,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    raw = cases_path.read_text(encoding="utf-8")
    dataset = json.loads(raw)
    run = run_source_check(cases_path, fixture_set_dir, policy_path, base_dir)
    result = summarize(run, dataset, load_source_map(fixture_set_dir))
    result["generated_at"] = datetime.now(UTC).isoformat()
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a non-billable Knowledge diagnostic over the evaluation draft."
    )
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--knowledge-dir", type=Path, default=None)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args(argv)

    result = run_diagnostic(args.cases, args.fixtures, args.policy, args.knowledge_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(result), encoding="utf-8", newline="\n")
    args.results.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    metrics = result["knowledge_metrics"]
    print(
        f"DIAGNOSTIC ONLY: {result['case_count']} cases / {result['item_count']} items; "
        f"Knowledge expected-source hits {metrics['expected_citation_hits']}/"
        f"{metrics['expected_citation_cases']}; source-map problems "
        f"{result['source_map_problem_count']}"
    )
    print(f"Report: {args.report}")
    print(f"Results: {args.results}")
    return 1 if result["source_map_problem_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
