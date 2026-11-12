"""Unit tests for local synthetic reviewed-example fixture lookup only."""
import pytest

from cdit_support_mao.agents.triage.reviewed_examples import (
    FactCode, FixtureCatalogError, SyntheticFixtureExampleCatalog,
)


@pytest.fixture
def fixture_catalog():
    provision, lookup = object(), object()
    catalog = SyntheticFixtureExampleCatalog(catalog_version="V1", provisioning_capability=provision,
        lookup_capability=lookup)
    return catalog, provision, lookup


def example(**changes):
    value = {
        "source": {"source_id": "SYN-EXAMPLE-001", "version": "V1"},
        "reviewed_fixture": True,
        "review_fixture_ref": "SYN-REVIEW-001",
        "conditions": [{"field": "ISSUE_TYPE", "value": "PAYROLL"},
                       {"field": "PAY_PERIOD", "value": "CURRENT"}],
        "exceptions": [{"field": "SUSPECTED_FRAUD", "value": "PRESENT"}],
    }
    return {**value, **changes}


def observed(**values):
    return [{"field": field, "value": value} for field, value in values.items()]


def ready(fixture_catalog):
    catalog, provision, lookup = fixture_catalog
    catalog.provision(example(), capability=provision)
    catalog.seal(capability=provision)
    return catalog, provision, lookup


def test_matching_conditions_and_exception_are_inference_only(fixture_catalog):
    catalog, _, lookup = ready(fixture_catalog)
    result = catalog.lookup(observed(ISSUE_TYPE="PAYROLL", PAY_PERIOD="CURRENT", SUSPECTED_FRAUD="PRESENT"),
        expected_catalog_version="V1", capability=lookup)
    assert result.status == "candidates_found" and len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.label == "inference" and candidate.source.source_id == "SYN-EXAMPLE-001"
    assert candidate.review_fixture_ref == "SYN-REVIEW-001"
    assert [c.relation for c in candidate.conditions] == ["matched", "matched"]
    assert [c.relation for c in candidate.exceptions] == ["matched"]
    assert candidate.category is candidate.urgency is candidate.destination is None
    assert candidate.dispatch_allowed is False and candidate.human_review_required is True
    assert result.dispatch_allowed is False and result.human_review_required is True


def test_missing_and_different_facts_are_explicit_including_exceptions(fixture_catalog):
    catalog, _, lookup = ready(fixture_catalog)
    result = catalog.lookup(observed(ISSUE_TYPE="PAYROLL", PAY_PERIOD="PRIOR"),
        expected_catalog_version="V1", capability=lookup)
    candidate = result.candidates[0]
    assert [c.relation for c in candidate.conditions] == ["matched", "different"]
    assert [c.relation for c in candidate.exceptions] == ["missing"]
    assert candidate.conditions[1].observed.value == "PRIOR"
    assert candidate.exceptions[0].observed is None
    assert candidate.urgency is None and candidate.dispatch_allowed is False
    result = catalog.lookup(observed(ISSUE_TYPE="PAYROLL", SUSPECTED_FRAUD="ABSENT"),
        expected_catalog_version="V1", capability=lookup)
    assert [c.relation for c in result.candidates[0].conditions] == ["matched", "missing"]
    assert [c.relation for c in result.candidates[0].exceptions] == ["different"]


def test_no_shared_conditions_and_stale_catalog_produce_no_candidates(fixture_catalog):
    catalog, _, lookup = ready(fixture_catalog)
    no_match = catalog.lookup(observed(ISSUE_TYPE="ACCESS"), expected_catalog_version="V1", capability=lookup)
    stale = catalog.lookup(observed(ISSUE_TYPE="PAYROLL"), expected_catalog_version="V2", capability=lookup)
    assert no_match.status == "no_shared_conditions" and no_match.candidates == ()
    assert no_match.observed_facts[0].value == "ACCESS"
    assert stale.status == "version_mismatch" and stale.candidates == ()
    assert not no_match.dispatch_allowed and not stale.dispatch_allowed


@pytest.mark.parametrize("reviewed", [False, None, 1, "true"])
def test_unreviewed_or_non_boolean_fixture_is_rejected(fixture_catalog, reviewed):
    catalog, provision, _ = fixture_catalog
    with pytest.raises(FixtureCatalogError, match="^invalid_reviewed_fixture$"):
        catalog.provision(example(reviewed_fixture=reviewed), capability=provision)


def test_unauthorized_capability_cannot_provision_or_lookup(fixture_catalog):
    catalog, provision, lookup = fixture_catalog
    secret = "PRIVATE_SYNTHETIC_CODE"
    with pytest.raises(FixtureCatalogError, match="^unauthorized_fixture_provision$") as error:
        catalog.provision(example(conditions=[{"field": "ISSUE", "value": secret}]), capability=object())
    assert secret not in repr(error.value)
    catalog.provision(example(), capability=provision)
    catalog.seal(capability=provision)
    with pytest.raises(FixtureCatalogError, match="^unauthorized_fixture_lookup$"):
        catalog.lookup(observed(ISSUE_TYPE="PAYROLL"), expected_catalog_version="V1", capability=object())
    assert catalog.lookup(observed(ISSUE_TYPE="PAYROLL"), expected_catalog_version="V1", capability=lookup).candidates


def test_provision_seal_and_version_are_immutable(fixture_catalog):
    catalog, provision, lookup = fixture_catalog
    catalog.provision(example(), capability=provision)
    with pytest.raises(FixtureCatalogError, match="^duplicate_example_id$"):
        catalog.provision(example(), capability=provision)
    with pytest.raises(FixtureCatalogError, match="^catalog_not_sealed$"):
        catalog.lookup([], expected_catalog_version="V1", capability=lookup)
    catalog.seal(capability=provision)
    with pytest.raises(FixtureCatalogError, match="^catalog_sealed$"):
        catalog.provision(example(source={"source_id":"SYN-EXAMPLE-002", "version":"V1"}), capability=provision)


def test_fact_content_absent_from_repr_and_errors(fixture_catalog):
    catalog, provision, lookup = fixture_catalog
    marker = "SYNTHETIC_PRIVATE_MARKER"
    catalog.provision(example(conditions=[{"field": "ISSUE_TYPE", "value": marker}]), capability=provision)
    catalog.seal(capability=provision)
    result = catalog.lookup(observed(ISSUE_TYPE=marker), expected_catalog_version="V1", capability=lookup)
    assert marker not in repr(result) and marker not in repr(result.candidates[0])
    assert marker not in repr(FactCode(field="ISSUE_TYPE", value=marker))
    with pytest.raises(FixtureCatalogError, match="^invalid_observed_facts$") as error:
        catalog.lookup([{"field":"ISSUE_TYPE", "value":marker, "untrusted_extra":marker}],
            expected_catalog_version="V1", capability=lookup)
    assert marker not in repr(error.value)


def test_duplicate_fields_are_rejected_without_echo(fixture_catalog):
    catalog, provision, lookup = fixture_catalog
    repeated = [{"field":"ISSUE_TYPE", "value":"ONE"}, {"field":"ISSUE_TYPE", "value":"TWO"}]
    with pytest.raises(FixtureCatalogError, match="^invalid_reviewed_fixture$"):
        catalog.provision(example(conditions=repeated), capability=provision)
    catalog.provision(example(), capability=provision)
    catalog.seal(capability=provision)
    with pytest.raises(FixtureCatalogError, match="^duplicate_observed_field$"):
        catalog.lookup(repeated, expected_catalog_version="V1", capability=lookup)


def test_extra_observed_fields_remain_visible_as_unassessed(fixture_catalog):
    catalog, _, lookup = ready(fixture_catalog)
    result = catalog.lookup(observed(ISSUE_TYPE="PAYROLL", UNKNOWN_CONTEXT="PRESENT"),
        expected_catalog_version="V1", capability=lookup)
    candidate = result.candidates[0]
    assert [(f.field, f.value) for f in candidate.unassessed_observed] == [("UNKNOWN_CONTEXT", "PRESENT")]
    assert "UNKNOWN_CONTEXT" not in repr(result)
    assert candidate.label == "inference" and candidate.dispatch_allowed is False
