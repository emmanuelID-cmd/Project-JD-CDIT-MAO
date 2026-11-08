"""Synthetic development examples are references, not priority policy."""
from datetime import UTC, datetime
import hashlib
from pathlib import Path

import pytest

from cdit_support_mao.agents.coordinator import Coordinator, FixtureCaseVersions, FixturePolicyVersions, FixtureSession, FixtureSessionAuthority
from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.development_examples import (
    DevelopmentCatalogError,
    DevelopmentExampleCatalog,
    load_project_category_taxonomy,
    lookup_development_examples,
)

NOW = datetime(2026, 11, 4, 12, tzinfo=UTC)
SOURCE = Path(__file__).resolve().parents[1] / "docs/requirements/CASE-SCENARIOS.md"


def read_source_lf():
    return SOURCE.read_bytes().replace(b"\r\n", b"\n")


def pipeline(message):
    owner, sender, receiver = object(), object(), object()
    sessions = FixtureSessionAuthority(provisioning_capability=owner, ttl_seconds=3600)
    versions = FixtureCaseVersions(provisioning_capability=owner)
    versions.set_version("SYN-CASE-01",1,expected_version=None,capability=owner)
    policy = FixturePolicyVersions(provisioning_capability=owner,active=frozenset({"SYN-POLICY-1"}))
    token = sessions.issue(FixtureSession(actor_id="SYN-ACTOR-1",role="staff",active=True,
        allowed_case_ids=("SYN-CASE-01",)),capability=owner)
    intake = Coordinator(sessions,case_versions=versions,policy_versions=policy).prepare(
        {"case_id":"SYN-CASE-01","case_version":1,"policy_version":"SYN-POLICY-1",
         "message":message,"data_classification":"synthetic"},session_token=token)
    registry = HandoffRegistry(sender_capability=sender,receiver_capability=receiver,timeout_seconds=30,
        actor_sessions=sessions,case_versions=versions,policy_versions=policy)
    handoff = registry.prepare(intake,capability=sender,session_token=token,now=NOW)
    ack = registry.acknowledge(handoff.handoff_id,expected_version=1,capability=receiver,context=intake.context,now=NOW)
    catalog = DevelopmentExampleCatalog(provisioning_capability=owner)
    catalog.provision(read_source_lf(),capability=owner)
    return registry,ack,intake,sender,receiver,versions,owner,catalog


def lookup(p,index=1,**overrides):
    args = dict(handoff_id=p[1].handoff_id,expected_version=p[1].state_version,
        receiver_capability=p[4],context=p[2].context,item_index=index,catalog=p[7],now=NOW)
    args.update(overrides)
    return lookup_development_examples(p[0],**args)


def test_actual_table_parses_all_80_rows_with_exact_source_digest():
    owner = object()
    catalog = DevelopmentExampleCatalog(provisioning_capability=owner)
    source = read_source_lf()
    catalog.provision(source,capability=owner)
    rows,digest = catalog._snapshot()
    assert len(rows) == 80 and [r.row for r in rows] == list(range(1,81))
    assert digest == hashlib.sha256(source).hexdigest()
    assert rows[0].category == "Workplace safety" and rows[-1].row == 80


def test_exact_sample_is_reference_only_not_case_classification():
    message = "My expected pay did not arrive today."
    p = pipeline(message)
    result = lookup(p)
    assert result.status == "exact_reference_only" and len(result.references) == 1
    ref = result.references[0]
    assert (ref.row,ref.example_category,ref.example_band) == (17,"Missing wages","Medium [P2]")
    assert ref.source_sha256 == hashlib.sha256(read_source_lf()).hexdigest()
    assert ref.sample_status == "unverified_synthetic_development_example"
    assert (result.category,result.urgency,result.destination) == ("unknown","unknown","unknown")
    assert result.human_review_required and not result.dispatched and not result.downstream_allowed
    assert "not been assessed" in result.uncertainty[1]
    assert message not in repr(result) and message not in repr(p[0].events())


def test_example_reference_id_is_bound_to_its_catalog_row():
    from pydantic import ValidationError
    from cdit_support_mao.agents.triage.development_examples import DevelopmentReference

    result = lookup(pipeline("My expected pay did not arrive today."))
    raw = result.references[0].model_dump()
    raw["example_id"] = "SYN-EXAMPLE-018"
    with pytest.raises(ValidationError, match="example_id_row_mismatch"):
        DevelopmentReference.model_validate(raw)


@pytest.mark.parametrize("message", ["My expected pay has not arrived today.","my expected pay did not arrive today."])
def test_paraphrase_and_case_variant_never_inherit_a_label(message):
    result = lookup(pipeline(message))
    assert result.status == "no_reference" and not result.references
    assert result.category == result.urgency == "unknown" and result.human_review_required


def test_ambiguous_segmentation_does_not_offer_reference():
    p = pipeline('"My expected pay did not arrive today.')
    result = lookup(p)
    assert result.status == "ambiguous_segmentation" and not result.references


def test_catalog_is_trusted_provisioned_sealed_and_requires_complete_table():
    owner = object()
    catalog = DevelopmentExampleCatalog(provisioning_capability=owner)
    with pytest.raises(DevelopmentCatalogError,match="unauthorized_fixture_provision"):
        catalog.provision(read_source_lf(),capability=object())
    with pytest.raises(DevelopmentCatalogError,match="invalid_source_table"):
        catalog.provision(b"not the 80-row table",capability=owner)
    catalog.provision(read_source_lf(),capability=owner)
    with pytest.raises(DevelopmentCatalogError,match="catalog_already_provisioned"):
        catalog.provision(read_source_lf(),capability=owner)


def test_stale_and_wrong_receiver_stop_lookup():
    p = pipeline("My expected pay did not arrive today.")
    with pytest.raises(HandoffError,match="unauthorized_receiver"):
        lookup(p,receiver_capability=object())
    p[5].set_version("SYN-CASE-01",2,expected_version=1,capability=p[6])
    with pytest.raises(HandoffError,match="stale_case_version"):
        lookup(p)


def test_late_cancellation_blocks_return(monkeypatch):
    import cdit_support_mao.agents.triage.development_examples as module
    p = pipeline("My expected pay did not arrive today.")
    original = module.extract_request_parts
    def cancel(*args,**kwargs):
        value = original(*args,**kwargs)
        p[0].cancel(p[1].handoff_id,expected_version=p[1].state_version,capability=p[3],now=NOW)
        return value
    monkeypatch.setattr(module,"extract_request_parts",cancel)
    with pytest.raises(HandoffError,match="stale_handoff_version"):
        lookup(p)


def test_invalid_duplicate_row_band_and_category_rejected():
    raw = read_source_lf()
    duplicate = raw.replace(b"| 80 | Performance-review", b"| 79 | Performance-review")
    invalid_band = raw.replace(b"| 17 | Missing wages |", b"| 17 | Missing wages |", 1).replace(b"| Medium [P2] | Time-sensitive individual impact;", b"| Critical [P0] | Time-sensitive individual impact;", 1)
    blank_category = raw.replace(b"| 17 | Missing wages |", b"| 17 |   |", 1)
    for content in (duplicate, invalid_band, blank_category):
        owner = object()
        with pytest.raises(DevelopmentCatalogError, match="invalid_source_table"):
            DevelopmentExampleCatalog(provisioning_capability=owner).provision(content, capability=owner)


def test_other_parent_item_never_validates_equivalence_or_rules():
    p = pipeline("My expected pay did not arrive today.; I have an unrelated deadline")
    result = lookup(p)
    assert result.status == "exact_reference_only"
    assert result.references[0].content_trust == "untrusted_synthetic_example"
    assert result.urgency == "unknown" and not result.downstream_allowed
    assert "differences" in result.uncertainty[1]


def test_modified_valid_bytes_do_not_claim_verified_file_origin():
    p = pipeline("My expected pay did not arrive today.")
    changed = read_source_lf().replace(b"## Generic ticket-condition catalog", b"## Generic ticket-condition catalog", 1) + b"\n<!-- synthetic fixture modification -->\n"
    assert changed != read_source_lf()
    fixture = DevelopmentExampleCatalog(provisioning_capability=p[6])
    fixture.provision(changed, capability=p[6])
    result = lookup(p, catalog=fixture)
    ref = result.references[0]
    assert ref.source_sha256 == hashlib.sha256(changed).hexdigest()
    assert ref.source_origin == "unverified_provisioner_claim"
    assert ref.claimed_source_path == "docs/requirements/CASE-SCENARIOS.md"
    assert "source_path" not in ref.model_dump()


def test_project_taxonomy_pin_accepts_crlf_checkout(monkeypatch):
    lf_source = read_source_lf()
    crlf_source = lf_source.replace(b"\n", b"\r\n")
    original_read_bytes = Path.read_bytes

    def read_bytes_with_crlf(path):
        if path.resolve() == SOURCE.resolve():
            return crlf_source
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", read_bytes_with_crlf)
    taxonomy = load_project_category_taxonomy()

    assert taxonomy.source_sha256 == hashlib.sha256(lf_source).hexdigest()
    assert taxonomy.categories
