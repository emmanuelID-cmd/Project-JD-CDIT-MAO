"""Bounded, synthetic fixture attention signals; never a priority policy.

Literal matches are case-sensitive and identify only text appearing in an untrusted report. Absence of
matches does not assess risk, and a match does not establish an incident. The first
occurrence of each configured literal is returned for each bounded item span; IDs
lack cross-instance version or digest guarantees. Inspect the full parent for context.
"""
from __future__ import annotations

from datetime import datetime
from threading import Lock
from typing import Literal

from pydantic import Field, model_validator

from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.input import read_acknowledged_input
from cdit_support_mao.contracts.common import RunContext, SourceRef, StrictModel


class FixtureAttentionPatterns:
    """Sealed, capability-provisioned test patterns; not approved policy."""

    def __init__(self, *, provisioning_capability: object):
        if provisioning_capability is None or isinstance(provisioning_capability, (str, bytes, int, bool)):
            raise ValueError("private fixture capability required")
        self._capability = provisioning_capability
        self._entries: dict[str, str] = {}
        self._sealed = False
        self._lock = Lock()

    def add(self, pattern_id: str, literal: str, *, capability: object) -> None:
        if capability is not self._capability:
            raise ValueError("unauthorized_fixture_provisioning")
        if (not isinstance(pattern_id, str) or not pattern_id.startswith("SYN-")
                or not pattern_id.isascii() or not all(c.isalnum() or c == "-" for c in pattern_id)
                or len(pattern_id) > 60 or len(pattern_id) < 5):
            raise ValueError("invalid_fixture_pattern_id")
        if (not isinstance(literal, str) or not 3 <= len(literal) <= 200
                or not literal.strip() or any(ord(c) < 32 for c in literal)):
            raise ValueError("invalid_fixture_pattern")
        with self._lock:
            if self._sealed or pattern_id in self._entries or len(self._entries) >= 32:
                raise ValueError("fixture_pattern_not_mutable")
            self._entries[pattern_id] = literal

    def seal(self, *, capability: object) -> None:
        if capability is not self._capability:
            raise ValueError("unauthorized_fixture_provisioning")
        with self._lock:
            self._sealed = True

    def _snapshot(self) -> tuple[tuple[str, str], ...]:
        with self._lock:
            if not self._sealed:
                raise HandoffError("fixture_patterns_not_sealed")
            return tuple(self._entries.items())


class AttentionMatch(StrictModel):
    fixture_pattern_id: str
    source: SourceRef
    start_codepoint: int = Field(strict=True, ge=0)
    end_codepoint: int = Field(strict=True, ge=1)
    attribution: Literal["untrusted_case_text_match_only"] = "untrusted_case_text_match_only"

    @model_validator(mode="after")
    def validate_span(self) -> AttentionMatch:
        if self.start_codepoint >= self.end_codepoint:
            raise ValueError("attention_span_must_be_nonempty")
        return self


class AttentionSignal(StrictModel):
    trace_id: str
    handoff_id: str
    handoff_state_version: int = Field(strict=True, ge=2)
    context: RunContext
    status: Literal["potential_attention", "not_assessed"]
    matches: tuple[AttentionMatch, ...]
    review_note: Literal[
        "A configured synthetic phrase matched; a human must inspect its full context. This does not verify an incident or assign urgency."
    ] | None = None
    human_review_required: Literal[True] = True
    urgency: Literal["unknown"] = "unknown"
    downstream_allowed: Literal[False] = False
    dispatched: Literal[False] = False
    incident_verified: Literal[False] = False

    @model_validator(mode="after")
    def validate_signal(self) -> AttentionSignal:
        if (self.status == "potential_attention") != bool(self.matches):
            raise ValueError("attention_status_match_mismatch")
        if (self.status == "potential_attention") != (self.review_note is not None):
            raise ValueError("attention_review_note_mismatch")
        return self


def inspect_attention_signal(
    registry: HandoffRegistry, *, handoff_id: str, expected_version: int,
    receiver_capability: object, context: RunContext,
    fixture_patterns: FixtureAttentionPatterns,
    item_spans: tuple[tuple[int, int], ...] | None = None,
    now: datetime | None = None,
) -> AttentionSignal:
    """Inspect fixture literals in the authorized full source; do not dispatch.

    A matched substring is neither contextual risk assessment nor verified
    event. Reviewer must inspect the complete authorized parent for quoted,
    negated, historical, or other context. A later consumer must revalidate
    authorization and state; the caller-supplied clock is fixture-only.
    """
    if not isinstance(fixture_patterns, FixtureAttentionPatterns):
        raise HandoffError("invalid_fixture_patterns")
    patterns = fixture_patterns._snapshot()
    packet = read_acknowledged_input(registry, handoff_id=handoff_id,
        expected_version=expected_version, receiver_capability=receiver_capability,
        context=context, now=now)
    spans = item_spans or ((0, len(packet.reported_message)),)
    if (len(spans) > 8 or any(
        start < 0 or start >= end or end > len(packet.reported_message)
        for start, end in spans
    ) or any(spans[index][1] > spans[index + 1][0] for index in range(len(spans) - 1))):
        raise HandoffError("invalid_attention_item_spans")
    matches = []
    for pattern_id, literal in patterns:
        for span_start, span_end in spans:
            start = packet.reported_message.find(literal, span_start, span_end)
            if start >= 0:
                matches.append(AttentionMatch(fixture_pattern_id=pattern_id, source=packet.source,
                    start_codepoint=start, end_codepoint=start + len(literal)))
    result = AttentionSignal(trace_id=packet.trace_id, handoff_id=handoff_id,
        handoff_state_version=expected_version, context=context,
        status="potential_attention" if matches else "not_assessed", matches=tuple(matches),
        review_note=(
            "A configured synthetic phrase matched; a human must inspect its full context. "
            "This does not verify an incident or assign urgency."
            if matches else None
        ))
    registry.validate_active(handoff_id, expected_version=expected_version,
        capability=receiver_capability, context=context, now=now)
    return result
