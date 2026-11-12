"""Approved synthetic attention benchmarks; no operational SLA assertions."""
from datetime import UTC, datetime, timedelta, timezone

import pytest

from cdit_support_mao.agents.triage.benchmark import BenchmarkInputError, evaluate_benchmark

START = datetime(2026, 11, 5, 12, tzinfo=UTC)


def case(*, priority="P2", at=START, safety=False, events=None):
    return {"case_id":"SYN-CASE-01", "data_classification":"synthetic", "priority":priority,
            "safety_concern_ongoing":safety, "safety_flag_previously_recorded":False,
            "safety_started_at":START if safety is True else None, "events":events or [{"kind":"in_progress","at":START}],
            "as_of":at}


def kinds(result):
    return {flag.kind for flag in result.flags}


@pytest.mark.parametrize("priority,threshold", [("P1",timedelta(minutes=15)),
    ("P2",timedelta(hours=4)), ("P3",timedelta(hours=24))])
def test_threshold_boundaries_use_elapsed_in_progress(priority,threshold):
    before=evaluate_benchmark(case(priority=priority,at=START+threshold-timedelta(microseconds=1)))
    at=evaluate_benchmark(case(priority=priority,at=START+threshold))
    assert "benchmark_followup" not in kinds(before)
    assert "benchmark_followup" in kinds(at)
    assert ("p1_immediate" in kinds(at)) == (priority == "P1")
    assert at.priority == priority and at.human_review_required
    assert not at.priority_changed and not at.ticket_state_changed and not at.notification_sent
    assert not at.ticket_resolved and not at.is_sla_or_breach
    flag=next(f for f in at.flags if f.kind == "benchmark_followup")
    assert flag.baseline_event_index == 0 and flag.baseline_at == START and flag.observed_at == at.observed_at
    assert flag.evidence_status == "synthetic_fixture_report_not_independently_verified"


def test_p1_immediate_even_before_followup_and_while_waiting():
    now=evaluate_benchmark(case(priority="P1"))
    assert kinds(now) == {"p1_immediate"}
    events=[{"kind":"in_progress","at":START},{"kind":"waiting_on_customer","at":START+timedelta(minutes=2)}]
    waiting=evaluate_benchmark(case(priority="P1",at=START+timedelta(days=3),events=events))
    assert waiting.current_state == "waiting_on_customer" and waiting.elapsed_in_progress_seconds is None
    assert kinds(waiting) == {"p1_immediate"}


def test_waiting_period_excluded_and_response_resets_ordinary_clock():
    wait=START+timedelta(hours=3)
    reply=START+timedelta(days=2)
    events=[{"kind":"in_progress","at":START},{"kind":"waiting_on_customer","at":wait},
            {"kind":"customer_response","at":reply}]
    result=evaluate_benchmark(case(priority="P2",at=reply+timedelta(hours=1),events=events))
    assert result.current_state == "in_progress" and result.baseline_at == reply and result.baseline_event_index == 2
    assert result.elapsed_in_progress_seconds == 3600 and "benchmark_followup" not in kinds(result)
    later=evaluate_benchmark(case(priority="P2",at=reply+timedelta(hours=4),events=events))
    assert "benchmark_followup" in kinds(later)


@pytest.mark.parametrize("priority", ["P1","P2","P3","unknown"])
@pytest.mark.parametrize("waiting", [False, True])
def test_ongoing_safety_preserves_attention_and_continuous_timeline(priority,waiting):
    events=[{"kind":"in_progress","at":START}]
    if waiting: events.append({"kind":"waiting_on_customer","at":START+timedelta(minutes=1)})
    result=evaluate_benchmark(case(priority=priority,at=START+timedelta(days=3),safety=True,events=events))
    assert result.reason_code == "safety_human_review" and result.status == "needs_human"
    assert result.safety_flag_preserved and "safety_attention" in kinds(result)
    assert ("benchmark_followup" in kinds(result)) == (not waiting and priority != "unknown")
    assert not result.priority_changed


def test_safety_after_customer_response_never_implies_safety_clock_reset():
    events=[{"kind":"in_progress","at":START},
            {"kind":"waiting_on_customer","at":START+timedelta(hours=1)},
            {"kind":"customer_response","at":START+timedelta(days=1)}]
    result=evaluate_benchmark(case(priority="P2",at=START+timedelta(days=1,hours=6),safety=True,events=events))
    assert result.safety_flag_preserved and result.reason_code == "safety_human_review"
    assert result.safety_started_at == START and result.safety_elapsed_context_seconds == 30*3600
    assert result.human_response_priority == "safety_review"
    assert "benchmark_followup" in kinds(result)


def test_unknown_urgency_and_unknown_safety_go_to_human():
    unknown=evaluate_benchmark(case(priority="unknown",at=START+timedelta(days=10)))
    assert unknown.reason_code == "unknown_urgency" and "unknown_urgency" in kinds(unknown)
    assert not unknown.priority_changed and "benchmark_followup" not in kinds(unknown)
    safety=evaluate_benchmark(case(safety=None,at=START+timedelta(days=10)))
    assert safety.status == "needs_human" and safety.reason_code == "safety_status_unknown"
    assert "benchmark_followup" in kinds(safety)


@pytest.mark.parametrize("events", [[],
    [{"kind":"waiting_on_customer","at":START}],
    [{"kind":"customer_response","at":START}],
    [{"kind":"in_progress","at":START},{"kind":"customer_response","at":START+timedelta(seconds=1)}],
    [{"kind":"in_progress","at":START},{"kind":"waiting_on_customer","at":START}],
    [{"kind":"in_progress","at":START},{"kind":"waiting_on_customer","at":START-timedelta(seconds=1)}],
    [{"kind":"in_progress","at":START},{"kind":"waiting_on_customer","at":START+timedelta(seconds=1)},
     {"kind":"waiting_on_customer","at":START+timedelta(seconds=2)}],
    [{"kind":"in_progress","at":START},{"kind":"resolved","at":START+timedelta(seconds=1)}]])
def test_invalid_timeline_fails_closed(events):
    raw=case(at=START+timedelta(days=1))
    raw["events"]=events
    with pytest.raises(BenchmarkInputError): evaluate_benchmark(raw)


def test_future_event_and_naive_or_numeric_timestamps_rejected():
    with pytest.raises(BenchmarkInputError,match="future_benchmark_event"):
        evaluate_benchmark(case(at=START-timedelta(seconds=1)))
    for bad in (datetime(2026,11,5,12), 0, None, True):
        raw=case(); raw["as_of"]=bad
        with pytest.raises(BenchmarkInputError,match="invalid_synthetic_benchmark_input"):
            evaluate_benchmark(raw)
    raw=case(); raw["events"]=[{"kind":"in_progress","at":datetime(2026,11,5,12)}]
    with pytest.raises(BenchmarkInputError): evaluate_benchmark(raw)


def test_synthetic_boundary_and_strict_safety_field():
    for changes in ({"case_id":"REAL-CASE"},{"data_classification":"real"},
                    {"safety_concern_ongoing":"false"},{"priority":"critical"}):
        raw=case(); raw.update(changes)
        with pytest.raises(BenchmarkInputError): evaluate_benchmark(raw)


def test_aware_offsets_compare_actual_elapsed_time():
    original=START.astimezone(timezone(timedelta(hours=-5)))
    result=evaluate_benchmark(case(at=START+timedelta(hours=4),events=[{"kind":"in_progress","at":original}]))
    assert result.elapsed_in_progress_seconds == 14400 and "benchmark_followup" in kinds(result)


def test_recorded_safety_flag_cannot_be_cleared_by_false_or_unknown_status():
    for status in (False, None):
        raw=case(safety=status,at=START+timedelta(hours=3))
        raw.update(safety_flag_previously_recorded=True,safety_started_at=START)
        result=evaluate_benchmark(raw)
        assert result.safety_flag_preserved and result.reason_code == "safety_human_review"
        assert result.safety_elapsed_context_seconds == 10800
        assert result.human_response_priority == "safety_review" and "safety_attention" in kinds(result)
        assert not result.notification_sent and not result.ticket_resolved


def test_original_safety_timeline_includes_waiting_without_setting_deadline():
    events=[{"kind":"in_progress","at":START},{"kind":"waiting_on_customer","at":START+timedelta(hours=1)},
            {"kind":"customer_response","at":START+timedelta(days=2)}]
    result=evaluate_benchmark(case(priority="P1",safety=True,events=events,at=START+timedelta(days=2,hours=1)))
    assert result.safety_elapsed_context_seconds == 49*3600
    assert result.elapsed_in_progress_seconds == 3600
    safety=next(flag for flag in result.flags if flag.kind == "safety_attention")
    assert safety.evidence_field == "safety_started_at" and safety.baseline_at == START
    assert not result.is_sla_or_breach and not result.ticket_resolved and not result.notification_sent


def test_missing_original_safety_start_preserves_flag_and_requests_human():
    raw=case(safety=True,at=START+timedelta(hours=3))
    raw["safety_started_at"]=None
    result=evaluate_benchmark(raw)
    assert result.reason_code == "safety_start_unknown" and result.safety_flag_preserved
    assert result.safety_elapsed_context_seconds is None and result.human_review_required
    safety=next(flag for flag in result.flags if flag.kind == "safety_attention")
    assert safety.evidence_field == "safety_start_unknown" and safety.baseline_at is None


def test_safety_start_must_be_aware_not_in_future_and_prior_flag_explicit():
    raw=case(safety=True)
    for value in (datetime(2026,11,5,12), 0, True):
        raw["safety_started_at"]=value
        with pytest.raises(BenchmarkInputError): evaluate_benchmark(raw)
    raw["safety_started_at"]=START+timedelta(seconds=1)
    with pytest.raises(BenchmarkInputError,match="future_safety_start"): evaluate_benchmark(raw)
    raw=case(); del raw["safety_flag_previously_recorded"]
    with pytest.raises(BenchmarkInputError): evaluate_benchmark(raw)


def test_earlier_safety_start_is_preserved_without_invented_case_baseline():
    raw=case(safety=True,at=START+timedelta(hours=1))
    raw["safety_started_at"]=START-timedelta(hours=2)
    result=evaluate_benchmark(raw)
    assert result.safety_started_at == START-timedelta(hours=2)
    assert result.safety_elapsed_context_seconds == 10800


@pytest.mark.parametrize("safety", [False, True, None])
def test_under_investigation_is_human_led_and_ordinary_benchmark_not_assessed(safety):
    events=[{"kind":"in_progress","at":START},
            {"kind":"under_investigation","at":START+timedelta(hours=1)}]
    result=evaluate_benchmark(case(priority="P2",safety=safety,events=events,at=START+timedelta(days=3)))
    assert result.current_state == "under_investigation" and result.investigation_reported
    assert result.elapsed_in_progress_seconds is None and "benchmark_followup" not in kinds(result)
    assert not result.agent_intervention_allowed and not result.ticket_state_changed
    assert result.status == "needs_human" and not result.notification_sent
    if safety is True:
        assert result.safety_flag_preserved and result.safety_elapsed_context_seconds == 72*3600
        assert result.human_response_priority == "safety_review"
    elif safety is False:
        assert result.reason_code == "human_investigation_in_progress"


def test_investigation_can_start_during_waiting_but_resumption_policy_is_unknown():
    events=[{"kind":"in_progress","at":START},
            {"kind":"waiting_on_customer","at":START+timedelta(hours=1)},
            {"kind":"under_investigation","at":START+timedelta(hours=2)}]
    result=evaluate_benchmark(case(events=events,at=START+timedelta(hours=3)))
    assert result.investigation_reported and result.reason_code == "human_investigation_in_progress"
    events.append({"kind":"in_progress","at":START+timedelta(hours=4)})
    with pytest.raises(BenchmarkInputError,match="invalid_benchmark_sequence"):
        evaluate_benchmark(case(events=events,at=START+timedelta(hours=5)))


def test_fall_back_fold_uses_real_elapsed_time_and_order():
    from datetime import tzinfo
    class TestFallBack(tzinfo):
        def utcoffset(self, dt):
            return timedelta(hours=-5 if dt.fold else -4)
        def dst(self, dt):
            return timedelta(0)
    zone=TestFallBack()
    before=datetime(2026,11,1,1,30,tzinfo=zone,fold=0)
    after=datetime(2026,11,1,1,30,tzinfo=zone,fold=1)
    raw=case(priority="P1",at=after,events=[{"kind":"in_progress","at":before}])
    result=evaluate_benchmark(raw)
    assert result.elapsed_in_progress_seconds == 3600 and "benchmark_followup" in kinds(result)
    raw["events"].append({"kind":"waiting_on_customer","at":after})
    waiting=evaluate_benchmark(raw)
    assert waiting.current_state == "waiting_on_customer" and waiting.elapsed_in_progress_seconds is None


def test_p1_and_unknown_attention_are_not_labeled_routine():
    p1=evaluate_benchmark(case(priority="P1"))
    assert p1.human_response_priority == "immediate_attention"
    unknown=evaluate_benchmark(case(priority="unknown"))
    assert unknown.human_response_priority == "unknown"
    safety_unknown=evaluate_benchmark(case(safety=None))
    assert safety_unknown.human_response_priority == "unknown"
    flagged=evaluate_benchmark(case(priority="P1",safety=True))
    assert flagged.human_response_priority == "safety_review"


def test_investigation_state_is_a_report_not_verified_human_action():
    events=[{"kind":"in_progress","at":START},
            {"kind":"under_investigation","at":START+timedelta(minutes=1)}]
    result=evaluate_benchmark(case(events=events,at=START+timedelta(minutes=2)))
    assert result.investigation_reported
    assert result.investigation_evidence_status == "synthetic_fixture_report_not_independently_verified"
    assert not result.agent_intervention_allowed and not result.notification_sent


def test_active_safety_does_not_hide_ordinary_p1_followup():
    result=evaluate_benchmark(case(priority="P1",safety=True,at=START+timedelta(minutes=15)))
    assert {"p1_immediate","benchmark_followup","safety_attention"} <= kinds(result)
    assert result.human_response_priority == "safety_review"
    assert not result.priority_changed and not result.notification_sent


def test_timestamp_strings_require_explicit_iso_timezone_not_epoch_strings():
    for bad in ("0", "1762344000", "2026-11-05T12:00:00", "2026-11-05"):
        raw=case(); raw["as_of"]=bad
        with pytest.raises(BenchmarkInputError,match="invalid_synthetic_benchmark_input"):
            evaluate_benchmark(raw)
    raw=case(); raw["as_of"]="2026-11-05T16:00:00Z"
    assert "benchmark_followup" in kinds(evaluate_benchmark(raw))
