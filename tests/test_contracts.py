"""Contract rules from the PRD: evidence labels, bands, synthetic IDs, immutability."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from cdit_support_mao.contracts import (
    CONFIDENCE_CALIBRATED,
    CheckpointOutcome,
    Claim,
    ClaimLabel,
    ConfidenceBand,
    RunContext,
    SourceKind,
    SourceRef,
    band_for,
    min_band,
    stable_id,
)

REF = SourceRef(kind=SourceKind.KB_SECTION, source_id="KB-NAV-001", version="2.1", locator="s1")


def test_verified_claim_requires_source() -> None:
    with pytest.raises(ValidationError, match="verified claim"):
        Claim(statement="x", label=ClaimLabel.VERIFIED, confidence=ConfidenceBand.HIGH)
    assert Claim(statement="x", label=ClaimLabel.VERIFIED, sources=(REF,), confidence=ConfidenceBand.HIGH)


def test_inference_requires_basis_and_unknown_cannot_be_high() -> None:
    with pytest.raises(ValidationError, match="basis"):
        Claim(statement="x", label=ClaimLabel.INFERENCE, confidence=ConfidenceBand.MEDIUM)
    with pytest.raises(ValidationError, match="unknown claim"):
        Claim(statement="x", label=ClaimLabel.UNKNOWN, confidence=ConfidenceBand.HIGH)


@pytest.mark.parametrize(
    ("score", "band"),
    [(1.0, "high"), (0.85, "high"), (0.8499, "medium"), (0.60, "medium"), (0.5999, "low"), (0.0, "low")],
)
def test_provisional_band_thresholds(score: float, band: str) -> None:
    assert band_for(score) == band
    assert CONFIDENCE_CALIBRATED is False


def test_band_rejects_out_of_range_and_min_band_takes_weakest() -> None:
    with pytest.raises(ValueError):
        band_for(1.2)
    assert min_band(ConfidenceBand.HIGH, ConfidenceBand.LOW, ConfidenceBand.MEDIUM) is ConfidenceBand.LOW
    assert min_band() is ConfidenceBand.LOW


@pytest.mark.parametrize("case_id", ["CASE-1", "syn-case-1", "SYN-", "REAL-SF-00012"])
def test_run_context_accepts_only_synthetic_case_ids(case_id: str) -> None:
    with pytest.raises(ValidationError):
        RunContext(run_id="RUN-1", case_id=case_id, case_version=1, policy_version="P")


def test_run_context_rejects_non_synthetic_classification() -> None:
    with pytest.raises(ValidationError):
        RunContext(
            run_id="RUN-1",
            case_id="SYN-CASE-1",
            case_version=1,
            policy_version="P",
            data_classification="production",
        )


def test_failed_checkpoint_needs_reason() -> None:
    with pytest.raises(ValidationError, match="reason code"):
        CheckpointOutcome(checkpoint="A3", passed=False)


def test_contributions_are_frozen_strict_and_always_need_human_review(make_triage) -> None:
    triage = make_triage("Where is the enrollment report export?")
    with pytest.raises(ValidationError):
        triage.status = "blocked"  # type: ignore[misc]
    data = triage.model_dump()
    with pytest.raises(ValidationError):
        type(triage).model_validate({**data, "human_review_required": False})
    with pytest.raises(ValidationError):
        type(triage).model_validate({**data, "unexpected_field": 1})
    with pytest.raises(ValidationError, match="timezone-aware"):
        type(triage).model_validate({**data, "created_at": datetime(2026, 11, 3, 12, 0)})
    with pytest.raises(ValidationError, match="if and only if"):
        type(triage).model_validate(
            {**data, "checkpoint": {"checkpoint": "A2", "passed": False, "reason_codes": ["upstream_blocked"]}}
        )


def test_stable_id_is_deterministic_and_prefix_sensitive() -> None:
    assert stable_id("KNW", "a", 1) == stable_id("KNW", "a", 1)
    assert stable_id("KNW", "a", 1) != stable_id("KNW", "a", 2)
    assert stable_id("TRI", "a").split("-")[1] != stable_id("ESC", "a").split("-")[1]


def test_citation_is_ascii() -> None:
    assert REF.cite() == "KB-NAV-001 v2.1 #s1"
    assert REF.cite().isascii()


def test_escalation_handoff_contract_invariants(context) -> None:
    from datetime import UTC
    from cdit_support_mao.contracts.handoffs import EscalationHandoff
    from cdit_support_mao.contracts.common import AgentStatus

    now = datetime(2026, 11, 4, 12, 0, tzinfo=UTC)
    handoff = EscalationHandoff(
        contribution_id="ESC-TEST-1",
        agent="escalation-agent",
        agent_version="0.1.0",
        context=context,
        created_at=now,
        status=AgentStatus.COMPLETED,
        checkpoint=CheckpointOutcome(checkpoint="A5", passed=True),
        must_escalate=False,
        triggers=(),
        recommendation="no_escalation_proposed",
        reason="Routine handling.",
        confidence=ConfidenceBand.HIGH,
        confidence_rationale="High confidence based on verified rules.",
    )
    assert handoff.stage == "escalation"
    assert handoff.human_review_required is True

    # Mutability check
    with pytest.raises(ValidationError):
        handoff.must_escalate = True  # type: ignore[misc]

    # Human review invariant
    data = handoff.model_dump()
    with pytest.raises(ValidationError):
        EscalationHandoff.model_validate({**data, "human_review_required": False})

    # Extra fields forbidden
    with pytest.raises(ValidationError):
        EscalationHandoff.model_validate({**data, "unexpected_attribute": "forbidden"})
