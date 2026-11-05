"""Process-local, version-checked coordinator handoffs for synthetic fixtures.

This registry is not a durable blackboard and does not authenticate callers.
Only trusted runtime code may hold the receiver capability. A restart loses the
registry; callers must route interrupted work to human/manual recovery.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum
import hashlib
from threading import Lock
from uuid import uuid4

from pydantic import ValidationError

from cdit_support_mao.agents.coordinator.case_versions import FixtureCaseVersions, FixturePolicyVersions
from cdit_support_mao.agents.coordinator.intake import FixtureSessionAuthority, IntakeResult, IntakeStatus
from cdit_support_mao.agents.coordinator.guards import scan_for_injection, scan_for_sensitive_data
from cdit_support_mao.contracts.common import CONTRACT_VERSION, RunContext


class HandoffState(StrEnum):
    AWAITING_ACK = "awaiting_ack"
    ACCEPTED = "accepted"
    AWAITING_HUMAN = "awaiting_human"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    BLOCKED = "blocked"


class HandoffError(ValueError):
    """A handoff could not safely advance; messages contain no case content."""


@dataclass(frozen=True, slots=True)
class HandoffCheckpoint:
    handoff_id: str
    trace_id: str
    context: RunContext
    contract_version: str
    sender: str
    recipient: str
    current_owner: str
    requirement_ids: tuple[str, ...]
    completed_work: tuple[str, ...]
    pending_work: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    message_claim_status: str
    unknowns: tuple[str, ...]
    side_effect_status: str
    prd_version: str
    policy_generation: int
    prompt_version: str
    model_version: str
    tool_version: str
    state: HandoffState
    state_version: int
    created_at: datetime
    expires_at: datetime
    next_action: str


@dataclass(frozen=True, slots=True)
class HandoffEvent:
    sequence: int
    trace_id: str
    run_id: str
    handoff_id: str
    event: str
    owner: str
    status: str
    agent_id: str
    policy_version: str
    policy_generation: int
    state_version: int
    timestamp: datetime
    contract_version: str



class HandoffRegistry:
    """One process's in-memory handoff ledger; no tool dispatch or writes.

    ``receiver_capability`` is a private object shared by trusted runtime code,
    not something accepted from a case, model, tool result, or web request.
    The timeout is explicit because no project retry/timeout policy is approved.
    """

    def __init__(self, *, sender_capability: object, receiver_capability: object, timeout_seconds: int,
                 actor_sessions: FixtureSessionAuthority, case_versions: FixtureCaseVersions, policy_versions: FixturePolicyVersions,
                 reviewer_sessions: FixtureSessionAuthority | None = None):
        if (sender_capability is None or receiver_capability is None
                or isinstance(sender_capability, (str, bytes, int, bool))
                or isinstance(receiver_capability, (str, bytes, int, bool))
                or sender_capability is receiver_capability):
            raise ValueError("sender and receiver capabilities must be distinct private runtime objects")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, int) or not 1 <= timeout_seconds <= 86400:
            raise ValueError("timeout_seconds must be between 1 and 86400")
        self._sender_capability = sender_capability
        self._receiver_capability = receiver_capability
        if not isinstance(actor_sessions, FixtureSessionAuthority):
            raise ValueError("actor sessions must be a trusted fixture authority")
        if not isinstance(policy_versions, FixturePolicyVersions):
            raise ValueError("trusted synthetic policy versions are required")
        self._policy_versions = policy_versions
        self._actor_sessions = actor_sessions
        if not isinstance(case_versions, FixtureCaseVersions):
            raise ValueError("trusted synthetic case versions are required")
        self._case_versions = case_versions
        if reviewer_sessions is not None and not isinstance(reviewer_sessions, FixtureSessionAuthority):
            raise ValueError("reviewer sessions must be a trusted fixture authority")
        self._reviewer_sessions = reviewer_sessions
        self._timeout = timedelta(seconds=timeout_seconds)
        self._lock = Lock()
        self._entries: dict[str, HandoffCheckpoint] = {}
        self._runs: dict[str, str] = {}
        self._events: list[HandoffEvent] = []
        self._payloads: dict[str, str] = {}
        self._fingerprints: dict[str, str] = {}
        self._session_bindings: dict[str, tuple[FixtureSessionAuthority, str]] = {}
        self._closed = False

    def prepare(self, intake: IntakeResult, *, capability: object, session_token: object, now: datetime | None = None) -> HandoffCheckpoint:
        if capability is not self._sender_capability:
            raise HandoffError("unauthorized_sender")
        now = self._time(now)
        if not isinstance(intake, IntakeResult):
            raise HandoffError("invalid_intake_type")
        try:
            intake = IntakeResult.model_validate(intake.model_dump())
        except ValidationError as exc:
            raise HandoffError("invalid_intake_output") from None
        if (intake.status is not IntakeStatus.READY_FOR_TRIAGE or intake.context is None
                or intake.untrusted_message is None or intake.next_action != "triage"
                or intake.contract_version != CONTRACT_VERSION):
            raise HandoffError("intake_not_eligible")
        if scan_for_sensitive_data(intake.untrusted_message) or scan_for_injection(intake.untrusted_message):
            raise HandoffError("untrusted_packet_requires_review")
        fingerprint = hashlib.sha256(intake.untrusted_message.encode("utf-8")).hexdigest()
        session_ref = self._actor_sessions._digest(session_token)

        def authorized_prepare(session):
            if (session is None or not session.active or session.role not in ("staff", "admin")
                    or intake.context.case_id not in session.allowed_case_ids
                    or session_ref is None or intake.session_ref is None
                    or session_ref != intake.session_ref.get_secret_value()):
                raise HandoffError("session_revoked_or_scope_changed")
            def check_version(current):
                if current != intake.context.case_version:
                    raise HandoffError("stale_case_version")
                def check_policy(active, generation):
                    if intake.context.policy_version not in active or generation != intake.policy_generation:
                        raise HandoffError("stale_policy_version")
                    with self._lock:
                        if self._closed:
                            raise HandoffError("registry_closed_manual_recovery")
                        prior_id = self._runs.get(intake.context.run_id)
                        if prior_id is not None:
                            prior = self._entries[prior_id]
                            if (prior.context != intake.context or self._fingerprints[prior_id] != fingerprint
                                or self._session_bindings[prior_id] != (self._actor_sessions, session_ref)):
                                raise HandoffError("run_id_reused_with_changed_input")
                            return prior
                        item = HandoffCheckpoint(handoff_id=f"HOF-{uuid4()}", trace_id=intake.trace_id, context=intake.context,
                            contract_version=CONTRACT_VERSION, sender="coordinator", recipient="triage",
                            current_owner="coordinator", requirement_ids=("A0", "A1"),
                            completed_work=("synthetic_intake_validation",), pending_work=("triage",),
                            evidence_refs=(f"case:{intake.context.case_id}:v{intake.context.case_version}:message",),
                            message_claim_status="unknown", unknowns=("reported_case_content_not_independently_verified",),
                            side_effect_status="none", prd_version="PRD-v3", policy_generation=intake.policy_generation, prompt_version="not_configured",
                            model_version="not_configured", tool_version="no_external_tools",
                            state=HandoffState.AWAITING_ACK, state_version=1, created_at=now,
                            expires_at=now + self._timeout,
                            next_action="await_triage_acknowledgment")
                        self._entries[item.handoff_id] = item
                        self._session_bindings[item.handoff_id] = (self._actor_sessions, session_ref)
                        self._payloads[item.handoff_id] = intake.untrusted_message
                        self._fingerprints[item.handoff_id] = fingerprint
                        self._runs[item.context.run_id] = item.handoff_id
                        self._record(item, "handoff_prepared", now)
                        return item
                return self._policy_versions.with_snapshot(check_policy)
            return self._case_versions.with_version(intake.context.case_id, check_version)

        return self._actor_sessions.with_session(session_token, authorized_prepare)

    def acknowledge(self, handoff_id: str, *, expected_version: int, capability: object,
                    context: RunContext, now: datetime | None = None) -> HandoffCheckpoint:
        if capability is not self._receiver_capability:
            raise HandoffError("unauthorized_receiver")
        now = self._time(now)
        def transition(item):
            if type(expected_version) is not int or expected_version < 1:
                raise HandoffError("invalid_handoff_version")
            if item.state_version != expected_version:
                raise HandoffError("stale_handoff_version")
            if not isinstance(context, RunContext) or type(context.case_version) is not int:
                raise HandoffError("invalid_context")
            if item.context != context:
                raise HandoffError("context_mismatch")
            if item.state is not HandoffState.AWAITING_ACK:
                raise HandoffError("handoff_not_awaiting_ack")
            if now >= item.expires_at:
                return self._expire(item, now)
            item = replace(item, state=HandoffState.ACCEPTED, state_version=item.state_version + 1,
                           current_owner="triage", next_action="triage_may_read_untrusted_packet")
            self._entries[handoff_id] = item
            self._record(item, "handoff_accepted", now)
            return item
        return self._with_current_session(handoff_id, transition)

    def cancel(self, handoff_id: str, *, expected_version: int, capability: object,
               now: datetime | None = None) -> HandoffCheckpoint:
        if capability is not self._sender_capability:
            raise HandoffError("unauthorized_sender")
        now = self._time(now)
        with self._lock:
            item = self._get(handoff_id)
            if type(expected_version) is not int or expected_version < 1:
                raise HandoffError("invalid_handoff_version")
            if item.state_version != expected_version:
                raise HandoffError("stale_handoff_version")
            if item.state not in (HandoffState.AWAITING_ACK, HandoffState.ACCEPTED, HandoffState.AWAITING_HUMAN):
                raise HandoffError("handoff_not_cancellable")
            item = replace(item, state=HandoffState.CANCELLED, state_version=item.state_version + 1,
                           current_owner="coordinator", next_action="stop")
            self._entries[handoff_id] = item
            self._payloads.pop(handoff_id, None)
            self._record(item, "handoff_cancelled", now)
            return item

    def pause_for_human(self, handoff_id: str, *, expected_version: int, capability: object,
                        now: datetime | None = None) -> HandoffCheckpoint:
        if capability is not self._sender_capability:
            raise HandoffError("unauthorized_sender")
        now = self._time(now)
        with self._lock:
            item = self._get(handoff_id)
            if type(expected_version) is not int or expected_version < 1:
                raise HandoffError("invalid_handoff_version")
            if item.state_version != expected_version:
                raise HandoffError("stale_handoff_version")
            if item.state not in (HandoffState.AWAITING_ACK, HandoffState.ACCEPTED):
                raise HandoffError("handoff_not_pausable")
            if now >= item.expires_at:
                return self._expire(item, now)
            item = replace(item, state=HandoffState.AWAITING_HUMAN, state_version=item.state_version + 1,
                           current_owner="human_review", next_action="await_human_review")
            self._entries[handoff_id] = item
            self._record(item, "handoff_paused_for_review", now)
            return item

    def resume_after_fixture_review(self, handoff_id: str, *, expected_version: int,
                                    capability: object, reviewer_token: object,
                                    context: RunContext, now: datetime | None = None) -> HandoffCheckpoint:
        """Revalidate a synthetic reviewer and the same context before re-acknowledgment.

        This is a fixture review event, not proof of real human approval.
        """
        if capability is not self._sender_capability:
            raise HandoffError("unauthorized_sender")
        if not isinstance(context, RunContext) or type(context.case_version) is not int:
            raise HandoffError("invalid_context")
        now = self._time(now)
        if self._reviewer_sessions is None:
            raise HandoffError("unauthorized_reviewer")

        def transition(reviewer):
            if reviewer is None or not reviewer.active or reviewer.role not in ("staff", "admin"):
                raise HandoffError("unauthorized_reviewer")
            # Preliminary check without holding the ledger while waiting on the
            # case-version lock. Repeat under the lock before changing state.
            with self._lock:
                item = self._get(handoff_id)
                if type(expected_version) is not int or expected_version < 1:
                    raise HandoffError("invalid_handoff_version")
                if item.state_version != expected_version:
                    raise HandoffError("stale_handoff_version")
                if item.state is not HandoffState.AWAITING_HUMAN:
                    raise HandoffError("handoff_not_awaiting_human")
                if item.context != context:
                    raise HandoffError("context_mismatch")
                if context.case_id not in reviewer.allowed_case_ids:
                    raise HandoffError("unauthorized_reviewer")
                expected_policy_generation = item.policy_generation

            def check_version(current):
                def check_policy(active, generation):
                    if context.policy_version not in active or generation != expected_policy_generation:
                        self._block_stale_policy(handoff_id)
                        raise HandoffError("stale_policy_version")
                    with self._lock:
                        item = self._get(handoff_id)
                        if item.state_version != expected_version:
                            raise HandoffError("stale_handoff_version")
                        if item.state is not HandoffState.AWAITING_HUMAN or item.context != context:
                            raise HandoffError("handoff_changed")
                        if current != context.case_version:
                            item = replace(item,state=HandoffState.BLOCKED,state_version=item.state_version+1,
                                           current_owner="human_review",next_action="human_or_manual_recovery")
                            self._entries[handoff_id] = item
                            self._payloads.pop(handoff_id, None)
                            self._record(item,"stale_case_version",now)
                            raise HandoffError("stale_case_version")
                        if now >= item.expires_at:
                            return self._expire(item, now)
                        item = replace(item,state=HandoffState.AWAITING_ACK,state_version=item.state_version+1,
                                       current_owner="coordinator",next_action="await_triage_acknowledgment")
                        self._entries[handoff_id] = item
                        self._session_bindings[handoff_id] = (self._reviewer_sessions,self._reviewer_sessions._digest(reviewer_token))
                        self._record(item,"fixture_review_resume",now)
                        return item
                return self._policy_versions.with_snapshot(check_policy)
            return self._case_versions.with_version(context.case_id, check_version)

        # Lock order: reviewer session, case version, policy version, registry. No lock is held
        # across an actual human interaction or a model/tool call.
        return self._reviewer_sessions.with_session(reviewer_token, transition)

    def validate_active(self, handoff_id: str, *, expected_version: int, capability: object,
                        context: RunContext, now: datetime | None = None) -> HandoffCheckpoint:
        """Check active fixture permissions and ownership before packet use."""
        if capability is not self._receiver_capability:
            raise HandoffError("unauthorized_receiver")
        now = self._time(now)
        def transition(item):
            if type(expected_version) is not int or expected_version < 1:
                raise HandoffError("invalid_handoff_version")
            if item.state_version != expected_version:
                raise HandoffError("stale_handoff_version")
            if not isinstance(context, RunContext) or type(context.case_version) is not int:
                raise HandoffError("invalid_context")
            if item.context != context:
                raise HandoffError("context_mismatch")
            if item.state is not HandoffState.ACCEPTED:
                raise HandoffError("handoff_not_accepted")
            if now >= item.expires_at:
                self._expire(item, now)
                raise HandoffError("handoff_expired_manual_recovery")
            return item
        return self._with_current_session(handoff_id, transition)

    def read_untrusted_message(self, handoff_id: str, *, expected_version: int,
                               capability: object, context: RunContext,
                               now: datetime | None = None) -> str:
        """Release minimized text to the acknowledged receiver while scope remains valid."""
        if capability is not self._receiver_capability:
            raise HandoffError("unauthorized_receiver")
        now = self._time(now)
        def transition(item):
            if type(expected_version) is not int or expected_version < 1:
                raise HandoffError("invalid_handoff_version")
            if item.state_version != expected_version:
                raise HandoffError("stale_handoff_version")
            if not isinstance(context, RunContext) or type(context.case_version) is not int:
                raise HandoffError("invalid_context")
            if item.context != context:
                raise HandoffError("context_mismatch")
            if item.state is not HandoffState.ACCEPTED:
                raise HandoffError("handoff_not_accepted")
            if now >= item.expires_at:
                self._expire(item, now)
                raise HandoffError("handoff_expired_manual_recovery")
            return self._payloads[handoff_id]
        return self._with_current_session(handoff_id, transition)

    def _with_current_session(self, handoff_id: str, operation):
        # Never hold the registry lock while waiting for a session lock.
        with self._lock:
            self._get(handoff_id)
            binding = self._session_bindings[handoff_id]
            item = self._get(handoff_id)
            case_id_version = (item.context.case_id, item.context.case_version)
            policy_version = item.context.policy_version
            policy_generation = item.policy_generation
        authority, session_ref = binding
        def checked(session):
            def check_version(current):
                if current != case_id_version[1]:
                    self._block_stale_case(handoff_id)
                    raise HandoffError("stale_case_version")
                def check_policy(active, generation):
                    if policy_version not in active or generation != policy_generation:
                        self._block_stale_policy(handoff_id)
                        raise HandoffError("stale_policy_version")
                    with self._lock:
                        item = self._get(handoff_id)
                        if self._session_bindings[handoff_id] != binding:
                            raise HandoffError("session_binding_changed")
                        if (session is None or not session.active or session.role not in ("staff", "admin")
                                or item.context.case_id not in session.allowed_case_ids):
                            if item.state not in (HandoffState.CANCELLED, HandoffState.EXPIRED, HandoffState.BLOCKED):
                                item = replace(item, state=HandoffState.BLOCKED, state_version=item.state_version + 1,
                                               current_owner="human_review", next_action="human_or_manual_recovery")
                                self._entries[handoff_id] = item
                                self._payloads.pop(handoff_id, None)
                                self._record(item, "session_revoked_or_scope_changed", datetime.now(UTC))
                            raise HandoffError("session_revoked_or_scope_changed")
                        return operation(item)
                return self._policy_versions.with_snapshot(check_policy)
            return self._case_versions.with_version(case_id_version[0], check_version)

        return authority.with_session_ref(session_ref, checked)

    def expire(self, handoff_id: str, *, expected_version: int, capability: object,
               now: datetime | None = None) -> HandoffCheckpoint:
        """Let the trusted coordinator stop an unresponsive or overdue receiver."""
        if capability is not self._sender_capability:
            raise HandoffError("unauthorized_sender")
        now = self._time(now)
        with self._lock:
            item = self._get(handoff_id)
            if type(expected_version) is not int or expected_version < 1:
                raise HandoffError("invalid_handoff_version")
            if item.state_version != expected_version:
                raise HandoffError("stale_handoff_version")
            if item.state not in (HandoffState.AWAITING_ACK, HandoffState.ACCEPTED, HandoffState.AWAITING_HUMAN):
                raise HandoffError("handoff_not_expirable")
            if now < item.expires_at:
                raise HandoffError("handoff_not_expired")
            return self._expire(item, now)

    def _expire(self, item: HandoffCheckpoint, now: datetime) -> HandoffCheckpoint:
        item = replace(item, state=HandoffState.EXPIRED, state_version=item.state_version + 1,
                       current_owner="human_review", next_action="human_or_manual_recovery")
        self._entries[item.handoff_id] = item
        self._payloads.pop(item.handoff_id, None)
        self._record(item, "handoff_expired", now)
        return item

    def _block_stale_case(self, handoff_id: str) -> None:
        with self._lock:
            item = self._get(handoff_id)
            if item.state not in (HandoffState.CANCELLED, HandoffState.EXPIRED, HandoffState.BLOCKED):
                item = replace(item, state=HandoffState.BLOCKED, state_version=item.state_version + 1,
                               current_owner="human_review", next_action="human_or_manual_recovery")
                self._entries[handoff_id] = item
                self._payloads.pop(handoff_id, None)
                self._record(item, "stale_case_version", datetime.now(UTC))

    def close(self, *, capability: object, now: datetime | None = None) -> None:
        """Record cancellation, remove messages and prevent late work after shutdown."""
        if capability is not self._sender_capability:
            raise HandoffError("unauthorized_sender")
        now = self._time(now)
        with self._lock:
            for item in self._entries.values():
                if item.state not in (HandoffState.CANCELLED, HandoffState.EXPIRED, HandoffState.BLOCKED):
                    stopped = replace(item,state=HandoffState.CANCELLED,state_version=item.state_version+1,
                                      current_owner="coordinator",next_action="stop")
                    self._record(stopped,"registry_shutdown",now)
            self._closed = True
            self._payloads.clear()
            self._entries.clear()
            self._session_bindings.clear()
            self._fingerprints.clear()
            self._runs.clear()

    def _block_stale_policy(self, handoff_id: str) -> None:
        with self._lock:
            item = self._get(handoff_id)
            if item.state not in (HandoffState.CANCELLED, HandoffState.EXPIRED, HandoffState.BLOCKED):
                item = replace(item, state=HandoffState.BLOCKED, state_version=item.state_version + 1,
                               current_owner="human_review", next_action="human_or_manual_recovery")
                self._entries[handoff_id] = item
                self._payloads.pop(handoff_id, None)
                self._record(item, "stale_policy_version", datetime.now(UTC))

    def events(self) -> tuple[HandoffEvent, ...]:
        """Return ordered metadata-only events from this process."""
        with self._lock:
            return tuple(self._events)

    def _record(self, item: HandoffCheckpoint, event: str, timestamp: datetime) -> None:
        self._events.append(HandoffEvent(sequence=len(self._events) + 1, trace_id=item.trace_id,
            run_id=item.context.run_id, handoff_id=item.handoff_id, event=event, owner=item.current_owner, status=item.state.value,
            agent_id="coordinator", policy_version=item.context.policy_version, policy_generation=item.policy_generation,
            state_version=item.state_version, timestamp=timestamp,
            contract_version=item.contract_version))

    def _get(self, handoff_id: str) -> HandoffCheckpoint:
        if self._closed:
            raise HandoffError("registry_closed_manual_recovery")
        try:
            return self._entries[handoff_id]
        except KeyError as exc:
            raise HandoffError("handoff_not_found_manual_recovery") from None

    @staticmethod
    def _time(value: datetime | None) -> datetime:
        value = value or datetime.now(UTC)
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value
