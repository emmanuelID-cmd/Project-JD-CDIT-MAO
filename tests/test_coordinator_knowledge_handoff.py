"""Synthetic A2 declaration and Knowledge acknowledgment: fixture only."""
from datetime import UTC, datetime, timedelta

import pytest

from cdit_support_mao.agents.coordinator import Coordinator, FixtureCaseVersions, FixturePolicyVersions, FixtureSession, FixtureSessionAuthority
from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.coordinator.knowledge_handoff import FixtureA2Declarations, KnowledgeFixtureRegistry

NOW = datetime(2026, 11, 5, 12, tzinfo=UTC)


def setup(message, make_triage):
    owner, sender, triage, ks, kr, declarer = (object() for _ in range(6))
    sessions = FixtureSessionAuthority(provisioning_capability=owner, ttl_seconds=3600)
    versions = FixtureCaseVersions(provisioning_capability=owner)
    versions.set_version("SYN-CASE-01", 1, expected_version=None, capability=owner)
    policy = FixturePolicyVersions(provisioning_capability=owner, active=frozenset({"SYN-POLICY-1"}))
    token = sessions.issue(FixtureSession(actor_id="SYN-ACTOR-1", role="staff", active=True,
        allowed_case_ids=("SYN-CASE-01",)), capability=owner)
    intake = Coordinator(sessions, case_versions=versions, policy_versions=policy).prepare(
        {"case_id":"SYN-CASE-01", "case_version":1, "policy_version":"SYN-POLICY-1",
         "message":message, "data_classification":"synthetic"}, session_token=token)
    source = HandoffRegistry(sender_capability=sender, receiver_capability=triage, timeout_seconds=30,
        actor_sessions=sessions, case_versions=versions, policy_versions=policy)
    prepared = source.prepare(intake, capability=sender, session_token=token, now=NOW)
    ack = source.acknowledge(prepared.handoff_id, expected_version=1, capability=triage, context=intake.context, now=NOW)
    declarations = FixtureA2Declarations(provisioning_capability=declarer)
    ledger = KnowledgeFixtureRegistry(source_registry=source, triage_capability=triage,
        sender_capability=ks, knowledge_capability=kr, declarations=declarations, timeout_seconds=20)
    candidate = make_triage(message, run_context=intake.context)
    return source, ack, intake, sender, triage, ks, kr, declarer, declarations, ledger, candidate, versions, policy, owner, sessions, token


def declared(p):
    p[8].declare(source_handoff_id=p[1].handoff_id, source_version=p[1].state_version,
        contribution=p[10], capability=p[7], next_stage="knowledge_fixture", single_independent_nonurgent=True)


def prepare(p):
    return p[9].prepare(p[10], source_handoff_id=p[1].handoff_id,
        source_version=p[1].state_version, capability=p[5], now=NOW)


def accept(p, receipt):
    return p[9].acknowledge(receipt.receipt_id, expected_version=receipt.state_version,
        capability=p[6], context=p[2].context, now=NOW)


def consume(p, receipt, **kwargs):
    args=dict(expected_version=receipt.state_version, capability=p[6], context=p[2].context, now=NOW)
    args.update(kwargs)
    return p[9].consume(receipt.receipt_id, **args)


def test_only_registry_ack_creates_fixture_ack_set(make_triage):
    p = setup("Where is the report?", make_triage)
    with pytest.raises(HandoffError, match="fixture_declaration_missing"):
        prepare(p)
    declared(p)
    pending=prepare(p)
    with pytest.raises(HandoffError, match="fixture_receipt_wrong_state"):
        consume(p, pending)
    ready=accept(p,pending)
    candidate, ack = consume(p,ready)
    assert ack == frozenset({candidate.contribution_id}) and ready.fixture_only
    assert ready.recipient == "knowledge_fixture"
    assert p[2].untrusted_message not in repr(ready)


@pytest.mark.parametrize("urgency", ["high", "medium", "unknown"])
def test_unresolved_or_higher_priority_cannot_be_fixture_attested(make_triage, urgency):
    p=setup("Where is the report?", make_triage)
    altered=p[10].model_copy(update={"urgency":urgency})
    with pytest.raises(HandoffError, match="fixture_triage_not_eligible"):
        p[8].declare(source_handoff_id=p[1].handoff_id, source_version=2, contribution=altered,
            capability=p[7], next_stage="knowledge_fixture", single_independent_nonurgent=True)


def test_missing_declaration_or_forged_candidate_cannot_pass(make_triage):
    p=setup("Where is the report?", make_triage)
    declared(p)
    p=list(p)
    p[10]=p[10].model_copy(update={"category":"different"})
    with pytest.raises(HandoffError, match="fixture_declaration_missing"):
        prepare(p)
    with pytest.raises(HandoffError, match="unauthorized_fixture_declaration"):
        p[8].declare(source_handoff_id=p[1].handoff_id, source_version=2, contribution=p[10],
            capability=object(), next_stage="knowledge_fixture", single_independent_nonurgent=True)


def test_multi_and_ambiguous_source_fail_closed(make_triage):
    for message in ("Need a form; payroll is missing", "Login fails and payroll is wrong"):
        p=setup(message, make_triage)
        declared(p)
        with pytest.raises(HandoffError, match="fixture_source_mismatch_or_ambiguous"):
            prepare(p)


def test_wrong_receiver_stale_version_and_expiry_fail_closed(make_triage):
    p=setup("Where is the report?", make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    with pytest.raises(HandoffError, match="unauthorized_fixture_receiver"):
        consume(p,ready,capability=object())
    with pytest.raises(HandoffError, match="stale_fixture_receipt"):
        consume(p,ready,expected_version=1)
    with pytest.raises(HandoffError, match="fixture_receipt_expired"):
        consume(p,ready,now=NOW+timedelta(seconds=20))


def test_source_cancel_and_policy_change_reject_receipt(make_triage):
    p=setup("Where is the report?", make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    p[0].cancel(p[1].handoff_id, expected_version=2, capability=p[3], now=NOW)
    with pytest.raises(HandoffError, match="stale_handoff_version"):
        consume(p,ready)
    p=setup("Where is the report?", make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    p[12].replace(frozenset({"SYN-POLICY-1"}), expected_generation=1, capability=p[13])
    with pytest.raises(HandoffError, match="stale_policy_version"):
        consume(p,ready)


def test_changes_during_fixture_callback_discard_result(make_triage):
    p=setup("Where is the report?", make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    def callback(candidate, ack):
        p[0].cancel(p[1].handoff_id, expected_version=2, capability=p[3], now=NOW)
        return "MUST_NOT_ESCAPE"
    with pytest.raises(HandoffError, match="stale_handoff_version"):
        p[9].run_fixture(ready.receipt_id, expected_version=ready.state_version, capability=p[6],
            context=p[2].context, fixture_call=callback, now=NOW)


def test_cancelled_acknowledgment_cannot_be_reused(make_triage):
    p=setup("Where is the report?", make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    p[9].cancel(ready.receipt_id, expected_version=ready.state_version, capability=p[5])
    with pytest.raises(HandoffError, match="stale_fixture_receipt"):
        consume(p,ready)


def test_failed_prepare_recheck_discards_pending_receipt(make_triage, monkeypatch):
    p=setup("Where is the report?", make_triage)
    declared(p)
    original=p[9]._source_check
    count=0
    def changing(*args, **kwargs):
        nonlocal count
        count += 1
        if count == 2:
            raise HandoffError("synthetic_source_changed")
        return original(*args, **kwargs)
    monkeypatch.setattr(p[9], "_source_check", changing)
    with pytest.raises(HandoffError, match="synthetic_source_changed"):
        prepare(p)
    assert p[9]._entries == {}


def test_failed_ack_recheck_blocks_receipt(make_triage, monkeypatch):
    p=setup("Where is the report?", make_triage)
    declared(p)
    pending=prepare(p)
    original=p[9]._source_check
    count=0
    def changing(*args, **kwargs):
        nonlocal count
        count += 1
        if count == 3:
            raise HandoffError("synthetic_source_changed")
        return original(*args, **kwargs)
    monkeypatch.setattr(p[9], "_source_check", changing)
    with pytest.raises(HandoffError, match="synthetic_source_changed"):
        accept(p,pending)
    receipt=p[9]._entries[pending.receipt_id][0]
    assert receipt.state == "blocked" and receipt.state_version == 3
    with pytest.raises(HandoffError, match="fixture_receipt_wrong_state"):
        consume(p,receipt)


@pytest.mark.parametrize("changed", ["case", "policy"])
def test_version_change_during_callback_discards_result(make_triage, changed):
    p=setup("Where is the report?", make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    def callback(candidate, ack):
        if changed == "case":
            p[11].set_version("SYN-CASE-01", 2, expected_version=1, capability=p[13])
        else:
            p[12].replace(frozenset({"SYN-POLICY-1"}), expected_generation=1, capability=p[13])
        return "MUST_NOT_ESCAPE"
    with pytest.raises(HandoffError, match="stale_case_version|stale_policy_version"):
        p[9].run_fixture(ready.receipt_id, expected_version=ready.state_version, capability=p[6],
            context=p[2].context, fixture_call=callback, now=NOW)


def test_session_revocation_during_callback_discards_result(make_triage):
    p=setup("Where is the report?", make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    def callback(candidate, ack):
        p[14].revoke(p[15], capability=p[13])
        return "MUST_NOT_ESCAPE"
    with pytest.raises(HandoffError, match="session_revoked_or_scope_changed"):
        p[9].run_fixture(ready.receipt_id, expected_version=ready.state_version, capability=p[6],
            context=p[2].context, fixture_call=callback, now=NOW)


@pytest.mark.parametrize("change", [{"category":"unknown"}, {"category":" "}, {"category":None}, {"unknowns":("impact unknown",)}, {"missing_facts":("scope",)}])
def test_unknown_fixture_outputs_cannot_be_declared(make_triage, change):
    p=setup("Where is the report?", make_triage)
    altered=p[10].model_copy(update=change)
    with pytest.raises(HandoffError, match="fixture_triage_not_eligible"):
        p[8].declare(source_handoff_id=p[1].handoff_id, source_version=2, contribution=altered,
            capability=p[7], next_stage="knowledge_fixture", single_independent_nonurgent=True)


def policy_case(make_triage):
    from cdit_support_mao.agents.triage.fixture_policy import SyntheticPolicyCatalog, propose_from_synthetic_policy
    from cdit_support_mao.contracts.common import Claim, ClaimLabel, ConfidenceBand
    p=list(setup("Where is the report?", make_triage))
    provision=object()
    catalog=SyntheticPolicyCatalog(policy_version="SYN-POLICY-1", provision_capability=provision)
    catalog.add({"rule_id":"SYN-RULE-REPORT", "exact_report":"Where is the report?",
        "category":"report-navigation", "urgency":"low", "proposed_destination":"knowledge_review"}, capability=provision)
    catalog.seal(capability=provision)
    proposal=propose_from_synthetic_policy(p[0], handoff_id=p[1].handoff_id, expected_version=2,
        receiver_capability=p[4], context=p[2].context, item_index=1, catalog=catalog, now=NOW)
    claim=Claim(statement="Synthetic fixture inference: category=report-navigation; urgency=low",
        label=ClaimLabel.INFERENCE, sources=(proposal.reported_source,proposal.policy_source),
        basis=f"synthetic fixture policy sha256:{proposal.fixture_digest}", confidence=ConfidenceBand.LOW)
    p[10]=p[10].model_copy(update={"agent":"synthetic-triage-stand-in", "agent_version":"fixture-0.1", "category":"report-navigation", "urgency":"low", "claims":(claim,),
        "confidence":ConfidenceBand.LOW, "category_confidence":ConfidenceBand.LOW})
    p[9]=KnowledgeFixtureRegistry(source_registry=p[0], triage_capability=p[4], sender_capability=p[5],
        knowledge_capability=p[6], declarations=p[8], timeout_seconds=20, policy_catalog=catalog)
    return p,catalog,proposal


def test_policy_inference_requires_recomputed_source_and_records_digest(make_triage):
    p,catalog,proposal=policy_case(make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    item, ack=consume(p,ready)
    assert ready.fixture_basis == "policy_inference" and ready.fixture_policy_digest == proposal.fixture_digest
    assert item.claims[0].sources == (proposal.reported_source,proposal.policy_source)
    assert ack == frozenset({item.contribution_id}) and not proposal.downstream_allowed


def test_no_claim_standin_is_not_labeled_policy_inference(make_triage):
    p=setup("Where is the report?", make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    assert ready.fixture_basis == "standalone_declaration" and ready.fixture_policy_digest is None


@pytest.mark.parametrize("label", ["verified", "unknown"])
def test_non_inference_claim_rejected(make_triage, label):
    from cdit_support_mao.contracts.common import ClaimLabel
    p,_,_=policy_case(make_triage)
    p[10]=p[10].model_copy(update={"claims":(p[10].claims[0].model_copy(update={"label":ClaimLabel(label)}),)})
    with pytest.raises(HandoffError, match="fixture_claim_not_eligible"):
        declared(p)


def test_extra_claim_is_rejected(make_triage):
    p,_,_=policy_case(make_triage)
    p[10]=p[10].model_copy(update={"claims":p[10].claims*2})
    with pytest.raises(HandoffError, match="fixture_triage_not_eligible"):
        declared(p)


@pytest.mark.parametrize("field,value", [("basis","synthetic fixture policy sha256:"+"0"*64),
    ("statement","Synthetic fixture inference: category=other; urgency=low")])
def test_tampered_inference_cannot_be_declared_into_a_usable_receipt(make_triage,field,value):
    p,_,_=policy_case(make_triage)
    p[10]=p[10].model_copy(update={"claims":(p[10].claims[0].model_copy(update={field:value}),)})
    declared(p)
    with pytest.raises(HandoffError, match="fixture_policy_claim_mismatch"):
        prepare(p)


def test_changed_contents_same_policy_version_blocks_consumption(make_triage):
    from cdit_support_mao.agents.triage.fixture_policy import SyntheticPolicyCatalog
    p,_,_=policy_case(make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    provision=object()
    replaced=SyntheticPolicyCatalog(policy_version="SYN-POLICY-1",provision_capability=provision)
    replaced.add({"rule_id":"SYN-RULE-OTHER", "exact_report":"Where is the report?",
        "category":"report-navigation", "urgency":"low", "proposed_destination":"knowledge_review"},capability=provision)
    replaced.seal(capability=provision)
    p[9]._policy_catalog=replaced
    with pytest.raises(HandoffError, match="fixture_policy_claim_mismatch"):
        consume(p,ready)


def test_policy_inference_requires_configured_catalog(make_triage):
    p,_,_=policy_case(make_triage)
    declared(p)
    p[9]._policy_catalog=None
    with pytest.raises(HandoffError, match="fixture_policy_not_configured"):
        prepare(p)


def test_prepare_rechecks_live_clock_after_slow_source(make_triage, monkeypatch):
    p=setup("Where is the report?",make_triage)
    declared(p)
    times=iter((NOW,NOW,NOW+timedelta(seconds=21)))
    monkeypatch.setattr(p[9], "_time", lambda value: value if value is not None else next(times))
    with pytest.raises(HandoffError, match="fixture_receipt_expired"):
        p[9].prepare(p[10], source_handoff_id=p[1].handoff_id, source_version=2, capability=p[5])
    assert p[9]._entries == {}


def test_consume_rechecks_live_clock_after_slow_source(make_triage, monkeypatch):
    p=setup("Where is the report?",make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    times=iter((NOW,NOW,NOW+timedelta(seconds=21)))
    monkeypatch.setattr(p[9], "_time", lambda value: value if value is not None else next(times))
    with pytest.raises(HandoffError, match="fixture_receipt_expired"):
        p[9].consume(ready.receipt_id, expected_version=ready.state_version,
            capability=p[6], context=p[2].context)


@pytest.mark.parametrize("source_index", [0, 1])
def test_forged_source_lineage_is_not_accepted(make_triage, source_index):
    p,_,_=policy_case(make_triage)
    claim=p[10].claims[0]
    sources=list(claim.sources)
    sources[source_index]=sources[source_index].model_copy(update={"source_id":"SYN-FORGED-SOURCE"})
    p[10]=p[10].model_copy(update={"claims":(claim.model_copy(update={"sources":tuple(sources)}),)})
    declared(p)
    with pytest.raises(HandoffError, match="fixture_policy_claim_mismatch"):
        prepare(p)


def test_policy_fixture_cannot_masquerade_as_actual_triage(make_triage):
    p,_,_=policy_case(make_triage)
    p[10]=p[10].model_copy(update={"agent":"triage", "agent_version":"1.0"})
    with pytest.raises(HandoffError, match="fixture_claim_not_eligible"):
        declared(p)


def test_policy_change_during_knowledge_fixture_discards_result(make_triage):
    from cdit_support_mao.agents.triage.fixture_policy import SyntheticPolicyCatalog
    p,_,_=policy_case(make_triage)
    declared(p)
    ready=accept(p,prepare(p))
    provision=object()
    replacement=SyntheticPolicyCatalog(policy_version="SYN-POLICY-1",provision_capability=provision)
    replacement.add({"rule_id":"SYN-RULE-OTHER", "exact_report":"Where is the report?",
        "category":"report-navigation", "urgency":"low", "proposed_destination":"knowledge_review"},capability=provision)
    replacement.seal(capability=provision)
    def fixture_call(candidate, ack):
        p[9]._policy_catalog=replacement
        return "MUST_NOT_ESCAPE"
    with pytest.raises(HandoffError, match="fixture_policy_claim_mismatch"):
        p[9].run_fixture(ready.receipt_id, expected_version=ready.state_version,
            capability=p[6], context=p[2].context, fixture_call=fixture_call, now=NOW)


def test_malformed_context_in_standin_fails_without_echo_or_serializer_warning(make_triage):
    import warnings
    p=list(setup("Where is the report?",make_triage))
    marker="SYNTHETIC-PRIVATE-MARKER"
    p[10]=p[10].model_copy(update={"context":marker})
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with pytest.raises(HandoffError, match="invalid_fixture_triage") as error:
            declared(p)
    assert marker not in str(error.value) and not caught
