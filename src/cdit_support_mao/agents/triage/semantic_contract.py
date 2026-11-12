"""Strict provider-neutral contract for synthetic semantic Triage proposals.

This module validates model-shaped JSON but performs no model call. Categories
are suggestions from the development taxonomy only; urgency and destination
remain Unknown until approved policy and a separate human route are available.
"""
from __future__ import annotations

import json
from typing import Literal

from pydantic import Field, ValidationError, model_validator

from cdit_support_mao.contracts.common import StrictModel


class TriageModelItemInput(StrictModel):
    item_index: int = Field(strict=True, ge=1, le=8)
    text: str = Field(min_length=1, max_length=2000, repr=False)


class TriageSemanticRequest(StrictModel):
    """Minimal data a future model call may receive; no case IDs or policy claims."""
    items: tuple[TriageModelItemInput, ...] = Field(min_length=1, max_length=8, repr=False)
    allowed_categories: tuple[str, ...] = Field(min_length=1, max_length=80)
    data_classification: Literal["synthetic"] = "synthetic"

    @model_validator(mode="after")
    def validate_lists(self) -> TriageSemanticRequest:
        indexes = tuple(item.item_index for item in self.items)
        if indexes != tuple(sorted(set(indexes))):
            raise ValueError("triage_item_indexes_must_be_unique_and_ordered")
        categories = tuple(category.strip() for category in self.allowed_categories)
        if any(not value or len(value) > 100 for value in categories) or len(set(categories)) != len(categories):
            raise ValueError("triage_categories_must_be_unique_and_bounded")
        return self


class TriageSemanticItemOutput(StrictModel):
    item_index: int = Field(strict=True, ge=1, le=8)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    category_label: Literal["inference", "unknown"]
    evidence_quote: str | None = Field(default=None, min_length=1, max_length=300, repr=False)
    rationale: str | None = Field(default=None, min_length=1, max_length=500, repr=False)
    missing_questions: tuple[str, ...] = Field(default=(), max_length=8, repr=False)
    urgency: Literal["unknown"] = "unknown"
    urgency_label: Literal["unknown"] = "unknown"
    destination: Literal["unknown"] = "unknown"
    destination_label: Literal["unknown"] = "unknown"
    human_review_required: Literal[True] = True
    downstream_allowed: Literal[False] = False

    @model_validator(mode="after")
    def validate_category_evidence(self) -> TriageSemanticItemOutput:
        if self.category is None:
            if self.category_label != "unknown" or self.evidence_quote is not None or self.rationale is not None:
                raise ValueError("unknown_category_must_not_claim_inference")
        elif self.category_label != "inference" or not self.evidence_quote or not self.rationale:
            raise ValueError("category_inference_requires_quote_and_rationale")
        if any(not question.strip() or len(question) > 300 for question in self.missing_questions):
            raise ValueError("invalid_missing_question")
        return self


class TriageSemanticOutput(StrictModel):
    items: tuple[TriageSemanticItemOutput, ...] = Field(min_length=1, max_length=8, repr=False)
    human_review_required: Literal[True] = True
    parent_complete: Literal[False] = False
    downstream_allowed: Literal[False] = False
    dispatched: Literal[False] = False


class TriageSemanticContractError(ValueError):
    """Content-free failure for invalid or unsupported model output."""

    def __init__(self, code: str) -> None:
        fields = (
            "items", "item_index", "category", "category_label", "evidence_quote",
            "rationale", "missing_questions", "urgency", "urgency_label", "destination",
            "destination_label", "human_review_required", "downstream_allowed",
            "parent_complete", "dispatched", "unknown_field",
        )
        error_types = (
            "missing", "too_short", "too_long", "tuple_type", "list_type", "dict_type",
            "model_type", "string_type", "int_type", "bool_type", "literal_error",
            "extra_forbidden", "value_error", "other",
        )
        allowed = {
            "invalid_triage_model_output",
            "triage_model_output_invalid_json",
            "triage_model_output_schema_invalid",
            "triage_model_item_coverage_mismatch",
            "triage_model_category_outside_development_taxonomy",
            "triage_model_quote_not_in_source_item",
            *{f"triage_model_output_schema_invalid_{field}_{error_type}"
              for field in fields for error_type in error_types},
        }
        self.code = code if code in allowed else "invalid_triage_model_output"
        super().__init__(self.code)


def validate_semantic_output(raw: object, *, request: TriageSemanticRequest) -> TriageSemanticOutput:
    """Validate exact item coverage, taxonomy membership and source-quoted inference."""
    if not isinstance(raw, str) or not raw or len(raw) > 12_000:
        raise TriageSemanticContractError("invalid_triage_model_output")
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        raise TriageSemanticContractError("triage_model_output_invalid_json") from None
    try:
        output = TriageSemanticOutput.model_validate(payload)
    except ValidationError as exc:
        known_fields = {
            "items", "item_index", "category", "category_label", "evidence_quote",
            "rationale", "missing_questions", "urgency", "urgency_label", "destination",
            "destination_label", "human_review_required", "downstream_allowed",
            "parent_complete", "dispatched",
        }
        field = "unknown_field"
        error_type = "other"
        for error in exc.errors(include_url=False, include_context=False, include_input=False):
            location = error.get("loc", ())
            candidate = next((value for value in reversed(location) if isinstance(value, str)), None)
            if candidate in known_fields:
                field = candidate
                allowed_error_types = {
                    "missing", "too_short", "too_long", "tuple_type", "list_type", "dict_type",
                    "model_type", "string_type", "int_type", "bool_type", "literal_error",
                    "extra_forbidden", "value_error",
                }
                observed_type = error.get("type")
                error_type = observed_type if observed_type in allowed_error_types else "other"
                break
        raise TriageSemanticContractError(
            f"triage_model_output_schema_invalid_{field}_{error_type}"
        ) from None
    except (TypeError, ValueError):
        raise TriageSemanticContractError("triage_model_output_schema_invalid") from None

    expected_indexes = tuple(item.item_index for item in request.items)
    if tuple(item.item_index for item in output.items) != expected_indexes:
        raise TriageSemanticContractError("triage_model_item_coverage_mismatch")
    category_set = frozenset(request.allowed_categories)
    input_by_index = {item.item_index: item.text for item in request.items}
    for item in output.items:
        if item.category is not None and item.category not in category_set:
            raise TriageSemanticContractError("triage_model_category_outside_development_taxonomy")
        if item.evidence_quote is not None and item.evidence_quote not in input_by_index[item.item_index]:
            raise TriageSemanticContractError("triage_model_quote_not_in_source_item")
    return output
