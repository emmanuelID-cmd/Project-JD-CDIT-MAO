# Coordinator A0/A1 — synthetic fixture boundary

**Status:** Phase 1 local synthetic fixture implementation reviewed. Shared Lane receiver review remains an integration gate. This is a process-local fixture runtime, not production authentication or a durable blackboard. PRD-v4 is the project lead's approved Manny build baseline; contract `0.1.0-proposed` is the accepted working interface version, without changing Shawn-owned schemas.

## Scope and trust

A trusted bootstrap provisions expiring synthetic sessions and case versions in memory. The Coordinator accepts an opaque fixture token separately from case data and enforces active Staff/Admin role, explicit case scope, current case version, configured synthetic policy version, strict input schema, and A0/A1 guards. User client-side submission remains separate. This fixture system is not connected to an HTTP endpoint and does not authenticate real people. A synthetic label or matching ID does not prove real data is synthetic; real records and credentials remain excluded.

Case messages and later agent content remain untrusted. Pattern matches trigger a human-review stop; non-matches do not establish safety. The receiver receives a minimized message only after a version-matched acknowledgment and current session/case checks. No model, external action, database, or ticket write is configured.

## Process-local coordination

The handoff ledger records an immutable checkpoint, current owner, case/run/policy/contract versions, evidence reference, unknowns, pending work, no-effect status, and metadata-only events. Sender and receiver capabilities are separate trusted runtime objects. Atomic compare-and-update holds short locks in session → case version → policy version → handoff order; the ledger does not support multiple processes. A repeated run with changed content or session is rejected. Case and policy version authorities are in-memory fixtures; replacing a version blocks stale handoffs. Stale, revoked, cancelled, expired, missing, and unacknowledged work is blocked or routed to manual recovery. No automatic retries occur. On process loss, the in-memory ledger is unavailable and work requires manual recovery; it does not reconstruct accepted state.

A fixture-review pause can resume only after the synthetic reviewer session, case scope, same context and current version are rechecked, followed by a fresh receiver acknowledgment. This simulates a review transition; a real human-review UI and durable approval records are not implemented. The session lifetime and handoff timeout are explicitly supplied by the trusted harness; the code's range guard is not a CDIT SLA or approved operational timeout.

## Evidence and remaining work

Focused tests cover synthetic role/case scope, invalid fields, direct and indirect risk signals, benign multilingual input, redaction, acknowledgment, stale case and policy versions, duplicate runs, cancellation, timeout, revocation, fixture review and concurrent acknowledgments. The developer fixture harness uses eight synthetic cases, not approved D-09 labels. The shared-state persistence choice, approved operating budgets, production identity, actual Triage execution, cross-agent integration, and project-wide evaluation remain open or belong to later phases. See `COORDINATOR-AGENT-CONTRACT.md` and `COORDINATOR-HARNESS-PLAN.md` for the contract and evaluation limits.
