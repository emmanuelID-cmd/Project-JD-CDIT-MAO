# Phase 1 — Coordinator and Intake Boundary (Manny)

**Status:** Local synthetic fixture implementation and direct review completed on 2026-11-04. Shared Lane receiver review is deferred to the integration gate by project-lead direction; database, production authentication, actual Triage execution, and multi-process state remain outside this local phase.

## Purpose and work

Implement Coordinator-owned A0/A1 run boundaries and minimized, versioned handoffs without external action authority.

- Define input/output schemas and run/case/stage identity using the accepted contract.
- Enforce the approved local account/session and role/scope boundary; validate schema, permitted fields, synthetic-data status, and type/size bounds before dispatch. Local authentication infrastructure ownership remains open under D-15.
- Treat tickets, attachments, retrieved text, stored state, and agent output as untrusted data; policy and tool authority stay outside content.
- Carry provenance, versions, claim labels, uncertainty, timestamps, and explicit acknowledgment through handoffs.
- Define bounded retry, timeout, cancellation, duplicate/replay, missing acknowledgment, stale-state, unavailable-agent, pause, and fallback behavior.
- Add deterministic validators and synthetic direct/indirect injection tests at Manny-owned boundaries. Detection is a risk signal, never a trust decision.

## Handoff and exit evidence

Publish Coordinator/intake contracts for Shared connection checks and receiver review. Connector defects go to Shared; Coordinator behavior defects stay Manny-owned. Defined synthetic must-stop cases stop before downstream work; valid fixture requests are minimized/version-bound; traces are correlated and redacted; no external write path exists. Pattern detection is not a guarantee against all unsafe inputs.

## Boundaries

No live ticket ingestion, production database/auth, model provider, external action, or changes to Shawn's internals.

## Local evidence — 2026-11-04

- Python 3.13.15: 86 focused Coordinator and shared-contract tests passed. The developer fixture harness passed 8/8 cases; these are not the D-09 holdout labels.
- See `docs/lanes/manny/COORDINATOR-A0-A1.md`, `COORDINATOR-AGENT-CONTRACT.md`, and `COORDINATOR-HARNESS-PLAN.md` for the actual implementation and limitations.
- Direct security and read-only review of the actual changed files covered fixture session and case scope, case/policy version checks, sender/receiver capabilities, acknowledgment, cancellation, timeout, fixture-review resumption, redacted trace and no external dispatch. This was not an independent reviewer. No production security or multi-process guarantee is claimed.
- Shared Lane receiver review, persistent storage, actual Triage and cross-agent runtime integration remain open; the project lead explicitly deferred receiver review to integration.
