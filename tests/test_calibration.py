"""Knowledge calibration set and runner (D-08 evidence): label integrity, safety gate, determinism."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cdit_support_mao.agents.knowledge import KnowledgeAgent
from cdit_support_mao.contracts import AgentStatus, ConfidenceBand
from cdit_support_mao.lane_calibration import (
    SWEEP_CUTOFFS,
    CalibrationRun,
    SafetyChecker,
    classify,
    load_calibration_set,
    main,
    render_report,
    results_json,
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
    report, results = tmp_path / "report.md", tmp_path / "results.json"
    code = main(
        [
            str(SET_PATH),
            "--knowledge-dir", str(KNOWLEDGE_DIR),
            "--policy", str(POLICY_PATH),
            "--report", str(report),
            "--results", str(results),
        ]
    )
    assert code == 0
    assert "critical errors 0" in capsys.readouterr().out
    assert report.read_text(encoding="utf-8").startswith("# Knowledge Agent Calibration Report")
    assert len(json.loads(results.read_text(encoding="utf-8"))["cases"]) >= 100


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
