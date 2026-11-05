"""Integration tests for the Combined Six-Agent Workflow Harness (Shared Lane)."""
from __future__ import annotations

from pathlib import Path
import pytest

from cdit_support_mao.combined_harness import CombinedWorkflowHarness, load_case
from cdit_support_mao.contracts import AgentStatus, ClaimLabel
from conftest import CASES_DIR, NOW


def test_combined_six_agent_workflow_executes_all_cases(corpus, policy) -> None:
    harness = CombinedWorkflowHarness(corpus, policy)
    case_paths = sorted(CASES_DIR.glob("*.json"))
    assert len(case_paths) == 12

    for path in case_paths:
        run = harness.run(load_case(path), now=NOW)
        # All contributions are tagged to the exact run context
        for contrib in (run.triage, run.knowledge, run.troubleshooting, run.escalation, run.documentation):
            assert contrib.context == run.context
            assert contrib.human_review_required is True

        # Invariant: Every verified claim has a source
        for contrib in (run.knowledge, run.troubleshooting, run.escalation, run.documentation):
            for claim in contrib.claims:
                if claim.label is ClaimLabel.VERIFIED:
                    assert claim.sources


def test_combined_workflow_golden_case_generates_complete_draft(corpus, policy) -> None:
    harness = CombinedWorkflowHarness(corpus, policy)
    case = load_case(CASES_DIR / "case-01-golden-report-export.json")
    run = harness.run(case, now=NOW)

    assert run.knowledge.status is AgentStatus.COMPLETED
    assert run.troubleshooting.status is AgentStatus.COMPLETED
    assert run.escalation.status is AgentStatus.COMPLETED
    assert run.escalation.must_escalate is False
    assert run.escalation.recommendation == "no_escalation_proposed"
    assert run.documentation.status is AgentStatus.COMPLETED
    assert run.documentation.draft is not None
    assert "no ticket state changed" in run.documentation.draft.rendered_text


def test_combined_workflow_privacy_incident_escalates_and_documents(corpus, policy) -> None:
    harness = CombinedWorkflowHarness(corpus, policy)
    case = load_case(CASES_DIR / "case-11-cross-site-data-exposure.json")
    run = harness.run(case, now=NOW)

    assert run.escalation.must_escalate is True
    assert run.escalation.recommendation == "escalate_support_lead"
    assert "possible_privacy_incident" in run.escalation.triggers
    assert run.documentation.status is AgentStatus.COMPLETED


def test_combined_workflow_blocked_triage_halts_downstream(corpus, policy) -> None:
    harness = CombinedWorkflowHarness(corpus, policy)
    case = load_case(CASES_DIR / "case-12-triage-blocked-upstream.json")
    run = harness.run(case, now=NOW)

    assert run.triage.status is AgentStatus.BLOCKED
    assert run.knowledge.status is AgentStatus.BLOCKED
    assert run.troubleshooting.status is AgentStatus.BLOCKED
    assert run.documentation.status is AgentStatus.BLOCKED
