"""Knowledge-side source check for the synthetic evaluation draft (Shawn's Lane).

Runs the Knowledge agent over every evaluation item that the agreed routing rule lets
reach Knowledge, with the evaluation corpus (the runtime corpus plus one
evaluation-only fixture set) at the dataset's pinned ``evaluation_as_of``, and compares
each result with the Knowledge-side source map.

Routing input is the draft's own category label: an item whose category is unknown
stays with the human Auditor and is reported as held, never run. An item with an
inferred category reaches Knowledge while its urgency stays Unknown. This module does
not run Triage, the connector, Troubleshooting, or any model, and it does not score or
approve the evaluation. Synthetic data only.

    python -m cdit_support_mao.lane_eval_sources --report <md> --results <json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError

from cdit_support_mao.agents.knowledge import (
    EvaluationCorpus,
    KnowledgeAgent,
    load_evaluation_corpus,
)
from cdit_support_mao.agents.knowledge.agent import AGENT_VERSION as KNOWLEDGE_AGENT_VERSION
from cdit_support_mao.agents.knowledge.corpus import ineligibility_reason
from cdit_support_mao.agents.troubleshooting import TroubleshootingPolicy, load_policy
from cdit_support_mao.contracts import (
    AgentStatus,
    CheckpointOutcome,
    ConfidenceBand,
    ReasonCode,
    RunContext,
    TriageHandoff,
)
from cdit_support_mao.contracts.common import StrictModel

DEFAULT_CASES = Path("synthetic_data/evaluation_draft/v1/cases.json")
DEFAULT_FIXTURES = Path("synthetic_data/evaluation_knowledge/eval-draft-v1")
# The evaluation draft cites SYN-TS-POLICY 0.1.1 (RR-03, RR-04), which 0.1.2 left unchanged.
# Move this with the draft's citations when Manny updates them.
DEFAULT_POLICY = Path("synthetic_data/policy/troubleshooting-policy_v0.1.1.json")
SOURCE_MAP = "source-map.json"
UNKNOWN_CATEGORY = "unknown"

ExpectedOutcome = Literal[
    "cited", "abstain_stale", "abstain_conflict", "abstain_injection", "not_a_knowledge_source"
]
ABSTAIN_REASON: dict[str, ReasonCode] = {
    "abstain_stale": ReasonCode.STALE_SOURCE_ONLY,
    "abstain_conflict": ReasonCode.CONFLICTING_SOURCES,
    "abstain_injection": ReasonCode.RETRIEVED_INJECTION,
}

Verdict = Literal[
    "cited_expected",
    "abstained_as_expected",
    "abstained_other_reason",
    "missed_abstained",
    "cited_other_source",
    "no_source_expected_abstained",
    "answered_without_expected_source",
    "held_for_auditor",
    "unmapped_citation",
]
SAFE_VERDICTS = frozenset(
    {"cited_expected", "abstained_as_expected", "no_source_expected_abstained", "held_for_auditor"}
)


class SourceMapEntry(StrictModel):
    citation: str = Field(min_length=1, max_length=80)
    placeholder_ids: tuple[str, ...] = ()
    kind: Literal["kb_article", "troubleshooting_policy_rule", "requirement"]
    corpus: Literal["base", "evaluation_fixture", "policy", "prd"]
    source_id: str
    version: str
    section: str | None = None
    rule_id: str | None = None
    status: str
    effective_date: date | None = None
    review_due: date | None = None
    freshness_at_as_of: str
    expected_outcome: ExpectedOutcome
    supports: tuple[str, ...] = Field(min_length=1)
    routing_note: str | None = None
    related_base_source: str | None = None


class SourceMap(StrictModel):
    source_map_id: str
    version: str
    use: Literal["evaluation_only"]
    evaluation_dataset_id: str
    fixture_set_id: str
    evaluation_as_of: date
    as_of_rationale: str = Field(min_length=1)
    expected_outcomes: dict[str, str]
    entries: tuple[SourceMapEntry, ...] = Field(min_length=1)

    def by_citation(self) -> dict[str, SourceMapEntry]:
        return {entry.citation: entry for entry in self.entries}


def load_source_map(fixture_set_dir: Path) -> SourceMap:
    path = fixture_set_dir / SOURCE_MAP
    try:
        return SourceMap.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (FileNotFoundError, json.JSONDecodeError, ValidationError) as error:
        raise ValueError(f"invalid source map {path}: {error}") from error


def validate_source_map(
    source_map: SourceMap, evaluation: EvaluationCorpus, policy: TroubleshootingPolicy
) -> list[str]:
    """Problems that make the source map disagree with the corpus, policy, or manifest."""
    problems: list[str] = []
    as_of = source_map.evaluation_as_of
    if as_of != evaluation.manifest.evaluation_as_of:
        problems.append("source map evaluation_as_of differs from the fixture manifest")
    if source_map.fixture_set_id != evaluation.manifest.fixture_set_id:
        problems.append("source map fixture_set_id differs from the fixture manifest")
    if source_map.evaluation_dataset_id != evaluation.manifest.evaluation_dataset_id:
        problems.append("source map evaluation_dataset_id differs from the fixture manifest")
    citations = [entry.citation for entry in source_map.entries]
    for citation, count in Counter(citations).items():
        if count > 1:
            problems.append(f"{citation}: listed {count} times")
    articles = {(a.doc_id, a.version): a for a in evaluation.corpus.articles}
    rules = {rule.rule_id for rule in policy.restricted_request_rules}
    for entry in source_map.entries:
        where = entry.citation
        if entry.kind == "kb_article":
            article = articles.get((entry.source_id, entry.version))
            if article is None:
                problems.append(f"{where}: no such article version")
                continue
            if where != f"{entry.source_id}#{entry.section} v{entry.version}":
                problems.append(f"{where}: citation does not match source, section, and version")
            if entry.section not in {section.section_id for section in article.sections}:
                problems.append(f"{where}: no such section")
            fixture = entry.source_id in evaluation.fixture_doc_ids
            if (entry.corpus == "evaluation_fixture") != fixture:
                problems.append(f"{where}: corpus label is {entry.corpus}")
            reason = ineligibility_reason(article, as_of)
            freshness = "current" if reason is None else reason.value
            if (entry.status, entry.effective_date, entry.review_due, entry.freshness_at_as_of) != (
                article.status, article.effective_date, article.review_due, freshness
            ):
                problems.append(f"{where}: status or dates differ from the corpus at {as_of}")
            if entry.expected_outcome == "cited" and freshness != "current":
                problems.append(f"{where}: expected to be cited but is {freshness}")
            if entry.expected_outcome == "abstain_stale" and freshness != ReasonCode.SOURCE_STALE.value:
                problems.append(f"{where}: expected stale but is {freshness}")
        elif entry.kind == "troubleshooting_policy_rule":
            if (entry.source_id, entry.version) != (policy.policy_id, policy.version):
                problems.append(f"{where}: policy id or version differs from {policy.policy_id} {policy.version}")
            if entry.rule_id not in rules:
                problems.append(f"{where}: no such policy rule")
            if entry.status != policy.status:
                problems.append(f"{where}: policy status is {policy.status}")
            if entry.expected_outcome != "not_a_knowledge_source":
                problems.append(f"{where}: a policy rule is not a Knowledge source")
        elif entry.expected_outcome != "not_a_knowledge_source":
            problems.append(f"{where}: a requirement is not a Knowledge source")
    return problems


@dataclass(frozen=True)
class ItemResult:
    case_id: str
    item_id: str
    scenario: str
    category: str
    route: Literal["knowledge", "auditor"]
    expected: tuple[str, ...]
    knowledge_status: str | None
    reason_codes: tuple[str, ...]
    cited: tuple[str, ...]
    verdict: Verdict


@dataclass(frozen=True)
class CaseNote:
    case_id: str
    note: str


@dataclass(frozen=True)
class SourceCheckRun:
    dataset_id: str
    cases_sha256: str
    evaluation_as_of: date
    source_set_version: str
    knowledge_agent_version: str
    source_map_problems: tuple[str, ...]
    items: tuple[ItemResult, ...]
    case_notes: tuple[CaseNote, ...]


def _stand_in(context: RunContext, text: str, now: datetime) -> TriageHandoff:
    """A minimal A2 stand-in: Knowledge queries only the item text (K-3)."""
    return TriageHandoff(
        contribution_id="TRI-EVAL-SOURCE-CHECK",
        agent="evaluation-source-check-stand-in",
        agent_version="fixture",
        context=context,
        created_at=now,
        status=AgentStatus.COMPLETED,
        checkpoint=CheckpointOutcome(checkpoint="A2", passed=True, reason_codes=()),
        confidence=ConfidenceBand.LOW,
        confidence_rationale="Evaluation source check stand-in; not a Triage result.",
        case_summary=text,
        product_area=None,
        category="evaluation_item",
        category_confidence=ConfidenceBand.LOW,
        urgency="unknown",
    )


def _verdict(
    entries: list[SourceMapEntry], status: str, reasons: set[str], cited: set[str]
) -> Verdict:
    expected_cited = {e.citation for e in entries if e.expected_outcome == "cited"}
    abstain = [e for e in entries if e.expected_outcome in ABSTAIN_REASON]
    answered = status == AgentStatus.COMPLETED.value
    if expected_cited:
        if cited & expected_cited:
            return "cited_expected"
        return "cited_other_source" if answered else "missed_abstained"
    if abstain:
        if answered:
            return "cited_other_source"
        wanted = {ABSTAIN_REASON[e.expected_outcome].value for e in abstain}
        return "abstained_as_expected" if reasons & wanted else "abstained_other_reason"
    return "answered_without_expected_source" if answered else "no_source_expected_abstained"


def run_source_check(
    cases_path: Path, fixture_set_dir: Path, policy_path: Path, base_dir: Path | None = None
) -> SourceCheckRun:
    raw = cases_path.read_bytes()
    dataset = json.loads(raw.decode("utf-8"))
    evaluation = load_evaluation_corpus(fixture_set_dir, base_dir)
    source_map = load_source_map(fixture_set_dir)
    policy = load_policy(policy_path)
    problems = validate_source_map(source_map, evaluation, policy)
    as_of = date.fromisoformat(dataset["evaluation_as_of"])
    if as_of != source_map.evaluation_as_of:
        problems.append(f"case file evaluation_as_of {as_of} differs from the source map")
    if dataset["dataset_id"] != source_map.evaluation_dataset_id:
        problems.append("case file dataset_id differs from the source map")

    now = datetime.combine(as_of, time(12, 0), tzinfo=UTC)
    agent = KnowledgeAgent(evaluation.corpus)
    by_citation = source_map.by_citation()
    items: list[ItemResult] = []
    notes: list[CaseNote] = []
    for case in dataset["cases"]:
        expected = tuple(case["evidence_expectations"]["expected_source_ids"])
        unmapped = [c for c in expected if c not in by_citation]
        entries = [by_citation[c] for c in expected if c in by_citation]
        context = RunContext(
            run_id="RUN-EVAL-SOURCE-CHECK",
            case_id=case["case_id"],
            case_version=1,
            policy_version="SYN-EVAL-SOURCE-CHECK",
        )
        reached: set[str] = set()
        held = False
        for item in case["items"]:
            category = item["triage_proposal"]["category"]
            common = {
                "case_id": case["case_id"],
                "item_id": item["item_id"],
                "scenario": case["scenario_key"].rsplit("-", 1)[0],
                "category": category,
                "expected": expected,
            }
            if category == UNKNOWN_CATEGORY:
                held = True
                items.append(ItemResult(**common, route="auditor", knowledge_status=None,
                                        reason_codes=(), cited=(), verdict="held_for_auditor"))
                continue
            result = agent.run(context, _stand_in(context, item["text"], now),
                               acknowledged={"TRI-EVAL-SOURCE-CHECK"}, as_of=as_of, now=now)
            cited = tuple(f"{p.source.source_id}#{p.source.locator} v{p.source.version}" for p in result.passages)
            reasons = tuple(code.value for code in result.checkpoint.reason_codes)
            reached.update(cited)
            verdict: Verdict = (
                "unmapped_citation" if unmapped
                else _verdict(entries, result.status.value, set(reasons), set(cited))
            )
            items.append(ItemResult(**common, route="knowledge", knowledge_status=result.status.value,
                                    reason_codes=reasons, cited=cited, verdict=verdict))
        if unmapped:
            notes.append(CaseNote(case["case_id"], f"citations not in the source map: {', '.join(unmapped)}"))
        expected_cited = {e.citation for e in entries if e.expected_outcome == "cited"}
        missing = sorted(expected_cited - reached)
        if held and missing:
            notes.append(CaseNote(
                case["case_id"],
                f"{', '.join(missing)} cannot be reached at A2: the only item it fits is held for the "
                "Auditor (unknown category). It applies only after a human assigns a category.",
            ))
        dispatch = case["current_runtime_expectation"].get("knowledge_dispatch_candidate")
        inferred = any(i["triage_proposal"]["category"] != UNKNOWN_CATEGORY for i in case["items"])
        if dispatch is False and inferred:
            notes.append(CaseNote(
                case["case_id"],
                "knowledge_dispatch_candidate is false, but an item has an inferred category. Under the "
                "agreed routing rule it reaches Knowledge while urgency stays Unknown, unless another "
                "gate (for example a simulated unavailable component) stops the run first.",
            ))

    return SourceCheckRun(
        dataset_id=dataset["dataset_id"],
        # Line endings are normalised so the fingerprint matches on CRLF and LF checkouts.
        cases_sha256=hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest(),
        evaluation_as_of=as_of,
        source_set_version=evaluation.corpus.source_set_version,
        knowledge_agent_version=KNOWLEDGE_AGENT_VERSION,
        source_map_problems=tuple(problems),
        items=tuple(items),
        case_notes=tuple(notes),
    )


def results_json(run: SourceCheckRun) -> str:
    payload = {
        "dataset_id": run.dataset_id,
        "cases_sha256": run.cases_sha256,
        "evaluation_as_of": run.evaluation_as_of.isoformat(),
        "source_set_version": run.source_set_version,
        "knowledge_agent_version": run.knowledge_agent_version,
        "source_map_problems": list(run.source_map_problems),
        "verdicts": dict(sorted(Counter(item.verdict for item in run.items).items())),
        "items": [asdict(item) for item in run.items],
        "case_notes": [asdict(note) for note in run.case_notes],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"


def _ids(case_ids: list[str]) -> str:
    return ", ".join(cid.removeprefix("SYN-EVAL-") for cid in case_ids)


def render_report(run: SourceCheckRun) -> str:
    counts = Counter(item.verdict for item in run.items)
    lines = [
        "# Evaluation draft v1: Knowledge source check",
        "",
        "Generated by `python -m cdit_support_mao.lane_eval_sources`. Synthetic data only; no model call. "
        "This is a Knowledge-side source check, not a score, and it does not approve any label.",
        "",
        f"- Dataset: `{run.dataset_id}` (case file SHA-256 `{run.cases_sha256[:16]}…`)",
        f"- `evaluation_as_of`: {run.evaluation_as_of.isoformat()}",
        f"- Evaluation corpus: `{run.source_set_version}` (runtime corpus plus the evaluation-only fixture set)",
        f"- Knowledge agent: {run.knowledge_agent_version}",
        f"- Source map problems: {len(run.source_map_problems)}",
        "",
        "## Verdicts",
        "",
        "| Verdict | Items |",
        "| :--- | ---: |",
    ]
    lines += [f"| `{verdict}` | {count} |" for verdict, count in sorted(counts.items())]
    lines += [f"| **Total** | {len(run.items)} |", "", "## By scenario", "",
              "| Cases | Scenario | Item | Expected | Knowledge result | Verdict |",
              "| :--- | :--- | :---: | :--- | :--- | :--- |"]
    grouped: dict[tuple, list[str]] = {}
    for item in run.items:
        index = item.item_id.rsplit("-I", 1)[-1]
        result = "not run (held)" if item.route == "auditor" else (
            f"{item.knowledge_status}" + (f" ({', '.join(item.reason_codes)})" if item.reason_codes else "")
            + (f": {', '.join(item.cited[:2])}" if item.cited else "")
        )
        key = (item.scenario, index, ", ".join(item.expected) or "none", result, item.verdict)
        grouped.setdefault(key, []).append(item.case_id)
    for (scenario, index, expected, result, verdict), case_ids in grouped.items():
        lines.append(f"| {_ids(case_ids)} | {scenario} | {index} | {expected} | {result} | `{verdict}` |")
    lines += ["", "## Case notes", ""]
    by_note: dict[str, list[str]] = {}
    for note in run.case_notes:
        by_note.setdefault(note.note, []).append(note.case_id)
    lines += [f"- {_ids(case_ids)}: {note}" for note, case_ids in by_note.items()] or ["- None."]
    lines += ["", "## Source map problems", ""]
    lines += [f"- {problem}" for problem in run.source_map_problems] or ["- None."]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Knowledge-side source check for the evaluation draft.")
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--knowledge-dir", type=Path, default=None)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--results", type=Path, default=None)
    args = parser.parse_args(argv)
    run = run_source_check(args.cases, args.fixtures, args.policy, args.knowledge_dir)
    if args.report:
        args.report.write_text(render_report(run), encoding="utf-8", newline="\n")
    if args.results:
        args.results.write_text(results_json(run), encoding="utf-8", newline="\n")
    counts = Counter(item.verdict for item in run.items)
    print(f"{len(run.items)} items | " + " | ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    print(f"source map problems {len(run.source_map_problems)} | case notes {len(run.case_notes)}")
    return 1 if run.source_map_problems or counts.get("unmapped_citation") else 0


if __name__ == "__main__":
    raise SystemExit(main())
