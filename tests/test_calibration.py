"""Knowledge calibration set and runner (D-08 evidence): label integrity, safety gate, determinism."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cdit_support_mao.agents.knowledge import KnowledgeAgent
from cdit_support_mao.agents.knowledge.agent import MAX_PASSAGES
from cdit_support_mao.agents.knowledge.retrieval import LexicalIndex
from cdit_support_mao.contracts import AgentStatus, ConfidenceBand
from cdit_support_mao.lane_calibration import (
    RECALL_KS,
    SWEEP_CUTOFFS,
    CalibrationRun,
    SafetyChecker,
    classify,
    load_calibration_set,
    main,
    ranking_rank,
    render_report,
    results_json,
    retrieval_metrics,
    returned_rank,
    run_calibration,
    set_fingerprint,
    to_lane_case,
    wilson,
)
from cdit_support_mao.lane_harness import check_expectations

from conftest import KNOWLEDGE_DIR, NOW, POLICY_PATH, REPO_ROOT

SET_PATH = REPO_ROOT / "synthetic_data" / "calibration" / "knowledge-calibration-v1.json"
REPORT_PATH = REPO_ROOT / "docs" / "lanes" / "shawn" / "calibration" / "KNOWLEDGE-CALIBRATION-REPORT.md"
RESULTS_PATH = REPO_ROOT / "docs" / "lanes" / "shawn" / "calibration" / "knowledge-calibration-v1.results.json"


@pytest.fixture(scope="module")
def calibration():
    return load_calibration_set(SET_PATH)


@pytest.fixture(scope="module")
def calibration_run(calibration, corpus, policy) -> CalibrationRun:
    return run_calibration(calibration, corpus, policy, fingerprint=set_fingerprint(SET_PATH))


def test_set_is_large_synthetic_and_covers_every_kind(calibration) -> None:
    assert calibration.data_classification == "synthetic"
    assert len(calibration.cases) >= 100
    expects = {case.expect for case in calibration.cases}
    assert expects == {"answer", "abstain"}
    kinds = {case.kind for case in calibration.cases}
    assert {"direct", "paraphrase", "no_coverage", "near_miss", "ineligible_only", "conflict", "injection"} <= kinds
    assert all(case.case_id.startswith("SYN-KCAL-") for case in calibration.cases)


def test_labels_point_at_approved_current_sections(calibration_run) -> None:
    assert calibration_run.label_problems == []


def test_safety_gate_has_no_critical_errors(calibration_run) -> None:
    # AGENTS.md: any critical hallucination or false verification label blocks progression.
    assert calibration_run.critical_errors == []


def test_every_case_ran_through_all_three_agents(calibration_run) -> None:
    for result in calibration_run.results:
        assert result.troubleshooting_status in set(AgentStatus)
        assert result.documentation_status in set(AgentStatus)
        if result.status is not AgentStatus.COMPLETED:
            assert result.troubleshooting_status is not AgentStatus.COMPLETED


def test_sweep_answers_fewer_cases_as_the_cutoff_rises(calibration_run) -> None:
    answered = [row["answered"] for row in calibration_run.sweep]
    assert [row["cutoff"] for row in calibration_run.sweep] == list(SWEEP_CUTOFFS)
    assert answered == sorted(answered, reverse=True)


def test_committed_report_and_results_are_current(calibration_run) -> None:
    """The committed evidence must match a fresh run (re-run the CLI after any corpus or agent change)."""
    assert REPORT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n") == render_report(calibration_run)
    assert RESULTS_PATH.read_text(encoding="utf-8").replace("\r\n", "\n") == results_json(calibration_run)


def test_cli_writes_report_and_exits_zero(tmp_path: Path, capsys) -> None:
    report, results, timing = tmp_path / "report.md", tmp_path / "results.json", tmp_path / "timing.json"
    code = main(
        [
            str(SET_PATH),
            "--knowledge-dir", str(KNOWLEDGE_DIR),
            "--policy", str(POLICY_PATH),
            "--report", str(report),
            "--results", str(results),
            "--timing", str(timing),
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "critical errors 0" in out
    assert "ranking recall@3" in out
    assert "Per-agent duration in ms" in out
    assert report.read_text(encoding="utf-8").startswith("# Knowledge Agent Calibration Report")
    assert len(json.loads(results.read_text(encoding="utf-8"))["cases"]) >= 100
    measured = json.loads(timing.read_text(encoding="utf-8"))
    assert measured["model_calls"] == 0 and measured["provider_cost_usd"] == 0.0
    assert set(measured["durations_ms"]) == {"knowledge", "troubleshooting", "documentation", "lane_total"}


# --- N-02: retrieval recall@k, exclusions, and durations -------------------------------------------


def test_recall_at_k_is_consistent_with_outcomes(calibration_run) -> None:
    metrics = retrieval_metrics(calibration_run.results)
    answerable = [r for r in calibration_run.results if r.case.expect == "answer"]
    assert metrics["answerable_cases"] == len(answerable)
    for key in ("ranking_recall_at_k", "returned_recall_at_k"):
        hits = [metrics[key][str(k)]["hits"] for k in RECALL_KS]
        assert hits == sorted(hits), f"{key} must not fall as k grows"
    # Returned recall@1 is exactly the correct-answer count, and @3 is "correct anywhere in top 3".
    returned = metrics["returned_recall_at_k"]
    assert returned["1"]["hits"] == sum(r.outcome == "correct_answer" for r in answerable)
    assert returned["3"]["hits"] == sum(bool(r.correct_any) for r in answerable if r.answered)
    assert returned[str(RECALL_KS[-1])]["hits"] == returned[str(MAX_PASSAGES)]["hits"]
    assert metrics["answerable_not_ranked"] == sum(r.ranking_rank is None for r in answerable)


def test_exclusion_counts_match_case_results(calibration_run) -> None:
    metrics = retrieval_metrics(calibration_run.results)
    total = sum(entry["excluded_sections"] for entry in metrics["excluded_sources_by_reason"].values())
    assert total == sum(len(r.excluded_reasons) for r in calibration_run.results)
    assert metrics["ineligible_passages_returned"] == 0
    for entry in metrics["excluded_sources_by_reason"].values():
        assert entry["cases"] <= entry["excluded_sections"]


def test_ranking_and_returned_rank_definitions(harness, calibration, corpus) -> None:
    index = LexicalIndex(corpus)
    eligible = {(a.doc_id, a.version) for a in corpus.eligible_articles(calibration.as_of)}
    case, run = _run_case(harness, calibration, "SYN-KCAL-0001")
    assert ranking_rank(case, index, eligible) == 1
    assert returned_rank(case, run.knowledge) == 1

    off_topic = case.model_copy(update={"summary": "zzqx vbnm"})
    assert ranking_rank(off_topic, index, eligible) is None

    abstain = case.model_copy(update={"expect": "abstain", "acceptable_sources": ()})
    assert ranking_rank(abstain, index, eligible) is None
    assert returned_rank(abstain, run.knowledge) is None

    _, conflict_run = _run_case(harness, calibration, "SYN-KCAL-0105")
    assert conflict_run.knowledge.status is AgentStatus.ABSTAINED
    assert returned_rank(case, conflict_run.knowledge) is None


def test_durations_stay_out_of_committed_evidence(calibration_run) -> None:
    assert set(calibration_run.durations) == {"knowledge", "troubleshooting", "documentation", "lane_total"}
    assert calibration_run.durations["lane_total"]["cases"] == len(calibration_run.results)
    for text in (render_report(calibration_run), results_json(calibration_run)):
        assert "median_ms" not in text and "durations_ms" not in text


def _run_case(harness, calibration, case_id: str):
    case = next(c for c in calibration.cases if c.case_id == case_id)
    return case, harness.run(to_lane_case(case, calibration.as_of), now=NOW)


def test_classify_covers_each_outcome(harness, calibration) -> None:
    answer_case, run = _run_case(harness, calibration, "SYN-KCAL-0001")
    assert run.knowledge.status is AgentStatus.COMPLETED
    assert classify(answer_case, run.knowledge) == ("correct_answer", True)

    wrong = answer_case.model_copy(update={"acceptable_sources": ("KB-PRN-270#s1",)})
    assert classify(wrong, run.knowledge)[0] == "wrong_answer"

    abstain = answer_case.model_copy(update={"expect": "abstain", "acceptable_sources": ()})
    assert classify(abstain, run.knowledge)[0] == "unsupported_answer"

    conflict_case, conflict_run = _run_case(harness, calibration, "SYN-KCAL-0105")
    assert conflict_run.knowledge.status is AgentStatus.ABSTAINED
    assert classify(conflict_case, conflict_run.knowledge)[0] == "correct_abstention"
    as_answer = conflict_case.model_copy(update={"expect": "answer", "acceptable_sources": ("KB-UPL-031#s1",)})
    assert classify(as_answer, conflict_run.knowledge)[0] == "false_abstention"


def test_safety_checker_flags_tampered_output(harness, calibration, corpus, policy) -> None:
    checker = SafetyChecker(corpus, policy, calibration.as_of)
    _, run = _run_case(harness, calibration, "SYN-KCAL-0001")
    assert checker.check(run) == ()

    passage = run.knowledge.passages[0]
    altered_text = passage.model_copy(update={"text": passage.text + " Also open Admin."})
    tampered = run.knowledge.model_copy(update={"passages": (altered_text, *run.knowledge.passages[1:])})
    assert any("not verbatim" in e for e in checker.check(_replace(run, knowledge=tampered)))

    unknown = passage.model_copy(update={"version": "9.9"})
    tampered = run.knowledge.model_copy(update={"passages": (unknown,)})
    assert any("unknown source" in e for e in checker.check(_replace(run, knowledge=tampered)))

    step = run.troubleshooting.steps[0]
    invented = step.model_copy(update={"text": "Ask the user to email the admin team."})
    tampered = run.troubleshooting.model_copy(update={"steps": (invented,)})
    assert any("not quoted" in e for e in checker.check(_replace(run, troubleshooting=tampered)))

    inflated = run.troubleshooting.model_copy(update={"confidence": ConfidenceBand.HIGH})
    low_knowledge = run.knowledge.model_copy(update={"confidence": ConfidenceBand.LOW})
    errors = checker.check(_replace(run, knowledge=low_knowledge, troubleshooting=inflated))
    assert any("exceeds knowledge confidence" in e for e in errors)


def test_safety_checker_flags_leaked_injected_text(harness, calibration, corpus, policy) -> None:
    checker = SafetyChecker(corpus, policy, calibration.as_of)
    _, run = _run_case(harness, calibration, "SYN-KCAL-0001")
    injected = next(a for a in corpus.articles if a.doc_id == "KB-KBD-370").sections[0].text
    leaked = run.knowledge.model_copy(update={"unknowns": (injected,)})
    assert any("unsafe or ineligible" in e for e in checker.check(_replace(run, knowledge=leaked)))


def test_wilson_interval_brackets_the_rate() -> None:
    low, high = wilson(29, 29)
    assert 0.85 < low < 1.0 and high == 1.0
    low, high = wilson(5, 10)
    assert low < 0.5 < high
    assert wilson(0, 0) is None


def test_min_relevance_override_is_explicit(corpus, context, make_triage) -> None:
    triage = make_triage("Site user cannot find where to export the site enrollment report.", product_area="reports")
    default = KnowledgeAgent(corpus).run(context, triage, acknowledged={triage.contribution_id}, as_of=NOW.date(), now=NOW)
    same = KnowledgeAgent(corpus, min_relevance=0.60).run(
        context, triage, acknowledged={triage.contribution_id}, as_of=NOW.date(), now=NOW
    )
    swept = KnowledgeAgent(corpus, min_relevance=0.45).run(
        context, triage, acknowledged={triage.contribution_id}, as_of=NOW.date(), now=NOW
    )
    assert default.contribution_id == same.contribution_id
    assert swept.contribution_id != default.contribution_id
    with pytest.raises(ValueError):
        KnowledgeAgent(corpus, min_relevance=0)


def test_lane_case_without_expected_outcome_is_reported(harness, calibration) -> None:
    _, run = _run_case(harness, calibration, "SYN-KCAL-0001")
    assert run.case.expected is None
    assert check_expectations(run) == ["case declares no expected outcome"]


def _replace(run, **changes):
    from dataclasses import replace

    return replace(run, **changes)


# --- SYN-KCAL v2: held-out measurement set for L-1 and L-2 (baseline recorded 2026-11-09) ---

V2_SET_PATH = REPO_ROOT / "synthetic_data" / "calibration" / "knowledge-calibration-v2.json"
V2_REPORT_PATH = REPO_ROOT / "docs" / "lanes" / "shawn" / "calibration" / "KNOWLEDGE-CALIBRATION-REPORT-v2.md"
V2_RESULTS_PATH = REPO_ROOT / "docs" / "lanes" / "shawn" / "calibration" / "knowledge-calibration-v2.results.json"
V2_KINDS = {"short_query", "padded_query", "numeric_detail", "stale_shadow"}


@pytest.fixture(scope="module")
def calibration_v2():
    return load_calibration_set(V2_SET_PATH)


@pytest.fixture(scope="module")
def calibration_v2_run(calibration_v2, corpus, policy) -> CalibrationRun:
    return run_calibration(calibration_v2, corpus, policy, fingerprint=set_fingerprint(V2_SET_PATH))


def test_v2_targets_the_item_path_and_does_not_reuse_v1(calibration, calibration_v2) -> None:
    assert (calibration_v2.version, str(calibration_v2.as_of)) == ("2.0", "2026-11-10")
    assert V2_KINDS <= {case.kind for case in calibration_v2.cases}
    # Linked items reach Knowledge without a product area, so v2 never sets one.
    assert all(case.product_area is None for case in calibration_v2.cases)
    assert not {c.case_id for c in calibration_v2.cases} & {c.case_id for c in calibration.cases}
    norm = lambda text: " ".join(text.lower().split())  # noqa: E731
    assert not {norm(c.summary) for c in calibration_v2.cases} & {norm(c.summary) for c in calibration.cases}


def test_v2_labels_and_safety_gate(calibration_v2_run) -> None:
    assert calibration_v2_run.label_problems == []
    assert calibration_v2_run.critical_errors == []


def test_v2_committed_baseline_is_current(calibration_v2_run) -> None:
    """Re-run the CLI on v2 after any corpus, policy, or agent change, as for v1."""
    assert V2_REPORT_PATH.read_text(encoding="utf-8").replace("\r\n", "\n") == render_report(calibration_v2_run)
    assert V2_RESULTS_PATH.read_text(encoding="utf-8").replace("\r\n", "\n") == results_json(calibration_v2_run)
