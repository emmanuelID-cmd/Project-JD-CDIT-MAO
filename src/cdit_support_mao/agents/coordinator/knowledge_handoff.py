"""Fixture-only Coordinator -> Knowledge acknowledgment; not a production gate.

A separately provisioned declaration marks a test stand-in, not actual approval,
grounding or an accepted Shared handoff. FixturePolicyProposal remains blocked.
No database, authentication, network dispatch or ticket write is implemented.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from threading import Lock
from uuid import uuid4

from pydantic import ValidationError

from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.segment import extract_request_parts
from cdit_support_mao.agents.triage.fixture_policy import SyntheticPolicyCatalog, propose_from_synthetic_policy
from cdit_support_mao.contracts.common import AgentStatus, ClaimLabel, ConfidenceBand, RunContext
from cdit_support_mao.contracts.handoffs import TriageHandoff


def _valid_capability(value: object) -> bool:
    return value is not None and not isinstance(value, (str, bytes, int, float, bool))


def _candidate(value: object) -> TriageHandoff:
    if not isinstance(value, TriageHandoff):
        raise HandoffError("invalid_fixture_triage")
    raw = value.model_dump(warnings="none")
    raw_context = raw.get("context")
    if not isinstance(raw_context, dict) or type(raw_context.get("case_version")) is not int:
        raise HandoffError("invalid_fixture_triage")
    try:
        obj = TriageHandoff.model_validate(raw)
    except (ValidationError, ValueError, TypeError):
        raise HandoffError("invalid_fixture_triage") from None
    if (obj.status is not AgentStatus.COMPLETED or obj.checkpoint.checkpoint != "A2"
            or not obj.checkpoint.passed or not obj.category or not obj.category.strip() or obj.category.strip().lower() == "unknown" or obj.urgency != "low"
            or obj.unknowns or obj.missing_facts or len(obj.claims) > 1 or obj.case_facts):
        raise HandoffError("fixture_triage_not_eligible")
    if obj.claims:
        claim = obj.claims[0]
        if (obj.agent != "synthetic-triage-stand-in" or obj.agent_version != "fixture-0.1"
                or claim.label is not ClaimLabel.INFERENCE or claim.confidence is not ConfidenceBand.LOW
                or obj.confidence is not ConfidenceBand.LOW or obj.category_confidence is not ConfidenceBand.LOW
                or len(claim.sources) != 2):
            raise HandoffError("fixture_claim_not_eligible")
    return obj


def _fingerprint(obj: TriageHandoff) -> str:
    return hashlib.sha256(obj.model_dump_json().encode("utf-8")).hexdigest()


class FixtureA2Declarations:
    """Private synthetic test declarations; not actual approval or evidence."""
    def __init__(self, *, provisioning_capability: object):
        if not _valid_capability(provisioning_capability):
            raise ValueError("invalid_fixture_capability")
        self._provisioner = provisioning_capability
        self._entries: set[tuple[str, int, str, str]] = set()
        self._lock = Lock()

    def declare(self, *, source_handoff_id: str, source_version: int,
                contribution: TriageHandoff, capability: object,
                next_stage: str, single_independent_nonurgent: bool) -> None:
        if capability is not self._provisioner:
            raise HandoffError("unauthorized_fixture_declaration")
        obj = _candidate(contribution)
        if next_stage != "knowledge_fixture" or single_independent_nonurgent is not True:
            raise HandoffError("invalid_fixture_declaration")
        if not isinstance(source_handoff_id, str) or type(source_version) is not int or source_version < 2:
            raise HandoffError("invalid_fixture_declaration")
        with self._lock:
            entry = (source_handoff_id, source_version, obj.context.run_id, _fingerprint(obj))
            if len(self._entries) >= 100 and entry not in self._entries:
                raise HandoffError("fixture_declarations_full")
            self._entries.add(entry)

    def _check(self, source_id: str, source_version: int, obj: TriageHandoff) -> None:
        with self._lock:
            if (source_id, source_version, obj.context.run_id, _fingerprint(obj)) not in self._entries:
                raise HandoffError("fixture_declaration_missing")


@dataclass(frozen=True, slots=True)
class KnowledgeFixtureCheckpoint:
    receipt_id: str
    source_handoff_id: str
    source_version: int
    context: RunContext
    contribution_id: str
    contribution_digest: str
    recipient: str
    state: str
    state_version: int
    created_at: datetime
    expires_at: datetime
    fixture_basis: str
    fixture_policy_digest: str | None
    fixture_only: bool = True


class KnowledgeFixtureRegistry:
    """Single-process test harness: no runtime authorization or durable state.

    Source and receipt checks are independent point-in-time checks, not a
    cross-registry transaction. Use run_fixture for a test callback and discard
    its result if the source or receipt changes while it executes. The fixture
    declaration cannot establish facts, policy approval, or Shared acceptance.
    """
    def __init__(self, *, source_registry: HandoffRegistry, triage_capability: object,
                 sender_capability: object, knowledge_capability: object,
                 declarations: FixtureA2Declarations, timeout_seconds: int,
                 policy_catalog: SyntheticPolicyCatalog | None = None):
        caps = (triage_capability, sender_capability, knowledge_capability)
        if (not isinstance(source_registry, HandoffRegistry) or not isinstance(declarations, FixtureA2Declarations)
                or any(not _valid_capability(c) for c in caps)
                or any(caps[i] is caps[j] for i in range(3) for j in range(i))):
            raise ValueError("invalid_fixture_setup")
        if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 86400:
            raise ValueError("invalid_fixture_timeout")
        self._source, self._triage_cap = source_registry, triage_capability
        if policy_catalog is not None and not isinstance(policy_catalog, SyntheticPolicyCatalog):
            raise ValueError("invalid_fixture_policy")
        self._sender, self._receiver, self._declarations = sender_capability, knowledge_capability, declarations
        self._policy_catalog = policy_catalog
        self._timeout = timedelta(seconds=timeout_seconds)
        self._lock = Lock()
        self._entries: dict[str, tuple[KnowledgeFixtureCheckpoint, TriageHandoff]] = {}

    @staticmethod
    def _time(now: datetime | None) -> datetime:
        value = now if now is not None else datetime.now(UTC)
        if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value

    def _source_check(self, source_id: str, source_version: int, context: RunContext,
                      obj: TriageHandoff, now: datetime) -> None:
        parts = extract_request_parts(self._source, handoff_id=source_id, expected_version=source_version,
            receiver_capability=self._triage_cap, context=context, now=now)
        if (parts.context != obj.context or parts.status != "segmented_needs_classification"
                or len(parts.items) != 1 or parts.items[0].reported_text != obj.case_summary):
            raise HandoffError("fixture_source_mismatch_or_ambiguous")
        self._declarations._check(source_id, source_version, obj)
        if obj.claims:
            if self._policy_catalog is None:
                raise HandoffError("fixture_policy_not_configured")
            proposal = propose_from_synthetic_policy(self._source, handoff_id=source_id,
                expected_version=source_version, receiver_capability=self._triage_cap,
                context=context, item_index=1, catalog=self._policy_catalog, now=now)
            claim = obj.claims[0]
            expected_statement = f"Synthetic fixture inference: category={obj.category}; urgency={obj.urgency}"
            if (proposal.status != "synthetic_fixture_inference" or proposal.reason != "exact_fixture_rule"
                    or proposal.proposed_category != obj.category or proposal.proposed_urgency != obj.urgency
                    or proposal.proposed_destination != "knowledge_review" or proposal.policy_source is None
                    or proposal.fixture_digest is None or proposal.reported_source != parts.items[0].source
                    or (proposal.start_codepoint, proposal.end_codepoint) !=
                       (parts.items[0].start_codepoint, parts.items[0].end_codepoint)
                    or claim.sources != (proposal.reported_source, proposal.policy_source)
                    or claim.statement != expected_statement
                    or claim.basis != f"synthetic fixture policy sha256:{proposal.fixture_digest}"):
                raise HandoffError("fixture_policy_claim_mismatch")

    def prepare(self, contribution: TriageHandoff, *, source_handoff_id: str,
                source_version: int, capability: object, now: datetime | None = None) -> KnowledgeFixtureCheckpoint:
        if capability is not self._sender:
            raise HandoffError("unauthorized_fixture_sender")
        clock_override = now
        now = self._time(clock_override)
        obj = _candidate(contribution)
        self._source_check(source_handoff_id, source_version, obj.context, obj, now)
        checkpoint = KnowledgeFixtureCheckpoint(receipt_id=f"KHF-{uuid4()}", source_handoff_id=source_handoff_id,
            source_version=source_version, context=obj.context, contribution_id=obj.contribution_id,
            contribution_digest=_fingerprint(obj), recipient="knowledge_fixture", state="awaiting_ack",
            state_version=1, created_at=now, expires_at=now+self._timeout,
            fixture_basis="policy_inference" if obj.claims else "standalone_declaration",
            fixture_policy_digest=obj.claims[0].basis.removeprefix("synthetic fixture policy sha256:") if obj.claims else None)
        with self._lock:
            if len(self._entries) >= 1000:
                raise HandoffError("fixture_registry_full")
            self._entries[checkpoint.receipt_id] = (checkpoint, obj)
        # No lock spans separate registries; reject if the source changed meanwhile.
        try:
            checked_at = self._time(clock_override)
            self._source_check(source_handoff_id, source_version, obj.context, obj, checked_at)
            checked_at = self._time(clock_override)
            self._source.validate_active(source_handoff_id, expected_version=source_version,
                capability=self._triage_cap, context=obj.context, now=checked_at)
            if checked_at >= checkpoint.expires_at:
                raise HandoffError("fixture_receipt_expired")
        except Exception:
            with self._lock:
                if self._entries.get(checkpoint.receipt_id) == (checkpoint, obj):
                    self._entries.pop(checkpoint.receipt_id, None)
            raise
        return checkpoint

    def _read(self, receipt_id: str, *, expected_version: int, capability: object,
              context: RunContext, state: str, now: datetime,
              clock_override: datetime | None) -> tuple[KnowledgeFixtureCheckpoint, TriageHandoff]:
        if capability is not self._receiver:
            raise HandoffError("unauthorized_fixture_receiver")
        if type(expected_version) is not int or expected_version < 1:
            raise HandoffError("invalid_fixture_receipt_version")
        with self._lock:
            try:
                receipt, obj = self._entries[receipt_id]
            except KeyError:
                raise HandoffError("fixture_receipt_not_found") from None
        if receipt.state_version != expected_version:
            raise HandoffError("stale_fixture_receipt")
        if receipt.state != state:
            raise HandoffError("fixture_receipt_wrong_state")
        if not isinstance(context, RunContext) or type(context.case_version) is not int or receipt.context != context:
            raise HandoffError("fixture_context_mismatch")
        if now >= receipt.expires_at:
            raise HandoffError("fixture_receipt_expired")
        obj = _candidate(obj)
        expected_basis = "policy_inference" if obj.claims else "standalone_declaration"
        expected_digest = obj.claims[0].basis.removeprefix("synthetic fixture policy sha256:") if obj.claims else None
        if (obj.contribution_id != receipt.contribution_id or _fingerprint(obj) != receipt.contribution_digest
                or receipt.fixture_basis != expected_basis or receipt.fixture_policy_digest != expected_digest):
            raise HandoffError("fixture_contribution_changed")
        self._source_check(receipt.source_handoff_id, receipt.source_version, context, obj, now)
        checked_at = self._time(clock_override)
        self._source_check(receipt.source_handoff_id, receipt.source_version, context, obj, checked_at)
        checked_at = self._time(clock_override)
        self._source.validate_active(receipt.source_handoff_id, expected_version=receipt.source_version,
            capability=self._triage_cap, context=context, now=checked_at)
        if checked_at >= receipt.expires_at:
            raise HandoffError("fixture_receipt_expired")
        with self._lock:
            if self._entries.get(receipt_id) != (receipt, obj):
                raise HandoffError("stale_fixture_receipt")
        return receipt, obj

    def acknowledge(self, receipt_id: str, *, expected_version: int, capability: object,
                    context: RunContext, now: datetime | None = None) -> KnowledgeFixtureCheckpoint:
        clock_override = now
        now = self._time(clock_override)
        receipt, obj = self._read(receipt_id, expected_version=expected_version,
            capability=capability, context=context, state="awaiting_ack", now=now, clock_override=clock_override)
        with self._lock:
            if self._entries[receipt_id][0] != receipt:
                raise HandoffError("stale_fixture_receipt")
            accepted = replace(receipt, state="accepted", state_version=receipt.state_version+1)
            self._entries[receipt_id] = (accepted, obj)
        try:
            checked_at = self._time(clock_override)
            self._source_check(receipt.source_handoff_id, receipt.source_version, context, obj, checked_at)
            checked_at = self._time(clock_override)
            self._source.validate_active(receipt.source_handoff_id, expected_version=receipt.source_version,
                capability=self._triage_cap, context=context, now=checked_at)
            if checked_at >= accepted.expires_at:
                raise HandoffError("fixture_receipt_expired")
        except Exception:
            with self._lock:
                if self._entries.get(receipt_id) == (accepted, obj):
                    self._entries[receipt_id] = (replace(accepted, state="blocked", state_version=accepted.state_version+1), obj)
            raise
        return accepted

    def consume(self, receipt_id: str, *, expected_version: int, capability: object,
                context: RunContext, now: datetime | None = None) -> tuple[TriageHandoff, frozenset[str]]:
        """Return fixture input and internally derived ack; not a durable grant."""
        clock_override = now
        now = self._time(clock_override)
        _, obj = self._read(receipt_id, expected_version=expected_version,
            capability=capability, context=context, state="accepted", now=now, clock_override=clock_override)
        return obj, frozenset({obj.contribution_id})

    def run_fixture(self, receipt_id: str, *, expected_version: int, capability: object,
                    context: RunContext, fixture_call, now: datetime | None = None):
        """Call trusted local test code; discard result if later validation fails.

        Callbacks are test-only and have no authorized external effects. A fixed
        `now` is trusted test-clock injection, not production time validation.
        """
        obj, acknowledged = self.consume(receipt_id, expected_version=expected_version,
            capability=capability, context=context, now=now)
        result = fixture_call(obj, acknowledged)
        checked, ack2 = self.consume(receipt_id, expected_version=expected_version,
            capability=capability, context=context, now=now)
        if _fingerprint(checked) != _fingerprint(obj) or ack2 != acknowledged:
            raise HandoffError("fixture_contribution_changed")
        return result

    def cancel(self, receipt_id: str, *, expected_version: int, capability: object) -> None:
        if capability is not self._sender:
            raise HandoffError("unauthorized_fixture_sender")
        with self._lock:
            try:
                receipt, obj = self._entries[receipt_id]
            except KeyError:
                raise HandoffError("fixture_receipt_not_found") from None
            if type(expected_version) is not int or receipt.state_version != expected_version:
                raise HandoffError("stale_fixture_receipt")
            if receipt.state not in ("awaiting_ack", "accepted"):
                raise HandoffError("fixture_receipt_wrong_state")
            self._entries[receipt_id] = (replace(receipt, state="cancelled", state_version=receipt.state_version+1), obj)
