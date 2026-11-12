"""Manny-owned linked-item candidate; not an accepted Shared handoff."""
from __future__ import annotations
from typing import Literal
from pydantic import Field, model_validator
from cdit_support_mao.contracts.common import RunContext, SourceKind, SourceRef, StrictModel
from cdit_support_mao.agents.triage.development_examples import DevelopmentReference

class LinkedTriageItem(StrictModel):
    item_index: int = Field(strict=True, ge=1, le=8)
    reported_text: str = Field(min_length=1, max_length=2000, repr=False)
    source_start: int = Field(strict=True, ge=0)
    source_end: int = Field(strict=True, ge=1)
    source: SourceRef
    segmentation: Literal["candidate_boundary", "ambiguous_parent"]
    depends_on: tuple[int, ...] = Field(default=(), max_length=7)
    dependency_sources: tuple[SourceRef, ...] = Field(default=(), max_length=8)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    category_label: Literal["inference", "unknown"] = "unknown"
    category_sources: tuple[SourceRef, ...] = Field(default=(), max_length=8)
    category_basis: str | None = Field(default=None, max_length=500, repr=False)
    category_evidence_quote: str | None = Field(default=None, min_length=1, max_length=300, repr=False)
    urgency: Literal["low", "medium", "high", "unknown"] = "unknown"
    urgency_label: Literal["inference", "unknown"] = "unknown"
    urgency_sources: tuple[SourceRef, ...] = Field(default=(), max_length=8)
    urgency_basis: str | None = Field(default=None, max_length=500, repr=False)
    destination: str | None = Field(default=None, min_length=1, max_length=80)
    destination_label: Literal["inference", "unknown"] = "unknown"
    destination_sources: tuple[SourceRef, ...] = Field(default=(), max_length=8)
    destination_basis: str | None = Field(default=None, max_length=500, repr=False)
    example_reference_status: Literal["exact_reference_only", "no_reference", "ambiguous_segmentation"] = "no_reference"
    example_references: tuple[DevelopmentReference, ...] = Field(default=(), max_length=80)
    status: Literal["proposal_for_human_review", "abstained_needs_human"]
    missing_facts: tuple[str, ...] = Field(default=(), max_length=16, repr=False)
    conflicts_present: bool = False
    human_review_required: Literal[True] = True
    downstream_allowed: Literal[False] = False

    @property
    def auditor_review_reasons(self) -> tuple[str, ...]:
        """Local review metadata; it does not dispatch or authorize an action."""
        reasons: list[str] = []
        if self.category_label == "unknown":
            reasons.append("unknown_category")
        if self.urgency_label == "unknown":
            reasons.append("unknown_urgency")
        if self.destination_label == "unknown":
            reasons.append("unknown_destination")
        if self.segmentation == "ambiguous_parent":
            reasons.append("ambiguous_segmentation")
        return tuple(reasons)

    @model_validator(mode="after")
    def validate_claims(self) -> LinkedTriageItem:
        if self.source.kind is not SourceKind.CASE_FIELD or self.source.locator != "message":
            raise ValueError("item_source_must_be_case_message")
        if self.source_start >= self.source_end or self.source_end-self.source_start != len(self.reported_text):
            raise ValueError("item_span_length_mismatch")
        if self.conflicts_present and self.status != "abstained_needs_human":
            raise ValueError("conflict_requires_abstention")
        if self.segmentation == "ambiguous_parent" and any(label == "inference" for label in
            (self.category_label, self.urgency_label, self.destination_label)):
            raise ValueError("ambiguous_segmentation_requires_abstention")
        if (self.example_reference_status == "exact_reference_only") != bool(self.example_references):
            raise ValueError("example_reference_status_mismatch")
        if self.segmentation == "ambiguous_parent" and self.example_references:
            raise ValueError("ambiguous_segmentation_cannot_reference_example")
        if self.depends_on and not self.dependency_sources:
            raise ValueError("dependency_requires_trusted_source")
        if not self.depends_on and self.dependency_sources:
            raise ValueError("dependency_source_without_dependency")
        for value,label,sources,basis in (
            (self.category,self.category_label,self.category_sources,self.category_basis),
            (self.urgency if self.urgency!="unknown" else None,self.urgency_label,self.urgency_sources,self.urgency_basis),
            (self.destination,self.destination_label,self.destination_sources,self.destination_basis)):
            if label=="unknown" and (value is not None or sources or basis): raise ValueError("unknown_claim_must_not_include_proposal")
            if label=="inference" and (value is None or not basis or not sources): raise ValueError("inference_requires_value_basis_and_sources")
        if self.category_label == "inference":
            if (self.category_evidence_quote is None
                    or self.category_evidence_quote not in self.reported_text):
                raise ValueError("category_inference_requires_exact_item_quote")
        elif self.category_evidence_quote is not None:
            raise ValueError("unknown_category_must_not_include_quote")
        proposed=any(label=="inference" for _,label,_,_ in (
            (self.category,self.category_label,self.category_sources,self.category_basis),
            (self.urgency if self.urgency!="unknown" else None,self.urgency_label,self.urgency_sources,self.urgency_basis),
            (self.destination,self.destination_label,self.destination_sources,self.destination_basis)))
        if (self.status=="proposal_for_human_review") != proposed: raise ValueError("proposal_status_mismatch")
        return self

class MultiItemTriageCandidate(StrictModel):
    contract_status: Literal["manny_local_candidate_shared_review_pending"] = "manny_local_candidate_shared_review_pending"
    contract_version: Literal["manny-multi-item-candidate-v0.1"] = "manny-multi-item-candidate-v0.1"
    context: RunContext
    source: SourceRef
    source_text: str = Field(min_length=1,max_length=2000,repr=False)
    items: tuple[LinkedTriageItem,...] = Field(min_length=1,max_length=8,repr=False)
    parent_status: Literal["incomplete_needs_human_review"] = "incomplete_needs_human_review"
    parent_complete: Literal[False] = False
    human_review_required: Literal[True] = True
    downstream_allowed: Literal[False] = False
    dispatched: Literal[False] = False

    @model_validator(mode="after")
    def validate_parent(self) -> MultiItemTriageCandidate:
        if (self.source.kind is not SourceKind.CASE_FIELD or self.source.source_id!=self.context.case_id
            or self.source.version!=str(self.context.case_version) or self.source.locator!="message"):
            raise ValueError("parent_source_context_mismatch")
        if tuple(x.item_index for x in self.items)!=tuple(range(1,len(self.items)+1)):
            raise ValueError("item_indexes_must_be_contiguous")
        previous_end=0
        for item in self.items:
            if item.source!=self.source or item.source_end>len(self.source_text): raise ValueError("item_source_mismatch")
            if self.source_text[item.source_start:item.source_end]!=item.reported_text: raise ValueError("item_span_does_not_match_source")
            if item.source_start<previous_end: raise ValueError("item_spans_overlap_or_unsorted")
            previous_end=item.source_end
            if any(i<1 or i>len(self.items) or i==item.item_index for i in item.depends_on): raise ValueError("invalid_item_dependency")
            if len(set(item.depends_on))!=len(item.depends_on): raise ValueError("duplicate_item_dependency")
            for evidence in item.dependency_sources:
                if evidence.kind not in (SourceKind.STAFF_ENTRY, SourceKind.POLICY_RULE):
                    raise ValueError("dependency_source_not_trusted_kind")
                if evidence.kind is SourceKind.STAFF_ENTRY and evidence.source_id!=self.context.case_id:
                    raise ValueError("dependency_case_source_mismatch")
                if evidence.kind is SourceKind.POLICY_RULE and evidence.version!=self.context.policy_version:
                    raise ValueError("dependency_policy_version_mismatch")
            for sources in (item.category_sources,item.urgency_sources,item.destination_sources):
                for evidence in sources:
                    if evidence.kind is SourceKind.CASE_FIELD and (evidence.source_id!=self.context.case_id or evidence.version!=str(self.context.case_version)):
                        raise ValueError("claim_case_source_mismatch")
                    if evidence.kind is SourceKind.POLICY_RULE:
                        if evidence.source_id == "SYN-TICKET-CATEGORY-TAXONOMY":
                            digest = evidence.locator.removeprefix("category_sha256:") if evidence.locator else ""
                            if (len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest)
                                    or evidence.locator != f"category_sha256:{digest}"
                                    or evidence.version != f"sha256-{digest[:16]}"):
                                raise ValueError("claim_taxonomy_source_version_mismatch")
                        elif evidence.version != self.context.policy_version:
                            raise ValueError("claim_policy_version_mismatch")
        graph={item.item_index:item.depends_on for item in self.items}
        visiting=set()
        visited=set()
        def visit(index: int) -> None:
            if index in visiting: raise ValueError("cyclic_item_dependencies")
            if index in visited: return
            visiting.add(index)
            for dependency in graph[index]: visit(dependency)
            visiting.remove(index); visited.add(index)
        for index in graph: visit(index)
        return self
