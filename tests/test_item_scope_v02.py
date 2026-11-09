"""S-1.1: item scope 0.2, the attention check status, and the taxonomy citation.

Covers the shared change approved by Manny on 2026-11-08
(docs/lanes/shawn/S-1.1-ITEM-SCOPE-PROPOSAL.md, answers Q1 to Q5):

- Q1: ``attention_check`` is ``potential_attention``, ``no_configured_match``, or
  ``check_not_run``, with its consistency rules.
- Q2: only the pinned taxonomy source ID is exempt from the policy-version rule,
  and only as a self-consistent, content-addressed reference.
- Q3: ``check_not_run`` is information for Staff/Admin and adds no hold.
- Q4: new scopes are 0.2; legacy 0.1 scopes keep the S-1 rules.
- Q5 (2026-11-09): ``attention_check`` is required on every 0.2 scope, now that
  Manny's connector always supplies it (``1c822c8``); legacy 0.1 scopes still omit it.

All data is synthetic.
"""

from __future__ import annotations

import hashlib
import json

import pytest
from pydantic import ValidationError

from cdit_support_mao.agents.documentation import DocumentationAgent
from cdit_support_mao.contracts import (
    CATEGORY_TAXONOMY_SOURCE_ID,
    LEGACY_TRIAGE_ITEM_SCOPE_VERSION,
    TRIAGE_ITEM_SCOPE_VERSION,
    AgentStatus,
    ClaimLabel,
    EscalationHandoff,
    ReasonCode,
    SourceKind,
    SourceRef,
    TriageHandoff,
    is_category_taxonomy_ref,
)

from conftest import AS_OF, NOW
from test_item_scope import item_case, passages_of, revalidate

DIGEST = hashlib.sha256(b"synthetic category names").hexdigest()
TAXONOMY_REF = {
    "kind": "policy_rule",
    "source_id": CATEGORY_TAXONOMY_SOURCE_ID,
    "version": f"sha256-{DIGEST[:16]}",
    "locator": f"category_sha256:{DIGEST}",
}
CHECK_PREFIX = "Attention check:"


def determined(**scope: object):
    return item_case(urgency="low", auditor_review="band_and_route_determined", **scope)


def with_category_sources(triage: TriageHandoff, *extra: dict) -> list[dict]:
    return [*triage.model_dump(mode="json")["item_scope"]["category_sources"], *extra]


def lines_of(documentation) -> list:
    return [line for section in documentation.draft.sections for line in section.lines]


def check_lines(documentation) -> list:
    return [line for line in lines_of(documentation) if line.text.startswith(CHECK_PREFIX)]


def rechain(run, triage: TriageHandoff, knowledge_agent, troubleshooting_agent):
    """Run Shawn's agents again on a revalidated Triage handoff (fresh digests)."""
    context = triage.context
    knowledge = knowledge_agent.run(context, triage, acknowledged={triage.contribution_id}, as_of=AS_OF, now=NOW)
    troubleshooting = troubleshooting_agent.run(
        context, triage, knowledge, acknowledged={triage.contribution_id, knowledge.contribution_id}, now=NOW
    )
    escalation = EscalationHandoff.model_validate(
        {**run.escalation.model_dump(mode="json"), "input_refs": [triage.as_input_ref().model_dump(mode="json")]}
    )
    acknowledged = {c.contribution_id for c in (triage, knowledge, troubleshooting, escalation)}
    documentation = DocumentationAgent().run(
        context, triage=triage, knowledge=knowledge, troubleshooting=troubleshooting,
        escalation=escalation, acknowledged=acknowledged, now=NOW,
    )
    return knowledge, troubleshooting, documentation


# ---------------------------------------------------------------------------
# Q4: scope version
# ---------------------------------------------------------------------------


def test_new_item_scopes_are_version_0_2_and_the_echo_carries_it(harness) -> None:
    run = harness.run(item_case(), now=NOW)
    ident = run.triage.item_scope.identity
    assert TRIAGE_ITEM_SCOPE_VERSION == "triage-item-scope-0.2-proposed"
    assert ident.scope_contract_version == TRIAGE_ITEM_SCOPE_VERSION and not ident.is_legacy_scope
    assert run.knowledge.item_scope_ref == ident


# A legacy 0.1 scope never states the attention check (Q4, Q5).
LEGACY_SCOPE = {
    "item_scope.identity.scope_contract_version": LEGACY_TRIAGE_ITEM_SCOPE_VERSION,
    "item_scope.attention_check": None,
}


def test_unknown_scope_version_is_rejected(harness) -> None:
    triage = harness.run(item_case(), now=NOW).triage
    with pytest.raises(ValidationError, match="scope_contract_version"):
        revalidate(triage, **{"item_scope.identity.scope_contract_version": "triage-item-scope-0.3-proposed"})


def test_legacy_0_1_scope_still_flows_under_the_s1_rules(harness, knowledge_agent, troubleshooting_agent) -> None:
    run = harness.run(determined(), now=NOW)
    legacy = revalidate(run.triage, **LEGACY_SCOPE)
    assert legacy.item_scope.identity.is_legacy_scope and legacy.item_scope.attention_check is None
    knowledge, troubleshooting, documentation = rechain(run, legacy, knowledge_agent, troubleshooting_agent)
    assert knowledge.item_scope_ref.scope_contract_version == LEGACY_TRIAGE_ITEM_SCOPE_VERSION
    assert passages_of(knowledge) == passages_of(run.knowledge)
    assert troubleshooting.status is AgentStatus.COMPLETED
    assert documentation.status is AgentStatus.COMPLETED
    (line,) = check_lines(documentation)
    assert line.label is ClaimLabel.UNKNOWN and "did not say" in line.text


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"item_scope.attention_check": "no_configured_match"}, "attention_check_requires_scope_0_2"),
        ({"item_scope.category_sources": "taxonomy"}, "item_claim_policy_version_mismatch"),
    ],
    ids=["attention_check", "taxonomy_ref"],
)
def test_legacy_0_1_scope_rejects_the_s1_1_additions(harness, changes, error) -> None:
    triage = harness.run(item_case(), now=NOW).triage
    if changes.get("item_scope.category_sources") == "taxonomy":
        changes = {"item_scope.category_sources": with_category_sources(triage, TAXONOMY_REF)}
    with pytest.raises(ValidationError, match=error):
        revalidate(
            triage, **{**LEGACY_SCOPE, **changes}
        )


# ---------------------------------------------------------------------------
# Q1: attention check status rules
# ---------------------------------------------------------------------------

ATTENTION_REF = {"kind": "case_field", "source_id": "SYN-CASE-0901", "version": "1", "locator": "attention-flag:0-6"}


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"item_scope.attention_check": "potential_attention"}, "attention_check_ref_mismatch"),
        (
            {"item_scope.attention_check": "no_configured_match", "item_scope.attention_ref": ATTENTION_REF,
             "item_scope.parent_attention_flagged": True},
            "attention_check_ref_mismatch",
        ),
        (
            {"item_scope.attention_check": "check_not_run", "item_scope.parent_attention_flagged": True},
            "attention_check_not_run_but_parent_flagged",
        ),
        ({"item_scope.attention_check": "none_found"}, "attention_check"),
        ({"item_scope.attention_check": "not_assessed"}, "attention_check"),
    ],
    ids=["flag_without_ref", "ref_without_flag", "not_run_with_parent_flag", "none_found", "not_assessed"],
)
def test_schema_rejects_inconsistent_attention_check(harness, changes, error) -> None:
    triage = harness.run(item_case(), now=NOW).triage
    with pytest.raises(ValidationError, match=error):
        revalidate(triage, **changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"item_scope.attention_check": "potential_attention", "item_scope.attention_ref": ATTENTION_REF,
         "item_scope.parent_attention_flagged": True},
        {"item_scope.attention_check": "no_configured_match", "item_scope.parent_attention_flagged": True},
        {"item_scope.attention_check": "no_configured_match"},
        {"item_scope.attention_check": "check_not_run"},
    ],
    ids=["flagged", "match_elsewhere", "no_match", "not_run"],
)
def test_schema_accepts_consistent_attention_check(harness, changes) -> None:
    triage = harness.run(item_case(), now=NOW).triage
    assert revalidate(triage, **changes).item_scope.attention_check == changes["item_scope.attention_check"]


def test_q5_attention_check_is_required_on_a_0_2_scope(harness) -> None:
    triage = harness.run(item_case(), now=NOW).triage
    assert not triage.item_scope.identity.is_legacy_scope
    with pytest.raises(ValidationError, match="attention_check_required_for_scope_0_2"):
        revalidate(triage, **{"item_scope.attention_check": None})


@pytest.mark.parametrize(
    ("stand_in", "expected"),
    [
        ({"attention_on_item": True}, "potential_attention"),
        ({"parent_attention_flagged": True}, "no_configured_match"),
        ({}, "check_not_run"),
        ({"attention_check": "no_configured_match"}, "no_configured_match"),
    ],
    ids=["flagged", "flag_elsewhere", "silent", "stated"],
)
def test_harness_derives_the_check_like_the_connector(harness, stand_in, expected) -> None:
    scope = harness.run(item_case(**stand_in), now=NOW).triage.item_scope
    assert scope.attention_check == expected
    assert (scope.attention_ref is not None) == (expected == "potential_attention")


# ---------------------------------------------------------------------------
# Q2: content-addressed taxonomy citation
# ---------------------------------------------------------------------------


def test_taxonomy_reference_is_accepted_on_a_0_2_scope(harness) -> None:
    triage = harness.run(item_case(), now=NOW).triage
    cited = revalidate(triage, **{"item_scope.category_sources": with_category_sources(triage, TAXONOMY_REF)})
    taxonomy = SourceRef.model_validate(TAXONOMY_REF)
    assert taxonomy in cited.item_scope.category_sources and is_category_taxonomy_ref(taxonomy)


@pytest.mark.parametrize(
    ("override", "error"),
    [
        ({"version": "sha256-0000000000000000"}, "item_claim_taxonomy_source_mismatch"),
        ({"locator": "category_names"}, "item_claim_taxonomy_source_mismatch"),
        ({"locator": f"category_sha256:{DIGEST[:63]}"}, "item_claim_taxonomy_source_mismatch"),
        (
            {"locator": f"category_sha256:{DIGEST.upper()}", "version": f"sha256-{DIGEST[:16].upper()}"},
            "item_claim_taxonomy_source_mismatch",
        ),
        ({"source_id": "SYN-OTHER-POLICY"}, "item_claim_policy_version_mismatch"),
    ],
    ids=["version_not_derived", "no_digest", "short_digest", "upper_case", "other_policy_source"],
)
def test_malformed_or_other_policy_sources_are_rejected(harness, override, error) -> None:
    triage = harness.run(item_case(), now=NOW).triage
    bad = {**TAXONOMY_REF, **override}
    with pytest.raises(ValidationError, match=error):
        revalidate(triage, **{"item_scope.category_sources": with_category_sources(triage, bad)})


def test_other_policy_sources_still_need_the_run_policy_version(harness) -> None:
    triage = harness.run(item_case(), now=NOW).triage
    current = {"kind": "policy_rule", "source_id": "SYN-OTHER-POLICY", "version": triage.context.policy_version}
    assert revalidate(triage, **{"item_scope.category_sources": with_category_sources(triage, current)})


def test_taxonomy_helper_only_matches_the_pinned_source() -> None:
    ref = SourceRef.model_validate(TAXONOMY_REF)
    assert is_category_taxonomy_ref(ref)
    assert not is_category_taxonomy_ref(ref.model_copy(update={"kind": SourceKind.CASE_FIELD}))
    assert not is_category_taxonomy_ref(ref.model_copy(update={"source_id": "SYN-OTHER-POLICY"}))


def test_documentation_cites_the_taxonomy_on_the_category_line(harness, knowledge_agent, troubleshooting_agent) -> None:
    run = harness.run(determined(attention_check="no_configured_match"), now=NOW)
    cited = revalidate(run.triage, **{"item_scope.category_sources": with_category_sources(run.triage, TAXONOMY_REF)})
    _, _, documentation = rechain(run, cited, knowledge_agent, troubleshooting_agent)
    assert documentation.status is AgentStatus.COMPLETED and not documentation.privacy_findings
    category = next(line for line in lines_of(documentation) if line.text.startswith("Proposed category"))
    assert SourceRef.model_validate(TAXONOMY_REF) in category.sources


# ---------------------------------------------------------------------------
# Q1 and Q3: Documentation lines, no extra hold, Knowledge unaffected
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("check", "label", "phrase"),
    [
        ("no_configured_match", ClaimLabel.INFERENCE, "This is not a risk assessment."),
        ("check_not_run", ClaimLabel.INFERENCE, "Information only; the Auditor's urgency review still applies."),
    ],
    ids=["no_match", "not_run"],
)
def test_documentation_states_the_attention_check(harness, check, label, phrase) -> None:
    run = harness.run(determined(attention_check=check), now=NOW)
    assert run.documentation.status is AgentStatus.COMPLETED
    (line,) = check_lines(run.documentation)
    assert line.label is label and phrase in line.text
    assert not any(other.text.startswith("Attention flag present") for other in lines_of(run.documentation))


def test_flagged_item_keeps_the_flag_line_and_no_check_line(harness) -> None:
    run = harness.run(determined(attention_on_item=True), now=NOW)
    assert any(line.text.startswith("Attention flag present") for line in lines_of(run.documentation))
    assert check_lines(run.documentation) == []


def test_flag_on_another_item_is_shown_with_this_items_check(harness) -> None:
    run = harness.run(determined(parent_attention_flagged=True, attention_check="no_configured_match"), now=NOW)
    texts = [line.text for line in lines_of(run.documentation)]
    assert any(text.startswith("Another item of the parent case") for text in texts)
    assert any(text.startswith(f"{CHECK_PREFIX} no configured phrase") for text in texts)


@pytest.mark.parametrize("auditor", ["pending", "band_and_route_determined"])
def test_check_not_run_adds_no_hold(harness, auditor) -> None:
    """Q3: the status is information only; the existing Auditor gates decide."""
    urgency = "unknown" if auditor == "pending" else "low"
    runs = [
        harness.run(item_case(urgency=urgency, auditor_review=auditor, attention_check=check), now=NOW)
        for check in ("check_not_run", "no_configured_match")
    ]
    statuses = [(r.knowledge.status, r.troubleshooting.status, r.documentation.status) for r in runs]
    reasons = [tuple(r.troubleshooting.checkpoint.reason_codes) for r in runs]
    assert statuses[0] == statuses[1] and reasons[0] == reasons[1]
    if auditor == "pending":
        assert ReasonCode.MISSING_DEPENDENCY in reasons[0]
    else:
        assert statuses[0] == (AgentStatus.COMPLETED,) * 3


def test_knowledge_ignores_the_attention_check(harness) -> None:
    runs = [harness.run(item_case(attention_check=check), now=NOW) for check in ("check_not_run", "no_configured_match")]
    runs.append(harness.run(item_case(), now=NOW))
    assert passages_of(runs[0].knowledge) == passages_of(runs[1].knowledge) == passages_of(runs[2].knowledge)
    for run in runs:
        assert "attention" not in json.dumps(run.knowledge.model_dump(mode="json"))
