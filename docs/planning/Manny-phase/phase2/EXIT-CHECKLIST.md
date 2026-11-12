# Manny Phase 2 — Ordered Exit Checklist

**Current state (2026-11-08):** Manny's connected A0–A3 path, S-1.1 item connector, synthetic Auditor-resume path through A6, and local assigned-case authorization are implemented. Phase 2 **exit readiness remains estimated at 95%** as a planning estimate, not a test metric; Manny's approval of the 100-case labels and the subsequent scored evaluation remain open.

**Forecast rule:** Percentages below are cumulative expected Phase 2 exit readiness after each whole step passes, assuming no rework. They are not additive, and a passing unit test alone does not satisfy a gate.

## Step 1 — Complete Manny-owned Triage integration — expected readiness: 85%

Owner: **Manny**. Shawn is not a prerequisite for this implementation step.

- [x] Reconcile the working docs: S-1 (`TriageHandoff.item_scope`) and S-2 (`InputRef.content_digest`) were approved and merged in PR #9; the remaining shared gate is review of the connected handoff, not acceptance of those fields from scratch.
- [x] Wire the real Manny A0–A2 runtime through `CombinedWorkflowHarness.run_manny_connected` into the Knowledge receiver. Ordinary tests use fake clients; the harness never constructs a provider client or loads credentials.
- [x] Build Manny's connector from each validated linked Triage item to the merged item-scoped Knowledge handoff. Preserve parent/run/case version, stable item ID/index/count, exact source and category-evidence spans, category inference sources, Unknown urgency, attention references, and canonical content digest.
- [x] Keep unresolved/ambiguous items on the human Auditor path and the parent incomplete. Urgency remains Unknown at this boundary; the connector cannot set a band, override, SLA, or customer status. Attention remains a source-bound review cue; Under Investigation remains human-managed.
- [x] Add connected synthetic checks for single/multiple requests, unknown/ambiguous items, stale source, prompt injection, and safe fallback. Existing component tests cover dependency/conflict rejection. Verify zero ticket writes, external dispatch, and customer notifications.
- [x] Record the category vocabulary by the active synthetic policy snapshot and exact taxonomy digest. The 80-row catalog remains development examples, not labels or operational policy. The category vocabulary is not CDIT policy and does not establish operational SLAs.
- [x] Prepare 100 synthetic evaluation cases with draft expected labels and source expectations at `synthetic_data/evaluation_draft/v1/cases.json`. They are explicitly draft, unapproved, and unscored; no accuracy claim is made.

**After Step 1:** expected Phase 2 exit readiness is about **85%**. N1–N3 are complete; this does not close the shared receiver or label gates. The authenticated app/Auditor interface is now implemented in the local database/auth workstream, including assigned-case access.

## Step 2 — Receiver and shared-connection acceptance — expected readiness: 95%

Owners: **Manny for the connector; Shawn for her Knowledge receiver; Shared Lane for connection checks.** Start this review after Step 1 has a concrete connected path to inspect.

- [x] Shawn reviewed the connected receiver in PR #12 and accepted with findings: Knowledge receives the correct item text and preserves identity, parent, span, source/version, digest, and Auditor status without using category/urgency to bias retrieval. Manny's F-1/F-2 fixes are included in merged PR #12 at `a363724`.
- [x] Shared combined-harness checks cover item joins, stale-state rejection, safe failure routing, and Auditor-resume behavior across A3–A6. The focused connected integration set passed 58 tests; the full Python suite passed 689 tests after the local assignment work.
- [x] Manny fixed F-1 and F-2: normalize CRLF before checking the trusted synthetic taxonomy pin, and find the first configured attention literal separately within each item span. Focused regressions: 49 passed; full suite: 618 passed.
- [x] Normalize CRLF in the raw CASE-SCENARIOS fixtures used by the Manny Triage flow and development-example tests. Focused Triage modules: 40 passed; full suite: 618 passed (2026-11-08). Shawn's Windows checkout rerun remains to confirm the reported failures are resolved there.
- [x] Review and merge S-1.1 for F-3 attention-check state and F-4 taxonomy citation in PR #15; Manny's connector supplies item-specific values and exact taxonomy provenance.
- [x] Resolve the current receiver findings by ownership: Manny changed only his connector; Shawn's contract/receiver changes remain in her ownership. The combined receiver tests pass without changing Shawn's agent internals.
- [x] Set the synthetic labeling process: Manny is the single author, reviewer, and approver; no independent peer review or evaluator agent is claimed. The actual draft labels still require his review before scoring.

**After Step 2:** expected Phase 2 exit readiness is about **95%**. A blocked or rejected receiver review keeps this step open; it does not require stopping unrelated Manny-owned work before review begins.

## Step 3 — Human decisions, evidence, and Phase 2 exit review — expected readiness: 100%

Owners: **Manny/project lead for label approval and phase review; Manny for evaluation protocol and evidence.**

- [x] Finalize the synthetic evaluation protocol: claim classes and denominators, per-gate positive/negative counts, holdout handling, confidence method, and finite-set reporting limits are documented. The dataset remains draft until label approval.
- [x] Run the authorized 100-case synthetic live A0–A2 diagnostic on 2026-11-09 and retain the reconciled trace. It produced 45 validated model responses, 8 A1 stops, and 47 `semantic_result_unavailable` fallbacks; exact failed SDK-attempt count is not instrumented. This is a live diagnostic, not full-MAO execution or an approved score.
- [x] Record Manny's case-level adjudication: SYN-EVAL-068 and SYN-EVAL-070 are confirmed category failures against “Product how-to / documentation request”; both returned “Employment record copy.” This decision applies only to these two cases; global dataset approval remains false.
- [x] Record the remediation disposition for SYN-EVAL-068 and SYN-EVAL-070: deferred until after Phase 2 and excluded from this phase's exit gate by Manny's 2026-11-09 direction. Both remain confirmed failures, not passes; the original trace is unchanged. Reopen as post-Phase-2 follow-up with a new trace/version and regression evidence.
- [ ] Investigate/remediate the unexpected split/missing-item results and `semantic_result_unavailable` causes. Add regression evidence and report any retest under a new trace/version; do not overwrite the original 2026-11-09 results.
- [ ] Review and approve the 100-case expected labels/source expectations before scoring. Record Manny as label author/reviewer/approver; no real user/customer/employee records.
- [x] Record the historical smoke-trace limitation honestly: its original exact request body/hash was not captured and cannot be reconstructed. A user-authorized replacement call ran once on 2026-11-06 using the already pinned `claude-sonnet-5-5`; its prompt/request digests and usage are recorded. It safely returned Unknown category for Auditor review and remains unscored. See the linked trace report.
- [x] Run engineering integration checks with synthetic fixtures; retain their actual results and safe-fallback evidence. The connected test suite passed 58 tests. The full Python suite passed 717 tests after the evaluation metric correction on 2026-11-09. These are not model accuracy scores and do not replace the approved label-scoring run.
- [ ] Review all Phase 2 exit criteria against the PRD and update `Checklist.md` only where evidence is present. Phase 2 reaches 100% only when every required gate has evidence or an explicitly approved deferral.

**After Step 3:** expected Phase 2 exit readiness is **100% only if every non-deferred required gate has accepted evidence**. D-22 excludes only remediation of cases 068 and 070; the failures stay visible and do not count as passes. Any other open required gate keeps Phase 2 open; readiness is not rounded up.

## Direct decisions and handoffs

### Manny / project lead

- **No new ticket taxonomy or tier decision is requested here.** Use the already discussed category set and Low/Medium/High, P1 attention, Unknown-to-Auditor, and Under Investigation rules. Actual operational SLA thresholds and override authority remain deferred under D-01 and do not become guarantees in this synthetic prototype.
- Approve the final expected labels for the 100 synthetic cases before they are scored.
- The replacement synthetic call was authorized and completed with the existing `claude-sonnet-5-5` pin. Anthropic's current model status page lists it as Active, with retirement not sooner than September 28, 2027. No model-pin change is needed.
- Review the evidence and declare Phase 2 accepted only when the gates above are met.

### Shawn

- No action is needed before Manny continues Step 1.
- At Step 2, Shawn reviews the real connected item handoff as the Knowledge receiver. Manny alone owns synthetic label authoring, review, and approval for this assignment.
- If a finding requires changing her agents' internals, she owns that implementation; Manny only fixes his connector and shared boundary.

### Deferred and not Phase 2 blockers

- The Staff/Admin Auditor form and synthetic decision history use the assigned-case model: Staff can access only assigned cases; Admin can access/assign all; assignment history records Admin actions; Admin decisions require an override reason. API tests pass. Manual browser/accessibility review remains open.
- Production authentication, real company policy/data, live Salesforce, ticket writes, email, customer notifications, and third-party dispatch remain out of scope.
- Phase 3 and Phase 4 have their own acceptance gates; Phase 2 completion does not mark those phases complete.
