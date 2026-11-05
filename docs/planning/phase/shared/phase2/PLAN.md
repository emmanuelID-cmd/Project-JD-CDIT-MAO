# Shared Phase 2 — Combined Workflow Harness

**Status:** Planned; depends on approved contracts, owner components, and test authorization.

## Purpose

Build test-only integration infrastructure beyond Shawn's lane-only harness. This is not a seventh agent or production orchestration runtime.

## Work

- Invoke all six actual components through approved contracts; correlate run/agent/handoff/check/state-version events with timestamps/time zone and redacted evidence references.
- Exercise the approved direct pipeline and approved parallel routes only. Shared does not modify Shawn's component harness.
- Assert legal stage/status transitions, recipient acknowledgment, evidence/uncertainty preservation, version matching, duplicate/replay handling, bounded retries, cancellation, recovery, and human pause/resume.
- Exercise missing/rejected/unacknowledged handoffs, stale/conflicting results, timeouts/outages, exhausted budgets, coordinator failure/reassignment, late results, malformed outputs, and fallback.
- Prove no customer message, external alert, ticket write/state change, resolution/closure, or production integration can occur.

## Ownership and exit evidence

Shared fixes connector/harness defects. Internal agent/harness defects are recorded and returned to the owner. Direct and approved parallel paths have reproducible correlated results; failures stop safely.
