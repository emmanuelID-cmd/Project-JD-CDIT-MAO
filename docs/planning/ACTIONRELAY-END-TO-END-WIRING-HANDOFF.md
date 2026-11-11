# ActionRelay end-to-end wiring handoff

**Snapshot:** 2026-11-11
**Purpose:** Resume the remaining app-level integration without rebuilding completed components or changing their approved decisions. This file is the current handoff source if work is interrupted. Update the status and obtain Shawn's acknowledgment when the cross-lane connection is handed over.

## Why the remaining work exists

The six agents and their shared contracts were implemented and exercised through connected synthetic harnesses. The Shared phase plan explicitly scoped that combined harness as test infrastructure, not the app's runtime router. The local app/auth plan also kept agent writes outside that workstream. Therefore, harness coverage and a user-facing working application were mistakenly treated as the same completion point. They are not. The app has connected paths; this change adds a unified case-version view over persisted Triage, Auditor-resume and outcome runs. This is not a new normalized event ledger, and end-to-end validation remains outstanding.

## Current implementation — keep and extend

- The authenticated local app and four seeded synthetic accounts are in the project. Auditor is a Staff account with Auditor capability; it is not a fourth role.
- User case submission calls the fixed resource outcome gate in `web.py` and `actionrelay_outcomes.py`. Eligible catalogued forms/resources can be delivered in the ticket; a qualified Low routine resource request can resolve, while Medium/High can receive the safe resource response and remain open. Personal records, sensitive details, mixed requests, uncertain matches, missing files, and unsupported requests stay open. This resource route is deterministic and does not call Claude.
- Admin can start a live Claude Triage call through `actionrelay_live.py`. It requires the server flag and an explicit one-call billable authorization. The route now accepts submitted synthetic user requests up to 2,000 characters rather than only three exact prompts. The shared likely-sensitive-input screen blocks probable personal details before provider dispatch. Each exact case version permits at most one provider attempt. It records Coordinator/Triage and always preserves the Triage human-review result.
- An assigned Auditor can save a version-bound decision. `actionrelay_review.py` then runs the existing local Knowledge, Troubleshooting, Escalation, and Documentation agents in order, stopping at the first abstention or failed gate. Results are recorded in the review-run row. The user interface invokes this resume path after a saved decision.
- `combined_harness.py` and `manny_connected_harness.py` provide synthetic cross-agent integration evidence. They are harnesses, not the authenticated app's durable shared blackboard.
- Current review assets and known behaviors are summarized in [`ACTIONRELAY-REVIEW.md`](../presentations/ACTIONRELAY-REVIEW.md) and [`ACTIONRELAY-BUILD-CHECKPOINT.md`](../presentations/ACTIONRELAY-BUILD-CHECKPOINT.md). The current PRD is [`PRD-v4.md`](../requirements/PRD-v4.md).

## Remaining app-level wiring

1. Trace the existing authenticated User → Admin/Staff/Auditor flow and current schemas before editing. Reuse the existing agents, contracts, assignments, version checks, resource gate, and review endpoint.
2. The activity API now joins persisted Coordinator/Triage, Auditor-resume and application-outcome rows by exact case ID and case version. The UI renders one timeline while the existing run rows remain the durable sources. Validate stale, blocked, abstained and completed stage results end-to-end. A normalized per-stage event ledger and per-stage timestamps are not implemented.
3. Preserve current ownership. Manny owns Coordinator, Triage, and Escalation internals. Shawn owns Knowledge, Troubleshooting, and Documentation internals. Cross-lane work may fix the connector, mapping, state, and event wiring only. If a receiver rejects a valid handoff because its internal behavior needs changing, record the defect and return it to that agent's owner.
4. Keep the direct approved resource path available for simple blank-form requests. Do not add a model call when the fixed catalog is sufficient. Personal W-2, payroll changes, name corrections, health/leave facts, and other personal-record or account changes must not be auto-written. Route those to the appropriate human department.
5. For live Claude use, preserve synthetic-only scope, per-run billable authorization, the 2,000-character cap, the shared heuristic screen for likely personal/sensitive details, active handoff preflight, strict output validation, and no hidden retries. A synthetic database flag cannot prove human-entered content is fictional. Use synthetic requests only; document that the screen can miss sensitive details.
6. Follow the approved workflow: intake and minimization → Triage → permitted parallel Knowledge/Escalation checks → compatible acknowledged join → Troubleshooting → Documentation → deterministic application write gate or human handoff. Do not let model text authorize a tool, destination, status change, external message, or permission.
7. Keep human decision points intact. Unknown/ambiguous classification, weak or conflicting evidence, personal or health details, mixed intents, stale versions, and must-escalate signals stop for review. Low-band automatic fulfillment is limited to complete, approved routine resources and the deterministic gate. Resolved means delivered; only authorized Staff/Admin can close.
8. The case activity UI now shows one version-matched timeline spanning Coordinator/Triage, Auditor decision, downstream stages and the deterministic application outcome when one exists for that version. It shows stage states and bounded reason codes; it does not yet show per-stage timestamps or evidence/source references. Never show an incomplete/abstained run as a successful resolution. Keep run analytics derived from recorded runs, not synthetic assumptions.
9. Add/update focused synthetic tests for direct paths, human pause/resume, stale/duplicate writes, parallel joins, unsupported evidence, missing resources, and safe recovery. Record actual command/results here and in `Checklist.md`; do not claim production/CDIT readiness.
10. Reconcile this handoff, PRD, architecture, and checkpoint after the integration. Keep final video/slides as separate deliverables described in [`ACTIONRELAY-FINAL-VIDEO-SLIDES-HANDOFF.md`](../presentations/ACTIONRELAY-FINAL-VIDEO-SLIDES-HANDOFF.md).

## Shawn handoff acknowledgment

This section is a handoff record, not a message already sent. Complete it when Shawn reviews the connected work.

- **Change carried into handoff:** local resource delivery, live Triage checkpoint, versioned Auditor decisions, and downstream local-agent resume already exist; full app-level durable six-agent run history remains to be completed.
- **Connector changes completed in this handoff:** live Triage is widened from three exact prompts to bounded synthetic requests with per-call authorization and the existing likely-sensitive-input screen; persisted workflow records are joined by exact case version into one UI timeline; bounded stage reason codes and Triage item categories are displayed. Changes are not yet end-to-end validated or committed.
- **Agent-internal changes:** none authorized by this handoff.
- **Handoff commit / PR:** fill in after publishing.
- **Validation evidence:** Python syntax compilation and JavaScript syntax checking only. No live provider call or app-wired end-to-end validation was performed for these edits. Record actual focused synthetic results here; do not copy old harness results as app-wired evidence.
- **Open issues or owner returns:** fill in with exact stage and receiving owner.
- **Shawn acknowledgment:** pending — confirm reviewed contracts, connector-only scope, carried changes, and any returned lane-owned findings.

## Completion definition

The app shows a traceable synthetic request moving through applicable stages and any human pause, resumes only from a current authorized decision, and combines persisted results by exact case version. Only the deterministic application gate may commit a fully eligible Low routine outcome. Unsupported, sensitive, stale or abstained cases remain open with a clear human next step. Focused synthetic end-to-end validation remains required; no production data/integration is claimed.
