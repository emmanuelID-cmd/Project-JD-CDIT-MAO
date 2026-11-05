"""Synthetic, request-local A0/A1 intake; no production authentication or I/O."""
from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
import hashlib
import secrets
from threading import Lock
from time import monotonic
from typing import Literal
from uuid import uuid4

from pydantic import Field, SecretStr, ValidationError, field_validator, model_validator

from cdit_support_mao.agents.coordinator.case_versions import FixtureCaseVersions, FixturePolicyVersions
from cdit_support_mao.agents.coordinator.guards import scan_for_injection, scan_for_sensitive_data
from cdit_support_mao.contracts.common import CONTRACT_VERSION, RunContext, StrictModel


class IntakeStatus(StrEnum):
    READY_FOR_TRIAGE = "ready_for_triage"
    REJECTED_INPUT = "rejected_input"
    BLOCKED_CHECKPOINT = "blocked_checkpoint"
    FAILED_DEPENDENCY_MANUAL_FALLBACK = "failed_dependency_manual_fallback"


class FixtureSession(StrictModel):
    """Synthetic session supplied by a trusted local fixture adapter, never case text."""
    actor_id: str = Field(pattern=r"^SYN-ACTOR-[A-Z0-9-]{1,48}$")
    role: Literal["user", "staff", "admin"]
    active: bool = Field(strict=True)
    allowed_case_ids: tuple[str, ...] = Field(min_length=1, max_length=100)

    @field_validator("allowed_case_ids")
    @classmethod
    def synthetic_scopes_only(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        import re
        if any(re.fullmatch(r"SYN-[A-Z0-9][A-Z0-9-]{0,58}", value) is None for value in values):
            raise ValueError("case scope must contain synthetic case IDs")
        return values


class FixtureSessionAuthority:
    """Process-local synthetic sessions; trusted bootstrap code provisions roles.

    This is not production authentication and exposes no HTTP endpoint. Tokens
    are opaque, never stored in plaintext, and are not accepted as case data.
    """
    def __init__(self, *, provisioning_capability: object, ttl_seconds: int, clock=monotonic):
        if provisioning_capability is None or isinstance(provisioning_capability, (str, bytes, int, bool)):
            raise ValueError("provisioning capability must be a private runtime object")
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, int) or not 1 <= ttl_seconds <= 86400:
            raise ValueError("fixture session lifetime must be between 1 and 86400 seconds")
        self._provisioner = provisioning_capability
        self._ttl = ttl_seconds
        self._clock = clock
        self._sessions: dict[str, tuple[FixtureSession, float]] = {}
        self._lock = Lock()

    def issue(self, session: FixtureSession, *, capability: object) -> str:
        if capability is not self._provisioner or not isinstance(session, FixtureSession):
            raise ValueError("unauthorized fixture provisioning")
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode("ascii")).hexdigest()
        with self._lock:
            self._sessions[digest] = (session, self._clock() + self._ttl)
        return token

    def revoke(self, token: str, *, capability: object) -> None:
        if capability is not self._provisioner:
            raise ValueError("unauthorized fixture provisioning")
        digest = self._digest(token)
        if digest is not None:
            with self._lock:
                self._sessions.pop(digest, None)

    def close(self, *, capability: object) -> None:
        """Revoke all process-local fixture sessions during runtime cleanup."""
        if capability is not self._provisioner:
            raise ValueError("unauthorized fixture provisioning")
        with self._lock:
            self._sessions.clear()

    def resolve(self, token: object) -> FixtureSession | None:
        digest = self._digest(token)
        if digest is None:
            return None
        with self._lock:
            return self._active_session(digest)

    def with_session(self, token: object, operation):
        """Serialize fixture revocation with one short, trusted state transition."""
        digest = self._digest(token)
        if digest is None:
            return operation(None)
        with self._lock:
            return operation(self._active_session(digest))

    def with_session_ref(self, session_ref: str, operation):
        """Trusted runtime lookup; the opaque session reference is never case data."""
        with self._lock:
            return operation(self._active_session(session_ref))

    def _active_session(self, digest: str) -> FixtureSession | None:
        item = self._sessions.get(digest)
        if item is None:
            return None
        session, deadline = item
        if self._clock() >= deadline:
            self._sessions.pop(digest, None)
            return None
        return session

    @staticmethod
    def _digest(token: object) -> str | None:
        if not isinstance(token, str) or not 32 <= len(token) <= 128 or not token.isascii():
            return None
        return hashlib.sha256(token.encode("ascii")).hexdigest()


class IntakeRequest(StrictModel):
    case_id: str = Field(pattern=r"^SYN-[A-Z0-9][A-Z0-9-]{0,58}$")
    case_version: int = Field(strict=True, ge=1, le=2147483647)
    policy_version: str = Field(pattern=r"^SYN-[A-Z0-9][A-Z0-9.-]{0,55}$")
    message: str = Field(min_length=1, max_length=2000)
    data_classification: Literal["synthetic"]

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be blank")
        return value


class IntakeEvent(StrictModel):
    trace_id: str
    run_id: str | None
    sequence: int
    checkpoint: Literal["A0", "A1"]
    status: Literal["passed", "stopped"]
    timestamp: datetime
    reason_code: str | None = None


class IntakeResult(StrictModel):
    trace_id: str = Field(default_factory=lambda: f"TRACE-{uuid4()}", pattern=r"^TRACE-[0-9a-f-]{36}$")
    status: IntakeStatus
    checkpoint: Literal["A0", "A1"]
    reason_code: str | None = None
    risk_signals: tuple[str, ...] = ()
    context: RunContext | None = None
    policy_generation: int | None = Field(default=None, strict=True, ge=1)
    session_ref: SecretStr | None = Field(default=None, repr=False)
    contract_version: Literal["0.1.0-proposed"] = CONTRACT_VERSION
    untrusted_message: str | None = Field(default=None, min_length=1, max_length=2000, repr=False)
    created_at: datetime
    next_action: Literal["triage", "human_review", "stop"]
    events: tuple[IntakeEvent, ...]

    @field_validator("session_ref")
    @classmethod
    def valid_session_reference(cls, value: SecretStr | None) -> SecretStr | None:
        import re
        if value is not None and re.fullmatch(r"[0-9a-f]{64}", value.get_secret_value()) is None:
            raise ValueError("invalid session reference")
        return value

    @model_validator(mode="after")
    def consistent_result(self) -> IntakeResult:
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        if not self.events or any(event.trace_id != self.trace_id for event in self.events):
            raise ValueError("checkpoint events must match trace")
        if tuple(event.sequence for event in self.events) != tuple(range(1, len(self.events) + 1)):
            raise ValueError("checkpoint event sequence is invalid")
        if any(event.timestamp.tzinfo is None or event.timestamp.utcoffset() is None for event in self.events):
            raise ValueError("checkpoint timestamps must be timezone-aware")
        if any(left.timestamp > right.timestamp for left, right in zip(self.events, self.events[1:])):
            raise ValueError("checkpoint timestamps must be ordered")
        expected = (("A0", "stopped"),) if self.checkpoint == "A0" else (
            ("A0", "passed"), ("A1", "passed" if self.status is IntakeStatus.READY_FOR_TRIAGE else "stopped"))
        if tuple((event.checkpoint, event.status) for event in self.events) != expected:
            raise ValueError("checkpoint events disagree with result")
        if self.events[-1].timestamp != self.created_at or self.events[-1].reason_code != self.reason_code:
            raise ValueError("terminal checkpoint must match result")
        if any(event.status == "passed" and event.reason_code is not None for event in self.events):
            raise ValueError("passed checkpoints cannot carry stop reasons")
        if len(self.events) == 2 and (self.events[0].run_id is None or self.events[0].run_id != self.events[1].run_id):
            raise ValueError("checkpoint events must share a run")
        if self.status is IntakeStatus.READY_FOR_TRIAGE:
            if self.risk_signals or self.reason_code is not None:
                raise ValueError("flagged intake cannot be triage-ready")
            if self.context is None or self.policy_generation is None or self.session_ref is None or self.untrusted_message is None or self.next_action != "triage" or self.checkpoint != "A1":
                raise ValueError("triage-ready intake requires context and minimized message")
            if any(event.run_id != self.context.run_id for event in self.events):
                raise ValueError("checkpoint events must match run")
        elif self.context is not None or self.policy_generation is not None or self.session_ref is not None or self.untrusted_message is not None or self.next_action == "triage" or not self.reason_code:
            raise ValueError("stopped intake must omit message and context and carry a reason")
        return self


class Coordinator:
    """Validate a synthetic staff request; never dispatch agents or write tickets.

    Security boundary: a trusted runtime provisions synthetic fixture sessions.
    This is not production authentication and is not exposed by the web API.
    A role asserted in case content cannot grant permissions.
    """

    def __init__(self, sessions: FixtureSessionAuthority, *, case_versions: FixtureCaseVersions,
                 policy_versions: FixturePolicyVersions):
        if not isinstance(case_versions, FixtureCaseVersions):
            raise TypeError("trusted synthetic case versions are required")
        if not isinstance(policy_versions, FixturePolicyVersions):
            raise TypeError("trusted synthetic policy versions are required")
        if not isinstance(sessions, FixtureSessionAuthority):
            raise TypeError("a trusted fixture session authority is required")
        self._case_versions = case_versions
        self._policy_versions = policy_versions
        self._sessions = sessions

    def prepare(self, raw: object, *, session_token: object) -> IntakeResult:
        trace_id = f"TRACE-{uuid4()}"
        session_ref = self._sessions._digest(session_token)
        try:
            return self._sessions.with_session(
                session_token, lambda session: self._prepare_for_session(raw, session, session_ref, trace_id, self._policy_versions, self._case_versions)
            )
        except Exception as exc:
            timestamp = datetime.now(UTC)
            reason = "fixture_dependency_unavailable" if isinstance(exc, (RuntimeError, OSError, TimeoutError)) else "coordinator_internal_error"
            event = IntakeEvent(trace_id=trace_id,run_id=None,sequence=1,checkpoint="A0",
                                status="stopped",timestamp=timestamp,reason_code=reason)
            return IntakeResult(trace_id=trace_id,status=IntakeStatus.FAILED_DEPENDENCY_MANUAL_FALLBACK,
                checkpoint="A0",reason_code=reason,created_at=timestamp,
                next_action="human_review",events=(event,))

    @staticmethod
    def _prepare_for_session(raw: object, session: FixtureSession | None,
                             session_ref: str | None, trace_id: str, policy_versions: FixturePolicyVersions,
                             case_versions: FixtureCaseVersions) -> IntakeResult:
        def reject(reason: str, *, human: bool = False, risks: tuple[str, ...] = ()) -> IntakeResult:
            timestamp = datetime.now(UTC)
            event = IntakeEvent(trace_id=trace_id,run_id=None,sequence=1,checkpoint="A0",
                                status="stopped",timestamp=timestamp,reason_code=reason)
            return IntakeResult(trace_id=trace_id,status=IntakeStatus.REJECTED_INPUT,checkpoint="A0",
                reason_code=reason,risk_signals=risks,created_at=timestamp,
                next_action="human_review" if human else "stop",events=(event,))
        if session is None or not session.active or session.role not in ("staff", "admin"):
            return reject("unauthorized_session")
        try:
            request = IntakeRequest.model_validate(raw.model_dump() if isinstance(raw, IntakeRequest) else raw)
        except ValidationError:
            return reject("invalid_synthetic_request")
        policy_allowed, policy_generation = policy_versions.with_snapshot(
            lambda active, generation: (request.policy_version in active, generation))
        if not policy_allowed:
            return reject("unknown_policy_version")
        if request.case_id not in session.allowed_case_ids:
            return reject("case_scope_denied")
        if case_versions.with_version(request.case_id, lambda current: current != request.case_version):
            return reject("stale_or_unknown_case_version")
        privacy = scan_for_sensitive_data(request.message)
        if privacy:
            return reject("sensitive_content",human=True,risks=privacy)
        context = RunContext(run_id=f"RUN-{uuid4()}",case_id=request.case_id,
                             case_version=request.case_version,policy_version=request.policy_version)
        a0 = IntakeEvent(trace_id=trace_id,run_id=context.run_id,sequence=1,checkpoint="A0",
                         status="passed",timestamp=datetime.now(UTC))
        try:
            signals = scan_for_injection(request.message)
        except Exception:
            finished = datetime.now(UTC)
            a1 = IntakeEvent(trace_id=trace_id,run_id=context.run_id,sequence=2,checkpoint="A1",
                             status="stopped",timestamp=finished,reason_code="input_guard_unavailable")
            return IntakeResult(trace_id=trace_id,status=IntakeStatus.FAILED_DEPENDENCY_MANUAL_FALLBACK,
                checkpoint="A1",reason_code="input_guard_unavailable",created_at=finished,
                next_action="human_review",events=(a0,a1))
        finished = datetime.now(UTC)
        if signals:
            a1 = IntakeEvent(trace_id=trace_id,run_id=context.run_id,sequence=2,checkpoint="A1",
                             status="stopped",timestamp=finished,reason_code="instruction_like_content")
            return IntakeResult(trace_id=trace_id,status=IntakeStatus.BLOCKED_CHECKPOINT,checkpoint="A1",
                reason_code="instruction_like_content",risk_signals=signals,created_at=finished,
                next_action="human_review",events=(a0,a1))
        a1 = IntakeEvent(trace_id=trace_id,run_id=context.run_id,sequence=2,checkpoint="A1",
                         status="passed",timestamp=finished)
        return IntakeResult(trace_id=trace_id,status=IntakeStatus.READY_FOR_TRIAGE,checkpoint="A1",
            context=context,policy_generation=policy_generation,session_ref=session_ref,untrusted_message=request.message,
            created_at=finished,next_action="triage",events=(a0,a1))
