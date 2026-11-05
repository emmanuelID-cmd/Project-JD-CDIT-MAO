"""Fixture-only composition tests for Manny's local linked-item candidate."""
from datetime import UTC, datetime
from pathlib import Path

import pytest

from cdit_support_mao.agents.coordinator import (
    Coordinator, FixtureCaseVersions, FixturePolicyVersions, FixtureSession,
    FixtureSessionAuthority,
)
from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.fixture_policy import SyntheticPolicyCatalog
from cdit_support_mao.agents.triage.development_examples import DevelopmentExampleCatalog
from cdit_support_mao.agents.triage.multi_item_adapter import prepare_multi_item_candidate

NOW = datetime(2026, 11, 5, 12, tzinfo=UTC)


@pytest.fixture
def pipeline():
    owner, sender, receiver = object(), object(), object()
    sessions = FixtureSessionAuthority(provisioning_capability=owner, ttl_seconds=3600)
    versions = FixtureCaseVersions(provisioning_capability=owner)
    versions.set_version("SYN-CASE-01", 1, expected_version=None, capability=owner)
    policies = FixturePolicyVersions(provisioning_capability=owner, active=frozenset({"SYN-POLICY-1"}))
    token = sessions.issue(FixtureSession(actor_id="SYN-ACTOR-1", role="staff", active=True,
        allowed_case_ids=("SYN-CASE-01",)), capability=owner)
    coordinator = Coordinator(sessions, case_versions=versions, policy_versions=policies)
    registry = HandoffRegistry(sender_capability=sender, receiver_capability=receiver,
        timeout_seconds=300, actor_sessions=sessions, case_versions=versions, policy_versions=policies)

    def start(message):
        intake = coordinator.prepare({"case_id": "SYN-CASE-01", "case_version": 1,
            "policy_version": "SYN-POLICY-1", "message": message,
            "data_classification": "synthetic"}, session_token=token)
        handoff = registry.prepare(intake, capability=sender, session_token=token, now=NOW)
        ack = registry.acknowledge(handoff.handoff_id, expected_version=1,
            capability=receiver, context=intake.context, now=NOW)
        return intake, ack

    def make_catalog(rule_specs):
        catalog = SyntheticPolicyCatalog(policy_version="SYN-POLICY-1", provision_capability=owner)
        for index, (report, category, urgency) in enumerate(rule_specs, 1):
            catalog.add({"rule_id": f"SYN-RULE-{index:02d}", "exact_report": report,
                "category": category, "urgency": urgency,
                "proposed_destination": "knowledge_review"}, capability=owner)
        catalog.seal(capability=owner)
        return catalog

    def make_development_catalog():
        catalog = DevelopmentExampleCatalog(provisioning_capability=owner)
        source = Path(__file__).resolve().parents[1] / "docs/requirements/CASE-SCENARIOS.md"
        catalog.provision(source.read_bytes(), capability=owner)
        return catalog

    def build(ack, intake, *, catalog=None, **overrides):
        args = dict(handoff_id=ack.handoff_id, expected_version=ack.state_version,
            receiver_capability=receiver, context=intake.context, catalog=catalog, now=NOW)
        args.update(overrides)
        return prepare_multi_item_candidate(registry, **args)

    return start, make_catalog, build, make_development_catalog, registry, receiver, versions, owner


def test_single_exact_fixture_proposal_is_source_bound_and_non_dispatching(pipeline):
    start, make_catalog, build, *_ = pipeline
    text = "Where is the report export control?"
    intake, ack = start(text)
    result = build(ack, intake, catalog=make_catalog([(text, "report-navigation", "low")]))
    item = result.items[0]
    assert item.category == "report-navigation" and item.category_label == "inference"
    assert item.urgency == "low" and item.urgency_label == "inference"
    assert item.source_start == 0 and item.source_end == len(text)
    assert item.category_sources[0] == item.source
    assert result.parent_status == "incomplete_needs_human_review"
    assert not result.downstream_allowed and not result.dispatched and not result.parent_complete


def test_multiple_items_preserve_spans_and_do_not_guess_dependencies(pipeline):
    start, make_catalog, build, *_ = pipeline
    text = "Need the form; portal access fails"
    intake, ack = start(text)
    result = build(ack, intake, catalog=make_catalog([("Need the form", "forms", "low")]))
    assert len(result.items) == 2
    assert [item.reported_text for item in result.items] == ["Need the form", "portal access fails"]
    # Current policy fixture deliberately abstains for multi-item parents.
    assert all(item.category is None and item.category_label == "unknown"
               and item.status == "abstained_needs_human" for item in result.items)
    assert all(item.depends_on == () for item in result.items)
    assert not result.downstream_allowed and not result.parent_complete


def test_exact_80_row_example_id_is_reference_only_on_matching_linked_item(pipeline):
    start, _, build, make_development_catalog, *_ = pipeline
    text = "My expected pay did not arrive today.; Need the form"
    intake, ack = start(text)
    result = build(ack, intake, development_catalog=make_development_catalog())

    matched, unmatched = result.items
    assert matched.reported_text == "My expected pay did not arrive today."
    assert matched.example_reference_status == "exact_reference_only"
    reference = matched.example_references[0]
    assert reference.example_id == "SYN-EXAMPLE-017"
    assert reference.row == 17
    assert reference.source_origin == "unverified_provisioner_claim"
    assert reference.sample_status == "unverified_synthetic_development_example"
    assert (matched.category, matched.urgency, matched.destination) == (None, "unknown", None)
    assert (matched.category_label, matched.urgency_label, matched.destination_label) == (
        "unknown", "unknown", "unknown")
    assert unmatched.example_reference_status == "no_reference"
    assert not unmatched.example_references
    assert result.parent_complete is False and result.downstream_allowed is False


def test_ambiguous_linked_parent_never_shows_example_reference(pipeline):
    start, _, build, make_development_catalog, *_ = pipeline
    text = '"My expected pay did not arrive today.; and portal access fails'
    intake, ack = start(text)
    result = build(ack, intake, development_catalog=make_development_catalog())
    item = result.items[0]

    assert item.segmentation == "ambiguous_parent"
    assert item.example_reference_status == "ambiguous_segmentation"
    assert not item.example_references
    assert item.category_label == item.urgency_label == "unknown"


def test_ambiguous_parent_is_preserved_as_single_auditor_item(pipeline):
    start, make_catalog, build, *_ = pipeline
    text = "Login fails and payroll is wrong"
    intake, ack = start(text)
    result = build(ack, intake, catalog=make_catalog([]))
    assert len(result.items) == 1 and result.items[0].reported_text == text
    assert result.items[0].segmentation == "ambiguous_parent"
    assert result.items[0].status == "abstained_needs_human"


def test_unknown_policy_and_wrong_receiver_fail_safely(pipeline):
    start, make_catalog, build, _, _, *_ = pipeline
    text = "Please send the form"
    intake, ack = start(text)
    result = build(ack, intake, catalog=None)
    assert result.items[0].status == "abstained_needs_human"
    with pytest.raises(HandoffError, match="unauthorized_receiver"):
        build(ack, intake, catalog=make_catalog([]), receiver_capability=object())


def test_stale_case_stops_before_return(pipeline):
    start, make_catalog, build, _, _, _, versions, owner = pipeline
    text = "Need the form"
    intake, ack = start(text)
    versions.set_version("SYN-CASE-01", 2, expected_version=1, capability=owner)
    with pytest.raises(HandoffError, match="stale_case_version"):
        build(ack, intake, catalog=make_catalog([(text, "forms", "low")]))


def test_repr_never_discloses_report_text(pipeline):
    start, make_catalog, build, *_ = pipeline
    text = "synthetic private marker"
    intake, ack = start(text)
    result = build(ack, intake, catalog=make_catalog([]))
    assert text not in repr(result)
