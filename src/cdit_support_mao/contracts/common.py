"""Shared handoff primitives for MAO agent contributions.

STATUS: PROPOSED v0.1 by Shawn's Lane. These types sit on the shared-state /
handoff integration boundary (PRD "Blackboard shared state and handoff
contracts"). They require Shared Lane agreement before Manny's Lane agents are
expected to produce or consume them. Changing them is a contract change that
must be coordinated across lanes.

Design rules taken from the PRD:
- Every material claim is labelled verified (with a source), inference (with a
  basis), or unknown.
- Confidence is a provisional band; it never establishes truth or authority.
- Contributions are case-scoped, versioned, attributable, and immutable after
  handoff (models are frozen; sequences are tuples).
- Human review is always required (the field cannot be set to False).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CONTRACT_VERSION = "0.1.0-proposed"

#: Provisional confidence-band thresholds from the PRD. They are NOT calibrated
#: (deferred decision D-08); do not read scores as probabilities of truth.
PROVISIONAL_BAND_THRESHOLDS: dict[str, float] = {"high": 0.85, "medium": 0.60}
CONFIDENCE_CALIBRATED = False

#: Prototype data boundary: only synthetic case identifiers are accepted.
SYNTHETIC_CASE_ID_PATTERN = r"^SYN-[A-Z0-9][A-Z0-9-]*$"


class StrictModel(BaseModel):
    """Immutable model that rejects unexpected fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ClaimLabel(StrEnum):
    VERIFIED = "verified"
    INFERENCE = "inference"
    UNKNOWN = "unknown"


class ConfidenceBand(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


_BAND_RANK = {ConfidenceBand.LOW: 0, ConfidenceBand.MEDIUM: 1, ConfidenceBand.HIGH: 2}


def band_for(score: float) -> ConfidenceBand:
    """Map a provisional 0..1 evidence score to a band (uncalibrated, see D-08)."""
    if not 0.0 <= score <= 1.0:
        raise ValueError(f"score must be within [0, 1], got {score}")
    if score >= PROVISIONAL_BAND_THRESHOLDS["high"]:
        return ConfidenceBand.HIGH
    if score >= PROVISIONAL_BAND_THRESHOLDS["medium"]:
        return ConfidenceBand.MEDIUM
    return ConfidenceBand.LOW


def min_band(*bands: ConfidenceBand) -> ConfidenceBand:
    """Return the weakest band; downstream confidence may never exceed upstream."""
    if not bands:
        return ConfidenceBand.LOW
    return min(bands, key=lambda band: _BAND_RANK[band])


class AgentStatus(StrEnum):
    COMPLETED = "completed"
    """Checks passed; output may be handed off for the next stage."""
    ABSTAINED = "abstained"
    """Agent ran safely but declined to produce guidance; reasons are recorded."""
    BLOCKED = "blocked"
    """Input or output failed validation; nothing usable was produced."""


class Stage(StrEnum):
    TRIAGE = "triage"
    KNOWLEDGE = "knowledge"
    TROUBLESHOOTING = "troubleshooting"
    ESCALATION = "escalation"
    DOCUMENTATION = "documentation"


class ReasonCode(StrEnum):
    """Machine-readable reasons for abstention, blocking, flags, and rejections."""

    # Connection / join integrity
    CONTEXT_MISMATCH = "context_mismatch"
    UPSTREAM_NOT_ACKNOWLEDGED = "upstream_not_acknowledged"
    UPSTREAM_BLOCKED = "upstream_blocked"
    UPSTREAM_CHAIN_MISMATCH = "upstream_chain_mismatch"
    MISSING_DEPENDENCY = "missing_dependency"
    # Knowledge (A3)
    NO_RELEVANT_SOURCE = "no_relevant_source"
    WEAK_EVIDENCE = "weak_evidence"
    STALE_SOURCE_ONLY = "stale_source_only"
    UNAPPROVED_SOURCE_ONLY = "unapproved_source_only"
    CONFLICTING_SOURCES = "conflicting_sources"
    MULTIPLE_APPROVED_VERSIONS = "multiple_approved_versions"
    RETRIEVED_INJECTION = "retrieved_injection"
    SOURCE_STALE = "source_stale"
    SOURCE_NOT_EFFECTIVE = "source_not_effective"
    SOURCE_UNAPPROVED = "source_unapproved"
    SOURCE_RETIRED = "source_retired"
    # Troubleshooting (A4)
    KNOWLEDGE_ABSTAINED = "knowledge_abstained"
    RESTRICTED_ACTION_REQUESTED = "restricted_action_requested"
    UNSUPPORTED_STEP_REJECTED = "unsupported_step_rejected"
    UNKNOWN_ACTION_TYPE = "unknown_action_type"
    STAFF_ONLY_PROCEDURE = "staff_only_procedure"
    POLICY_STOP_CONDITION = "policy_stop_condition"
    # Documentation (A6)
    SENSITIVE_DATA_DETECTED = "sensitive_data_detected"
    UNSUPPORTED_CLAIM = "unsupported_claim"


class SourceKind(StrEnum):
    KB_SECTION = "kb_section"
    KB_STEP = "kb_step"
    CASE_FIELD = "case_field"
    STAFF_ENTRY = "staff_entry"
    POLICY_RULE = "policy_rule"
    CONTRIBUTION = "contribution"


class SourceRef(StrictModel):
    """Pointer to the evidence behind a claim. Never carries the evidence text."""

    kind: SourceKind
    source_id: str = Field(min_length=1, max_length=120)
    version: str = Field(min_length=1, max_length=60)
    locator: str | None = Field(default=None, max_length=120)

    def cite(self) -> str:
        """ASCII citation, e.g. ``KB-NAV-001 v2.1 #s1/st2`` (safe for any case-note system)."""
        locator = f" #{self.locator}" if self.locator else ""
        return f"{self.source_id} v{self.version}{locator}"


class Claim(StrictModel):
    """A material statement with its evidence label, sources, and confidence."""

    statement: str = Field(min_length=1, max_length=2000)
    label: ClaimLabel
    sources: tuple[SourceRef, ...] = ()
    basis: str | None = Field(default=None, max_length=500)
    confidence: ConfidenceBand

    @model_validator(mode="after")
    def _label_rules(self) -> Claim:
        if self.label is ClaimLabel.VERIFIED and not self.sources:
            raise ValueError("a verified claim must name at least one source")
        if self.label is ClaimLabel.INFERENCE and not self.basis:
            raise ValueError("an inference must state its basis")
        if self.label is ClaimLabel.UNKNOWN and self.confidence is ConfidenceBand.HIGH:
            raise ValueError("an unknown claim cannot carry high confidence")
        return self


class RunContext(StrictModel):
    """Identifies the case run every contribution belongs to (join key)."""

    run_id: str = Field(pattern=r"^RUN-[A-Za-z0-9-]+$")
    case_id: str = Field(pattern=SYNTHETIC_CASE_ID_PATTERN)
    case_version: int = Field(ge=1)
    policy_version: str = Field(min_length=1, max_length=60)
    data_classification: Literal["synthetic"] = "synthetic"


class CheckpointOutcome(StrictModel):
    checkpoint: Literal["A2", "A3", "A4", "A5", "A6"]
    passed: bool
    reason_codes: tuple[ReasonCode, ...] = ()

    @model_validator(mode="after")
    def _failures_need_reasons(self) -> CheckpointOutcome:
        if not self.passed and not self.reason_codes:
            raise ValueError("a failed checkpoint must record at least one reason code")
        return self


class InputRef(StrictModel):
    """Records which upstream contribution (and contract version) was consumed."""

    contribution_id: str = Field(min_length=1, max_length=80)
    stage: Stage
    contract_version: str


class AgentContribution(StrictModel):
    """Common envelope for every agent contribution written to the blackboard."""

    contract_version: Literal["0.1.0-proposed"] = CONTRACT_VERSION
    contribution_id: str = Field(min_length=1, max_length=80)
    stage: Stage
    agent: str
    agent_version: str
    context: RunContext
    input_refs: tuple[InputRef, ...] = ()
    created_at: datetime
    status: AgentStatus
    checkpoint: CheckpointOutcome
    claims: tuple[Claim, ...] = ()
    confidence: ConfidenceBand
    confidence_rationale: str = Field(min_length=1, max_length=500)
    unknowns: tuple[str, ...] = ()
    human_review_required: Literal[True] = True

    @field_validator("created_at")
    @classmethod
    def _timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware (UTC recommended, see D-10)")
        return value

    @model_validator(mode="after")
    def _status_matches_checkpoint(self) -> AgentContribution:
        if (self.status is AgentStatus.COMPLETED) != self.checkpoint.passed:
            raise ValueError("status 'completed' if and only if the checkpoint passed")
        return self

    def as_input_ref(self) -> InputRef:
        return InputRef(
            contribution_id=self.contribution_id,
            stage=self.stage,
            contract_version=self.contract_version,
        )


def stable_id(prefix: str, *parts: object) -> str:
    """Deterministic identifier so repeated runs on the same inputs are idempotent."""
    payload = json.dumps([prefix, *(str(part) for part in parts)], separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16].upper()
    return f"{prefix}-{digest}"
