"""Synthetic integration checks across Manny's current intake and triage boundary.

These exercise fixture code only: there is no model, human dispatch, external
system, authorized routing decision, or durable state in this local flow.
"""
from datetime import UTC, datetime

import pytest

from cdit_support_mao.agents.coordinator import (
    Coordinator, FixtureCaseVersions, FixturePolicyVersions,
    FixtureSession, FixtureSessionAuthority,
)
from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.auditor import prepare_auditor_review
from cdit_support_mao.agents.triage.multi_item_adapter import prepare_multi_item_candidate
from cdit_support_mao.agents.triage.segment import extract_request_parts
from cdit_support_mao.agents.triage.semantic_pipeline import (
    TriageSemanticPreparationError,
    prepare_semantic_request,
)

NOW = datetime(2026, 11, 4, 12, tzinfo=UTC)


def start(message):
    owner, sender, receiver = object(), object(), object()
    sessions = FixtureSessionAuthority(provisioning_capability=owner, ttl_seconds=3600)
    versions = FixtureCaseVersions(provisioning_capability=owner)
    versions.set_version("SYN-CASE-01", 1, expected_version=None, capability=owner)
    policy = FixturePolicyVersions(provisioning_capability=owner, active=frozenset({"SYN-POLICY-1"}))
    token = sessions.issue(FixtureSession(actor_id="SYN-ACTOR-1", role="staff", active=True,
        allowed_case_ids=("SYN-CASE-01",)), capability=owner)
    intake = Coordinator(sessions, case_versions=versions, policy_versions=policy).prepare(
        {"case_id": "SYN-CASE-01", "case_version": 1, "policy_version": "SYN-POLICY-1",
         "message": message, "data_classification": "synthetic"}, session_token=token)
    registry = HandoffRegistry(sender_capability=sender, receiver_capability=receiver,
        timeout_seconds=30, actor_sessions=sessions, case_versions=versions, policy_versions=policy)
    handoff = registry.prepare(intake, capability=sender, session_token=token, now=NOW)
    return registry, handoff, intake, sender, receiver, versions, policy, owner


def ack(flow):
    registry, handoff, intake, _, receiver, _, _, _ = flow
    return registry.acknowledge(handoff.handoff_id, expected_version=handoff.state_version,
        capability=receiver, context=intake.context, now=NOW)


def args(flow, checkpoint):
    return dict(handoff_id=checkpoint.handoff_id, expected_version=checkpoint.state_version,
        receiver_capability=flow[4], context=flow[2].context, now=NOW)


def test_multi_request_intake_preserves_items_and_proposes_human_review_only():
    text = "  Need a blank form; I cannot access the portal; my pay is missing.  "
    flow = start(text)
    checkpoint = ack(flow)
    segmented = extract_request_parts(flow[0], **args(flow, checkpoint))
    assert [item.reported_text for item in segmented.items] == [
        "Need a blank form", "I cannot access the portal", "my pay is missing."]
    for item in segmented.items:
        assert text[item.start_codepoint:item.end_codepoint] == item.reported_text
        assert item.source.source_id == flow[2].context.case_id
    review = prepare_auditor_review(flow[0], item_index=2, **args(flow, checkpoint))
    assert review.reported_text == segmented.items[1].reported_text and review.item_count == 3
    assert review.status == "abstained_needs_human" and review.human_review_required
    assert (review.category, review.urgency, review.destination) == ("unknown", "unknown", "unknown")
    assert not review.dispatched and not review.downstream_allowed and not review.parent_complete
    assert [event.event for event in flow[0].events()] == ["handoff_prepared", "handoff_accepted"]
    assert text not in repr(flow[0].events()) and review.reported_text not in repr(flow[0].events())


def test_ambiguous_split_preserves_the_whole_parent_for_review():
    text = 'The customer wrote "need a form; cannot log in'
    flow = start(text)
    checkpoint = ack(flow)
    segmented = extract_request_parts(flow[0], **args(flow, checkpoint))
    review = prepare_auditor_review(flow[0], item_index=1, **args(flow, checkpoint))
    assert segmented.status == "needs_auditor" and len(segmented.items) == 1
    assert review.reported_text == text and review.segmentation_reason == "uncertain_segmentation"
    assert review.start_codepoint == 0 and review.end_codepoint == len(text)
    assert review.status == "abstained_needs_human" and not review.dispatched


def test_scope_and_version_are_checked_through_flow():
    flow = start("Please help with access.")
    checkpoint = ack(flow)
    bad = args(flow, checkpoint)
    bad["receiver_capability"] = object()
    with pytest.raises(HandoffError, match="unauthorized_receiver"):
        extract_request_parts(flow[0], **bad)
    flow[5].set_version("SYN-CASE-01", 2, expected_version=1, capability=flow[7])
    with pytest.raises(HandoffError, match="stale_case_version"):
        prepare_auditor_review(flow[0], item_index=1, **args(flow, checkpoint))


def test_cancellation_after_segmentation_prevents_later_review_preparation():
    flow = start("Need a form; I cannot access the portal")
    checkpoint = ack(flow)
    assert len(extract_request_parts(flow[0], **args(flow, checkpoint)).items) == 2
    flow[0].cancel(checkpoint.handoff_id, expected_version=checkpoint.state_version,
        capability=flow[3], now=NOW)
    with pytest.raises(HandoffError, match="stale_handoff_version"):
        prepare_auditor_review(flow[0], item_index=2, **args(flow, checkpoint))
    assert flow[0].events()[-1].event == "handoff_cancelled"


def test_semantic_preparation_sends_only_unambiguous_minimized_items():
    text = "Need a blank form; I cannot access the portal"
    flow = start(text)
    checkpoint = ack(flow)
    candidate = prepare_multi_item_candidate(flow[0], catalog=None, **args(flow, checkpoint))
    request = prepare_semantic_request(
        candidate,
        allowed_categories=("Access Request", "Form Request"),
    )

    assert request.data_classification == "synthetic"
    assert [(item.item_index, item.text) for item in request.items] == [
        (1, "Need a blank form"),
        (2, "I cannot access the portal"),
    ]
    assert request.allowed_categories == ("Access Request", "Form Request")
    assert "case_id" not in request.model_dump()
    assert "source" not in request.model_dump()
    assert "example_references" not in request.model_dump()


def test_semantic_preparation_refuses_ambiguous_parent_before_provider_call():
    flow = start('The customer wrote "need a form; cannot log in')
    checkpoint = ack(flow)
    candidate = prepare_multi_item_candidate(flow[0], catalog=None, **args(flow, checkpoint))

    with pytest.raises(TriageSemanticPreparationError, match="ambiguous_segmentation"):
        prepare_semantic_request(candidate, allowed_categories=("Form Request",))
