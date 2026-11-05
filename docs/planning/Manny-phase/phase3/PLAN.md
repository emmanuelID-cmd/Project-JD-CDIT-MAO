# Phase 3 — Escalation (Manny)

**Status:** Planned; depends on Phase 0 and approved A5 rules/contract.

## Work

- Translate approved must-escalate conditions into deterministic, testable code; record rule/policy versions and stop safely when rules are missing.
- Distinguish risk annotation, required human escalation, and ordinary routing. A scanner signal alone does not establish an incident or grant authority.
- Preserve evidence, source/policy versions, actions tried, unresolved questions, severity uncertainty, and handoff rationale.
- Validate the human handoff packet and local safe status; bound processing and stop/fallback on conflicts or unavailable dependencies.
- Add positive/negative rule tests for urgent/ambiguous severity, access/security concerns, stale/conflicting evidence, and injection.

## Handoff and exit evidence

Share A5 packet/schema and rule identifiers with Shared Lane. Human-review UI and notifications follow approved contract; email remains deferred. Identical policy facts produce deterministic outcomes; missing/conflicting policy routes safely to humans; no second-reviewer agent or external write/notification tool is introduced.

## Boundaries

No confidence-based adversarial winner, permission change, external alert, ticket resolution, or closure.
