# Phase 3 — Escalation (Manny)

**Status:** Completed locally on 2026-11-05. Fully implemented and verified with deterministic must-escalate evaluation, uncertainty preservation, and human handoff packet generation.

## Implementation evidence — 2026-11-05

- Implemented `EscalationAgent` in `src/cdit_support_mao/agents/escalation/agent.py` adhering to `EscalationHandoff` schema (`Stage.ESCALATION`, A5).
- Evaluates deterministic must-escalate rules:
  - **Privacy Incident**: `TS-SC-PRIVACY` / `possible_privacy_incident` -> `must_escalate=True`, `recommendation="escalate_support_lead"`.
  - **Security Incident**: `TS-SC-SECURITY` / `possible_security_incident` -> `must_escalate=True`, `recommendation="escalate_support_lead"`.
  - **High Urgency (P1)**: `triage.urgency == "high"` -> `must_escalate=True`, `recommendation="escalate_support_lead"`.
  - **Out of Tier 1 Scope**: Rejected case requests -> `must_escalate=True`, `recommendation="escalate_l2"`.
  - **Access & Identity**: `access_or_identity` / `authorized_staff_procedure_required` -> `must_escalate=True`, `recommendation="escalate_l2"`.
  - **Quoted Policy Override**: `quoted_policy_override_attempt` -> `must_escalate=True`, `recommendation="human_review"`.
  - **Conflicting / Stale Guidance**: Conflicting or unapproved sources -> preserves uncertainty (`must_escalate=None`), `recommendation="human_review"`, `confidence=LOW`.
  - **Routine Tier 1 Support**: `troubleshooting.status == "completed"` without escalation signals -> `must_escalate=False`, `recommendation="no_escalation_proposed"`.
- Added 10 tests in `tests/test_escalation_agent.py` covering all positive, negative, and adversarial injection scenarios. Full suite: 509 passed on Python 3.13.15; lane harness 12 passed.

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
