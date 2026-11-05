"""Synthetic Coordinator-to-Knowledge integration with an explicitly declared A2 stand-in.

This exercises the local Shawn KnowledgeAgent checkout. It does not represent a
real Triage output, accepted Shared handoff, approved policy, production access,
or the not-yet-reconciled remote developer branch.
"""
from datetime import UTC, date, datetime

import pytest

from cdit_support_mao.agents.coordinator import (
    Coordinator, FixtureCaseVersions, FixturePolicyVersions, FixtureSession,
    FixtureSessionAuthority,
)
from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.coordinator.knowledge_handoff import (
    FixtureA2Declarations, KnowledgeFixtureRegistry,
)
from cdit_support_mao.contracts import AgentStatus

NOW = datetime(2026, 11, 5, 12, tzinfo=UTC)
AS_OF = date(2026, 11, 3)
MESSAGE = "Site user cannot find where to export the site enrollment report."


def connection(make_triage):
    owner, sender, triage, knowledge_sender, knowledge_receiver, declarer = (object() for _ in range(6))
    sessions = FixtureSessionAuthority(provisioning_capability=owner, ttl_seconds=3600)
    versions = FixtureCaseVersions(provisioning_capability=owner)
    versions.set_version("SYN-CASE-01", 1, expected_version=None, capability=owner)
    policy = FixturePolicyVersions(provisioning_capability=owner, active=frozenset({"SYN-POLICY-1"}))
    token = sessions.issue(FixtureSession(actor_id="SYN-ACTOR-1", role="staff", active=True,
        allowed_case_ids=("SYN-CASE-01",)), capability=owner)
    intake = Coordinator(sessions, case_versions=versions, policy_versions=policy).prepare({
        "case_id":"SYN-CASE-01", "case_version":1, "policy_version":"SYN-POLICY-1",
        "message":MESSAGE, "data_classification":"synthetic"}, session_token=token)
    source = HandoffRegistry(sender_capability=sender, receiver_capability=triage, timeout_seconds=30,
        actor_sessions=sessions, case_versions=versions, policy_versions=policy)
    prepared = source.prepare(intake, capability=sender, session_token=token, now=NOW)
    source_ack = source.acknowledge(prepared.handoff_id, expected_version=1,
        capability=triage, context=intake.context, now=NOW)
    declarations = FixtureA2Declarations(provisioning_capability=declarer)
    ledger = KnowledgeFixtureRegistry(source_registry=source, triage_capability=triage,
        sender_capability=knowledge_sender, knowledge_capability=knowledge_receiver,
        declarations=declarations, timeout_seconds=20)
    # Explicit stand-in: it is never derived from the synthetic policy fixture.
    stand_in = make_triage(MESSAGE, product_area="reports", run_context=intake.context)
    declarations.declare(source_handoff_id=source_ack.handoff_id, source_version=source_ack.state_version,
        contribution=stand_in, capability=declarer, next_stage="knowledge_fixture", single_independent_nonurgent=True)
    pending = ledger.prepare(stand_in, source_handoff_id=source_ack.handoff_id,
        source_version=source_ack.state_version, capability=knowledge_sender, now=NOW)
    return ledger, pending, knowledge_receiver, knowledge_sender, intake, source, source_ack, sender, versions, owner


def acknowledge(c):
    return c[0].acknowledge(c[1].receipt_id, expected_version=c[1].state_version,
        capability=c[2], context=c[4].context, now=NOW)


def actual_knowledge(agent, context, stand_in, acknowledged):
    return agent.run(context, stand_in, acknowledged=acknowledged, as_of=AS_OF, now=NOW)


def test_declared_stand_in_reaches_actual_knowledge_agent_and_cited_corpus(knowledge_agent, make_triage):
    c = connection(make_triage)
    ready = acknowledge(c)
    calls = []
    def callback(stand_in, acknowledged):
        calls.append((stand_in.agent, acknowledged))
        return actual_knowledge(knowledge_agent, c[4].context, stand_in, acknowledged)
    result = c[0].run_fixture(ready.receipt_id, expected_version=ready.state_version,
        capability=c[2], context=c[4].context, fixture_call=callback, now=NOW)
    assert calls == [("triage-stand-in", frozenset({ready.contribution_id}))]
    assert ready.fixture_only and result.context == c[4].context
    assert result.status is AgentStatus.COMPLETED and result.checkpoint.checkpoint == "A3"
    assert result.passages[0].source.cite() == "KB-NAV-001 v2.1 #s1"
    assert result.passages[0].content_trust == "untrusted_evidence" and result.human_review_required
    assert MESSAGE not in repr(ready) and MESSAGE not in repr(c[5].events())


def test_unacknowledged_or_wrong_receiver_never_calls_knowledge(knowledge_agent, make_triage):
    c = connection(make_triage)
    calls = []
    def callback(stand_in, acknowledged):
        calls.append(True)
        return actual_knowledge(knowledge_agent, c[4].context, stand_in, acknowledged)
    with pytest.raises(HandoffError, match="fixture_receipt_wrong_state"):
        c[0].run_fixture(c[1].receipt_id, expected_version=c[1].state_version,
            capability=c[2], context=c[4].context, fixture_call=callback, now=NOW)
    ready = acknowledge(c)
    with pytest.raises(HandoffError, match="unauthorized_fixture_receiver"):
        c[0].run_fixture(ready.receipt_id, expected_version=ready.state_version,
            capability=object(), context=c[4].context, fixture_call=callback, now=NOW)
    assert not calls


@pytest.mark.parametrize("changed", ["source_cancel", "receipt_cancel", "case_version"])
def test_state_changes_during_actual_retrieval_discard_result(knowledge_agent, make_triage, changed):
    c = connection(make_triage)
    ready = acknowledge(c)
    internal_status = []
    def callback(stand_in, acknowledged):
        result = actual_knowledge(knowledge_agent, c[4].context, stand_in, acknowledged)
        internal_status.append(result.status)
        if changed == "source_cancel":
            c[5].cancel(c[6].handoff_id, expected_version=c[6].state_version, capability=c[7], now=NOW)
        elif changed == "receipt_cancel":
            c[0].cancel(ready.receipt_id, expected_version=ready.state_version, capability=c[3])
        else:
            c[8].set_version("SYN-CASE-01", 2, expected_version=1, capability=c[9])
        return result
    with pytest.raises(HandoffError, match="stale_handoff_version|stale_fixture_receipt|stale_case_version"):
        c[0].run_fixture(ready.receipt_id, expected_version=ready.state_version,
            capability=c[2], context=c[4].context, fixture_call=callback, now=NOW)
    assert internal_status == [AgentStatus.COMPLETED]


def test_source_stale_before_retrieval_never_calls_agent(knowledge_agent, make_triage):
    c = connection(make_triage)
    ready = acknowledge(c)
    c[8].set_version("SYN-CASE-01", 2, expected_version=1, capability=c[9])
    calls = []
    def callback(stand_in, acknowledged):
        calls.append(True)
        return actual_knowledge(knowledge_agent, c[4].context, stand_in, acknowledged)
    with pytest.raises(HandoffError, match="stale_case_version"):
        c[0].run_fixture(ready.receipt_id, expected_version=ready.state_version,
            capability=c[2], context=c[4].context, fixture_call=callback, now=NOW)
    assert not calls
