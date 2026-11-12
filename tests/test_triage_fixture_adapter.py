"""Synthetic A2 fixture adapter; these tests do not establish actual approval."""
from datetime import timedelta

import pytest
from pydantic import ValidationError

from cdit_support_mao.agents.coordinator.handoff import HandoffError
from cdit_support_mao.agents.triage.fixture_adapter import SyntheticAdapterEnvelope, derive_synthetic_stand_in
from cdit_support_mao.contracts import AgentStatus, ClaimLabel
from test_triage_fixture_policy import MESSAGE, NOW, catalog, fixture


def derive(p, policy, **overrides):
    args = dict(handoff_id=p[1].handoff_id, expected_version=p[1].state_version,
        receiver_capability=p[5], context=p[2].context, item_index=1, catalog=policy, now=NOW)
    args.update(overrides)
    return derive_synthetic_stand_in(p[0], **args)


def test_derived_stand_in_preserves_inference_source_and_fixture_disclaimers():
    p = fixture("  " + MESSAGE + "  ")
    out = derive(p, catalog(p[3]))
    triage, proposal = out.stand_in, out.proposal
    assert not out.stand_in_is_actual_a2 and not out.operational_policy_approved
    assert not out.shared_handoff_accepted and not out.dispatch_authorized and out.human_review_required
    assert triage.agent == "synthetic-triage-stand-in" and triage.status is AgentStatus.COMPLETED
    assert triage.case_summary == MESSAGE and triage.context == p[2].context
    assert triage.category == proposal.proposed_category and triage.urgency == "low"
    assert triage.claims[0].label is ClaimLabel.INFERENCE
    assert triage.claims[0].sources == (proposal.reported_source, proposal.policy_source)
    assert triage.claims[0].basis == f"synthetic fixture policy sha256:{proposal.fixture_digest}"
    assert p[2].untrusted_message[proposal.start_codepoint:proposal.end_codepoint] == MESSAGE
    assert not proposal.source_report_is_verified_event and proposal.semantic_completeness == "unknown"
    assert MESSAGE not in repr(out)


def test_absent_wrong_version_and_nonmatching_fixture_abstain():
    p = fixture()
    for policy in (None, catalog(p[3], version="SYN-POLICY-2"), catalog(p[3], rules=[])):
        with pytest.raises(HandoffError, match="fixture_adapter_abstained"):
            derive(p, policy)


@pytest.mark.parametrize("urgency", ["medium", "high"])
def test_higher_urgency_never_becomes_fixture_stand_in(urgency):
    p = fixture()
    rule = {"rule_id":"SYN-RULE-1", "exact_report":MESSAGE, "category":"security",
        "urgency":urgency, "proposed_destination":"knowledge_review"}
    with pytest.raises(HandoffError, match="fixture_adapter_abstained"):
        derive(p, catalog(p[3], rules=[rule]))


def test_multi_or_conflicting_fixture_never_becomes_stand_in():
    p = fixture(MESSAGE + "; another issue")
    with pytest.raises(HandoffError, match="fixture_adapter_abstained"):
        derive(p, catalog(p[3]))
    p = fixture()
    rules = [{"rule_id":"SYN-RULE-1", "exact_report":MESSAGE, "category":"report-navigation",
              "urgency":"low", "proposed_destination":"knowledge_review"},
             {"rule_id":"SYN-RULE-2", "exact_report":MESSAGE, "category":"security",
              "urgency":"high", "proposed_destination":"knowledge_review"}]
    with pytest.raises(HandoffError, match="fixture_adapter_abstained"):
        derive(p, catalog(p[3], rules=rules))


def test_wrong_receiver_stale_case_or_expired_handoff_blocks_adapter():
    p = fixture()
    with pytest.raises(HandoffError, match="unauthorized_receiver"):
        derive(p, catalog(p[3]), receiver_capability=object())
    p[6].set_version("SYN-CASE-01", 2, expected_version=1, capability=p[3])
    with pytest.raises(HandoffError, match="stale_case_version"):
        derive(p, catalog(p[3]))
    p = fixture()
    with pytest.raises(HandoffError, match="handoff_expired_manual_recovery"):
        derive(p, catalog(p[3]), now=NOW + timedelta(seconds=30))


def test_forged_envelope_never_satisfies_full_revalidation():
    p = fixture()
    out = derive(p, catalog(p[3]))
    bogus = out.stand_in.model_copy(update={"category":"security"})
    with pytest.raises(ValidationError):
        SyntheticAdapterEnvelope.model_validate(out.model_copy(update={"stand_in":bogus}).model_dump())
    forged = out.proposal.model_copy(update={"proposed_urgency":"high"})
    with pytest.raises(ValidationError):
        SyntheticAdapterEnvelope.model_validate(out.model_copy(update={"proposal":forged}).model_dump())
    with pytest.raises(TypeError):
        derive(p, catalog(p[3]), proposal=out.proposal)


def test_late_cancel_prevents_adapter_return(monkeypatch):
    import cdit_support_mao.agents.triage.fixture_adapter as adapter
    p = fixture()
    original = adapter.extract_request_parts
    def cancel_after_read(*args, **kwargs):
        value = original(*args, **kwargs)
        p[0].cancel(p[1].handoff_id, expected_version=p[1].state_version, capability=p[4], now=NOW)
        return value
    monkeypatch.setattr(adapter, "extract_request_parts", cancel_after_read)
    with pytest.raises(HandoffError, match="stale_handoff_version"):
        derive(p, catalog(p[3]))


def test_real_clock_mode_rechecks_time_and_rejects_expiry_mid_operation(monkeypatch):
    p = fixture()
    calls = []
    def clock(value):
        calls.append(value)
        assert value is None
        return NOW if len(calls) <= 5 else NOW + timedelta(seconds=30)
    monkeypatch.setattr(p[0], "_time", clock)
    with pytest.raises(HandoffError, match="handoff_expired_manual_recovery"):
        derive(p, catalog(p[3]), now=None)
    assert len(calls) >= 6


def test_adapter_policy_inference_reaches_actual_knowledge_only_via_declared_fixture(knowledge_agent):
    from datetime import date
    from cdit_support_mao.agents.coordinator.knowledge_handoff import FixtureA2Declarations, KnowledgeFixtureRegistry
    message = "Site user cannot find where to export the site enrollment report."
    p = fixture(message)
    rule = {"rule_id":"SYN-RULE-REPORT", "exact_report":message, "category":"report-navigation",
        "urgency":"low", "proposed_destination":"knowledge_review"}
    policy = catalog(p[3], rules=[rule])
    envelope = derive(p, policy)
    sender, receiver, declaration_capability = object(), object(), object()
    declarations = FixtureA2Declarations(provisioning_capability=declaration_capability)
    ledger = KnowledgeFixtureRegistry(source_registry=p[0], triage_capability=p[5],
        sender_capability=sender, knowledge_capability=receiver, declarations=declarations,
        timeout_seconds=20, policy_catalog=policy)
    with pytest.raises(HandoffError, match="fixture_declaration_missing"):
        ledger.prepare(envelope.stand_in, source_handoff_id=p[1].handoff_id,
            source_version=p[1].state_version, capability=sender, now=NOW)
    declarations.declare(source_handoff_id=p[1].handoff_id, source_version=p[1].state_version,
        contribution=envelope.stand_in, capability=declaration_capability,
        next_stage="knowledge_fixture", single_independent_nonurgent=True)
    pending = ledger.prepare(envelope.stand_in, source_handoff_id=p[1].handoff_id,
        source_version=p[1].state_version, capability=sender, now=NOW)
    assert pending.fixture_only and pending.fixture_basis == "policy_inference"
    assert pending.fixture_policy_digest == envelope.proposal.fixture_digest
    ready = ledger.acknowledge(pending.receipt_id, expected_version=pending.state_version,
        capability=receiver, context=p[2].context, now=NOW)
    result = ledger.run_fixture(ready.receipt_id, expected_version=ready.state_version,
        capability=receiver, context=p[2].context, now=NOW,
        fixture_call=lambda triage, ack: knowledge_agent.run(p[2].context, triage,
            acknowledged=ack, as_of=date(2026,11,3), now=NOW))
    assert result.status is AgentStatus.COMPLETED and result.human_review_required
    assert result.passages[0].source.cite() == "KB-NAV-001 v2.1 #s1"
    assert not envelope.stand_in_is_actual_a2 and not envelope.shared_handoff_accepted
    assert not envelope.dispatch_authorized and not envelope.proposal.downstream_allowed


def test_registry_recomputes_policy_even_if_wrong_stand_in_is_declared():
    from cdit_support_mao.agents.coordinator.knowledge_handoff import FixtureA2Declarations, KnowledgeFixtureRegistry
    p = fixture()
    policy = catalog(p[3])
    envelope = derive(p, policy)
    forged = envelope.stand_in.model_copy(update={"category":"security"})
    sender, receiver, declaration_capability = object(), object(), object()
    declarations = FixtureA2Declarations(provisioning_capability=declaration_capability)
    ledger = KnowledgeFixtureRegistry(source_registry=p[0], triage_capability=p[5],
        sender_capability=sender, knowledge_capability=receiver, declarations=declarations,
        timeout_seconds=20, policy_catalog=policy)
    declarations.declare(source_handoff_id=p[1].handoff_id, source_version=p[1].state_version,
        contribution=forged, capability=declaration_capability,
        next_stage="knowledge_fixture", single_independent_nonurgent=True)
    with pytest.raises(HandoffError, match="fixture_policy_claim_mismatch"):
        ledger.prepare(forged, source_handoff_id=p[1].handoff_id,
            source_version=p[1].state_version, capability=sender, now=NOW)


def ready_knowledge_fixture(message="Site user cannot find where to export the site enrollment report."):
    from cdit_support_mao.agents.coordinator.knowledge_handoff import FixtureA2Declarations, KnowledgeFixtureRegistry
    p = fixture(message)
    rule = {"rule_id":"SYN-RULE-REPORT", "exact_report":message, "category":"report-navigation",
        "urgency":"low", "proposed_destination":"knowledge_review"}
    policy = catalog(p[3], rules=[rule])
    envelope = derive(p, policy)
    sender, receiver, declaration_capability = object(), object(), object()
    declarations = FixtureA2Declarations(provisioning_capability=declaration_capability)
    ledger = KnowledgeFixtureRegistry(source_registry=p[0], triage_capability=p[5],
        sender_capability=sender, knowledge_capability=receiver, declarations=declarations,
        timeout_seconds=20, policy_catalog=policy)
    declarations.declare(source_handoff_id=p[1].handoff_id, source_version=p[1].state_version,
        contribution=envelope.stand_in, capability=declaration_capability,
        next_stage="knowledge_fixture", single_independent_nonurgent=True)
    pending = ledger.prepare(envelope.stand_in, source_handoff_id=p[1].handoff_id,
        source_version=p[1].state_version, capability=sender, now=NOW)
    ready = ledger.acknowledge(pending.receipt_id, expected_version=pending.state_version,
        capability=receiver, context=p[2].context, now=NOW)
    return p, envelope, ledger, ready, receiver, sender


def test_validated_knowledge_fixture_retains_receipt_source_and_policy_provenance(knowledge_agent, corpus):
    from datetime import date
    from cdit_support_mao.agents.triage.fixture_adapter import run_fixture_knowledge
    p, envelope, ledger, ready, receiver, _ = ready_knowledge_fixture()
    evidence = run_fixture_knowledge(ledger, receipt=ready, capability=receiver, context=p[2].context,
        envelope=envelope, agent=knowledge_agent, corpus=corpus, as_of=date(2026,11,3), now=NOW)
    assert evidence.fixture_only and evidence.human_review_required and evidence.unvalidated_metadata_untrusted
    assert not evidence.shared_handoff_accepted and not evidence.operational_policy_approved
    assert not evidence.semantic_entailment_verified and not evidence.downstream_allowed
    assert evidence.triage_contribution_id == envelope.stand_in.contribution_id
    assert evidence.triage_digest == ready.contribution_digest
    assert evidence.fixture_policy_digest == envelope.proposal.fixture_digest
    assert evidence.triage_inference == envelope.stand_in.claims[0]
    assert evidence.triage_inference.sources == (envelope.proposal.reported_source, envelope.proposal.policy_source)
    assert (evidence.reported_start_codepoint, evidence.reported_end_codepoint) == (
        envelope.proposal.start_codepoint, envelope.proposal.end_codepoint)
    assert evidence.source_handoff_id == p[1].handoff_id and evidence.source_set_version == corpus.source_set_version
    assert evidence.result.passages[0].source.cite() == "KB-NAV-001 v2.1 #s1"


@pytest.mark.parametrize("mutation", ["input_ref", "source_set", "checkpoint", "source_text", "source_date", "status"])
def test_knowledge_validator_rejects_forged_stale_or_mismatched_output(knowledge_agent, corpus, monkeypatch, mutation):
    from datetime import date
    from cdit_support_mao.agents.triage.fixture_adapter import run_fixture_knowledge
    from cdit_support_mao.contracts import CheckpointOutcome, ReasonCode
    p, envelope, ledger, ready, receiver, _ = ready_knowledge_fixture()
    actual = knowledge_agent.run(p[2].context, envelope.stand_in,
        acknowledged={envelope.stand_in.contribution_id}, as_of=date(2026,11,3), now=NOW)
    if mutation == "input_ref":
        changed = actual.model_copy(update={"input_refs":()})
    elif mutation == "source_set":
        changed = actual.model_copy(update={"source_set_version":"SRC-FAKE"})
    elif mutation == "checkpoint":
        changed = actual.model_copy(update={"checkpoint":CheckpointOutcome(checkpoint="A2", passed=True)})
    elif mutation == "status":
        changed = actual.model_copy(update={"status":AgentStatus.BLOCKED, "checkpoint":CheckpointOutcome(
            checkpoint="A3", passed=False, reason_codes=(ReasonCode.UPSTREAM_BLOCKED,))})
    else:
        passage = actual.passages[0]
        field, value = ("text", "fabricated text") if mutation == "source_text" else ("review_due", date(2020,1,1))
        changed = actual.model_copy(update={"passages":(passage.model_copy(update={field:value}),)})
    monkeypatch.setattr(knowledge_agent, "run", lambda *args, **kwargs: changed)
    with pytest.raises(HandoffError, match="invalid_fixture_knowledge_result|knowledge_fixture_result_unusable|knowledge_fixture_source_mismatch"):
        run_fixture_knowledge(ledger, receipt=ready, capability=receiver, context=p[2].context,
            envelope=envelope, agent=knowledge_agent, corpus=corpus, as_of=date(2026,11,3), now=NOW)


def test_knowledge_validator_rejects_changed_receipt_digest_or_wrong_corpus(knowledge_agent, corpus):
    from dataclasses import replace
    from datetime import date
    from cdit_support_mao.agents.triage.fixture_adapter import run_fixture_knowledge
    from cdit_support_mao.agents.knowledge.corpus import KnowledgeCorpus
    p, envelope, ledger, ready, receiver, _ = ready_knowledge_fixture()
    with pytest.raises(HandoffError, match="knowledge_fixture_binding_mismatch"):
        run_fixture_knowledge(ledger, receipt=replace(ready, fixture_policy_digest="0" * 64),
            capability=receiver, context=p[2].context, envelope=envelope, agent=knowledge_agent,
            corpus=corpus, as_of=date(2026,11,3), now=NOW)
    wrong = KnowledgeCorpus(articles=corpus.articles, source_set_version="SRC-FAKE")
    with pytest.raises(HandoffError, match="knowledge_fixture_source_set_mismatch"):
        run_fixture_knowledge(ledger, receipt=ready, capability=receiver, context=p[2].context,
            envelope=envelope, agent=knowledge_agent, corpus=wrong, as_of=date(2026,11,3), now=NOW)


def test_knowledge_validator_discards_result_if_source_cancelled_during_real_call(knowledge_agent, corpus, monkeypatch):
    from datetime import date
    from cdit_support_mao.agents.triage.fixture_adapter import run_fixture_knowledge
    p, envelope, ledger, ready, receiver, _ = ready_knowledge_fixture()
    original = knowledge_agent.run
    def run_and_cancel(*args, **kwargs):
        result = original(*args, **kwargs)
        p[0].cancel(p[1].handoff_id, expected_version=p[1].state_version, capability=p[4], now=NOW)
        return result
    monkeypatch.setattr(knowledge_agent, "run", run_and_cancel)
    with pytest.raises(HandoffError, match="stale_handoff_version"):
        run_fixture_knowledge(ledger, receipt=ready, capability=receiver, context=p[2].context,
            envelope=envelope, agent=knowledge_agent, corpus=corpus, as_of=date(2026,11,3), now=NOW)


def test_knowledge_validator_rejects_fabricated_extra_verified_claim(knowledge_agent, corpus, monkeypatch):
    from datetime import date
    from cdit_support_mao.agents.triage.fixture_adapter import run_fixture_knowledge
    from cdit_support_mao.contracts.common import Claim, ClaimLabel, ConfidenceBand
    p, envelope, ledger, ready, receiver, _ = ready_knowledge_fixture()
    actual = knowledge_agent.run(p[2].context, envelope.stand_in,
        acknowledged={envelope.stand_in.contribution_id}, as_of=date(2026,11,3), now=NOW)
    fake = Claim(statement="An unsupported incident occurred.", label=ClaimLabel.VERIFIED,
        sources=(actual.passages[0].source,), confidence=ConfidenceBand.HIGH)
    changed = actual.model_copy(update={"claims":actual.claims + (fake,)})
    monkeypatch.setattr(knowledge_agent, "run", lambda *args, **kwargs: changed)
    with pytest.raises(HandoffError, match="knowledge_fixture_claim_mismatch"):
        run_fixture_knowledge(ledger, receipt=ready, capability=receiver, context=p[2].context,
            envelope=envelope, agent=knowledge_agent, corpus=corpus, as_of=date(2026,11,3), now=NOW)


def test_knowledge_validator_recomputes_lexical_coverage(knowledge_agent, corpus, monkeypatch):
    from datetime import date
    from cdit_support_mao.agents.triage.fixture_adapter import run_fixture_knowledge
    from cdit_support_mao.contracts.common import ConfidenceBand
    p, envelope, ledger, ready, receiver, _ = ready_knowledge_fixture()
    actual = knowledge_agent.run(p[2].context, envelope.stand_in,
        acknowledged={envelope.stand_in.contribution_id}, as_of=date(2026,11,3), now=NOW)
    other_score = 0.1234 if actual.passages[0].relevance != 0.1234 else 0.2345
    forged_passage = actual.passages[0].model_copy(update={"relevance":other_score, "relevance_band":ConfidenceBand.LOW})
    changed = actual.model_copy(update={"passages":(forged_passage,)})
    monkeypatch.setattr(knowledge_agent, "run", lambda *args, **kwargs: changed)
    with pytest.raises(HandoffError, match="knowledge_fixture_relevance_mismatch"):
        run_fixture_knowledge(ledger, receipt=ready, capability=receiver, context=p[2].context,
            envelope=envelope, agent=knowledge_agent, corpus=corpus, as_of=date(2026,11,3), now=NOW)


def test_knowledge_validator_rejects_corpus_content_with_reused_source_version(knowledge_agent, corpus):
    from datetime import date
    from cdit_support_mao.agents.knowledge.corpus import KnowledgeCorpus
    from cdit_support_mao.agents.triage.fixture_adapter import run_fixture_knowledge
    p, envelope, ledger, ready, receiver, _ = ready_knowledge_fixture()
    mutated = corpus.articles[0].model_copy(update={"title":"changed synthetic title"})
    wrong = KnowledgeCorpus(articles=(mutated,) + corpus.articles[1:], source_set_version=corpus.source_set_version)
    with pytest.raises(HandoffError, match="knowledge_fixture_source_set_mismatch"):
        run_fixture_knowledge(ledger, receipt=ready, capability=receiver, context=p[2].context,
            envelope=envelope, agent=knowledge_agent, corpus=wrong, as_of=date(2026,11,3), now=NOW)


def test_knowledge_validator_rejects_weak_but_genuine_source(knowledge_agent, corpus, monkeypatch):
    from datetime import date
    from cdit_support_mao.agents.knowledge.agent import KnowledgeAgent
    from cdit_support_mao.agents.knowledge.retrieval import LexicalIndex
    from cdit_support_mao.agents.triage.fixture_adapter import run_fixture_knowledge
    from cdit_support_mao.contracts import CheckpointOutcome
    message = "export report alphaone betatwo gammathree deltafour epsilfive zetatoken"
    p, envelope, ledger, ready, receiver, _ = ready_knowledge_fixture(message)
    original = knowledge_agent.run(p[2].context, envelope.stand_in,
        acknowledged={envelope.stand_in.contribution_id}, as_of=date(2026,11,3), now=NOW)
    score = next(x for x in LexicalIndex(corpus).search(message) if x.article.doc_id == "KB-NAV-001" and x.article.version == "2.1")
    assert score.coverage < 0.6
    passage = KnowledgeAgent._passage(score, 1)
    changed = original.model_copy(update={"status":AgentStatus.COMPLETED,
        "checkpoint":CheckpointOutcome(checkpoint="A3", passed=True), "passages":(passage,),
        "injection_flags":(), "conflicts":(), "claims":()})
    monkeypatch.setattr(knowledge_agent, "run", lambda *args, **kwargs: changed)
    with pytest.raises(HandoffError, match="knowledge_fixture_weak_evidence"):
        run_fixture_knowledge(ledger, receipt=ready, capability=receiver, context=p[2].context,
            envelope=envelope, agent=knowledge_agent, corpus=corpus, as_of=date(2026,11,3), now=NOW)


def test_knowledge_validator_detects_suppressed_fixture_injection_signal(knowledge_agent, corpus, monkeypatch):
    from datetime import date
    from cdit_support_mao.agents.knowledge.agent import KnowledgeAgent
    from cdit_support_mao.agents.knowledge.retrieval import LexicalIndex
    from cdit_support_mao.agents.triage.fixture_adapter import run_fixture_knowledge
    from cdit_support_mao.contracts import CheckpointOutcome
    message = "How do I change my email notification preferences?"
    p, envelope, ledger, ready, receiver, _ = ready_knowledge_fixture(message)
    original = knowledge_agent.run(p[2].context, envelope.stand_in,
        acknowledged={envelope.stand_in.contribution_id}, as_of=date(2026,11,3), now=NOW)
    score = next(x for x in LexicalIndex(corpus).search(message) if x.article.doc_id == "KB-NTF-050")
    assert score.coverage >= 0.6 and len(score.matched_terms) >= 2
    passage = KnowledgeAgent._passage(score, 1)
    changed = original.model_copy(update={"status":AgentStatus.COMPLETED,
        "checkpoint":CheckpointOutcome(checkpoint="A3", passed=True), "passages":(passage,),
        "injection_flags":(), "conflicts":(), "claims":()})
    monkeypatch.setattr(knowledge_agent, "run", lambda *args, **kwargs: changed)
    with pytest.raises(HandoffError, match="knowledge_fixture_source_injection"):
        run_fixture_knowledge(ledger, receipt=ready, capability=receiver, context=p[2].context,
            envelope=envelope, agent=knowledge_agent, corpus=corpus, as_of=date(2026,11,3), now=NOW)
