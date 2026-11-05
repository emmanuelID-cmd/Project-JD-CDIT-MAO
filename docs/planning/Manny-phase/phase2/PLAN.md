# Phase 2 — Triage (Manny)

**Status:** Planned; depends on Phase 0 and Phase 1 contracts.

## Work

- Define a Triage-specific input/output schema, allowed policy fields, required evidence, verified/inference/unknown labels, and failure outputs.
- Propose category and urgency with rationale, missing facts, and source references; do not invent SLA, account facts, or product behavior.
- Encode approved deterministic urgency-upgrade floors and ambiguous-severity routing outside model judgment. If PRD v2 has not defined them, record a blocker instead of inventing thresholds.
- Keep human review mandatory and confidence non-authoritative. Any confidence signal is evidence/validator-derived and calibrated only through approved held-out evaluation.
- Add machine-checkable expected-output tests for ordinary, incomplete, ambiguous, severity-1, conflicting-policy, injection, and missing-detail-pressure cases.

## Handoff and exit evidence

Send the schema and synthetic examples to Knowledge and Shared Lane. Knowledge consumes only the minimized agreed packet; Shared checks fields, versions, and routing without changing Triage logic. Every material claim is supported or labeled; down-triage rules are tested; unsupported urgency/SLA claims abstain or go to human review; outputs pass contract validation.

## Boundaries

Triage proposes classification only. It does not set ticket urgency/state, contact customers, resolve tickets, or override policy.
