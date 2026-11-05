"""Fixture-only adapter from a recomputed inference to an A2 test stand-in.

A COMPLETED checkpoint here exists only to exercise the local fixture consumer;
it is not an approved A2, human decision, production authority or Shared handoff.
A separate capability-provisioned declaration and receiver acknowledgement are
required before the Coordinator fixture may pass this stand-in to Knowledge.
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime
from typing import Literal

from pydantic import Field, ValidationError, model_validator

from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.coordinator.knowledge_handoff import KnowledgeFixtureCheckpoint, KnowledgeFixtureRegistry
from cdit_support_mao.agents.knowledge.agent import KnowledgeAgent
from cdit_support_mao.agents.knowledge.corpus import KnowledgeCorpus, ineligibility_reason
from cdit_support_mao.agents.knowledge.retrieval import LexicalIndex
from cdit_support_mao.agents.knowledge.injection import scan_for_injection
from cdit_support_mao.agents.triage.fixture_policy import (
    FixturePolicyProposal, SyntheticPolicyCatalog, propose_from_synthetic_policy,
)
from cdit_support_mao.agents.triage.segment import extract_request_parts
from cdit_support_mao.contracts.common import (
    AgentStatus, CheckpointOutcome, Claim, ClaimLabel, ConfidenceBand, RunContext,
    PROVISIONAL_BAND_THRESHOLDS, SourceKind, StrictModel, band_for, stable_id,
)
from cdit_support_mao.contracts.handoffs import KnowledgeResult, TriageHandoff


def _claim(proposal: FixturePolicyProposal) -> Claim:
    return Claim(
        statement=f"Synthetic fixture inference: category={proposal.proposed_category}; urgency={proposal.proposed_urgency}",
        label=ClaimLabel.INFERENCE,
        sources=(proposal.reported_source, proposal.policy_source),
        basis=f"synthetic fixture policy sha256:{proposal.fixture_digest}",
        confidence=ConfidenceBand.LOW,
    )


class SyntheticAdapterEnvelope(StrictModel):
    """Snapshot containing the original source-bound proposal and test stand-in.

    Both are potentially stale immediately after return. Serialized payloads
    contain synthetic case text; do not put them into metadata-only logs.
    """
    proposal: FixturePolicyProposal
    stand_in: TriageHandoff = Field(repr=False)
    artifact: Literal["synthetic_fixture_stand_in"] = "synthetic_fixture_stand_in"
    stand_in_is_actual_a2: Literal[False] = False
    operational_policy_approved: Literal[False] = False
    shared_handoff_accepted: Literal[False] = False
    human_review_required: Literal[True] = True
    dispatch_authorized: Literal[False] = False

    @model_validator(mode="after")
    def check_binding(self) -> SyntheticAdapterEnvelope:
        proposal, triage = self.proposal, self.stand_in
        if (proposal.status != "synthetic_fixture_inference" or proposal.reason != "exact_fixture_rule"
                or proposal.item_count != 1 or proposal.item_index != 1
                or proposal.proposed_urgency != "low" or proposal.proposed_destination != "knowledge_review"
                or proposal.policy_source is None or proposal.fixture_digest is None
                or triage.context != proposal.context or triage.agent != "synthetic-triage-stand-in"
                or triage.agent_version != "fixture-0.1" or triage.category != proposal.proposed_category
                or triage.urgency != "low" or triage.product_area is not None
                or triage.status is not AgentStatus.COMPLETED or triage.checkpoint.checkpoint != "A2"
                or not triage.checkpoint.passed or triage.claims != (_claim(proposal),)
                or triage.unknowns or triage.case_facts or triage.missing_facts
                or triage.category_confidence is not ConfidenceBand.LOW
                or triage.confidence is not ConfidenceBand.LOW):
            raise ValueError("invalid_synthetic_adapter_binding")
        return self


def derive_synthetic_stand_in(
    registry: HandoffRegistry, *, handoff_id: str, expected_version: int,
    receiver_capability: object, context: RunContext, item_index: int,
    catalog: SyntheticPolicyCatalog, now: datetime | None = None,
) -> SyntheticAdapterEnvelope:
    """Recompute policy + case evidence and produce a non-dispatching stand-in.

    Only an explicitly provisioned sealed fixture catalog can produce a match.
    Exact match does not prove semantic completeness, truth, real policy or
    reviewer approval. The time override is only a trusted fixture hook. No
    caller-supplied proposal, classification, summary or claim is accepted.
    The downstream fixture registry must independently recompute evidence and
    explicitly declare/acknowledge the exact contribution before using it.
    """
    timestamp = now if now is not None else datetime.now(UTC)
    if not isinstance(timestamp, datetime) or timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp must be timezone-aware")
    kwargs = dict(handoff_id=handoff_id, expected_version=expected_version,
        receiver_capability=receiver_capability, context=context, item_index=item_index,
        catalog=catalog, now=now)
    proposal = propose_from_synthetic_policy(registry, **kwargs)
    if (proposal.status != "synthetic_fixture_inference" or proposal.item_count != 1
            or proposal.item_index != 1 or proposal.proposed_urgency != "low"
            or proposal.proposed_destination != "knowledge_review"):
        raise HandoffError("fixture_adapter_abstained")
    parts = extract_request_parts(registry, handoff_id=handoff_id, expected_version=expected_version,
        receiver_capability=receiver_capability, context=context, now=now)
    if (parts.trace_id != proposal.trace_id or parts.handoff_id != proposal.handoff_id
            or parts.context != proposal.context or parts.status != "segmented_needs_classification"
            or len(parts.items) != 1 or parts.items[0].source != proposal.reported_source
            or parts.items[0].start_codepoint != proposal.start_codepoint
            or parts.items[0].end_codepoint != proposal.end_codepoint):
        raise HandoffError("fixture_adapter_source_mismatch")
    stand_in = TriageHandoff(
        contribution_id=stable_id("SYN-A2", proposal.trace_id, proposal.handoff_id,
            proposal.handoff_state_version, proposal.fixture_digest, proposal.policy_source.source_id),
        agent="synthetic-triage-stand-in", agent_version="fixture-0.1", context=proposal.context,
        created_at=timestamp, status=AgentStatus.COMPLETED,
        checkpoint=CheckpointOutcome(checkpoint="A2", passed=True), claims=(_claim(proposal),),
        confidence=ConfidenceBand.LOW,
        confidence_rationale="Uncalibrated synthetic test inference; not policy or human approval.",
        case_summary=parts.items[0].reported_text, category=proposal.proposed_category,
        category_confidence=ConfidenceBand.LOW, urgency="low",
    )
    envelope = SyntheticAdapterEnvelope(proposal=proposal, stand_in=stand_in)
    again = propose_from_synthetic_policy(registry, **kwargs)
    if again != proposal:
        raise HandoffError("fixture_adapter_evidence_changed")
    return envelope


class SyntheticKnowledgeEvidence(StrictModel):
    """Validated synthetic fixture output, not a production Knowledge handoff."""
    receipt_id: str
    source_handoff_id: str
    source_version: int = Field(strict=True, ge=2)
    triage_contribution_id: str
    triage_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    fixture_policy_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    triage_inference: Claim
    reported_start_codepoint: int = Field(strict=True, ge=0)
    reported_end_codepoint: int = Field(strict=True, ge=1)
    source_set_version: str
    result: KnowledgeResult = Field(repr=False)
    fixture_only: Literal[True] = True
    shared_handoff_accepted: Literal[False] = False
    operational_policy_approved: Literal[False] = False
    semantic_entailment_verified: Literal[False] = False
    unvalidated_metadata_untrusted: Literal[True] = True
    downstream_allowed: Literal[False] = False
    human_review_required: Literal[True] = True


def run_fixture_knowledge(
    ledger: KnowledgeFixtureRegistry, *, receipt: KnowledgeFixtureCheckpoint,
    capability: object, context: RunContext, envelope: SyntheticAdapterEnvelope,
    agent: KnowledgeAgent, corpus: KnowledgeCorpus, as_of: date, now: datetime | None = None,
) -> SyntheticKnowledgeEvidence:
    """Run the local fixture callback and validate its returned KnowledgeResult.

    All dependencies are trusted synthetic fixtures, not production identity or
    authorization. Receipt state is rechecked by the fixture ledger before and
    after retrieval and after validation. Content/source-set checks do not prove
    relevance, truth, semantic entailment, or Shared acceptance. Other free-text
    metadata remains untrusted and cannot drive downstream instructions. Time override
    is trusted fixture-only; snapshots are not durable after return.
    """
    if (not isinstance(ledger, KnowledgeFixtureRegistry) or not isinstance(receipt, KnowledgeFixtureCheckpoint)
            or not isinstance(agent, KnowledgeAgent) or not isinstance(corpus, KnowledgeCorpus)
            or type(as_of) is not date):
        raise HandoffError("invalid_knowledge_fixture_setup")
    try:
        if not isinstance(envelope, SyntheticAdapterEnvelope):
            raise HandoffError("invalid_adapter_envelope")
        envelope = SyntheticAdapterEnvelope.model_validate(envelope.model_dump())
    except (ValidationError, ValueError, TypeError):
        raise HandoffError("invalid_adapter_envelope") from None
    proposal, triage = envelope.proposal, envelope.stand_in
    canonical_corpus = json.dumps([article.model_dump(mode="json") for article in corpus.articles],
        sort_keys=True, separators=(",", ":"))
    corpus_digest = hashlib.sha256(canonical_corpus.encode("utf-8")).hexdigest()[:12].upper()
    if corpus.source_set_version != f"SRC-{corpus_digest}":
        raise HandoffError("knowledge_fixture_source_set_mismatch")
    triage_digest = hashlib.sha256(triage.model_dump_json().encode("utf-8")).hexdigest()
    if (receipt.context != context or triage.context != context or receipt.fixture_only is not True
            or receipt.state != "accepted" or receipt.recipient != "knowledge_fixture"
            or receipt.source_handoff_id != proposal.handoff_id
            or receipt.source_version != proposal.handoff_state_version
            or receipt.contribution_id != triage.contribution_id or receipt.contribution_digest != triage_digest
            or receipt.fixture_basis != "policy_inference" or receipt.fixture_policy_digest != proposal.fixture_digest
            or agent.source_set_version != corpus.source_set_version):
        raise HandoffError("knowledge_fixture_binding_mismatch")
    result = ledger.run_fixture(receipt.receipt_id, expected_version=receipt.state_version,
        capability=capability, context=context, now=now,
        fixture_call=lambda current, ack: agent.run(context, current, acknowledged=ack, as_of=as_of, now=now))
    if not isinstance(result, KnowledgeResult):
        raise HandoffError("invalid_fixture_knowledge_result")
    try:
        result = KnowledgeResult.model_validate(result.model_dump())
    except (ValidationError, ValueError, TypeError):
        raise HandoffError("invalid_fixture_knowledge_result") from None
    if (result.context != context or result.source_set_version != corpus.source_set_version
            or result.status is not AgentStatus.COMPLETED or result.checkpoint.checkpoint != "A3"
            or not result.checkpoint.passed or result.input_refs != (triage.as_input_ref(),)
            or result.conflicts or result.injection_flags or not result.passages):
        raise HandoffError("knowledge_fixture_result_unusable")
    index = LexicalIndex(corpus)
    scored = {(entry.article.doc_id, entry.article.version, entry.section.section_id): entry
        for entry in index.search(triage.case_summary)}
    minimum_coverage = max(PROVISIONAL_BAND_THRESHOLDS["medium"], agent._min_relevance)
    minimum_terms = min(2, max(1, index.query_term_count(triage.case_summary)))
    canonical_claims = []
    for passage in result.passages:
        expected_score = scored.get((passage.doc_id, passage.version, passage.section_id))
        if (expected_score is None or passage.relevance != expected_score.coverage
                or passage.relevance_band is not band_for(expected_score.coverage)):
            raise HandoffError("knowledge_fixture_relevance_mismatch")
        if expected_score.coverage < minimum_coverage or len(expected_score.matched_terms) < minimum_terms:
            raise HandoffError("knowledge_fixture_weak_evidence")
        texts = (passage.heading, passage.text, *(x.text for x in passage.steps),
            *(x.prompt for x in passage.information_needed), *(x.text for x in passage.stop_conditions))
        if scan_for_injection(*texts):
            raise HandoffError("knowledge_fixture_source_injection")
        articles = tuple(article for article in corpus.articles
            if article.doc_id == passage.doc_id and article.version == passage.version)
        if len(articles) != 1 or ineligibility_reason(articles[0], as_of) is not None:
            raise HandoffError("knowledge_fixture_source_unusable")
        article = articles[0]
        sections = tuple(section for section in article.sections if section.section_id == passage.section_id)
        if (len(sections) != 1 or passage.source.kind is not SourceKind.KB_SECTION
                or passage.source.source_id != article.doc_id or passage.source.version != article.version
                or passage.source.locator != sections[0].section_id or passage.title != article.title
                or passage.topic != article.topic or passage.product_area != article.product_area
                or passage.effective_date != article.effective_date or passage.review_due != article.review_due
                or passage.heading != sections[0].heading or passage.text != sections[0].text
                or tuple((x.step_id, x.action_type, x.text) for x in passage.steps)
                   != tuple((x.step_id, x.action_type, x.text) for x in sections[0].steps)
                or tuple((x.field, x.prompt) for x in passage.information_needed)
                   != tuple((x.field, x.prompt) for x in sections[0].information_needed)
                or tuple((x.condition_id, x.text) for x in passage.stop_conditions)
                   != tuple((x.condition_id, x.text) for x in sections[0].stop_conditions)):
            raise HandoffError("knowledge_fixture_source_mismatch")
        eligible = corpus.eligible_articles(as_of)
        if (sum(a.doc_id == article.doc_id for a in eligible) != 1
                or any(a.topic == article.topic and a.doc_id != article.doc_id for a in eligible)):
            raise HandoffError("knowledge_fixture_conflicting_sources")
        canonical_claims.append(Claim(
            statement=f"{passage.source.cite()} is an approved source, effective {passage.effective_date.isoformat()}, review due {passage.review_due.isoformat()}.",
            label=ClaimLabel.VERIFIED, sources=(passage.source,), confidence=ConfidenceBand.HIGH))
        canonical_claims.append(Claim(
            statement=f"{passage.source.cite()} is relevant to the case query (term coverage {passage.relevance:.2f}).",
            label=ClaimLabel.INFERENCE, sources=(passage.source,),
            basis="Lexical query-term coverage against approved sources; not human-verified.",
            confidence=passage.relevance_band))
    if result.claims != tuple(canonical_claims):
        raise HandoffError("knowledge_fixture_claim_mismatch")
    current, ack = ledger.consume(receipt.receipt_id, expected_version=receipt.state_version,
        capability=capability, context=context, now=now)
    if current != triage or ack != frozenset({triage.contribution_id}):
        raise HandoffError("knowledge_fixture_binding_mismatch")
    return SyntheticKnowledgeEvidence(receipt_id=receipt.receipt_id, source_handoff_id=receipt.source_handoff_id,
        source_version=receipt.source_version, triage_contribution_id=triage.contribution_id,
        triage_digest=triage_digest, fixture_policy_digest=proposal.fixture_digest,
        triage_inference=triage.claims[0], reported_start_codepoint=proposal.start_codepoint,
        reported_end_codepoint=proposal.end_codepoint,
        source_set_version=corpus.source_set_version, result=result)
