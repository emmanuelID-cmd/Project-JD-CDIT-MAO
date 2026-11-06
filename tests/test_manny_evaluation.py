"""Tests for Manny Lane preliminary synthetic evaluation evidence."""
import cdit_support_mao.manny_evaluation as evaluation
from cdit_support_mao.manny_evaluation import (
    generate_markdown_report,
    run_coordinator_evaluation,
    run_end_to_end_evaluation,
    run_escalation_evaluation,
    run_triage_evaluation,
)


def test_coordinator_component_fixtures_pass():
    result = run_coordinator_evaluation()
    assert result["passed"] is True
    assert result["passed_count"] == result["total"]
    assert result["injection_contained"] is True


def test_in_progress_benchmark_fixtures_pass():
    result = run_triage_evaluation()
    assert result["passed"] is True
    assert result["passed_count"] == result["total"]


def test_escalation_component_fixtures_pass():
    result = run_escalation_evaluation()
    assert result["passed"] is True
    assert result["passed_count"] == result["total"]


def test_downstream_fixture_evidence_is_not_phase_acceptance():
    result = run_end_to_end_evaluation()
    assert result["fixture_assertions_passed"] is True
    assert result["status"] == "preliminary_fixture_evidence"
    assert result["phase_exit_ready"] is False
    assert result["scoring_status"] == "not_scored"
    assert result["integration_status"] == "not_ready"
    assert result["integrated_workflow_exercised"] is False
    assert result["cases_evaluated"] == 12
    assert result["fixture_expected_cases_checked"] == 12
    assert result["fixture_expected_cases_passed"] == 12
    assert all(case["fixture_expected_output_status"] == "pass" for case in result["cases"])
    assert result["labeled_cases_evaluated"] == 0
    assert result["labeled_case_target"] == 100

    gates = result["safety_gates"]
    assert gates["must_escalate_fixture_cases"]["checks"] == 4
    assert gates["injection_fixture_case"]["checks"] == 1
    assert gates["uncertainty_fixture_cases"]["checks"] == 3
    assert gates["unauthorized_dispatch"]["status"] == "not_tested"
    assert gates["unauthorized_dispatch"]["violations"] is None


def test_report_does_not_claim_integrated_or_prd_wide_pass():
    coordinator = run_coordinator_evaluation()
    benchmarks = run_triage_evaluation()
    escalation = run_escalation_evaluation()
    downstream = run_end_to_end_evaluation()
    report = generate_markdown_report(
        "2026-11-05T12:00:00+00:00", coordinator, benchmarks, escalation, downstream
    )
    assert "PRELIMINARY FIXTURE EVIDENCE ONLY" in report
    assert "NOT SCORED" in report
    assert "Declared fixture expected-output assertions (not approved gold labels)" in report
    assert "Fixture expected output" in report
    assert "Coordinator-to-semantic-Triage path" in report
    assert "Actual external dispatch/write behavior" in report
    assert "Overall Evaluation Status: PASSED" not in report
    assert "Integration with Shawn lane verified" not in report

def test_end_to_end_fixture_expected_output_mismatch_fails_the_fixture_gate(monkeypatch):
    monkeypatch.setattr(evaluation, "check_expectations", lambda run: ["synthetic mismatch"])

    result = evaluation.run_end_to_end_evaluation()

    gate = result["safety_gates"]["declared_case_expected_outputs"]
    assert gate["checks"] == 12
    assert gate["violations"] == 12
    assert gate["status"] == "fail"
    assert result["fixture_assertions_passed"] is False
    assert result["cases"][0]["fixture_expected_output_mismatches"] == ["synthetic mismatch"]
