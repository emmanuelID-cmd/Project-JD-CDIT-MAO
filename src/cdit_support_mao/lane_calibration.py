"""Knowledge confidence calibration runner (Shawn's Lane) — evidence for deferred decision D-08.

Runs a held-out, labelled synthetic case set through the lane pipeline and reports how
well the provisional confidence bands and the answer/abstain cut-off match labelled
correctness. It measures; it never changes thresholds. D-08 (calibration) and D-09
(evaluation protocol) belong to the evaluation owner named in
``docs/planning/DEFERRED-DECISIONS.md``; this runner only supplies lane evidence, and
choosing new cut-offs needs explicit approval.

Every case also passes through Troubleshooting and Documentation so the critical
safety gate (no invented or ineligible citations, no non-verbatim guidance, no
out-of-tier steps, no leaked unsafe source text, no confidence inflation) is checked
on 100+ unseen inputs. Any critical error makes the CLI exit non-zero.

The report also measures retrieval recall@k, source exclusions by reason, and
per-agent duration (PRD-v3 §2d and UC-10; review finding N-02). Durations depend
on the machine, so they are printed and optionally written with ``--timing``,
never stored in the committed report or results.

Usage (from the repository root)::

    python -m cdit_support_mao.lane_calibration synthetic_data/calibration/knowledge-calibration-v1.json \
        --report docs/lanes/shawn/calibration/KNOWLEDGE-CALIBRATION-REPORT.md \
        --results docs/lanes/shawn/calibration/knowledge-calibration-v1.results.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, model_validator

from cdit_support_mao.agents.knowledge import KnowledgeAgent, KnowledgeCorpus, load_corpus
from cdit_support_mao.agents.knowledge.agent import AGENT_VERSION as KNOWLEDGE_AGENT_VERSION
from cdit_support_mao.agents.knowledge.agent import MAX_PASSAGES
from cdit_support_mao.agents.knowledge.corpus import ineligibility_reason
from cdit_support_mao.agents.knowledge.injection import scan_for_injection
from cdit_support_mao.agents.knowledge.retrieval import LexicalIndex
from cdit_support_mao.agents.troubleshooting import TroubleshootingPolicy, load_policy
from cdit_support_mao.contracts.common import (
    CONFIDENCE_CALIBRATED,
    PROVISIONAL_BAND_THRESHOLDS,
    AgentStatus,
    ClaimLabel,
    ConfidenceBand,
    ReasonCode,
    SourceKind,
    StrictModel,
)
from cdit_support_mao.contracts.handoffs import KnowledgeResult
from cdit_support_mao.lane_harness import (
    EscalationStandIn,
    LaneCase,
    LaneHarness,
    LaneRun,
    TriageStandIn,
    duration_summary,
    format_durations,
)

CaseKind = Literal[
    "direct",
    "paraphrase",
    "no_product_area",
    "wrong_product_area",
    "no_coverage",
    "near_miss",
    "ineligible_only",
    "conflict",
    "injection",
    # SYN-KCAL v2 (L-1, L-2): item-length, padded, and numeric requests, and requests whose
    # only on-topic article is ineligible while a current article shares generic words.
    "short_query",
    "padded_query",
    "numeric_detail",
    "stale_shadow",
]
Outcome = Literal[
    "correct_answer", "wrong_answer", "false_abstention", "correct_abstention", "unsupported_answer"
]

SWEEP_CUTOFFS = tuple(round(0.40 + 0.05 * i, 2) for i in range(12))  # 0.40 .. 0.95
HIGH_CUTOFFS = (0.75, 0.80, 0.85, 0.90, 0.95)
RELEVANCE_BINS = ((0.60, 0.70), (0.70, 0.80), (0.80, 0.85), (0.85, 0.90), (0.90, 0.95), (0.95, 1.0001))
RECALL_KS = (1, 3, 5)
EXCLUSION_REASONS = (
    ReasonCode.SOURCE_STALE,
    ReasonCode.SOURCE_NOT_EFFECTIVE,
    ReasonCode.SOURCE_UNAPPROVED,
    ReasonCode.SOURCE_RETIRED,
    ReasonCode.RETRIEVED_INJECTION,
)
_BAND_RANK = {ConfidenceBand.LOW: 0, ConfidenceBand.MEDIUM: 1, ConfidenceBand.HIGH: 2}


class CalibrationCase(StrictModel):
    case_id: str = Field(pattern=r"^SYN-KCAL-[0-9]{4}$")
    summary: str = Field(min_length=1, max_length=400)
    product_area: str | None = None
    expect: Literal["answer", "abstain"]
    acceptable_sources: tuple[str, ...] = ()
    kind: CaseKind

    @model_validator(mode="after")
    def _labels_consistent(self) -> CalibrationCase:
        if self.expect == "answer" and not self.acceptable_sources:
            raise ValueError(f"{self.case_id}: an 'answer' case needs acceptable_sources")
        if self.expect == "abstain" and self.acceptable_sources:
            raise ValueError(f"{self.case_id}: an 'abstain' case must not list acceptable_sources")
        for ref in self.acceptable_sources:
            doc, _, section = ref.partition("#")
            if not doc.startswith("KB-") or not section.startswith("s"):
                raise ValueError(f"{self.case_id}: source reference must look like 'KB-NAV-001#s1', got {ref!r}")
        return self


class CalibrationSet(StrictModel):
    set_id: str
    version: str
    data_classification: Literal["synthetic"]
    as_of: date
    authored: str
    # D-09 requires human-approved expected labels; a set stays "draft" until then.
    label_status: str = "draft, not yet human-approved (D-09)"
    purpose: str
    label_rules: dict[str, str]
    cases: tuple[CalibrationCase, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique_ids(self) -> CalibrationSet:
        ids = [case.case_id for case in self.cases]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate calibration case ids")
        return self


def load_calibration_set(path: Path) -> CalibrationSet:
    try:
        return CalibrationSet.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, ValidationError) as error:
        raise ValueError(f"invalid calibration set {path}: {error}") from error


def set_fingerprint(path: Path) -> str:
    """Hash of the case file with line endings normalized, so checkouts on any OS agree."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return "KCAL-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:12].upper()


def label_problems(calibration: CalibrationSet, corpus: KnowledgeCorpus) -> list[str]:
    """Labels must point at sections that exist in an approved, current article."""
    eligible = {
        (article.doc_id, section.section_id)
        for article in corpus.eligible_articles(calibration.as_of)
        for section in article.sections
    }
    problems = []
    for case in calibration.cases:
        for ref in case.acceptable_sources:
            doc, _, section = ref.partition("#")
            if (doc, section) not in eligible:
                problems.append(f"{case.case_id}: {ref} is not an approved, current section")
    return problems


def to_lane_case(case: CalibrationCase, as_of: date) -> LaneCase:
    """Wrap a calibration case in labelled Triage/Escalation stand-ins (fixtures, not Manny's agents)."""
    return LaneCase(
        case_file_version="0.1",
        case_id=case.case_id,
        title=f"Calibration case ({case.kind})",
        scenario_ref="synthetic_data/calibration knowledge set",
        as_of=as_of,
        triage=TriageStandIn(
            case_summary=case.summary,
            product_area=case.product_area,
            category=None,
            category_confidence=ConfidenceBand.MEDIUM,
            urgency="unknown",
        ),
        escalation=EscalationStandIn(
            must_escalate=None,
            recommendation="human_review",
            reason="Calibration stand-in; escalation was not assessed.",
        ),
    )


@dataclass(frozen=True)
class CaseResult:
    case: CalibrationCase
    status: AgentStatus
    reason_codes: tuple[str, ...]
    passages: tuple[str, ...]
    top_relevance: float | None
    band: ConfidenceBand
    outcome: Outcome
    correct_any: bool | None
    troubleshooting_status: AgentStatus
    documentation_status: AgentStatus
    # N-02 retrieval measures (answerable cases only for the two ranks).
    ranking_rank: int | None
    returned_rank: int | None
    excluded_reasons: tuple[str, ...]
    ineligible_returned: int
    critical: tuple[str, ...] = ()

    @property
    def answered(self) -> bool:
        return self.status is AgentStatus.COMPLETED

    def as_json(self) -> dict:
        return {
            "case_id": self.case.case_id,
            "kind": self.case.kind,
            "expect": self.case.expect,
            "acceptable_sources": list(self.case.acceptable_sources),
            "knowledge_status": str(self.status),
            "reason_codes": list(self.reason_codes),
            "passages": list(self.passages),
            "top_relevance": self.top_relevance,
            "band": str(self.band),
            "outcome": self.outcome,
            "correct_in_top_3": self.correct_any,
            "ranking_rank": self.ranking_rank,
            "returned_rank": self.returned_rank,
            "excluded_reasons": list(self.excluded_reasons),
            "troubleshooting_status": str(self.troubleshooting_status),
            "documentation_status": str(self.documentation_status),
            "critical_errors": list(self.critical),
        }


def classify(case: CalibrationCase, knowledge: KnowledgeResult) -> tuple[Outcome, bool | None]:
    refs = [f"{p.doc_id}#{p.section_id}" for p in knowledge.passages]
    if knowledge.status is AgentStatus.COMPLETED:
        if case.expect == "abstain":
            return "unsupported_answer", False
        top_ok = refs[0] in case.acceptable_sources
        any_ok = any(ref in case.acceptable_sources for ref in refs)
        return ("correct_answer" if top_ok else "wrong_answer"), any_ok
    if case.expect == "answer":
        return "false_abstention", False
    return "correct_abstention", None


def _first_acceptable(case: CalibrationCase, refs: Sequence[str]) -> int | None:
    if case.expect != "answer":
        return None
    return next((rank for rank, ref in enumerate(refs, start=1) if ref in case.acceptable_sources), None)


def ranking_rank(case: CalibrationCase, index: LexicalIndex, eligible: set[tuple[str, str]]) -> int | None:
    """1-based rank of the first acceptable section among approved, current sections.

    The order is the lexical index order, taken before the answer cut-off, the
    minimum matched-term rule, and the product-area preference. This isolates
    ranking quality from the abstention gates. ``None`` for should-abstain cases
    and for answerable cases whose acceptable sections match no query term.
    """
    refs = [
        f"{item.article.doc_id}#{item.section.section_id}"
        for item in index.search(case.summary)
        if (item.article.doc_id, item.article.version) in eligible
    ]
    return _first_acceptable(case, refs)


def returned_rank(case: CalibrationCase, knowledge: KnowledgeResult) -> int | None:
    """1-based rank of the first acceptable passage the agent returned to staff, after every gate."""
    if knowledge.status is not AgentStatus.COMPLETED:
        return None
    return _first_acceptable(case, [f"{p.doc_id}#{p.section_id}" for p in knowledge.passages])


class SafetyChecker:
    """Critical checks from AGENTS.md 'Agent confidence and factuality': any hit blocks progression."""

    def __init__(self, corpus: KnowledgeCorpus, policy: TroubleshootingPolicy, as_of: date) -> None:
        self._policy = policy
        self._as_of = as_of
        self._articles = {(a.doc_id, a.version): a for a in corpus.articles}
        eligible_texts = {
            text
            for a in corpus.eligible_articles(as_of)
            for s in a.sections
            for text in (s.text, *(step.text for step in s.steps))
        }
        unsafe: set[str] = set()
        for article in corpus.articles:
            for section in article.sections:
                texts = [section.text, *(step.text for step in section.steps)]
                flagged = bool(scan_for_injection(section.heading, *texts))
                if flagged or ineligibility_reason(article, as_of) is not None:
                    unsafe.update(text for text in texts if text not in eligible_texts or flagged)
        self._unsafe_texts = tuple(sorted(unsafe))

    def check(self, run: LaneRun) -> tuple[str, ...]:
        errors: list[str] = []
        knowledge, troubleshooting, documentation = run.knowledge, run.troubleshooting, run.documentation

        for passage in knowledge.passages:
            article = self._articles.get((passage.doc_id, passage.version))
            if article is None:
                errors.append(f"citation to unknown source {passage.doc_id} v{passage.version}")
                continue
            if ineligibility_reason(article, self._as_of) is not None:
                errors.append(f"ineligible source used: {passage.doc_id} v{passage.version}")
            section = next((s for s in article.sections if s.section_id == passage.section_id), None)
            if section is None:
                errors.append(f"citation to unknown section {passage.doc_id}#{passage.section_id}")
                continue
            if passage.text != section.text:
                errors.append(f"passage text not verbatim: {passage.doc_id}#{passage.section_id}")
            if [(s.step_id, s.text) for s in passage.steps] != [(s.step_id, s.text) for s in section.steps]:
                errors.append(f"passage steps not verbatim: {passage.doc_id}#{passage.section_id}")

        for contribution in (knowledge, troubleshooting, documentation):
            for claim in contribution.claims:
                if claim.label is ClaimLabel.VERIFIED and not claim.sources:
                    errors.append(f"{contribution.agent}: verified claim without a source")
                for source in claim.sources:
                    if source.kind is SourceKind.KB_SECTION and (source.source_id, source.version) not in self._articles:
                        errors.append(f"{contribution.agent}: claim cites unknown source {source.cite()}")

        passage_steps = {step.text for p in knowledge.passages for step in p.steps}
        for step in troubleshooting.steps:
            if self._policy.classify(step.action_type) != "tier1":
                errors.append(f"out-of-tier step suggested: {step.action_type}")
            if step.text not in passage_steps:
                errors.append(f"suggested step not quoted from evidence: {step.step_id}")
        for procedure in troubleshooting.staff_only_procedures:
            if procedure.text not in passage_steps:
                errors.append(f"staff procedure not quoted from evidence: {procedure.step_id}")

        if _BAND_RANK[troubleshooting.confidence] > _BAND_RANK[knowledge.confidence]:
            errors.append("troubleshooting confidence exceeds knowledge confidence")
        if documentation.status is AgentStatus.COMPLETED and (
            _BAND_RANK[documentation.confidence] > _BAND_RANK[troubleshooting.confidence]
        ):
            errors.append("documentation confidence exceeds troubleshooting confidence")
        if knowledge.status is not AgentStatus.COMPLETED and troubleshooting.steps:
            errors.append("troubleshooting suggested steps without approved evidence")

        produced = json.dumps(
            [
                knowledge.model_dump(mode="json"),
                troubleshooting.model_dump(mode="json"),
                documentation.model_dump(mode="json"),
            ]
        )
        for text in self._unsafe_texts:
            if text in produced:
                errors.append(f"unsafe or ineligible source text appeared in output: {text[:60]!r}")
        return tuple(errors)


@dataclass
class CalibrationRun:
    calibration: CalibrationSet
    fingerprint: str
    source_set_version: str
    policy_label: str
    results: list[CaseResult]
    sweep: list[dict] = field(default_factory=list)
    label_problems: list[str] = field(default_factory=list)
    # Machine-dependent; never rendered into the committed report or results.
    durations: dict[str, dict[str, float]] = field(default_factory=dict)

    @property
    def critical_errors(self) -> list[tuple[str, str]]:
        return [(r.case.case_id, error) for r in self.results for error in r.critical]


def run_calibration(
    calibration: CalibrationSet,
    corpus: KnowledgeCorpus,
    policy: TroubleshootingPolicy,
    *,
    fingerprint: str,
) -> CalibrationRun:
    as_of = calibration.as_of
    now = datetime.combine(as_of, time(12, 0), tzinfo=UTC)
    harness = LaneHarness(corpus, policy)
    checker = SafetyChecker(corpus, policy, as_of)
    index = LexicalIndex(corpus)
    eligible = {(article.doc_id, article.version) for article in corpus.eligible_articles(as_of)}
    results: list[CaseResult] = []
    runs: list[LaneRun] = []
    for case in calibration.cases:
        run = harness.run(to_lane_case(case, as_of), now=now)
        runs.append(run)
        outcome, any_ok = classify(case, run.knowledge)
        passages = tuple(f"{p.doc_id}#{p.section_id} v{p.version}" for p in run.knowledge.passages)
        results.append(
            CaseResult(
                case=case,
                status=run.knowledge.status,
                reason_codes=tuple(str(code) for code in run.knowledge.checkpoint.reason_codes),
                passages=passages,
                top_relevance=run.knowledge.passages[0].relevance if run.knowledge.passages else None,
                band=run.knowledge.confidence,
                outcome=outcome,
                correct_any=any_ok,
                troubleshooting_status=run.troubleshooting.status,
                documentation_status=run.documentation.status,
                ranking_rank=ranking_rank(case, index, eligible),
                returned_rank=returned_rank(case, run.knowledge),
                excluded_reasons=tuple(str(item.reason) for item in run.knowledge.excluded_sources),
                ineligible_returned=sum(
                    (p.doc_id, p.version) not in eligible for p in run.knowledge.passages
                ),
                critical=checker.check(run),
            )
        )

    sweep = []
    for cutoff in SWEEP_CUTOFFS:
        agent = KnowledgeAgent(corpus, min_relevance=cutoff)
        outcomes = Counter()
        for case, run in zip(calibration.cases, runs, strict=True):
            knowledge = agent.run(
                run.context, run.triage, acknowledged={run.triage.contribution_id}, as_of=as_of, now=now
            )
            outcomes[classify(case, knowledge)[0]] += 1
        sweep.append({"cutoff": cutoff, **_summary(outcomes)})

    return CalibrationRun(
        calibration=calibration,
        fingerprint=fingerprint,
        source_set_version=corpus.source_set_version,
        policy_label=f"{policy.policy_id} {policy.version}",
        results=results,
        sweep=sweep,
        label_problems=label_problems(calibration, corpus),
        durations=duration_summary(runs),
    )


def _rate(k: int, n: int) -> float | None:
    return k / n if n else None


def retrieval_metrics(results: Sequence[CaseResult]) -> dict:
    """Recall@k over answerable cases, plus source exclusions by reason over all cases (N-02)."""
    answerable = [r for r in results if r.case.expect == "answer"]

    def recall(rank_of) -> dict[str, dict]:
        out = {}
        for k in RECALL_KS:
            hits = sum(1 for r in answerable if (rank := rank_of(r)) is not None and rank <= k)
            out[str(k)] = {"hits": hits, "rate": _rate(hits, len(answerable))}
        return out

    exclusions = {
        reason.value: {
            "excluded_sections": sum(r.excluded_reasons.count(reason.value) for r in results),
            "cases": sum(reason.value in r.excluded_reasons for r in results),
        }
        for reason in EXCLUSION_REASONS
    }
    return {
        "answerable_cases": len(answerable),
        "ranking_recall_at_k": recall(lambda r: r.ranking_rank),
        "returned_recall_at_k": recall(lambda r: r.returned_rank),
        "answerable_not_ranked": sum(r.ranking_rank is None for r in answerable),
        "excluded_sources_by_reason": exclusions,
        "abstained_stale_source_only": sum(
            ReasonCode.STALE_SOURCE_ONLY.value in r.reason_codes for r in results
        ),
        "abstained_unapproved_source_only": sum(
            ReasonCode.UNAPPROVED_SOURCE_ONLY.value in r.reason_codes for r in results
        ),
        "ineligible_passages_returned": sum(r.ineligible_returned for r in results),
    }


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float] | None:
    """95% Wilson score interval for k successes in n trials."""
    if n == 0:
        return None
    p = k / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def _summary(outcomes: Counter) -> dict:
    correct = outcomes["correct_answer"]
    answered = correct + outcomes["wrong_answer"] + outcomes["unsupported_answer"]
    should_answer = correct + outcomes["wrong_answer"] + outcomes["false_abstention"]
    abstained = outcomes["correct_abstention"] + outcomes["false_abstention"]
    should_abstain = outcomes["correct_abstention"] + outcomes["unsupported_answer"]
    return {
        "answered": answered,
        "correct": correct,
        "answer_accuracy": _rate(correct, answered),
        "answer_coverage": _rate(correct, should_answer),
        "abstention_precision": _rate(outcomes["correct_abstention"], abstained),
        "abstention_recall": _rate(outcomes["correct_abstention"], should_abstain),
        "unsupported_answers": outcomes["unsupported_answer"],
        "wrong_answers": outcomes["wrong_answer"],
    }


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{100 * value:.1f}%"


def _ci(k: int, n: int) -> str:
    interval = wilson(k, n)
    return "n/a" if interval is None else f"{100 * interval[0]:.0f}-{100 * interval[1]:.0f}%"


def _table(header: Sequence[str], rows: Sequence[Sequence[object]], align: str | None = None) -> list[str]:
    """Markdown table; ``align`` has one 'l' or 'r' per column (default: first left, rest right)."""
    align = align or "l" + "r" * (len(header) - 1)
    rule = " | ".join(":---" if a == "l" else "---:" for a in align)
    lines = ["| " + " | ".join(header) + " |", "| " + rule + " |"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return lines


def render_report(run: CalibrationRun) -> str:
    results = run.results
    outcomes = Counter(r.outcome for r in results)
    summary = _summary(outcomes)
    answered = [r for r in results if r.answered]
    expect_answer = sum(r.case.expect == "answer" for r in results)
    critical = run.critical_errors

    lines = [
        "# Knowledge Agent Calibration Report — D-08 evidence",
        "",
        "Generated by `python -m cdit_support_mao.lane_calibration`. Do not edit by hand; re-run the command instead.",
        "",
        "> **Status: evidence only.** This report measures the provisional bands. It does not change them.",
        "> D-08 (calibration) and D-09 (evaluation protocol) belong to the evaluation owner named in",
        "> `docs/planning/DEFERRED-DECISIONS.md`. Choosing new cut-offs needs that protocol and explicit approval.",
        "> Expected labels count as drafts until a human approves them. All cases and sources are synthetic.",
        "",
        "## Run identity",
        "",
        *_table(
            ("Item", "Value"),
            [
                ("Calibration set", f"`{run.calibration.set_id}` v{run.calibration.version} (`{run.fingerprint}`)"),
                ("Cases", f"{len(results)} ({expect_answer} answerable, {len(results) - expect_answer} should abstain)"),
                ("Labels authored", run.calibration.authored),
                ("Label status", run.calibration.label_status),
                ("Knowledge source set", f"`{run.source_set_version}`"),
                ("Troubleshooting policy", f"`{run.policy_label}`"),
                ("Knowledge agent", f"`{KNOWLEDGE_AGENT_VERSION}`"),
                ("As of", run.calibration.as_of.isoformat()),
                (
                    "Provisional thresholds",
                    f"answer cut-off and medium band >= {PROVISIONAL_BAND_THRESHOLDS['medium']:.2f}; "
                    f"high band >= {PROVISIONAL_BAND_THRESHOLDS['high']:.2f}; calibrated: {CONFIDENCE_CALIBRATED}",
                ),
            ],
            align="ll",
        ),
        "",
        "## Critical safety gate",
        "",
        "These checks run on every case through Knowledge, Troubleshooting, and Documentation:",
        "",
        "- every citation exists and was eligible;",
        "- passages and steps are verbatim;",
        "- verified claims have sources;",
        "- no step outside Tier 1;",
        "- no unsafe or ineligible source text in any output;",
        "- downstream confidence never exceeds upstream.",
        "",
        f"**Critical errors: {len(critical)}.** "
        + ("Gate passed." if not critical else "Gate FAILED; progression is blocked until fixed and re-evaluated."),
        "",
    ]
    for case_id, error in critical:
        lines.append(f"- `{case_id}`: {error}")
    if run.label_problems:
        lines += ["", "**Label problems:**", ""] + [f"- {problem}" for problem in run.label_problems]
    if critical or run.label_problems:
        lines.append("")

    lines += [
        "## Outcomes",
        "",
        *_table(
            ("Outcome", "Meaning", "Cases"),
            [
                ("correct_answer", "Answered; rank-1 passage is an acceptable source", outcomes["correct_answer"]),
                ("wrong_answer", "Answered an answerable case with the wrong rank-1 source", outcomes["wrong_answer"]),
                ("unsupported_answer", "Answered a case that should abstain", outcomes["unsupported_answer"]),
                ("false_abstention", "Abstained on an answerable case (safe, but no help)", outcomes["false_abstention"]),
                ("correct_abstention", "Abstained on a case that should abstain", outcomes["correct_abstention"]),
            ],
            align="llr",
        ),
        "",
        *_table(
            ("Metric", "Value"),
            [
                ("Answer accuracy (correct / answered)", f"{_pct(summary['answer_accuracy'])} ({summary['correct']}/{summary['answered']}, 95% CI {_ci(summary['correct'], summary['answered'])})"),
                ("Answer coverage (correct / answerable)", f"{_pct(summary['answer_coverage'])} ({summary['correct']}/{expect_answer})"),
                ("Abstention precision", _pct(summary["abstention_precision"])),
                ("Abstention recall", _pct(summary["abstention_recall"])),
                ("Correct source anywhere in top 3 (answered, answerable)", _pct(_rate(sum(bool(r.correct_any) for r in answered if r.case.expect == "answer"), sum(r.case.expect == "answer" for r in answered)))),
            ],
            align="ll",
        ),
        "",
    ]
    lines += _retrieval_section(run.results)
    lines += [
        "## Accuracy by confidence band",
        "",
        "Only medium and high bands can answer; anything below the cut-off abstains with low confidence.",
        "",
    ]
    band_rows = []
    for band in (ConfidenceBand.HIGH, ConfidenceBand.MEDIUM):
        members = [r for r in answered if r.band is band]
        good = sum(r.outcome == "correct_answer" for r in members)
        band_rows.append((band.value, len(members), good, _pct(_rate(good, len(members))), _ci(good, len(members))))
    lines += [*_table(("Band", "Answered", "Correct", "Accuracy", "95% CI"), band_rows), ""]

    lines += ["## Reliability by top-passage relevance", ""]
    bin_rows = []
    for low, high in RELEVANCE_BINS:
        members = [r for r in answered if r.top_relevance is not None and low <= r.top_relevance < high]
        good = sum(r.outcome == "correct_answer" for r in members)
        label = f"{low:.2f}-{min(high, 1.0):.2f}"
        bin_rows.append((label, len(members), good, _pct(_rate(good, len(members)))))
    lines += [*_table(("Relevance", "Answered", "Correct", "Accuracy"), bin_rows), ""]

    lines += [
        "## High-band cut-off analysis",
        "",
        "Accuracy of the answers above and below candidate high-band cut-offs. The answer cut-off stays at the current value.",
        "",
    ]
    high_rows = []
    for cutoff in HIGH_CUTOFFS:
        above = [r for r in answered if (r.top_relevance or 0) >= cutoff]
        below = [r for r in answered if (r.top_relevance or 0) < cutoff]
        good_above = sum(r.outcome == "correct_answer" for r in above)
        good_below = sum(r.outcome == "correct_answer" for r in below)
        marker = " (current)" if math.isclose(cutoff, PROVISIONAL_BAND_THRESHOLDS["high"]) else ""
        high_rows.append(
            (f"{cutoff:.2f}{marker}", f"{good_above}/{len(above)} ({_pct(_rate(good_above, len(above)))})",
             f"{good_below}/{len(below)} ({_pct(_rate(good_below, len(below)))})")
        )
    lines += [*_table(("High cut-off", "High band correct", "Medium band correct"), high_rows), ""]

    lines += [
        "## Answer cut-off sweep",
        "",
        "Re-runs the Knowledge agent with each candidate answer cut-off. Lower cut-offs answer more cases but risk unsupported answers.",
        "",
    ]
    sweep_rows = []
    for row in run.sweep:
        marker = " (current)" if math.isclose(row["cutoff"], PROVISIONAL_BAND_THRESHOLDS["medium"]) else ""
        sweep_rows.append(
            (
                f"{row['cutoff']:.2f}{marker}",
                row["answered"],
                _pct(row["answer_accuracy"]),
                _pct(row["answer_coverage"]),
                row["wrong_answers"],
                row["unsupported_answers"],
                _pct(row["abstention_recall"]),
            )
        )
    lines += [
        *_table(
            ("Cut-off", "Answered", "Accuracy", "Coverage", "Wrong", "Unsupported", "Abstention recall"),
            sweep_rows,
        ),
        "",
    ]

    lines += ["## Outcomes by case kind", ""]
    kind_rows = []
    for kind in CaseKind.__args__:
        members = [r for r in results if r.case.kind == kind]
        if not members:
            continue
        counts = Counter(r.outcome for r in members)
        kind_rows.append(
            (kind, len(members), counts["correct_answer"], counts["wrong_answer"], counts["unsupported_answer"],
             counts["false_abstention"], counts["correct_abstention"])
        )
    lines += [
        *_table(("Kind", "Cases", "Correct answer", "Wrong", "Unsupported", "False abstention", "Correct abstention"), kind_rows),
        "",
    ]

    lines += ["## Errors to review", ""]
    errors = [r for r in results if r.outcome in ("wrong_answer", "unsupported_answer", "false_abstention")]
    if not errors:
        lines += ["None.", ""]
    else:
        error_rows = []
        for r in errors:
            top = r.passages[0] if r.passages else "-"
            relevance = "-" if r.top_relevance is None else f"{r.top_relevance:.2f}"
            detail = ", ".join(r.reason_codes) or r.band.value
            error_rows.append(
                (f"`{r.case.case_id}`", r.outcome, r.case.kind, r.case.summary.replace("|", "/"), top, relevance, detail)
            )
        lines += [
            *_table(
                ("Case", "Outcome", "Kind", "Summary", "Top source", "Relevance", "Band / reasons"),
                error_rows,
                align="lllllrl",
            ),
            "",
        ]

    lines += [
        "## Latency and cost",
        "",
        "- The three lane agents are deterministic and make no model or network calls: 0 model calls and $0 provider cost per case.",
        "- Wall-clock duration per agent depends on the machine, so this report does not store it; the report must match a fresh run exactly.",
        "- The CLI prints the median, p95, and maximum duration per agent. `--timing PATH` also writes them to a JSON file.",
        "",
        "## Limits",
        "",
        f"- {len(results)} synthetic cases written by one author; intervals are wide and the set is not representative of real tickets.",
        "- Labels judge only the rank-1 Knowledge source; they do not judge Troubleshooting step quality.",
        "- Recall@k uses the same draft labels and measures lexical ranking only; it is not a comparison with another retrieval method (N-01).",
        "- Do not adjust thresholds or retrieval against this set. A change needs a new held-out set version to re-measure.",
        "",
    ]
    return "\n".join(lines)


def _hits(entry: dict, total: int) -> str:
    return f"{_pct(entry['rate'])} ({entry['hits']}/{total})"


def _retrieval_section(results: Sequence[CaseResult]) -> list[str]:
    metrics = retrieval_metrics(results)
    total = metrics["answerable_cases"]
    recall_rows = [
        (k, _hits(metrics["ranking_recall_at_k"][k], total), _hits(metrics["returned_recall_at_k"][k], total))
        for k in map(str, RECALL_KS)
    ]
    exclusion_rows = [
        (f"`{reason}`", counts["excluded_sections"], counts["cases"])
        for reason, counts in metrics["excluded_sources_by_reason"].items()
    ]
    return [
        "## Retrieval recall@k",
        "",
        f"Answerable cases only ({total}). A hit means an acceptable section is within the first k.",
        "",
        "- **Ranking:** approved, current sections in lexical-index order, before the answer cut-off, the minimum matched-term rule, and the product-area preference. This isolates ranking quality from the abstention gates.",
        f"- **Returned:** passages the agent returned to staff after every gate. The agent returns at most {MAX_PASSAGES} passages, so returned recall stops growing after k = {MAX_PASSAGES}.",
        "",
        *_table(("k", "Ranking recall@k", "Returned recall@k"), recall_rows),
        "",
        f"Answerable cases whose acceptable sections match no query term: {metrics['answerable_not_ranked']}.",
        "",
        "## Source freshness and exclusions",
        "",
        f"Sources the agent excluded across all {len(results)} cases. Only candidates that passed the answer cut-off are checked for eligibility, and only selected passages are scanned for injected instructions. Excluded sources are never returned as guidance.",
        "",
        *_table(("Exclusion reason", "Excluded sections", "Cases"), exclusion_rows, align="lrr"),
        "",
        f"- Abstained because only stale or not-yet-effective sources matched (`stale_source_only`): {metrics['abstained_stale_source_only']} cases.",
        f"- Abstained because only draft or retired sources matched (`unapproved_source_only`): {metrics['abstained_unapproved_source_only']} cases.",
        f"- Passages returned to staff from a stale, not-yet-effective, draft, or retired source: {metrics['ineligible_passages_returned']}.",
        "",
    ]


def results_json(run: CalibrationRun) -> str:
    payload = {
        "set_id": run.calibration.set_id,
        "set_version": run.calibration.version,
        "set_fingerprint": run.fingerprint,
        "label_status": run.calibration.label_status,
        "source_set_version": run.source_set_version,
        "policy": run.policy_label,
        "knowledge_agent_version": KNOWLEDGE_AGENT_VERSION,
        "as_of": run.calibration.as_of.isoformat(),
        "summary": _summary(Counter(r.outcome for r in run.results)),
        "retrieval": retrieval_metrics(run.results),
        "critical_errors": [{"case_id": c, "error": e} for c, e in run.critical_errors],
        "label_problems": run.label_problems,
        "sweep": run.sweep,
        "cases": [r.as_json() for r in run.results],
    }
    return json.dumps(payload, indent=2) + "\n"


def timing_json(run: CalibrationRun) -> str:
    """Per-agent durations for one run on this machine. Not reproducible, so not committed evidence."""
    payload = {
        "measured_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "set_id": run.calibration.set_id,
        "set_version": run.calibration.version,
        "cases": len(run.results),
        "python": platform.python_version(),
        "system": f"{platform.system()} {platform.machine()}",
        "model_calls": 0,
        "provider_cost_usd": 0.0,
        "durations_ms": run.durations,
    }
    return json.dumps(payload, indent=2) + "\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text if text.endswith("\n") else text + "\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure Knowledge confidence calibration on a held-out synthetic set.")
    parser.add_argument("calibration_set", type=Path)
    parser.add_argument("--knowledge-dir", type=Path, default=None)
    parser.add_argument("--policy", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None, help="Write the Markdown report here")
    parser.add_argument("--results", type=Path, default=None, help="Write per-case JSON results here")
    parser.add_argument(
        "--timing", type=Path, default=None, help="Write machine-dependent per-agent durations (JSON) here"
    )
    args = parser.parse_args(argv)

    calibration = load_calibration_set(args.calibration_set)
    run = run_calibration(
        calibration,
        load_corpus(args.knowledge_dir),
        load_policy(args.policy),
        fingerprint=set_fingerprint(args.calibration_set),
    )
    if args.report:
        _write(args.report, render_report(run))
    if args.results:
        _write(args.results, results_json(run))
    if args.timing:
        _write(args.timing, timing_json(run))

    summary = _summary(Counter(r.outcome for r in run.results))
    recall = retrieval_metrics(run.results)["ranking_recall_at_k"]
    print(
        f"{len(run.results)} cases | answered {summary['answered']} | accuracy {_pct(summary['answer_accuracy'])} | "
        f"coverage {_pct(summary['answer_coverage'])} | abstention recall {_pct(summary['abstention_recall'])} | "
        f"ranking recall@3 {_pct(recall['3']['rate'])} | "
        f"critical errors {len(run.critical_errors)} | label problems {len(run.label_problems)}"
    )
    print(format_durations(run.durations))
    return 1 if run.critical_errors or run.label_problems else 0


if __name__ == "__main__":
    sys.exit(main())
