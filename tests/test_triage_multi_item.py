"""Candidate linked-item schema tests; not Shared contract acceptance."""
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from cdit_support_mao.contracts.common import RunContext, SourceKind, SourceRef
from cdit_support_mao.agents.triage.multi_item import LinkedTriageItem, MultiItemTriageCandidate


CTX = RunContext(run_id="RUN-MULTI-01", case_id="SYN-CASE-01", case_version=1,
                 policy_version="SYN-POLICY-1")
CASE_SOURCE = SourceRef(kind=SourceKind.CASE_FIELD, source_id="SYN-CASE-01", version="1", locator="message")
POLICY_SOURCE = SourceRef(kind=SourceKind.POLICY_RULE, source_id="SYN-RULE-01", version="SYN-POLICY-1")


def item(index, text, start, end, **kwargs):
    data = dict(item_index=index, reported_text=text, source_start=start, source_end=end,
        source=CASE_SOURCE, segmentation="candidate_boundary", status="abstained_needs_human",
        missing_facts=("category and urgency not grounded",))
    data.update(kwargs)
    return LinkedTriageItem(**data)


def bundle(text, items):
    return MultiItemTriageCandidate(context=CTX, source=CASE_SOURCE, source_text=text, items=tuple(items))


def test_multi_item_parent_preserves_items_spans_and_blocks_completion():
    text = "Need form; portal access fails"
    result = bundle(text, [item(1, "Need form", 0, 9), item(2, "portal access fails", 11, 30)])
    assert result.parent_status == "incomplete_needs_human_review"
    assert not result.parent_complete and result.human_review_required
    assert not result.downstream_allowed and not result.dispatched
    assert [x.reported_text for x in result.items] == ["Need form", "portal access fails"]
    assert [x.item_index for x in result.items] == [1, 2]
    assert "Need form" not in repr(result)
    assert result.contract_status == "manny_local_candidate_shared_review_pending"


def test_supported_independent_item_remains_proposal_but_not_forwardable():
    text = "Need form; portal access fails"
    first = item(1, "Need form", 0, 9, category="forms", category_label="inference",
        category_sources=(POLICY_SOURCE,), category_basis="Exact synthetic fixture rule.",
        category_evidence_quote="Need form",
        status="proposal_for_human_review", missing_facts=())
    second = item(2, "portal access fails", 11, 30,
        missing_facts=("affected system and impact",))
    result = bundle(text, [first, second])
    assert result.items[0].status == "proposal_for_human_review"
    assert result.items[1].status == "abstained_needs_human"
    assert not result.downstream_allowed and not result.parent_complete


def test_source_span_mismatch_is_rejected():
    with pytest.raises(ValidationError, match="item_span_does_not_match_source"):
        bundle("Need form; portal access fails", [item(1, "Fake form", 0, 9)])


def test_stale_parent_source_version_is_rejected():
    stale = SourceRef(kind=SourceKind.CASE_FIELD, source_id="SYN-CASE-01", version="2", locator="message")
    with pytest.raises(ValidationError, match="parent_source_context_mismatch"):
        MultiItemTriageCandidate(context=CTX, source=stale, source_text="Need form",
            items=(item(1, "Need form", 0, 9, source=stale),))


def test_policy_reference_must_match_parent_policy_version():
    wrong = SourceRef(kind=SourceKind.POLICY_RULE, source_id="SYN-RULE-02", version="SYN-POLICY-OLD")
    proposed = item(1, "Need form", 0, 9, category="forms", category_label="inference",
        category_sources=(wrong,), category_basis="Synthetic rule example.", category_evidence_quote="Need form",
        status="proposal_for_human_review", missing_facts=())
    with pytest.raises(ValidationError, match="claim_policy_version_mismatch"):
        bundle("Need form", [proposed])


def test_duplicate_or_forward_item_links_are_rejected():
    text = "Need form; access fails"
    staff = SourceRef(kind=SourceKind.STAFF_ENTRY, source_id="SYN-CASE-01", version="1")
    with pytest.raises(ValidationError, match="duplicate_item_dependency"):
        bundle(text, [item(1, "Need form", 0, 9, depends_on=(2, 2), dependency_sources=(staff,)),
                      item(2, "access fails", 11, 23)])

def test_unknown_is_not_disguised_as_inference_or_verified():
    with pytest.raises(ValidationError, match="unknown_claim_must_not_include_proposal"):
        item(1, "Need form", 0, 9, category="forms")
    with pytest.raises(ValidationError):
        item(1, "Need form", 0, 9, category_label="verified")


def test_dependency_cycles_are_rejected():
    text = "Need form; access fails"
    staff = SourceRef(kind=SourceKind.STAFF_ENTRY, source_id="SYN-CASE-01", version="1")
    with pytest.raises(ValidationError, match="cyclic_item_dependencies"):
        bundle(text, [item(1, "Need form", 0, 9, depends_on=(2,), dependency_sources=(staff,)),
                      item(2, "access fails", 11, 23, depends_on=(1,), dependency_sources=(staff,))])


def test_ambiguous_segmentation_cannot_carry_inferences():
    with pytest.raises(ValidationError, match="ambiguous_segmentation_requires_abstention"):
        item(1, "Need form", 0, 9, segmentation="ambiguous_parent", category="forms",
             category_label="inference", category_sources=(POLICY_SOURCE,),
             category_basis="Fixture", status="proposal_for_human_review", missing_facts=())

def test_dependency_requires_trusted_explicit_evidence():
    text = "Need form; access fails"
    with pytest.raises(ValidationError, match="dependency_requires_trusted_source"):
        bundle(text,[item(1,"Need form",0,9,depends_on=(2,)),item(2,"access fails",11,23)])
    staff = SourceRef(kind=SourceKind.STAFF_ENTRY,source_id="SYN-CASE-01",version="1")
    result=bundle(text,[item(1,"Need form",0,9,depends_on=(2,),dependency_sources=(staff,)),
                        item(2,"access fails",11,23)])
    assert result.items[0].depends_on==(2,)
