"""Synthetic, in-progress attention benchmark; no ticket or notification action.

Timelines and bands are supplied synthetic fixture observations, not evidence of
real-world facts, operational SLA policy or authorization. Safety clock handling
is historical elapsed context, not a deadline. Results are snapshots and need fresh input at use.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
import re
from typing import Literal

from pydantic import Field, ValidationError, field_validator

from cdit_support_mao.contracts.common import StrictModel


class BenchmarkInputError(ValueError):
    """Fixed, content-free error; invalid fixtures cannot advance."""


def _timestamp_input(value: object) -> object:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})", value
    ):
        return value
    raise ValueError("timestamp_type_invalid")


class BenchmarkEvent(StrictModel):
    kind: Literal["in_progress", "waiting_on_customer", "customer_response", "under_investigation"]
    at: datetime

    @field_validator("at", mode="before")
    @classmethod
    def _timestamp_type(cls, value: object) -> object:
        return _timestamp_input(value)

    @field_validator("at")
    @classmethod
    def _aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timezone_required")
        return value


class BenchmarkInput(StrictModel):
    case_id: str = Field(pattern=r"^SYN-[A-Z0-9][A-Z0-9-]{0,58}$")
    data_classification: Literal["synthetic"]
    priority: Literal["P1", "P2", "P3", "unknown"]
    safety_concern_ongoing: bool | None
    safety_flag_previously_recorded: bool
    safety_started_at: datetime | None = None
    events: tuple[BenchmarkEvent, ...] = Field(min_length=1, max_length=100)
    as_of: datetime

    @field_validator("safety_concern_ongoing", "safety_flag_previously_recorded", mode="before")
    @classmethod
    def _strict_safety(cls, value: object) -> bool | None:
        if value is not None and type(value) is not bool:
            raise ValueError("strict_safety_required")
        return value

    @field_validator("safety_started_at", mode="before")
    @classmethod
    def _safety_timestamp_type(cls, value: object) -> object:
        return None if value is None else _timestamp_input(value)

    @field_validator("safety_started_at")
    @classmethod
    def _safety_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("timezone_required")
        return value

    @field_validator("as_of", mode="before")
    @classmethod
    def _timestamp_type(cls, value: object) -> object:
        return _timestamp_input(value)

    @field_validator("as_of")
    @classmethod
    def _aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timezone_required")
        return value


class BenchmarkFlag(StrictModel):
    kind: Literal["p1_immediate", "benchmark_followup", "safety_attention", "unknown_urgency"]
    reason: str = Field(min_length=1, max_length=200)
    baseline_event_index: int | None = Field(default=None, strict=True, ge=0)
    baseline_at: datetime | None
    observed_at: datetime
    evidence_field: Literal["case_timeline", "safety_started_at", "safety_start_unknown"] = "case_timeline"
    evidence_status: Literal["synthetic_fixture_report_not_independently_verified"] = "synthetic_fixture_report_not_independently_verified"


class BenchmarkResult(StrictModel):
    case_id: str
    priority: Literal["P1", "P2", "P3", "unknown"]
    current_state: Literal["in_progress", "waiting_on_customer", "under_investigation"]
    status: Literal["assessed", "needs_human"]
    reason_code: Literal["benchmark_assessed", "unknown_urgency", "safety_human_review", "safety_start_unknown", "safety_status_unknown", "human_investigation_in_progress"]
    baseline_event_index: int = Field(strict=True, ge=0)
    baseline_at: datetime
    observed_at: datetime
    elapsed_in_progress_seconds: int | None = Field(default=None, ge=0)
    flags: tuple[BenchmarkFlag, ...] = ()
    safety_flag_preserved: bool
    safety_started_at: datetime | None
    safety_elapsed_context_seconds: int | None = Field(default=None, ge=0)
    human_response_priority: Literal["safety_review", "immediate_attention", "unknown", "routine_review"]
    investigation_reported: bool
    investigation_evidence_status: Literal["synthetic_fixture_report_not_independently_verified"] = "synthetic_fixture_report_not_independently_verified"
    agent_intervention_allowed: Literal[False] = False
    human_review_required: Literal[True] = True
    priority_changed: Literal[False] = False
    ticket_state_changed: Literal[False] = False
    notification_sent: Literal[False] = False
    ticket_resolved: Literal[False] = False
    is_sla_or_breach: Literal[False] = False


_THRESHOLDS = {"P1": (timedelta(minutes=15), "15 minutes"),
               "P2": (timedelta(hours=4), "4 hours"),
               "P3": (timedelta(hours=24), "24 hours")}


def evaluate_benchmark(value: object) -> BenchmarkResult:
    """Evaluate one bounded, synthetic, elapsed-time fixture without side effects.

    A customer response after Waiting on Customer starts a fresh ordinary clock;
    no waiting time is counted. A separate original safety timeline continues
    through waiting as historical context, not a deadline. Case/user authorization and input
    provenance must be enforced by a caller before any real integration.
    """
    try:
        raw = value.model_dump(warnings="none") if isinstance(value, BenchmarkInput) else value
        item = BenchmarkInput.model_validate(raw)
    except (ValidationError, ValueError, TypeError):
        raise BenchmarkInputError("invalid_synthetic_benchmark_input") from None
    events = item.events
    if events[0].kind != "in_progress":
        raise BenchmarkInputError("invalid_benchmark_sequence")
    state = "in_progress"
    baseline_index = 0
    previous = events[0].at
    if previous.astimezone(UTC) > item.as_of.astimezone(UTC):
        raise BenchmarkInputError("future_benchmark_event")
    for index, event in enumerate(events[1:], 1):
        if event.at.astimezone(UTC) <= previous.astimezone(UTC):
            raise BenchmarkInputError("invalid_benchmark_sequence")
        if event.at.astimezone(UTC) > item.as_of.astimezone(UTC):
            raise BenchmarkInputError("future_benchmark_event")
        if state in ("in_progress", "waiting_on_customer") and event.kind == "under_investigation":
            state = "under_investigation"
        elif state == "in_progress" and event.kind == "waiting_on_customer":
            state = "waiting_on_customer"
        elif state == "waiting_on_customer" and event.kind == "customer_response":
            state = "in_progress"
            baseline_index = index
        else:
            raise BenchmarkInputError("invalid_benchmark_sequence")
        previous = event.at
    baseline = events[baseline_index].at
    if item.safety_started_at is not None and item.safety_started_at.astimezone(UTC) > item.as_of.astimezone(UTC):
        raise BenchmarkInputError("future_safety_start")
    safety_active = (item.safety_concern_ongoing is True or item.safety_flag_previously_recorded
                     or item.safety_started_at is not None)
    flags = []
    def flag(kind: str, reason: str, *, safety: bool = False) -> None:
        evidence = ("safety_started_at" if item.safety_started_at else "safety_start_unknown") if safety else "case_timeline"
        flags.append(BenchmarkFlag(kind=kind, reason=reason,
            baseline_event_index=None if safety else baseline_index,
            baseline_at=item.safety_started_at if safety else baseline,
            observed_at=item.as_of, evidence_field=evidence))
    if item.priority == "P1":
        flag("p1_immediate", "Synthetic P1 status requires immediate human attention.")
    if safety_active:
        flag("safety_attention", "Ongoing or uncleared synthetic safety concern: prioritize human-led safety review and appropriate response.", safety=True)
    if item.priority == "unknown":
        flag("unknown_urgency", "Urgency is unknown; a human Auditor must review the item.")
    # This field measures the current ordinary period only. It never supplies a
    # safety clock; while waiting it is intentionally absent.
    elapsed = item.as_of.astimezone(UTC) - baseline.astimezone(UTC) if state == "in_progress" else None
    if elapsed is not None and item.priority in _THRESHOLDS:
        threshold, text = _THRESHOLDS[item.priority]
        if elapsed >= threshold:
            flag("benchmark_followup", f"Synthetic case has been In Progress at least {text}; review current impact.")
    if safety_active:
        reason_code = "safety_human_review" if item.safety_started_at is not None else "safety_start_unknown"
    elif item.safety_concern_ongoing is None:
        reason_code = "safety_status_unknown"
    elif item.priority == "unknown":
        reason_code = "unknown_urgency"
    elif state == "under_investigation":
        reason_code = "human_investigation_in_progress"
    else:
        reason_code = "benchmark_assessed"
    return BenchmarkResult(case_id=item.case_id, priority=item.priority, current_state=state,
        status="assessed" if reason_code == "benchmark_assessed" else "needs_human",
        reason_code=reason_code, baseline_event_index=baseline_index, baseline_at=baseline,
        observed_at=item.as_of, elapsed_in_progress_seconds=int(elapsed.total_seconds()) if elapsed is not None else None,
        flags=tuple(flags), safety_flag_preserved=safety_active, safety_started_at=item.safety_started_at,
        safety_elapsed_context_seconds=int((item.as_of.astimezone(UTC)-item.safety_started_at.astimezone(UTC)).total_seconds()) if item.safety_started_at is not None else None,
        human_response_priority=("safety_review" if safety_active else
            "immediate_attention" if item.priority == "P1" else
            "unknown" if item.priority == "unknown" or item.safety_concern_ongoing is None else "routine_review"),
        investigation_reported=state == "under_investigation")
