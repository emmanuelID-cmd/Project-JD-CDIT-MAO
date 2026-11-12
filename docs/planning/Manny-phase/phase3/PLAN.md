# Phase 3 — Escalation (Manny)

**Status (2026-11-08):** A5 implementation and connected synthetic integration checks are complete. The combined harness exercises Auditor-resolved item handoff through Knowledge, Troubleshooting, Escalation, and Documentation; same-item provenance and High/P1 escalation are covered. Focused connected integration tests: 58 passed; full Python suite: 689 passed after the case-assignment change. Final checklist review remains separate from test success. The local Staff/Admin Auditor interface and assigned-case permission coverage are implemented; manual browser/accessibility review remains open.

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
- The focused `tests/test_escalation_agent.py` suite includes three regression cases for pending Unknown, Auditor-resolved P1, and distinct linked-item provenance. The connected integration set (`test_combined_workflow.py`, `test_escalation_agent.py`, `test_manny_connected_harness.py`, and `test_triage_knowledge_connection.py`) passed 58 tests. The full Python suite passed 686 tests.

## Work

- Translate approved must-escalate conditions into deterministic, testable code; record rule/policy versions and stop safely when rules are missing.
- Distinguish risk annotation, required human escalation, and ordinary routing. A scanner signal alone does not establish an incident or grant authority.
- Preserve evidence, source/policy versions, actions tried, unresolved questions, severity uncertainty, and handoff rationale.
- Validate the human handoff packet and local safe status; bound processing and stop/fallback on conflicts or unavailable dependencies.
- Add positive/negative rule tests for urgent/ambiguous severity, access/security concerns, stale/conflicting evidence, and injection.

## Handoff and exit evidence

The connected harness now verifies the item-scoped A2-to-A5 handoff through the accepted A3/A4 path. Human disposition remains human-authored and propose-only; the harness's Auditor fixture is synthetic test data, while the local Staff/Admin app provides the decision form and append-only decision history. The local app restricts Staff actions to assigned cases and records Admin assignment/override actions. No customer communication, third-party dispatch, external write, second-reviewer agent, or agent-originated case status change is enabled.

## Boundaries

No confidence-based adversarial winner, permission change, external alert, ticket resolution, or closure.
