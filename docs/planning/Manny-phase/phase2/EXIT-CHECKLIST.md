# Manny Phase 2 — Ordered Exit Checklist

**Current state (2026-11-08):** Manny's connected A0–A3 harness and N1–N3 synthetic verification are complete. Phase 2 **exit readiness is estimated at 85%**. This is a planning estimate, not a test metric; receiver acceptance, evaluation labels, and complete semantic evaluation evidence remain open.

**Forecast rule:** Percentages below are cumulative expected Phase 2 exit readiness after each whole step passes, assuming no rework. They are not additive, and a passing unit test alone does not satisfy a gate.

## Step 1 — Complete Manny-owned Triage integration — expected readiness: 85%

Owner: **Manny**. Shawn is not a prerequisite for this implementation step.

- [x] Reconcile the working docs: S-1 (`TriageHandoff.item_scope`) and S-2 (`InputRef.content_digest`) were approved and merged in PR #9; the remaining shared gate is review of the connected handoff, not acceptance of those fields from scratch.
- [x] Wire the real Manny A0–A2 runtime through `CombinedWorkflowHarness.run_manny_connected` into the Knowledge receiver. Ordinary tests use fake clients; the harness never constructs a provider client or loads credentials.
- [x] Build Manny's connector from each validated linked Triage item to the merged item-scoped Knowledge handoff. Preserve parent/run/case version, stable item ID/index/count, exact source and category-evidence spans, category inference sources, Unknown urgency, attention references, and canonical content digest.
- [x] Keep unresolved/ambiguous items on the human Auditor path and the parent incomplete. Urgency remains Unknown at this boundary; the connector cannot set a band, override, SLA, or customer status. Attention remains a source-bound review cue; Under Investigation remains human-managed.
- [x] Add connected synthetic checks for single/multiple requests, unknown/ambiguous items, stale source, prompt injection, and safe fallback. Existing component tests cover dependency/conflict rejection. Verify zero ticket writes, external dispatch, and customer notifications.
- [x] Record the category vocabulary by the active synthetic policy snapshot and exact taxonomy digest. The 80-row catalog remains development examples, not labels or operational policy. The category vocabulary is not CDIT policy and does not establish operational SLAs.
- [ ] Prepare the 100-case evaluation set and draft labels in parallel if useful, but do not score it as approved evidence until the review/approval step below.

**After Step 1:** expected Phase 2 exit readiness is about **85%**. N1–N3 are complete; this does not close the shared receiver or label gates. The authenticated app/Auditor interface remains deferred until database/auth work.

## Step 2 — Receiver and shared-connection acceptance — expected readiness: 95%

Owners: **Manny for the connector; Shawn for her Knowledge receiver; Shared Lane for connection checks.** Start this review after Step 1 has a concrete connected path to inspect.

- [x] Shawn reviewed the connected receiver in PR #12 and accepted with findings: Knowledge receives the correct item text and preserves identity, parent, span, source/version, digest, and Auditor status without using category/urgency to bias retrieval. Manny's F-1/F-2 fixes are included in merged PR #12 at `a363724`.
- [ ] Shared checks schema/version integrity, acknowledgements, item joins, stale-state rejection, failure routing, and end-to-end handoff behavior.
- [x] Manny fixed F-1 and F-2: normalize CRLF before checking the trusted synthetic taxonomy pin, and find the first configured attention literal separately within each item span. Focused regressions: 49 passed; full suite: 618 passed.
- [x] Normalize CRLF in the raw CASE-SCENARIOS fixtures used by the Manny Triage flow and development-example tests. Focused Triage modules: 40 passed; full suite: 618 passed (2026-11-08). Shawn's Windows checkout rerun remains to confirm the reported failures are resolved there.
- [ ] Review proposed shared S-1.1 treatment for F-3 (distinguish `flagged`, `none_found`, and `not_assessed`) and F-4 (taxonomy source citation). No shared contract change is made until the project lead approves the proposal.
- [ ] Resolve any remaining findings by ownership: Manny fixes Coordinator/Triage/connector defects; Shawn fixes Knowledge/Troubleshooting/Documentation behavior in her lane. Do not edit her agent internals from Manny's lane.
- [ ] Shawn or another project teammate peer-reviews the synthetic labels/results as required by the evaluation protocol; Manny remains the label owner and approver.

**After Step 2:** expected Phase 2 exit readiness is about **95%**. A blocked or rejected receiver review keeps this step open; it does not require stopping unrelated Manny-owned work before review begins.

## Step 3 — Human decisions, evidence, and Phase 2 exit review — expected readiness: 100%

Owners: **Manny/project lead for label approval and phase review; Manny for evaluation protocol and evidence.**

- [ ] Finalize the synthetic evaluation protocol: claim classes and denominators, minimum positive/negative counts per gate, holdout handling, confidence method, and reporting limits. Report results as applying to the tested set only.
- [ ] Complete the 100-case synthetic set and obtain Manny's approval of expected labels before scoring. Keep the case author, label approver, and peer reviewer recorded; no real user/customer/employee records.
- [x] Record the historical smoke-trace limitation honestly: its original exact request body/hash was not captured and cannot be reconstructed. A user-authorized replacement call ran once on 2026-11-06 using the already pinned `claude-sonnet-5-5`; its prompt/request digests and usage are recorded. It safely returned Unknown category for Auditor review and remains unscored. See the linked trace report.
- [ ] Run the approved, integrated synthetic Phase 2 checks; retain actual pass/fail counts, failures, trace IDs, source/policy versions, and safe-fallback evidence. Do not report preliminary fixture assertions as model accuracy.
- [ ] Review all Phase 2 exit criteria against the PRD and update `Checklist.md` only where evidence is present. Phase 2 reaches 100% only when every required gate has evidence or an explicitly approved deferral.

**After Step 3:** expected Phase 2 exit readiness is **100% only if all required evidence is accepted**. A deferred or failed required gate means Phase 2 remains open; it is not rounded up.

## Direct decisions and handoffs

### Manny / project lead

- **No new ticket taxonomy or tier decision is requested here.** Use the already discussed category set and Low/Medium/High, P1 attention, Unknown-to-Auditor, and Under Investigation rules. Actual operational SLA thresholds and override authority remain deferred under D-01 and do not become guarantees in this synthetic prototype.
- Approve the final expected labels for the 100 synthetic cases before they are scored.
- The replacement synthetic call was authorized and completed with the existing `claude-sonnet-5-5` pin. Anthropic's current model status page lists it as Active, with retirement not sooner than September 28, 2027. No model-pin change is needed.
- Review the evidence and declare Phase 2 accepted only when the gates above are met.

### Shawn

- No action is needed before Manny continues Step 1.
- At Step 2, review the real connected item handoff as the Knowledge receiver and peer-review synthetic labels/results (or identify another project teammate to do that review).
- If a finding requires changing her agents' internals, she owns that implementation; Manny only fixes his connector and shared boundary.

### Deferred and not Phase 2 blockers

- Auditor UI and authenticated review/recording flow remain deferred until database/auth work.
- Production authentication, real company policy/data, live Salesforce, ticket writes, email, customer notifications, and third-party dispatch remain out of scope.
- Phase 3 and Phase 4 have their own acceptance gates; Phase 2 completion does not mark those phases complete.
