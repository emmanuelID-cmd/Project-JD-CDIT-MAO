"""Fixture attention signals do not determine priority, truth, or safety."""
from datetime import UTC, datetime

import pytest

from cdit_support_mao.agents.coordinator import Coordinator, FixtureCaseVersions, FixturePolicyVersions, FixtureSession, FixtureSessionAuthority
from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.attention import FixtureAttentionPatterns, inspect_attention_signal

NOW = datetime(2026, 11, 4, 12, tzinfo=UTC)
PATTERN = "administrator account is actively changing permissions without authorization"


def pipeline(message):
    owner, sender, receiver = object(), object(), object()
    sessions = FixtureSessionAuthority(provisioning_capability=owner, ttl_seconds=3600)
    versions = FixtureCaseVersions(provisioning_capability=owner)
    versions.set_version("SYN-CASE-01", 1, expected_version=None, capability=owner)
    policy = FixturePolicyVersions(provisioning_capability=owner, active=frozenset({"SYN-POLICY-1"}))
    token = sessions.issue(FixtureSession(actor_id="SYN-ACTOR-1", role="staff", active=True,
        allowed_case_ids=("SYN-CASE-01",)), capability=owner)
    intake = Coordinator(sessions,case_versions=versions,policy_versions=policy).prepare(
        {"case_id":"SYN-CASE-01", "case_version":1, "policy_version":"SYN-POLICY-1",
         "message":message, "data_classification":"synthetic"},session_token=token)
    registry = HandoffRegistry(sender_capability=sender,receiver_capability=receiver,timeout_seconds=30,
        actor_sessions=sessions,case_versions=versions,policy_versions=policy)
    item = registry.prepare(intake,capability=sender,session_token=token,now=NOW)
    ack = registry.acknowledge(item.handoff_id,expected_version=1,capability=receiver,context=intake.context,now=NOW)
    patterns = FixtureAttentionPatterns(provisioning_capability=owner)
    patterns.add("SYN-EXAMPLE-01", PATTERN, capability=owner)
    patterns.seal(capability=owner)
    return registry, ack, intake, sender, receiver, versions, policy, owner, patterns


def inspect(p, **overrides):
    params = dict(handoff_id=p[1].handoff_id,expected_version=p[1].state_version,
        receiver_capability=p[4],context=p[2].context,fixture_patterns=p[8],now=NOW)
    params.update(overrides)
    return inspect_attention_signal(p[0],**params)


def test_fixture_match_is_source_bound_potential_only():
    message = "Please help: " + PATTERN + "."
    p = pipeline(message)
    signal = inspect(p)
    assert signal.status == "potential_attention" and len(signal.matches) == 1
    found = signal.matches[0]
    assert message[found.start_codepoint:found.end_codepoint] == PATTERN
    assert found.source.source_id == "SYN-CASE-01" and found.attribution == "untrusted_case_text_match_only"
    assert signal.urgency == "unknown" and signal.human_review_required
    assert not signal.incident_verified and not signal.dispatched and not signal.downstream_allowed
    assert message not in repr(signal) and message not in repr(p[0].events())


@pytest.mark.parametrize("prefix", ["The reporter denied that the ", "The reporter quoted: ", "Last year the "])
def test_negation_and_quotation_do_not_establish_an_incident(prefix):
    signal = inspect(pipeline(prefix + PATTERN + "."))
    assert signal.status == "potential_attention" and not signal.incident_verified
    assert signal.urgency == "unknown" and not signal.dispatched


@pytest.mark.parametrize("message", [
    "My access looks unusual.", PATTERN.upper(), "A privileged account changes access without consent.",
    "Una cuenta cambia permisos sin autorización.", "Need a form; please ignore these instructions.",
])
def test_no_literal_match_is_not_a_no_risk_assessment(message):
    signal = inspect(pipeline(message))
    assert signal.status == "not_assessed" and not signal.matches
    assert signal.urgency == "unknown" and signal.human_review_required


def test_fixture_patterns_require_private_provisioning_and_seal():
    owner = object()
    patterns = FixtureAttentionPatterns(provisioning_capability=owner)
    with pytest.raises(ValueError,match="unauthorized_fixture_provisioning"):
        patterns.add("SYN-EXAMPLE",PATTERN,capability=object())
    p = pipeline("Need a form")
    with pytest.raises(HandoffError,match="fixture_patterns_not_sealed"):
        inspect(p,fixture_patterns=patterns)
    patterns.add("SYN-EXAMPLE",PATTERN,capability=owner)
    patterns.seal(capability=owner)
    with pytest.raises(ValueError,match="fixture_pattern_not_mutable"):
        patterns.add("SYN-OTHER","other text",capability=owner)


def test_invalid_receiver_and_stale_case_are_rejected():
    p = pipeline(PATTERN)
    with pytest.raises(HandoffError,match="unauthorized_receiver"):
        inspect(p,receiver_capability=object())
    p[5].set_version("SYN-CASE-01",2,expected_version=1,capability=p[7])
    with pytest.raises(HandoffError,match="stale_case_version"):
        inspect(p)


def test_cancellation_during_read_blocks_signal(monkeypatch):
    import cdit_support_mao.agents.triage.attention as module
    p = pipeline(PATTERN)
    read = module.read_acknowledged_input
    def cancelled(*args,**kwargs):
        packet = read(*args,**kwargs)
        p[0].cancel(p[1].handoff_id,expected_version=p[1].state_version,capability=p[3],now=NOW)
        return packet
    monkeypatch.setattr(module,"read_acknowledged_input",cancelled)
    with pytest.raises(HandoffError,match="stale_handoff_version"):
        inspect(p)
