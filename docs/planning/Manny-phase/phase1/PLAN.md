# Phase 1 — Coordinator and Intake Boundary (Manny)

**Status:** Planned; depends on Phase 0 authorization and agreed interfaces.

## Purpose and work

Implement Coordinator-owned A0/A1 run boundaries and minimized, versioned handoffs without external action authority.

- Define input/output schemas and run/case/stage identity using the accepted contract.
- Enforce the approved local account/session and role/scope boundary; validate schema, permitted fields, synthetic-data status, and type/size bounds before dispatch. Local authentication infrastructure ownership remains open under D-15.
- Treat tickets, attachments, retrieved text, stored state, and agent output as untrusted data; policy and tool authority stay outside content.
- Carry provenance, versions, claim labels, uncertainty, timestamps, and explicit acknowledgment through handoffs.
- Define bounded retry, timeout, cancellation, duplicate/replay, missing acknowledgment, stale-state, unavailable-agent, pause, and fallback behavior.
- Add deterministic validators and synthetic direct/indirect injection tests at Manny-owned boundaries. Detection is a risk signal, never a trust decision.

## Handoff and exit evidence

Publish Coordinator/intake contracts for Shared connection checks and receiver review. Connector defects go to Shared; Coordinator behavior defects stay Manny-owned. A0/A1 tests prove unsafe inputs stop before downstream work; valid synthetic requests are minimized/version-bound; traces are correlated/redacted; no external write path exists.

## Boundaries

No live ticket ingestion, production database/auth, model provider, external action, or changes to Shawn's internals.
