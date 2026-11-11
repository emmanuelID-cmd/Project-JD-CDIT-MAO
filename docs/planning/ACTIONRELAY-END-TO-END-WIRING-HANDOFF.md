# ActionRelay end-to-end wiring handoff

**Snapshot:** 2026-11-11  
**Purpose:** Resume the remaining app-level integration without rebuilding completed components or changing their approved decisions. This file is the current handoff source if work is interrupted. Update the status and obtain Shawn's acknowledgment when the cross-lane connection is handed over.

## Why the remaining work exists

The six agents and their shared contracts were implemented and exercised through connected synthetic harnesses. The Shared phase plan explicitly scoped that combined harness as test infrastructure, not the app's runtime router. The local app/auth plan also kept agent writes outside that workstream. Therefore, harness coverage and a user-facing working application were mistakenly treated as the same completion point. They are not. The app has several real connected paths, but not one durable, full run timeline joining all six agents and the outcome gate.

## Current implementation — keep and extend

- The authenticated local app and four seeded synthetic accounts are in the project. Auditor is a Staff account with Auditor capability; it is not a fourth role.
- User case submission calls the fixed resource outcome gate in `web.py` and `actionrelay_outcomes.py`. Eligible catalogued forms/resources can be delivered in the ticket; a qualified Low routine resource request can resolve, while Medium/High can receive the safe resource response and remain open. Personal records, sensitive details, mixed requests, uncertain matches, missing files, and unsupported requests stay open. This resource route is deterministic and does not call Claude.
- Admin can start a live Claude Triage call through `actionrelay_live.py`. It requires the server flag and an explicit one-call billable authorization. At this snapshot the route accepts only three exact synthetic examples: IDNYC form, personal W-2, and unexpected payroll withholding. It records a Coordinator/Triage run and always preserves the Triage human-review result.
- An assigned Auditor can save a version-bound decision. `actionrelay_review.py` then runs the existing local Knowledge, Troubleshooting, Escalation, and Documentation agents in order, stopping at the first abstention or failed gate. Results are recorded in the review-run row. The user interface invokes this resume path after a saved decision.
- `combined_harness.py` and `manny_connected_harness.py` provide synthetic cross-agent integration evidence. They are harnesses, not the authenticated app's durable shared blackboard.
- Current review assets and known behaviors are summarized in [`ACTIONRELAY-REVIEW.md`](../presentations/ACTIONRELAY-REVIEW.md) and [`ACTIONRELAY-BUILD-CHECKPOINT.md`](../presentations/ACTIONRELAY-BUILD-CHECKPOINT.md). The current PRD is [`PRD-v4.md`](../requirements/PRD-v4.md).

## Remaining app-level wiring

1. Trace the existing authenticated User → Admin/Staff/Auditor flow and current schemas before editing. Reuse the existing agents, contracts, assignments, version checks, resource gate, and review endpoint.
2. Connect the actual app run to one durable, case-scoped run history. Correlate Coordinator, Triage, Knowledge, Troubleshooting, Escalation, Documentation, Auditor pause/resume, and final application-gate events by run, case, item, and source/policy version. Store only approved metadata and minimum necessary evidence; do not duplicate arbitrary ticket text or attachments into analytics.
3. Preserve current ownership. Manny owns Coordinator, Triage, and Escalation internals. Shawn owns Knowledge, Troubleshooting, and Documentation internals. Cross-lane work may fix the connector, mapping, state, and event wiring only. If a receiver rejects a valid handoff because its internal behavior needs changing, record the defect and return it to that agent's owner.
4. Keep the direct approved resource path available for simple blank-form requests. Do not add a model call when the fixed catalog is sufficient. Personal W-2, payroll changes, name corrections, health/leave facts, and other personal-record or account changes must not be auto-written. Route those to the appropriate human department.
5. For live Claude use, preserve synthetic-only scope, per-run billable authorization, minimized inputs, active handoff preflight, strict output validation, and no hidden retries. The three-sample allowlist is an app connection restriction, not a change to agent authority; any broadening must remain synthetic-only and keep each call explicitly authorized.
6. Follow the approved workflow: intake and minimization → Triage → permitted parallel Knowledge/Escalation checks → compatible acknowledged join → Troubleshooting → Documentation → deterministic application write gate or human handoff. Do not let model text authorize a tool, destination, status change, external message, or permission.
7. Keep human decision points intact. Unknown/ambiguous classification, weak or conflicting evidence, personal or health details, mixed intents, stale versions, and must-escalate signals stop for review. Low-band automatic fulfillment is limited to complete, approved routine resources and the deterministic gate. Resolved means delivered; only authorized Staff/Admin can close.
8. Make the UI show one understandable case activity timeline with completed stages, handoffs, evidence/source references, holds, and next action. Never show an incomplete/abstained run as a successful resolution. Keep run analytics derived from recorded events, not synthetic assumptions.
9. Add/update focused synthetic tests for direct paths, human pause/resume, stale/duplicate writes, parallel joins, unsupported evidence, missing resources, and safe recovery. Record actual command/results here and in `Checklist.md`; do not claim production/CDIT readiness.
10. Reconcile this handoff, PRD, architecture, and checkpoint after the integration. Keep final video/slides as separate deliverables described in [`ACTIONRELAY-FINAL-VIDEO-SLIDES-HANDOFF.md`](../presentations/ACTIONRELAY-FINAL-VIDEO-SLIDES-HANDOFF.md).

## Shawn handoff acknowledgment

This section is a handoff record, not a message already sent. Complete it when Shawn reviews the connected work.

- **Change carried into handoff:** local resource delivery, live Triage checkpoint, versioned Auditor decisions, and downstream local-agent resume already exist; full app-level durable six-agent run history remains to be completed.
- **Connector changes completed in this handoff:** none. This document records scope/status only.
- **Agent-internal changes:** none authorized by this handoff.
- **Handoff commit / PR:** fill in after publishing.
- **Validation evidence:** fill in with commands and results after integration; do not copy old harness results as app-wired evidence.
- **Open issues or owner returns:** fill in with exact stage and receiving owner.
- **Shawn acknowledgment:** pending — confirm reviewed contracts, connector-only scope, carried changes, and any returned lane-owned findings.

## Completion definition

The app shows a traceable synthetic request moving through the applicable agent stages and any required human pause, resumes only from a current authorized decision, records each actual stage result, and commits only a fully eligible Low routine outcome. Unsupported or stale cases remain open with a clear human next step. Existing lane tests remain green, app-wired integration evidence is recorded, the tree is clean after the approved commit, and no production data/integration is claimed.