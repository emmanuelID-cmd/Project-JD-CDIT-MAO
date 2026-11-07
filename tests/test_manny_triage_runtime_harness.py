"""End-to-end synthetic checks for Manny's Coordinator-to-Triage A0–A2 path."""
from datetime import UTC, datetime
import json
from pathlib import Path
from types import SimpleNamespace

from cdit_support_mao.agents.coordinator import (
    Coordinator,
    FixtureCaseVersions,
    FixturePolicyVersions,
    FixtureSession,
    FixtureSessionAuthority,
)
from cdit_support_mao.agents.coordinator.handoff import HandoffRegistry, HandoffState
from cdit_support_mao.agents.triage.runtime_harness import MannyA0A2Harness
from cdit_support_mao.agents.triage.attention import FixtureAttentionPatterns


NOW = datetime(2026, 11, 5, 12, tzinfo=UTC)


class FakeMessages:
    def __init__(self, *, category: str | None, quote: str | None):
        self.category = category
        self.quote = quote
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        payload = {
            "items": [{
                "item_index": 1,
                "category": self.category,
                "category_label": "inference" if self.category is not None else "unknown",
                "evidence_quote": self.quote,
                "rationale": "The synthetic request text supports this category proposal." if self.category is not None else None,
                "missing_questions": [] if self.category is not None else ["Which users or workflows are affected?"],
                "urgency": "unknown",
                "urgency_label": "unknown",
                "destination": "unknown",
                "destination_label": "unknown",
                "human_review_required": True,
                "downstream_allowed": False,
            }],
            "human_review_required": True,
            "parent_complete": False,
            "downstream_allowed": False,
            "dispatched": False,
        }
        return SimpleNamespace(
            stop_reason="end_turn",
            content=[SimpleNamespace(type="text", text=json.dumps(payload))],
            model="claude-sonnet-5-5",
            usage=SimpleNamespace(input_tokens=12, output_tokens=20),
        )


class FakeClient:
    def __init__(self, messages: FakeMessages):
        self.messages = messages
        self.options = None

    def with_options(self, **kwargs):
        self.options = kwargs
        return self


def harness_for(message: str, *, fixture_patterns: FixtureAttentionPatterns | None = None):
    owner, sender, receiver = object(), object(), object()
    sessions = FixtureSessionAuthority(provisioning_capability=owner, ttl_seconds=3600)
    token = sessions.issue(
        FixtureSession(
            actor_id="SYN-ACTOR-01",
            role="staff",
            active=True,
            allowed_case_ids=("SYN-CASE-01",),
        ),
        capability=owner,
    )
    versions = FixtureCaseVersions(provisioning_capability=owner)
    versions.set_version("SYN-CASE-01", 1, expected_version=None, capability=owner)
    policies = FixturePolicyVersions(
        provisioning_capability=owner,
        active=frozenset({"SYN-POLICY-1"}),
    )
    coordinator = Coordinator(sessions, case_versions=versions, policy_versions=policies)
    registry = HandoffRegistry(
        sender_capability=sender,
        receiver_capability=receiver,
        timeout_seconds=30,
        actor_sessions=sessions,
        case_versions=versions,
        policy_versions=policies,
    )
    harness = MannyA0A2Harness(
        coordinator,
        registry,
        sender_capability=sender,
        receiver_capability=receiver,
        fixture_patterns=fixture_patterns,
    )
    request = {
        "case_id": "SYN-CASE-01",
        "case_version": 1,
        "policy_version": "SYN-POLICY-1",
        "message": message,
        "data_classification": "synthetic",
    }
    return harness, request, token


def test_manny_a0_a2_harness_composes_intake_and_stops_safely_without_call():
    harness, request, token = harness_for("I cannot access the portal")

    result = harness.run(request, session_token=token, now=NOW)

    assert result.intake.status.value == "ready_for_triage"
    assert result.acknowledged_handoff is not None
    assert result.acknowledged_handoff.state is HandoffState.ACCEPTED
    assert result.triage is not None
    assert result.triage.status == "needs_human_review"
    assert result.triage.reason == "semantic_result_unavailable"
    assert result.triage.urgency == "unknown"
    assert result.triage.human_review_required
    assert not result.triage.downstream_allowed and not result.triage.dispatched
    assert [event.event for event in result.events] == ["handoff_prepared", "handoff_accepted"]


def test_manny_a0_a2_harness_uses_only_injected_fake_client_and_never_forwards():
    phrase = "cannot access"
    harness, request, token = harness_for("I cannot access the portal")
    messages = FakeMessages(category="Work access blocked", quote=phrase)
    client = FakeClient(messages)

    result = harness.run(
        request,
        session_token=token,
        client=client,
        billable_call_authorized=True,
        now=NOW,
    )

    assert result.triage is not None and result.triage.status == "proposal_for_human_review"
    item = result.triage.candidate.items[0]
    assert item.category == "Work access blocked" and item.category_label == "inference"
    assert item.category_evidence_quote == phrase
    assert result.triage.urgency == "unknown" and result.triage.destination == "unknown"
    assert result.triage.human_review_required
    assert not result.triage.downstream_allowed and not result.triage.dispatched
    assert len(messages.calls) == 1
    assert client.options == {"max_retries": 0, "timeout": 60}
    assert [event.event for event in result.events] == ["handoff_prepared", "handoff_accepted"]


def test_manny_a0_a2_harness_does_not_call_injected_client_without_run_authorization():
    harness, request, token = harness_for("I cannot access the portal")
    messages = FakeMessages(category="Work access blocked", quote="cannot access")
    client = FakeClient(messages)

    result = harness.run(request, session_token=token, client=client, now=NOW)

    assert result.triage is not None and result.triage.status == "needs_human_review"
    assert result.triage.reason == "semantic_result_unavailable"
    assert messages.calls == []
    assert result.triage.urgency == "unknown" and not result.triage.downstream_allowed


def test_approved_unknown_high_impact_case_runs_through_a0_a2_contract():
    repo_root = Path(__file__).resolve().parents[1]
    fixture = json.loads((repo_root / "synthetic_data" / "manny_triage_cases" / "unknown-high-impact.json").read_text(encoding="utf-8"))
    owner = object()
    patterns = FixtureAttentionPatterns(provisioning_capability=owner)
    patterns.add("SYN-ATTENTION-001", fixture["attention_fixture_literal"], capability=owner)
    patterns.seal(capability=owner)
    harness, request, token = harness_for(fixture["message"], fixture_patterns=patterns)
    messages = FakeMessages(category=None, quote=None)
    client = FakeClient(messages)

    result = harness.run(
        request,
        session_token=token,
        client=client,
        billable_call_authorized=True,
        now=NOW,
    )

    expected = fixture["expected"]
    assert result.triage is not None
    assert result.triage.status == "proposal_for_human_review"
    assert len(result.triage.candidate.items) == expected["item_count"]
    item = result.triage.candidate.items[0]
    assert item.category is expected["category"]
    assert item.category_label == expected["category_label"]
    assert item.status == expected["item_status"]
    assert result.triage.urgency == expected["urgency"]
    assert result.triage.destination == expected["destination"]
    assert list(item.auditor_review_reasons) == expected["auditor_review_reasons"]
    assert result.triage.attention_signal is not None
    assert result.triage.attention_signal.status == expected["attention_status"]
    assert result.triage.human_review_required == expected["human_review_required"]
    assert result.triage.candidate.parent_complete == expected["parent_complete"]
    assert result.triage.downstream_allowed == expected["downstream_allowed"]
    assert result.triage.dispatched == expected["dispatched"]
    match = result.triage.attention_signal.matches[0]
    assert result.triage.triage_input.reported_message[match.start_codepoint:match.end_codepoint] == fixture["attention_fixture_literal"]
    assert len(messages.calls) == 1
    assert client.options == {"max_retries": 0, "timeout": 60}
