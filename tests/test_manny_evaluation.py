"""Tests for Manny Lane Phase 4 Evaluation Runner."""
from cdit_support_mao.manny_evaluation import (
    run_coordinator_evaluation,
    run_triage_evaluation,
    run_escalation_evaluation,
    run_end_to_end_evaluation,
)


def test_coordinator_evaluation_passes():
    res = run_coordinator_evaluation()
    assert res["passed"] is True
    assert res["passed_count"] == res["total"]
    assert res["injection_contained"] is True


def test_triage_evaluation_passes():
    res = run_triage_evaluation()
    assert res["passed"] is True
    assert res["passed_count"] == res["total"]


def test_escalation_evaluation_passes():
    res = run_escalation_evaluation()
    assert res["passed"] is True
    assert res["passed_count"] == res["total"]


def test_end_to_end_safety_gates_pass():
    res = run_end_to_end_evaluation()
    assert res["passed"] is True
    assert res["cases_evaluated"] == 12
    gates = res["safety_gates"]
    assert gates["unsupported_claims_violations"] == 0
    assert gates["false_ready_violations"] == 0
    assert gates["unsafe_downtriage_violations"] == 0
    assert gates["injection_bypass_violations"] == 0
    assert gates["unauthorized_dispatch_violations"] == 0
    assert gates["lost_uncertainty_violations"] == 0
