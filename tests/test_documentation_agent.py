"""Documentation agent (A6): verified-fact drafts, labels, privacy suppression, manual fallback."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from cdit_support_mao.agents.documentation import DocumentationAgent
from cdit_support_mao.contracts import (
    AgentStatus,
    ClaimLabel,
    DocumentationResult,
    ReasonCode,
    RunContext,
)
from cdit_support_mao.lane_harness import load_case

from conftest import CASES_DIR, NOW


@pytest.fixture
def golden_run(harness):
    return harness.run(load_case(CASES_DIR / "case-01-golden-report-export.json"), now=NOW)


def _acknowledged(run) -> set[str]:
    return {
        run.triage.contribution_id,
        run.knowledge.contribution_id,
        run.troubleshooting.contribution_id,
        run.escalation.contribution_id,
    }


def _document(run, **overrides):
    kwargs = {
        "triage": run.triage,
        "knowledge": run.knowledge,
        "troubleshooting": run.troubleshooting,
        "escalation": run.escalation,
        "recorded_actions": (),
        "acknowledged": _acknowledged(run),
        "now": NOW,
    }
    kwargs.update(overrides)
    context = kwargs.pop("context", run.context)
    return DocumentationAgent().run(context, **kwargs)


def test_golden_draft_uses_only_labelled_cited_content(golden_run) -> None:
    result = golden_run.documentation
    assert result.status is AgentStatus.COMPLETED and result.draft is not None
    draft = result.draft
    assert draft.rendered_text.startswith(draft.banner)
    lines = [line for section in draft.sections for line in section.lines]
    assert all(line.sources for line in lines if line.label is ClaimLabel.VERIFIED)
    assert all(line.basis for line in lines if line.label is ClaimLabel.INFERENCE)
    headings = [section.heading for section in draft.sections]
    assert "Suggested Tier 1 steps (not performed)" in headings
    assert "KB-NAV-001 v2.1 #s1/st1" in draft.rendered_text
    # The unverified role appears only as unverified, never as a verified fact.
    verified_text = " ".join(line.text for line in lines if line.label is ClaimLabel.VERIFIED)
    assert "Site Coordinator" not in verified_text
    assert "Reported, not verified - user_role: Site Coordinator" in draft.rendered_text
    # Proposals from other agents are inferences, not facts.
    triage_section = next(s for s in draft.sections if s.heading.startswith("Triage proposal"))
    assert all(line.label is ClaimLabel.INFERENCE for line in triage_section.lines)
    assert "do not assume any step was performed" in draft.rendered_text
    assert draft.rendered_text.isascii()


def test_draft_is_idempotent(golden_run) -> None:
    first, second = _document(golden_run), _document(golden_run)
    assert first.contribution_id == second.contribution_id
    assert first.draft.draft_id == second.draft.draft_id


def test_missing_dependency_suppresses_draft(golden_run) -> None:
    result = _document(golden_run, escalation=None)
    assert result.status is AgentStatus.BLOCKED and result.draft is None
    assert result.manual_fallback.reason_codes == (ReasonCode.MISSING_DEPENDENCY,)
    assert result.manual_fallback.instructions


def test_unacknowledged_or_stale_inputs_suppress_draft(golden_run) -> None:
    unacked = _document(golden_run, acknowledged=_acknowledged(golden_run) - {golden_run.troubleshooting.contribution_id})
    assert ReasonCode.UPSTREAM_NOT_ACKNOWLEDGED in unacked.checkpoint.reason_codes

    newer = RunContext(**{**golden_run.context.model_dump(), "case_version": 2})
    stale = _document(golden_run, context=newer)
    assert stale.status is AgentStatus.BLOCKED
    assert ReasonCode.CONTEXT_MISMATCH in stale.checkpoint.reason_codes

    unlinked = golden_run.troubleshooting.model_copy(update={"input_refs": ()})
    chain = _document(golden_run, troubleshooting=unlinked)
    assert ReasonCode.UPSTREAM_CHAIN_MISMATCH in chain.checkpoint.reason_codes


def test_sensitive_data_suppresses_draft_without_echoing_value(harness) -> None:
    run = harness.run(load_case(CASES_DIR / "case-07-sensitive-data-in-facts.json"), now=NOW)
    result = run.documentation
    assert result.status is AgentStatus.BLOCKED and result.draft is None
    assert result.checkpoint.reason_codes == (ReasonCode.SENSITIVE_DATA_DETECTED,)
    assert {finding.category for finding in result.privacy_findings} >= {"date_of_birth"}
    assert "1980-04-12" not in result.model_dump_json()
    assert any("data-handling" in step for step in result.manual_fallback.instructions)


def test_recorded_actions_only_verified_ones_count_as_performed(harness) -> None:
    run = harness.run(load_case(CASES_DIR / "case-08-login-session-loop.json"), now=NOW)
    draft = run.documentation.draft
    actions = next(s for s in draft.sections if s.heading == "Actions taken (recorded by staff)")
    assert actions.lines[0].label is ClaimLabel.VERIFIED
    assert "Loop continued".lower() in actions.lines[0].text.lower()
    assert "Reported, not verified - browser: Chrome 129" in draft.rendered_text


def test_abstained_upstream_still_documents_without_guidance(harness) -> None:
    run = harness.run(load_case(CASES_DIR / "case-04-conflicting-upload-limits.json"), now=NOW)
    draft = run.documentation.draft
    assert run.documentation.status is AgentStatus.COMPLETED
    assert "Conflicting approved sources, not resolved by the assistant" in draft.rendered_text
    assert "No Tier 1 steps are suggested" in draft.rendered_text
    assert run.documentation.confidence == "low"


def test_result_requires_exactly_one_of_draft_or_fallback(golden_run) -> None:
    data = golden_run.documentation.model_dump()
    with pytest.raises(ValidationError, match="exactly one"):
        DocumentationResult.model_validate({**data, "draft": None})
