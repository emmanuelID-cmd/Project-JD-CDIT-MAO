"""Provider-free validation tests for synthetic semantic Triage output."""
import json

import pytest
from pydantic import ValidationError

from cdit_support_mao.agents.triage.semantic_contract import (
    TriageModelItemInput, TriageSemanticRequest, TriageSemanticContractError,
    validate_semantic_output,
)


def make_request():
    return TriageSemanticRequest(items=(
        TriageModelItemInput(item_index=1, text="The report export control is missing."),
        TriageModelItemInput(item_index=2, text="I cannot access the portal."),
    ), allowed_categories=("Report navigation", "Portal access"))


def valid_payload():
    return {"items": [
        {"item_index": 1, "category": "Report navigation", "category_label": "inference",
         "evidence_quote": "report export control", "rationale": "The request concerns locating a report control.",
         "missing_questions": [], "urgency": "unknown", "urgency_label": "unknown",
         "destination": "unknown", "destination_label": "unknown"},
        {"item_index": 2, "category": "Portal access", "category_label": "inference",
         "evidence_quote": "cannot access the portal", "rationale": "The report describes portal access trouble.",
         "missing_questions": ["Which portal and account are affected?"], "urgency": "unknown",
         "urgency_label": "unknown", "destination": "unknown", "destination_label": "unknown"},
    ]}


def test_semantic_categories_are_inferences_and_urgency_stays_unknown():
    result = validate_semantic_output(json.dumps(valid_payload()), request=make_request())
    assert [item.category_label for item in result.items] == ["inference", "inference"]
    assert [item.urgency for item in result.items] == ["unknown", "unknown"]
    assert all(item.human_review_required and not item.downstream_allowed for item in result.items)
    assert not result.parent_complete and not result.downstream_allowed and not result.dispatched


def test_unknown_category_can_only_return_questions_without_a_claim():
    payload = valid_payload()
    item = payload["items"][0]
    item.update(category=None, category_label="unknown", evidence_quote=None, rationale=None,
                missing_questions=["Which report are you trying to export?"])
    result = validate_semantic_output(json.dumps(payload), request=make_request())
    assert result.items[0].category is None and result.items[0].category_label == "unknown"
    assert result.items[0].missing_questions


@pytest.mark.parametrize("mutation", [
    lambda p: p["items"][0].update(category="Unlisted category"),
    lambda p: p["items"][0].update(evidence_quote="admin account changed"),
    lambda p: p["items"][0].update(urgency="high"),
    lambda p: p["items"][0].update(destination="payroll"),
    lambda p: p["items"][0].update(item_index=2),
    lambda p: p["items"][0].update(tool_call={"name": "write_ticket"}),
])
def test_unsupported_claims_authority_and_item_binding_fail_closed(mutation):
    payload = valid_payload()
    mutation(payload)
    with pytest.raises(TriageSemanticContractError):
        validate_semantic_output(json.dumps(payload), request=make_request())


def test_missing_or_forged_source_quote_fails_closed():
    payload = valid_payload()
    payload["items"][0].update(evidence_quote=None)
    with pytest.raises(TriageSemanticContractError):
        validate_semantic_output(json.dumps(payload), request=make_request())


def test_pydantic_request_rejects_duplicate_indices_or_categories():
    with pytest.raises(ValidationError):
        TriageSemanticRequest(items=(TriageModelItemInput(item_index=1, text="one"),
            TriageModelItemInput(item_index=1, text="two")), allowed_categories=("A",))
    with pytest.raises(ValidationError):
        TriageSemanticRequest(items=(TriageModelItemInput(item_index=1, text="one"),),
            allowed_categories=("A", "A"))
