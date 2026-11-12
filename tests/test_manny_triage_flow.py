"""Synthetic integration checks across Manny's current intake and triage boundary.

These exercise fixture code only: there is no model, human dispatch, external
system, authorized routing decision, or durable state in this local flow.
"""
from datetime import UTC, datetime
from pathlib import Path

import pytest

from cdit_support_mao.agents.coordinator import (
    Coordinator, FixtureCaseVersions, FixturePolicyVersions,
    FixtureSession, FixtureSessionAuthority,
)
from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.auditor import prepare_auditor_review
from cdit_support_mao.agents.triage.attention import FixtureAttentionPatterns
from cdit_support_mao.agents.triage.development_examples import (
    DevelopmentCatalogError,
    DevelopmentExampleCatalog,
    load_project_category_taxonomy,
)
from cdit_support_mao.agents.triage.multi_item_adapter import prepare_multi_item_candidate
from cdit_support_mao.agents.triage.segment import extract_request_parts
from cdit_support_mao.agents.triage.runtime import run_triage_runtime
from cdit_support_mao.agents.triage.semantic_pipeline import (
    TriageSemanticPreparationError,
    execute_semantic_triage,
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


def category_taxonomy():
    capability = object()
    catalog = DevelopmentExampleCatalog(provisioning_capability=capability)
    scenarios = Path(__file__).resolve().parents[1] / "docs" / "requirements" / "CASE-SCENARIOS.md"
    catalog.provision(scenarios.read_bytes().replace(b"\r\n", b"\n"), capability=capability)
    return catalog.category_taxonomy()


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


class _FakeMessages:
    def __init__(self, response=None, *, error: Exception | None = None):
        self.response = response
        self.error = error
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


class _FakeClient:
    def __init__(self, messages: _FakeMessages):
        self.messages = messages

    def with_options(self, **kwargs: object):
        return self


def _mock_model_response(items_payload: list[dict[str, object]]):
    import json
    from types import SimpleNamespace
    text = json.dumps({
        "items": items_payload,
        "human_review_required": True,
        "parent_complete": False,
        "downstream_allowed": False,
        "dispatched": False,
    })
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)],
        stop_reason="end_turn",
        model="claude-sonnet-5-5",
        usage=SimpleNamespace(input_tokens=150, output_tokens=90),
    )


def test_execute_semantic_triage_unauthorized_returns_none():
    flow = start("Need a blank form")
    checkpoint = ack(flow)
    candidate = prepare_multi_item_candidate(flow[0], catalog=None, **args(flow, checkpoint))
    client = _FakeClient(_FakeMessages())
    result = execute_semantic_triage(
        flow[0],
        candidate=candidate,
        allowed_categories=("Form Request",),
        client=client,
        billable_call_authorized=False,
        **args(flow, checkpoint),
    )
    assert result is None
    assert len(client.messages.calls) == 0


def test_execute_semantic_triage_authorized_executes_and_validates():
    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    candidate = prepare_multi_item_candidate(flow[0], catalog=None, **args(flow, checkpoint))
    fake_response = _mock_model_response([
        {
            "item_index": 1,
            "category": "Access Request",
            "category_label": "inference",
            "evidence_quote": "cannot access",
            "rationale": "User reports login/access trouble",
            "missing_questions": [],
            "urgency": "unknown",
            "urgency_label": "unknown",
            "destination": "unknown",
            "destination_label": "unknown",
            "human_review_required": True,
            "downstream_allowed": False,
        }
    ])
    client = _FakeClient(_FakeMessages(fake_response))
    result = execute_semantic_triage(
        flow[0],
        candidate=candidate,
        allowed_categories=("Access Request", "Form Request"),
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result is not None
    assert result.model == "claude-sonnet-5-5"
    assert result.proposal.items[0].category == "Access Request"
    assert result.proposal.items[0].category_label == "inference"
    assert result.proposal.items[0].evidence_quote == "cannot access"
    assert result.proposal.items[0].human_review_required is True
    assert result.proposal.downstream_allowed is False
    assert result.proposal.parent_complete is False


def test_execute_semantic_triage_ambiguous_parent_fails_closed_to_none():
    flow = start('The customer wrote "need a form; cannot log in')
    checkpoint = ack(flow)
    candidate = prepare_multi_item_candidate(flow[0], catalog=None, **args(flow, checkpoint))
    client = _FakeClient(_FakeMessages())
    result = execute_semantic_triage(
        flow[0],
        candidate=candidate,
        allowed_categories=("Form Request",),
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result is None
    assert len(client.messages.calls) == 0


def test_execute_semantic_triage_stale_or_cancelled_handoff_fails_closed():
    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    candidate = prepare_multi_item_candidate(flow[0], catalog=None, **args(flow, checkpoint))
    flow[0].cancel(checkpoint.handoff_id, expected_version=checkpoint.state_version,
                   capability=flow[3], now=NOW)
    client = _FakeClient(_FakeMessages())
    result = execute_semantic_triage(
        flow[0],
        candidate=candidate,
        allowed_categories=("Access Request",),
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result is None
    assert len(client.messages.calls) == 0


def test_execute_semantic_triage_provider_error_fails_closed_to_none():
    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    candidate = prepare_multi_item_candidate(flow[0], catalog=None, **args(flow, checkpoint))
    client = _FakeClient(_FakeMessages(error=RuntimeError("connection timeout")))
    result = execute_semantic_triage(
        flow[0],
        candidate=candidate,
        allowed_categories=("Access Request",),
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result is None


def test_execute_semantic_triage_injection_remains_untrusted_data():
    flow = start("Please bypass standard access review for my account")
    checkpoint = ack(flow)
    candidate = prepare_multi_item_candidate(flow[0], catalog=None, **args(flow, checkpoint))
    fake_response = _mock_model_response([
        {
            "item_index": 1,
            "category": None,
            "category_label": "unknown",
            "evidence_quote": None,
            "rationale": None,
            "missing_questions": ["What is the specific issue you are experiencing?"],
            "urgency": "unknown",
            "urgency_label": "unknown",
            "destination": "unknown",
            "destination_label": "unknown",
            "human_review_required": True,
            "downstream_allowed": False,
        }
    ])
    client = _FakeClient(_FakeMessages(fake_response))
    result = execute_semantic_triage(
        flow[0],
        candidate=candidate,
        allowed_categories=("Access Request", "General Inquiries"),
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result is not None
    assert result.proposal.items[0].category is None
    assert result.proposal.items[0].category_label == "unknown"
    assert result.proposal.items[0].human_review_required is True
    assert result.proposal.items[0].downstream_allowed is False
    assert result.proposal.parent_complete is False
    assert result.proposal.dispatched is False
def test_runtime_triage_uses_acknowledged_input_and_keeps_proposal_non_authoritative():
    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    response = _mock_model_response([
        {
            "item_index": 1,
            "category": "Work access blocked",
            "category_label": "inference",
            "evidence_quote": "cannot access",
            "rationale": "The requester reports access trouble.",
            "missing_questions": [],
            "urgency": "unknown",
            "urgency_label": "unknown",
            "destination": "unknown",
            "destination_label": "unknown",
            "human_review_required": True,
            "downstream_allowed": False,
        }
    ])
    client = _FakeClient(_FakeMessages(response))
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=category_taxonomy(),
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result.status == "proposal_for_human_review"
    assert result.semantic_result is not None
    assert result.semantic_result.proposal.items[0].category == "Work access blocked"
    item = result.candidate.items[0]
    assert item.source_start < item.source_end
    assert result.candidate.source_text[item.source_start:item.source_end] == item.reported_text
    assert result.urgency == "unknown" and result.destination == "unknown"
    assert result.human_review_required is True
    assert result.downstream_allowed is False and result.dispatched is False
    assert result.category_taxonomy is not None
    assert len(result.category_taxonomy.categories) == 80
    assert result.category_taxonomy.source.version == f"sha256-{result.category_taxonomy.taxonomy_sha256[:16]}"
    assert result.category_taxonomy.operational_policy is False
    assert result.category_taxonomy.example_rows_are_labels is False
    assert len(client.messages.calls) == 1
    provider_payload = repr(client.messages.calls[0])
    assert "SYN-EXAMPLE-" not in provider_payload
    assert "source_sha256" not in provider_payload
    assert "sample_band" not in provider_payload and "conditions" not in provider_payload
    proposed_item = result.candidate.items[0]
    assert proposed_item.category == "Work access blocked"
    assert proposed_item.category_label == "inference"
    assert proposed_item.category_evidence_quote == "cannot access"
    assert proposed_item.category_sources[0] == proposed_item.source
    assert proposed_item.category_sources[1].source_id == "SYN-TICKET-CATEGORY-TAXONOMY"
    assert proposed_item.category_sources[1].version == result.category_taxonomy.source.version
    assert proposed_item.category_sources[1].version != result.candidate.context.policy_version
    assert result.candidate.downstream_allowed is False and result.candidate.parent_complete is False


def test_runtime_triage_without_billable_authorization_routes_to_review_without_call():
    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    client = _FakeClient(_FakeMessages())
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=category_taxonomy(),
        client=client,
        **args(flow, checkpoint),
    )
    assert result.status == "needs_human_review"
    assert result.reason == "semantic_result_unavailable"
    assert result.urgency == "unknown" and result.destination == "unknown"
    assert result.human_review_required and not result.downstream_allowed and not result.dispatched
    assert client.messages.calls == []


def test_runtime_triage_rejects_stale_handoff_before_provider_call():
    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    client = _FakeClient(_FakeMessages())
    stale_args = args(flow, checkpoint)
    stale_args["expected_version"] += 1
    with pytest.raises(HandoffError):
        run_triage_runtime(
            flow[0],
            category_taxonomy=category_taxonomy(),
            client=client,
            billable_call_authorized=True,
            **stale_args,
        )
    assert client.messages.calls == []


def test_runtime_triage_routes_to_review_if_handoff_goes_stale_during_preflight(monkeypatch):
    import cdit_support_mao.agents.triage.runtime as runtime

    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    client = _FakeClient(_FakeMessages())
    original_prepare = runtime.prepare_multi_item_candidate

    def prepare_then_stale(*args, **kwargs):
        candidate = original_prepare(*args, **kwargs)
        flow[5].set_version("SYN-CASE-01", 2, expected_version=1, capability=flow[7])
        return candidate

    monkeypatch.setattr(runtime, "prepare_multi_item_candidate", prepare_then_stale)
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=category_taxonomy(),
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result.status == "needs_human_review"
    assert result.reason == "handoff_stale"
    assert client.messages.calls == []


def test_runtime_triage_without_taxonomy_routes_to_auditor_without_provider_call():
    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    client = _FakeClient(_FakeMessages())
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=None,
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result.status == "needs_human_review"
    assert result.reason == "category_taxonomy_unavailable"
    assert result.semantic_result is None
    assert result.category_taxonomy is None
    assert result.human_review_required and not result.downstream_allowed and not result.dispatched
    assert client.messages.calls == []


def test_runtime_triage_returns_attention_note_without_assigning_urgency_or_authority():
    flow = start("Please help: administrator account is actively changing permissions without authorization.")
    checkpoint = ack(flow)
    owner = object()
    patterns = FixtureAttentionPatterns(provisioning_capability=owner)
    pattern = "administrator account is actively changing permissions without authorization"
    patterns.add("SYN-ATTENTION-01", pattern, capability=owner)
    patterns.seal(capability=owner)
    response = _mock_model_response([{
        "item_index": 1,
        "category": "Security incident",
        "category_label": "inference",
        "evidence_quote": pattern,
        "rationale": "The reported text matches the synthetic security category.",
        "missing_questions": [],
        "urgency": "unknown",
        "urgency_label": "unknown",
        "destination": "unknown",
        "destination_label": "unknown",
        "human_review_required": True,
        "downstream_allowed": False,
    }])
    client = _FakeClient(_FakeMessages(response))
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=category_taxonomy(),
        fixture_patterns=patterns,
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    signal = result.attention_signal
    assert signal is not None and signal.status == "potential_attention"
    assert len(signal.matches) == 1
    match = signal.matches[0]
    assert result.triage_input.reported_message[match.start_codepoint:match.end_codepoint] == pattern
    assert match.source == result.triage_input.source
    assert signal.review_note is not None and "does not verify an incident" in signal.review_note
    assert signal.urgency == result.urgency == "unknown"
    assert signal.human_review_required and not signal.incident_verified
    assert not signal.downstream_allowed and not signal.dispatched
    assert not result.downstream_allowed and not result.dispatched


def test_runtime_attention_absence_is_not_assessed_and_does_not_change_triage():
    flow = start("I need a copy of a form.")
    checkpoint = ack(flow)
    owner = object()
    patterns = FixtureAttentionPatterns(provisioning_capability=owner)
    patterns.add("SYN-ATTENTION-01", "possible privacy incident", capability=owner)
    patterns.seal(capability=owner)
    response = _mock_model_response([{
        "item_index": 1,
        "category": "Routine form copy / resubmission",
        "category_label": "inference",
        "evidence_quote": "copy of a form",
        "rationale": "The requester asks for a form copy.",
        "missing_questions": [],
        "urgency": "unknown",
        "urgency_label": "unknown",
        "destination": "unknown",
        "destination_label": "unknown",
        "human_review_required": True,
        "downstream_allowed": False,
    }])
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=category_taxonomy(),
        fixture_patterns=patterns,
        client=_FakeClient(_FakeMessages(response)),
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result.attention_signal is not None
    assert result.attention_signal.status == "not_assessed"
    assert result.attention_signal.review_note is None
    assert result.urgency == "unknown" and result.human_review_required
    assert not result.downstream_allowed and not result.dispatched


def test_runtime_rejects_tampered_attention_span_and_wrong_source():
    from cdit_support_mao.agents.triage.attention import AttentionMatch, AttentionSignal
    from cdit_support_mao.agents.triage.runtime import TriageRuntimeResult
    from cdit_support_mao.contracts.common import SourceKind, SourceRef
    from pydantic import ValidationError

    flow = start("Please help: administrator account is actively changing permissions without authorization.")
    checkpoint = ack(flow)
    owner = object()
    patterns = FixtureAttentionPatterns(provisioning_capability=owner)
    pattern = "administrator account is actively changing permissions without authorization"
    patterns.add("SYN-ATTENTION-01", pattern, capability=owner)
    patterns.seal(capability=owner)
    response = _mock_model_response([{
        "item_index": 1,
        "category": "Security incident",
        "category_label": "inference",
        "evidence_quote": pattern,
        "rationale": "The reported text matches the synthetic security category.",
        "missing_questions": [],
        "urgency": "unknown",
        "urgency_label": "unknown",
        "destination": "unknown",
        "destination_label": "unknown",
        "human_review_required": True,
        "downstream_allowed": False,
    }])
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=category_taxonomy(),
        fixture_patterns=patterns,
        client=_FakeClient(_FakeMessages(response)),
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result.attention_signal is not None
    original = result.attention_signal.matches[0]
    out_of_bounds = original.model_copy(update={"end_codepoint": len(result.triage_input.reported_message) + 1})
    wrong_source = original.model_copy(update={
        "source": SourceRef(kind=SourceKind.CASE_FIELD, source_id="SYN-CASE-02", version="1", locator="message")
    })
    for bad_match in (out_of_bounds, wrong_source):
        bad_signal = result.attention_signal.model_copy(update={"matches": (bad_match,)})
        payload = result.model_dump()
        payload["attention_signal"] = bad_signal.model_dump()
        with pytest.raises(ValidationError, match="triage_runtime_attention_evidence_mismatch"):
            TriageRuntimeResult.model_validate(payload)
    with pytest.raises(ValidationError, match="attention_span_must_be_nonempty"):
        AttentionMatch.model_validate(original.model_copy(update={"start_codepoint": original.end_codepoint}).model_dump())


def test_runtime_rechecks_active_handoff_after_attention_before_fallback(monkeypatch):
    import cdit_support_mao.agents.triage.runtime as runtime

    flow = start("Please help: administrator account is actively changing permissions without authorization.")
    checkpoint = ack(flow)
    owner = object()
    patterns = FixtureAttentionPatterns(provisioning_capability=owner)
    patterns.add("SYN-ATTENTION-01", "administrator account is actively changing permissions without authorization", capability=owner)
    patterns.seal(capability=owner)
    client = _FakeClient(_FakeMessages())
    original_inspect = runtime.inspect_attention_signal

    def inspect_then_cancel(*args, **kwargs):
        signal = original_inspect(*args, **kwargs)
        flow[0].cancel(checkpoint.handoff_id, expected_version=checkpoint.state_version,
            capability=flow[3], now=NOW)
        return signal

    monkeypatch.setattr(runtime, "inspect_attention_signal", inspect_then_cancel)
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=None,
        fixture_patterns=patterns,
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result.status == "needs_human_review" and result.reason == "handoff_stale"
    assert result.attention_signal is None and result.semantic_result is None
    assert client.messages.calls == []


def test_runtime_routes_to_review_if_pinned_taxonomy_source_cannot_be_loaded(monkeypatch):
    import cdit_support_mao.agents.triage.runtime as runtime

    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    client = _FakeClient(_FakeMessages())

    def source_unavailable():
        raise DevelopmentCatalogError("trusted_category_taxonomy_changed")

    monkeypatch.setattr(runtime, "load_project_category_taxonomy", source_unavailable)
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=category_taxonomy(),
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result.status == "needs_human_review"
    assert result.reason == "category_taxonomy_unavailable"
    assert result.attention_signal is None
    assert result.semantic_result is None and client.messages.calls == []
    assert result.urgency == "unknown" and not result.downstream_allowed and not result.dispatched


def test_runtime_triage_rejects_mutated_taxonomy_before_provider_call():
    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    client = _FakeClient(_FakeMessages())
    taxonomy = category_taxonomy()
    altered_names = ("Unapproved Category", *taxonomy.categories[1:])
    tampered = taxonomy.model_copy(update={"categories": altered_names})
    with pytest.raises(HandoffError, match="invalid_category_taxonomy"):
        run_triage_runtime(
            flow[0],
            category_taxonomy=tampered,
            client=client,
            billable_call_authorized=True,
            **args(flow, checkpoint),
        )
    assert client.messages.calls == []


def test_runtime_triage_rejects_untrusted_taxonomy_source_before_provider_call():
    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    client = _FakeClient(_FakeMessages())
    taxonomy = load_project_category_taxonomy()
    untrusted = taxonomy.model_copy(update={"source_sha256": "f" * 64})
    with pytest.raises(HandoffError, match="invalid_category_taxonomy"):
        run_triage_runtime(
            flow[0],
            category_taxonomy=untrusted,
            client=client,
            billable_call_authorized=True,
            **args(flow, checkpoint),
        )
    assert client.messages.calls == []


def test_runtime_triage_splits_multiple_requests_and_proposes_categories_per_item():
    flow = start("Need a blank form; I cannot access the portal; my pay is missing.")
    checkpoint = ack(flow)
    response = _mock_model_response([
        {
            "item_index": 1,
            "category": "Routine form copy / resubmission",
            "category_label": "inference",
            "evidence_quote": "blank form",
            "rationale": "The first item requests a form copy.",
            "missing_questions": [],
            "urgency": "unknown",
            "urgency_label": "unknown",
            "destination": "unknown",
            "destination_label": "unknown",
            "human_review_required": True,
            "downstream_allowed": False,
        },
        {
            "item_index": 2,
            "category": "Work access blocked",
            "category_label": "inference",
            "evidence_quote": "cannot access the portal",
            "rationale": "The second item reports blocked work access.",
            "missing_questions": [],
            "urgency": "unknown",
            "urgency_label": "unknown",
            "destination": "unknown",
            "destination_label": "unknown",
            "human_review_required": True,
            "downstream_allowed": False,
        },
        {
            "item_index": 3,
            "category": "Missing wages",
            "category_label": "inference",
            "evidence_quote": "pay is missing",
            "rationale": "The third item reports missing pay.",
            "missing_questions": [],
            "urgency": "unknown",
            "urgency_label": "unknown",
            "destination": "unknown",
            "destination_label": "unknown",
            "human_review_required": True,
            "downstream_allowed": False,
        },
    ])
    client = _FakeClient(_FakeMessages(response))
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=category_taxonomy(),
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    assert result.status == "proposal_for_human_review"
    assert len(result.candidate.items) == 3
    assert [item.item_index for item in result.semantic_result.proposal.items] == [1, 2, 3]
    assert [item.category for item in result.semantic_result.proposal.items] == [
        "Routine form copy / resubmission", "Work access blocked", "Missing wages"
    ]
    for candidate_item, proposal_item in zip(result.candidate.items, result.semantic_result.proposal.items):
        assert result.candidate.source_text[candidate_item.source_start:candidate_item.source_end] == candidate_item.reported_text
        assert proposal_item.evidence_quote in candidate_item.reported_text
        assert proposal_item.category_label == "inference"
        assert proposal_item.urgency == "unknown" and proposal_item.destination == "unknown"
        assert proposal_item.human_review_required and not proposal_item.downstream_allowed
        bound_item = result.candidate.items[candidate_item.item_index - 1]
        assert bound_item.category == proposal_item.category
        assert bound_item.category_evidence_quote == proposal_item.evidence_quote
        assert {source.kind.value for source in bound_item.category_sources} == {"case_field", "policy_rule"}
    assert not result.dispatched and not result.downstream_allowed


def test_runtime_result_rejects_first_item_mismatch_when_later_item_matches():
    from cdit_support_mao.agents.triage.runtime import TriageRuntimeResult
    from pydantic import ValidationError

    flow = start("Need a blank form; I cannot access the portal.")
    checkpoint = ack(flow)
    response = _mock_model_response([
        {
            "item_index": 1,
            "category": "Routine form copy / resubmission",
            "category_label": "inference",
            "evidence_quote": "blank form",
            "rationale": "The first item requests a form copy.",
            "missing_questions": [],
            "urgency": "unknown",
            "urgency_label": "unknown",
            "destination": "unknown",
            "destination_label": "unknown",
            "human_review_required": True,
            "downstream_allowed": False,
        },
        {
            "item_index": 2,
            "category": "Work access blocked",
            "category_label": "inference",
            "evidence_quote": "cannot access the portal",
            "rationale": "The second item reports access trouble.",
            "missing_questions": [],
            "urgency": "unknown",
            "urgency_label": "unknown",
            "destination": "unknown",
            "destination_label": "unknown",
            "human_review_required": True,
            "downstream_allowed": False,
        },
    ])
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=category_taxonomy(),
        client=_FakeClient(_FakeMessages(response)),
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )
    first = result.candidate.items[0]
    wrong_first = first.model_copy(update={"category": "Work access blocked"})
    bad_candidate = result.candidate.model_copy(update={"items": (wrong_first, result.candidate.items[1])})
    payload = result.model_dump()
    payload["candidate"] = bad_candidate.model_dump()
    with pytest.raises(ValidationError, match="triage_runtime_candidate_mismatch"):
        TriageRuntimeResult.model_validate(payload)


def test_runtime_binding_validation_failure_returns_unbound_human_review(monkeypatch):
    import cdit_support_mao.agents.triage.runtime as runtime

    flow = start("I cannot access the portal")
    checkpoint = ack(flow)
    client = _FakeClient(_FakeMessages(_mock_model_response([{
        "item_index": 1,
        "category": "Work access blocked",
        "category_label": "inference",
        "evidence_quote": "cannot access",
        "rationale": "The request reports an access problem.",
        "missing_questions": [],
        "urgency": "unknown",
        "urgency_label": "unknown",
        "destination": "unknown",
        "destination_label": "unknown",
        "human_review_required": True,
        "downstream_allowed": False,
    }])))

    def reject_binding(*args, **kwargs):
        raise HandoffError("triage_runtime_item_validation_failed")

    monkeypatch.setattr(runtime, "_bind_category_proposals", reject_binding)
    result = run_triage_runtime(
        flow[0],
        category_taxonomy=category_taxonomy(),
        client=client,
        billable_call_authorized=True,
        **args(flow, checkpoint),
    )

    assert result.status == "needs_human_review"
    assert result.reason == "triage_result_validation_failed"
    assert result.semantic_result is None
    assert all(item.category is None and item.category_label == "unknown" for item in result.candidate.items)
    assert result.human_review_required and result.urgency == "unknown"
    assert not result.downstream_allowed and not result.dispatched
    assert len(client.messages.calls) == 1
