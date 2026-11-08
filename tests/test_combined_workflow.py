"""Integration tests for the Combined Six-Agent Workflow Harness (Shared Lane)."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import pytest

from cdit_support_mao.combined_harness import (
    AuditorDispositionFixture,
    CombinedWorkflowHarness,
    load_case,
)
from cdit_support_mao.contracts import AgentStatus, ClaimLabel
from conftest import CASES_DIR, NOW
from test_manny_connected_harness import FakeClient, make_harness


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


def _manny_connected_fixture(combined, message: str):
    triage_harness, request, token = make_harness(message, knowledge_agent=combined.knowledge_agent)
    connected = combined.run_manny_connected(
        triage_harness._triage_harness,
        request,
        session_token=token,
        as_of=date(2026, 11, 6),
        client=FakeClient(),
        billable_call_authorized=True,
        now=NOW,
    )
    return triage_harness, connected


def test_combined_manny_connected_resumes_only_after_synthetic_auditor_decision(corpus, policy) -> None:
    combined = CombinedWorkflowHarness(corpus, policy)
    triage_harness, connected = _manny_connected_fixture(
        combined, "I cannot find the report export control"
    )
    pending = connected.items[0]
    original = pending.dispatch.handoff
    assert connected.status == "awaiting_auditor_review"
    assert original is not None and original.item_scope is not None
    assert original.urgency == "unknown"
    assert original.item_scope.auditor_review == "pending"
    assert pending.knowledge is not None

    resumed = combined.continue_after_auditor(
        connected,
        triage_harness._triage_harness,
        (
            AuditorDispositionFixture(
                item_id=pending.dispatch.item_id,
                reviewer_id="SYN-AUDITOR-001",
                urgency="high",
                decided_at=NOW,
            ),
        ),
        as_of=date(2026, 11, 6),
        now=NOW,
    )

    assert resumed.status == "ready_for_human_review"
    assert resumed.human_review_required is True and resumed.parent_complete is False
    assert (resumed.ticket_writes, resumed.external_dispatches, resumed.customer_notifications) == (0, 0, 0)
    item = resumed.items[0]
    assert item.state == "ready_for_human_review"
    assert item.auditor_event is not None
    assert item.auditor_event.actor_id == "SYN-AUDITOR-001"
    assert item.auditor_event.decision == "band_and_route_determined"
    assert item.auditor_event.category == original.category
    assert item.auditor_event.source_digest == original.content_digest()
    assert item.triage is not None and item.triage.item_scope is not None
    assert item.triage.item_scope.identity == original.item_scope.identity
    assert item.triage.item_scope.auditor_review == "band_and_route_determined"
    assert item.triage.urgency == "high"
    assert item.triage.item_scope.category_sources == original.item_scope.category_sources
    assert item.triage.item_scope.attention_check == original.item_scope.attention_check
    assert item.triage.input_refs[0].content_digest == original.content_digest()
    assert item.knowledge is not None and item.knowledge.status is AgentStatus.COMPLETED
    assert item.knowledge.item_scope_ref == item.triage.item_scope.identity
    assert item.knowledge.input_refs[0].content_digest == item.triage.content_digest()
    assert item.troubleshooting is not None and item.troubleshooting.status is AgentStatus.COMPLETED
    assert item.escalation is not None and item.escalation.status is AgentStatus.COMPLETED
    assert item.escalation.must_escalate is True
    assert "high_urgency_p1" in item.escalation.triggers
    assert item.triage.as_input_ref() in item.escalation.input_refs
    assert item.knowledge.as_input_ref() in item.escalation.input_refs
    assert item.troubleshooting.as_input_ref() in item.escalation.input_refs
    assert item.documentation is not None and item.documentation.status is AgentStatus.COMPLETED
    for contribution in (item.triage, item.knowledge, item.troubleshooting, item.escalation, item.documentation):
        assert contribution.context == connected.upstream.intake.context
        assert contribution.human_review_required is True


def test_combined_manny_connected_keeps_undecided_items_at_auditor(corpus, policy) -> None:
    combined = CombinedWorkflowHarness(corpus, policy)
    triage_harness, connected = _manny_connected_fixture(
        combined, "I cannot find the report export control; I cannot access MFA"
    )
    assert len(connected.items) == 2
    first_id, second_id = (item.dispatch.item_id for item in connected.items)

    resumed = combined.continue_after_auditor(
        connected,
        triage_harness._triage_harness,
        (
            AuditorDispositionFixture(
                item_id=first_id,
                reviewer_id="SYN-AUDITOR-002",
                urgency="medium",
                decided_at=NOW,
            ),
        ),
        as_of=date(2026, 11, 6),
        now=NOW,
    )

    assert resumed.status == "awaiting_auditor_review"
    assert resumed.items[0].item_id == first_id
    assert resumed.items[0].state in {"ready_for_human_review", "knowledge_abstained_or_blocked"}
    assert resumed.items[1].item_id == second_id
    assert resumed.items[1].state == "awaiting_auditor_review"
    assert resumed.items[1].triage is not None
    assert resumed.items[1].triage.urgency == "unknown"
    assert resumed.items[1].triage.item_scope.auditor_review == "pending"
    assert resumed.items[1].troubleshooting is None
    assert resumed.items[1].escalation is None
    assert resumed.items[1].documentation is None


def test_combined_manny_connected_unknown_category_cannot_be_released_by_fixture(corpus, policy) -> None:
    combined = CombinedWorkflowHarness(corpus, policy)
    triage_harness, connected = _manny_connected_fixture(
        combined, "I have an unfamiliar internal question"
    )
    assert connected.items[0].dispatch.handoff is None

    with pytest.raises(ValueError, match="cannot_release_item_without_eligible_triage_handoff"):
        combined.continue_after_auditor(
            connected,
            triage_harness._triage_harness,
            (
                AuditorDispositionFixture(
                    item_id=connected.items[0].dispatch.item_id,
                    reviewer_id="SYN-AUDITOR-003",
                    urgency="high",
                    decided_at=NOW,
                ),
            ),
            as_of=date(2026, 11, 6),
            now=NOW,
        )


def test_combined_manny_connected_discards_audited_result_when_source_stales(corpus, policy) -> None:
    combined = CombinedWorkflowHarness(corpus, policy)
    triage_harness, connected = _manny_connected_fixture(
        combined, "I cannot find the report export control"
    )
    triage_harness._triage_harness.source_is_current = lambda _run, now=None: False

    resumed = combined.continue_after_auditor(
        connected,
        triage_harness._triage_harness,
        (
            AuditorDispositionFixture(
                item_id=connected.items[0].dispatch.item_id,
                reviewer_id="SYN-AUDITOR-004",
                urgency="low",
                decided_at=NOW,
            ),
        ),
        as_of=date(2026, 11, 6),
        now=NOW,
    )

    assert resumed.status == "source_stale"
    assert resumed.items[0].state == "discarded_stale_result"
    assert resumed.items[0].triage is None
    assert resumed.items[0].knowledge is None
    assert resumed.items[0].troubleshooting is None
    assert resumed.items[0].escalation is None
    assert resumed.items[0].documentation is None


def test_auditor_disposition_fixture_rejects_non_synthetic_or_naive_identity() -> None:
    with pytest.raises(ValueError, match="synthetic_reviewer_id"):
        AuditorDispositionFixture("ITM-0123456789ABCDEF", "AUDITOR-REAL", "low", NOW)
    with pytest.raises(ValueError, match="timezone_aware"):
        AuditorDispositionFixture(
            "ITM-0123456789ABCDEF", "SYN-AUDITOR-005", "low", datetime(2026, 11, 6)
        )
