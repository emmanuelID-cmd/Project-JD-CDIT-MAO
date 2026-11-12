"""Compose acknowledged synthetic proposals into Manny's local item bundle.

This is not a Shared contract, human dispatch, ticket update, or operational
classifier. The existing fixture policy matches complete single-item parents
only, so multi-item parents remain human-review-only.
"""
from __future__ import annotations

from datetime import datetime

from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.fixture_policy import SyntheticPolicyCatalog, propose_from_synthetic_policy
from cdit_support_mao.agents.triage.development_examples import DevelopmentExampleCatalog, lookup_development_examples
from cdit_support_mao.agents.triage.input import read_acknowledged_input
from cdit_support_mao.agents.triage.multi_item import LinkedTriageItem, MultiItemTriageCandidate
from cdit_support_mao.agents.triage.segment import extract_request_parts
from cdit_support_mao.contracts.common import RunContext, SourceKind, SourceRef


def prepare_multi_item_candidate(
    registry: HandoffRegistry, *, handoff_id: str, expected_version: int,
    receiver_capability: object, context: RunContext,
    catalog: SyntheticPolicyCatalog | None, now: datetime | None = None,
    development_catalog: DevelopmentExampleCatalog | None = None,
) -> MultiItemTriageCandidate:
    """Return one source-bound local candidate per conservatively split item."""
    packet = read_acknowledged_input(registry, handoff_id=handoff_id,
        expected_version=expected_version, receiver_capability=receiver_capability,
        context=context, now=now)
    parts = extract_request_parts(registry, handoff_id=handoff_id,
        expected_version=expected_version, receiver_capability=receiver_capability,
        context=context, now=now)
    if parts.context != packet.context or parts.trace_id != packet.trace_id or parts.handoff_id != packet.handoff_id:
        raise HandoffError("multi_item_source_changed")

    parent_source = SourceRef(kind=SourceKind.CASE_FIELD, source_id=context.case_id,
        version=str(context.case_version), locator="message")
    items: list[LinkedTriageItem] = []
    for item in parts.items:
        example_reference_status = "no_reference"
        example_references = ()
        if development_catalog is not None:
            example_lookup = lookup_development_examples(registry, handoff_id=handoff_id,
                expected_version=expected_version, receiver_capability=receiver_capability,
                context=context, item_index=item.item_index, catalog=development_catalog, now=now)
            if (example_lookup.context != parts.context or example_lookup.handoff_id != handoff_id
                    or example_lookup.handoff_state_version != expected_version
                    or example_lookup.item_index != item.item_index):
                raise HandoffError("multi_item_example_reference_binding_mismatch")
            example_reference_status = example_lookup.status
            example_references = example_lookup.references

        proposal = propose_from_synthetic_policy(registry, handoff_id=handoff_id,
            expected_version=expected_version, receiver_capability=receiver_capability,
            context=context, item_index=item.item_index, catalog=catalog, now=now)
        if (proposal.trace_id != parts.trace_id or proposal.handoff_id != handoff_id
                or proposal.handoff_state_version != expected_version or proposal.context != parts.context
                or proposal.item_index != item.item_index or proposal.item_count != len(parts.items)
                or proposal.reported_source != item.source or proposal.start_codepoint != item.start_codepoint
                or proposal.end_codepoint != item.end_codepoint):
            raise HandoffError("multi_item_proposal_binding_mismatch")

        if proposal.status == "synthetic_fixture_inference":
            basis = (f"Exact match to unverified synthetic rule {proposal.policy_source.source_id}; "
                     f"fixture digest {proposal.fixture_digest}. Not operational policy or proof of case facts.")
            kwargs = dict(
                category=proposal.proposed_category, category_label="inference",
                category_sources=(item.source, proposal.policy_source), category_basis=basis,
                category_evidence_quote=item.reported_text,
                urgency=proposal.proposed_urgency, urgency_label="inference",
                urgency_sources=(item.source, proposal.policy_source), urgency_basis=basis,
                destination=proposal.proposed_destination, destination_label="inference",
                destination_sources=(proposal.policy_source,), destination_basis=basis,
                status="proposal_for_human_review", missing_facts=())
        else:
            kwargs = dict(status="abstained_needs_human",
                missing_facts=(f"Human review required: {proposal.reason}.",),
                conflicts_present=proposal.reason == "conflicting_rules")
        items.append(LinkedTriageItem(item_index=item.item_index, reported_text=item.reported_text,
            source_start=item.start_codepoint, source_end=item.end_codepoint, source=item.source,
            segmentation="ambiguous_parent" if parts.status == "needs_auditor" else "candidate_boundary",
            depends_on=(), example_reference_status=example_reference_status,
            example_references=example_references, **kwargs))

    registry.validate_active(handoff_id, expected_version=expected_version,
        capability=receiver_capability, context=context, now=now)
    candidate = MultiItemTriageCandidate(context=parts.context, source=parent_source,
        source_text=packet.reported_message, items=tuple(items))
    try:
        candidate = MultiItemTriageCandidate.model_validate(candidate.model_dump())
    except Exception:
        raise HandoffError("invalid_multi_item_candidate") from None
    registry.validate_active(handoff_id, expected_version=expected_version,
        capability=receiver_capability, context=context, now=now)
    return candidate
