# Coordinator harness plan — Manny Phase 1

## Baseline and environment

PRD-v3 A0/A1, Manny Phase 1, and handoff version `0.1.0-proposed` define the current synthetic fixture checks. The runtime is Python 3.13 with Pydantic and pytest. No model, external API, database, actual agent dispatch or side effect is exercised. The fixture authority and handoff ledger are process-local; timing is supplied by the caller, and automatic retries are disabled.

## Requirement-to-check map

| Coverage | Expected behavior | Evidence |
| --- | --- | --- |
| Normal intake | Scoped active fixture, current case and policy produce a minimized untrusted packet | `tests/test_coordinator_intake.py` |
| Role/scope and malformed data | Missing, revoked, inactive, out-of-scope, non-synthetic, unexpected or invalid input stops at A0 | `tests/test_coordinator_intake.py` |
| Direct/indirect input risk | Known injection or sensitive-looking text is stopped; legitimate multilingual text is preserved | `tests/test_coordinator_intake.py`, `tests/test_coordinator_handoff.py` |
| Handoff and concurrency | Only trusted sender and receiver act; acknowledgment precedes packet read; simultaneous acknowledgment accepts at most one update | `tests/test_coordinator_handoff.py` |
| Recovery | Stale case/policy/context/state, cancelled, expired, unavailable, revoked or duplicate work cannot silently advance | `tests/test_coordinator_handoff.py` |
| Review and trace | Synthetic review requires scoped active reviewer, same context and new acknowledgment; traces omit message/token | `tests/test_coordinator_handoff.py` |

## Evaluation boundaries

These code tests are developer-authored synthetic fixtures, not the 111-case D-08/D-09 held-out set. Manny will review and approve the draft labels separately. No calibration, end-to-end MAO outcome, live service, release threshold or real human review is established by this suite. External effects are unavailable, so tests do not claim exactly-once delivery. Locks and state-version checks are limited to one process and cannot replace the future database or cross-process ownership design.

## Trace and review

Intake produces ordered A0/A1 events with trace and run IDs where available. Handoff events carry run, handoff, state version, current owner, status, contract version and zoned timestamp; no raw ticket text, token or private reasoning is logged. No separate agent terminal streams are claimed: there is no multi-agent runtime execution in this phase. The project lead deferred Shared Lane receiver review to the integration gate; it is not represented as complete. A direct read-only reviewer and scoped security inspection checked the changed files, actual fixture outputs, role/scope checks and stale/duplicate/cancellation behavior; no independent reviewer was used. Shared Lane receiver review is deferred to integration.
