# Phase 3 — Escalation (Manny)

**Status:** Escalation implementation and unit-test evidence exist locally; Phase 3 is not accepted or complete. The current A2 input and linked-item handoff are not integrated, so the planned integrated A2-to-A5 handoff and shared receiver checks remain blocked on Phase 2. The Auditor UI and authenticated review interface are deferred and are not being built now.

## Implementation evidence — 2026-11-05

- Implemented `EscalationAgent` in `src/cdit_support_mao/agents/escalation/agent.py` adhering to `EscalationHandoff` schema (`Stage.ESCALATION`, A5).
- A5 action claims now require a staff-entry source ID and version matching the current synthetic case context before a coordinator-supplied verified flag can be reflected as verified; unresolved-question claims preserve their source reference. This is a contract integrity check, not production authentication or independent proof of the staff record.
- Unknown urgency now routes to human review/Auditor without assigning a band. Potential attention signals require a current accepted A1 checkpoint and live Coordinator registry validation; the source-backed inference preserves pattern IDs and matched codepoint spans. A flag never assigns urgency. A current, source- and version-verified `Under Investigation` case fact routes for human review with its exact source, preserves investigation context under P1 precedence, and explicitly does not change status or contact a third party. Stale, cross-case, or unverified investigation facts do not trigger that rule.
- Evaluates deterministic must-escalate rules:
  - **Privacy Incident**: `TS-SC-PRIVACY` / `possible_privacy_incident` -> `must_escalate=True`, `recommendation="escalate_support_lead"`.
  - **Security Incident**: `TS-SC-SECURITY` / `possible_security_incident` -> `must_escalate=True`, `recommendation="escalate_support_lead"`.
  - **High Urgency (P1)**: `triage.urgency == "high"` -> `must_escalate=True`, `recommendation="escalate_support_lead"`.
  - **Out of Tier 1 Scope**: Rejected case requests -> `must_escalate=True`, `recommendation="escalate_l2"`.
  - **Access & Identity**: `access_or_identity` / `authorized_staff_procedure_required` -> `must_escalate=True`, `recommendation="escalate_l2"`.
  - **Quoted Policy Override**: `quoted_policy_override_attempt` -> `must_escalate=True`, `recommendation="human_review"`.
  - **Conflicting / Stale Guidance**: Conflicting or unapproved sources -> preserves uncertainty (`must_escalate=None`), `recommendation="human_review"`, `confidence=LOW`.
  - **Routine Tier 1 Support**: `troubleshooting.status == "completed"` without escalation signals -> `must_escalate=False`, `recommendation="no_escalation_proposed"`.
- The focused `tests/test_escalation_agent.py` suite has 29 passing tests, including verified/unverified staff-recorded action provenance, unknown urgency, attention preservation/rejection/live-state freshness, investigation status provenance, P1 precedence, cross-case/stale-source rejection, unresolved-question provenance, and action-sensitive contribution IDs. The full Python 3.13.15 suite passes 565 tests after the developer fast-forward; integrated Phase 3 acceptance remains open.

## Work

- Translate approved must-escalate conditions into deterministic, testable code; record rule/policy versions and stop safely when rules are missing.
- Distinguish risk annotation, required human escalation, and ordinary routing. A scanner signal alone does not establish an incident or grant authority.
- Preserve evidence, source/policy versions, actions tried, unresolved questions, severity uncertainty, and handoff rationale.
- Validate the human handoff packet and local safe status; bound processing and stop/fallback on conflicts or unavailable dependencies.
- Add positive/negative rule tests for urgent/ambiguous severity, access/security concerns, stale/conflicting evidence, and injection.

## Handoff and exit evidence

Share the A5 packet/schema and rule identifiers with Shared Lane after Phase 2 produces its accepted input. The local agent tests verify deterministic rules and uncertainty preservation; they do not prove an integrated A2-to-A5 handoff. Human-review UI/authentication is deferred and not built; outbound email remains deferred. No second-reviewer agent or external write/notification tool is introduced.

## Boundaries

No confidence-based adversarial winner, permission change, external alert, ticket resolution, or closure.
