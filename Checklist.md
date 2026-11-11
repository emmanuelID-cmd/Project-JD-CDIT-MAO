# Project Completion and Lane Checklist

Use this checklist as the live project status record. Check an item only when its evidence is present and reviewed. Planning completion is not implementation completion; an unchecked item blocks a completion claim unless the project lead explicitly marks it out of scope or deferred.

**Current phase:** Manny Phase 2 connected Triage path is implemented; exit remains open pending the single-owner label sign-off and source-grounded evaluation. Phase 3 integration and Shared workflow harness are implemented and validated on synthetic fixtures. PRD-v4 is the current requirements source.
**Planning deadline:** November 11, 2026
**Current implementation status (2026-11-09):** SQLite foundation, local synthetic User/Staff/Admin authentication, role routes/previews, Staff/Admin Auditor review, and case-assignment authorization are implemented. Full Python suite: 689 passed; evaluation-draft validator: 5 passed; focused assignment/auth/auditor/lifecycle tests: 23 passed; JavaScript syntax and `git diff --check` pass. Manual browser/accessibility review remains open. The 100-case draft is still unapproved and unscored. Current draft validator: 5/5 passed; targeted deterministic retrieval probe: stale source, both conflict sources, and the planted-injection article were retrieved as expected. These checks do not approve labels or close Phase 2/4 scoring gates.
**Current case-lifecycle update:** Seeded demo cases are assigned to `SYN-STAFF-001`; new User requests remain unassigned until Admin assigns them. Staff case access is restricted server-side to assigned cases; Admin sees all and can assign/reassign. User view remains scoped to the requester's own requests; agent writes remain disabled. Browser/accessibility review remains open.
**Antigravity provenance:** The project lead confirms Antigravity only merged PR #6; all other completion/work claims in its handoff are false. Existing repository artifacts are tracked separately and are not attributed to Antigravity.
**Completion status:** In progress; do not claim project completion or begin release workflow.

## Current phase evidence — 2026-11-08

- Manny's linked-item connector now carries S-1.1 attention-check states and the item's taxonomy source. Shawn's S-1.1 contract change is merged in PR #15. The combined synthetic harness resumes Auditor-reviewed items through Knowledge, Troubleshooting, Escalation (A5), and Documentation (A6); Unknown/ambiguous items and stale inputs fail closed.
- Phase 2/3/shared integration checks: 58 focused tests passed across the combined workflow, escalation, connected Triage, and Knowledge receiver suites. The latest full Python suite passed 689 tests.
- Phase 4 has a 100-case synthetic evaluation draft. Manny-lane preparation now removes scenario markers from ticket text, pins `evaluation_as_of` to `2026-11-10`, replaces placeholder source IDs with Shawn's reviewed mappings, makes stale/conflict requests concrete, and makes linked conflict items eligible for Knowledge while urgency remains Unknown. Cases remain `DRAFT_NOT_APPROVED` and unscored. Manny is the single label author/reviewer/approver; the batch label/source-expectation sign-off remains open. Proposed Shawn fixtures and `SYN-TS-POLICY` are not active runtime evidence until accepted and merged. No independent peer review or evaluator agent is claimed.
- The Auditor interface reuses Staff/Admin access with case-level authorization: Staff may access only assigned cases, while Admin can see and assign all cases. Assignment/reassignment actor, prior/new assignee, and timestamp are recorded; Admin Auditor decisions require a reason. Focused tests cover role denial and reassignment visibility. Manual browser/accessibility review remains open.
- No new decision is needed to retain the current synthetic/propose-only behavior or the already-agreed category, Unknown-to-Auditor, and inferred-category-with-Unknown-urgency routing rules. Manny's remaining decision is one batch approval of the 100 case-level label and source expectations. Shawn's proposed source fixtures/policy must be available and accepted before the full grounding/retrieval gate can be scored. Manual browser/accessibility review also remains pending.

## Shared project baseline

- [x] PRD-v4 defines the authenticated local User/Staff/Admin app, SQLite foundation, minimal Product Health metadata, and separate unauthenticated role showcase.
- [x] Local SQL planning branch `manny/sql-foundation` created from Manny lane commit `a363724`; SQL and connected Manny branches are locally aligned at `4486a02` before this assignment feature, with no unique branch commits created.
- [x] Implement initial SQLite v1 migration for synthetic accounts, sessions, cases, app-only Product Health events/summaries, Admin access audit events, and session extension alerts; include constraints, indexes, checksum migration tracking, seed/reset, and retention purge. Cross-agent workflow/evaluation persistence remains separate pending boundary review.
- [x] Implement local synthetic authentication and server-side User/Staff/Admin authorization under Manny; verify direct page/API denial and Admin audit events. Approved session and retention rules are specified in PRD-v4.
- [x] Build the separate three-view no-login showcase using fabricated static data and inert privileged controls.
- [x] Seed and show all 80 CASE-SCENARIOS entries as Staff/Admin-only development examples, kept separate from User requests and gold evaluation labels; API role visibility checks pass.
- [x] Verify Staff edits/status/Auditor decisions are limited to assigned cases; Admin can see all and assign/reassign/unassign only to active Staff; assignment events record actor, old/new assignee, and timestamp; requester ownership remains separate. Assignment API tests pass.
- [x] Verify Admin override reason is required and stored for Admin Auditor decisions; Staff cannot submit an override reason.
- [x] Verify Staff/Admin human edits and allowed status changes are audited with bounded metadata; verify User own-request edit only while Submitted, In Progress display as In Review, post-transition edit denial, and unresolved cancellation; lifecycle API tests pass.
- [x] Confirm agent authority remains read-only while Staff/Admin human case management is enabled; [ ] manual browser/accessibility review remains open.
- [x] Verify auth/API boundaries, user case scoping, Admin audit and session controls, SQL parameter handling, and static preview isolation in focused synthetic tests. Product Health schema remains bounded and existing database tests cover retention and prohibited fields.
- [ ] Complete manual keyboard/screen-reader and responsive browser review; exercise database-unavailable recovery in the running UI.

- [x] PRD is the current requirements source and includes milestones, agent gates, confidence/factuality, prompt-injection controls, case authority, blackboard state, and handoffs.
- [x] PRD-v3 is retained as the historical prior requirements version; PRD-v4 is the current project baseline, approved 2026-11-08.
- [x] The project lead approved `PRD-v4.md` as the current synthetic-prototype requirements source; dated PRD-v3 decisions remain historical.
- [x] User Needs and prioritized use cases have a linked companion file.
- [x] Synthetic evaluation and routing examples are in `docs/requirements/CASE-SCENARIOS.md`.
- [x] Deferred policy and implementation decisions are tracked in `docs/planning/DEFERRED-DECISIONS.md`.
- [x] Synthetic account model recorded as User (client view), Staff (back-end view), and Admin (same back-end plus privileged account/access controls); no extra staff tiers or interfaces.
- [x] Product Health/evaluation scope recorded as synthetic metadata and fixtures only; no real customer records or real-world interview/activity.
- [x] The updated field guide includes the interactive PRD-v3 architecture diagram; the PRD-v2 sketch remains available as a standalone historical artifact.
- [ ] Team reviews and accepts the PRD, agent ownership, interfaces, and current scope.
- [ ] All planning milestone exit evidence and decisions are recorded.
- [x] Project lead explicitly authorized the local technology-stack foundation scaffold on 2026-11-03.
- [x] Project lead authorized Manny’s synthetic-lane phase sequence beyond the local scaffold on 2026-11-04; production and real-data work remain unauthorized.
- [x] Agent build, injection-risk, harness, and integration phase plan recorded in [`AGENT-IMPLEMENTATION-PHASE-PLAN.md`](docs/planning/AGENT-IMPLEMENTATION-PHASE-PLAN.md).
- [x] Standalone proposal for additions to the implementation phase plan recorded in [`AGENT-IMPLEMENTATION-PHASE-ADDITIONS.md`](docs/planning/AGENT-IMPLEMENTATION-PHASE-ADDITIONS.md); the current plan remains unchanged pending review.
- [x] Standalone Claude critique and PRD-v2 correction plan recorded in [`PRD-V2-CLAUDE-CRITIQUE-PLAN.md`](docs/planning/PRD-V2-CLAUDE-CRITIQUE-PLAN.md); the current PRD remains unchanged pending review.
- [x] PRD v2 assessment and lane-specific phase guides recorded in [PHASE-PLAN-INDEX.md](docs/planning/PHASE-PLAN-INDEX.md); Manny's guide is his obligation, Shawn's is voluntary, and neither authorizes implementation.

## Shared foundation scaffold

- [x] Python 3.13 package metadata and FastAPI/Pydantic dependencies are configured.
- [x] FastAPI health endpoint and local SQLite connection helper are scaffolded.
- [x] Local setup instructions and synthetic-data configuration example are documented.
- [ ] Agree and implement domain schemas, authentication, and audit/retention behavior before adding those capabilities.
- [x] Install project dependencies in the local Python 3.13 virtual environment.
- [x] Start the local service and confirm the health endpoint on the contributor machine. (2026-11-04, Shawn's machine: Python 3.13.17, `GET /health` returned 200 `{"status":"ok","database":"ok"}`.)

## Manny lane — Coordinator, Triage, Escalation

- [x] Confirm owner availability and accept the Coordinator, Triage, and Escalation assignment (Manny’s approved lane sequence).
- [x] Manny Phase 1: implement and review the process-local synthetic A0/A1 fixture boundary and versioned handoff; Shared receiver review remains an integration gate.
- [x] Phase 2 local Triage input boundary, conservative linked-item segmentation, unknown/Auditor proposals, source-span checks, and linked-item Knowledge connector are implemented; these components do not alone constitute Phase 2 exit.
- [x] Add exact 80-row development-example references to linked items as unverified IDs; the match does not classify category or urgency, and ambiguous segmentation receives no reference. Focused checks: 30 passed; full synthetic-only suite after current Phase 2 changes: 463 passed.
- [x] Select and document Anthropic Claude Sonnet 5.5 (`claude-sonnet-5-5`) for synthetic Triage. The local ignored `.env` was configured by the user. Two one-attempt authorized synthetic smoke calls are recorded; the 2026-11-06 call uses the connected harness and its output remains unscored. No key value is stored in this checklist.
- [x] Add a provider-free semantic output validator for category inference, exact source quotes, and forced Unknown urgency/destination; no model call or shared-contract change. Full synthetic-only suite: 463 passed.
- [x] Add a synthetic-only Anthropic client adapter boundary with per-run billable authorization, immediate handoff preflight, retry disabled, provisional 60-second timeout, injection-as-data handling, and strict output validation; prepare minimized item requests and block ambiguous segmentation before provider use. Pin/install Anthropic SDK 2.5.0 and python-dotenv 1.2.4; the ignored `.env` is local-only. One synthetic API smoke call is recorded; see its trace report for limits.
- [x] Decide the model alias/snapshot and regression policy with Shared Lane before model-backed evaluation (D-20); SDK 2.5.0 and dotenv 1.2.4 are pinned.
- [x] Define and implement Coordinator behavior, tools, schemas, internal validation, stop conditions, retries, and recovery from the current PRD.
- [x] Implement the approved Triage behavior: independently classify separable requests, preserve exact source spans, keep categories as inference, send Unknown/ambiguous items to the Auditor, and attach item attention-check results. The item-scoped connector uses the merged S-1.1 contract and taxonomy provenance. Attention remains a review cue, not a live risk detector or operational urgency policy. Operational urgency/destination remain Unknown until the human Auditor decides.
- [x] Add `run_triage_runtime` as a callable boundary over acknowledged Coordinator input; fake-client tests verify source-bound candidates, Unknown urgency/destination, mandatory human review, and no downstream/dispatch. The function does not construct a client or load credentials.
- [x] Build `MannyA0A2Harness` to run synthetic Coordinator intake through acknowledged Triage. It accepts only an injected client, leaves billable-call authorization false by default, stops before Knowledge/Shared, and records metadata-only handoff events. Focused tests verify no-call fallback and a fake-client A2 proposal.
- [x] Add `SYN-MANNY-TRIAGE-0001`, a user-approved Unknown-severity/possible-major-impact contract case. The A0–A2 fake-client run preserves Unknown, human review, source-bound attention, and no dispatch. It is not a gold label or model-accuracy score.
- [x] Attach the optional source-bound synthetic attention signal to Triage runtime results. It carries exact message offsets and a human-context note; a match does not verify an incident or urgency, and no match remains not assessed. Validate source/span/context and recheck the handoff before returning; stale snapshots fall back without a signal. Focused boundary tests cover match/no-match, tampering, and cancellation.
- [x] Align runtime documentation and tests with both stale-handoff windows: stale before candidate creation raises; a stale state detected during semantic preflight returns human review without a provider call. The runtime uses the existing synthetic category vocabulary with source/version provenance; the 80 case texts, bands, and conditions are not model labels.
- [x] Fail closed to `needs_human_review` when a provider result passes its schema but fails Manny's linked-item binding validation; preserve the unbound candidate and suppress the semantic result. Focused fake-client regression covered; no provider call or Shared contract change.
- [x] Future synthetic Triage call results carry a stable prompt ID and SHA-256 hashes for the source prompt and exact serialized request body; do not retain raw prompt/request or key in result metadata. Fake-client tests verify the recorded digest equals the exact body sent. This cannot retroactively recover the prior smoke call's missing body hash.
- [x] Add a retrospective smoke-trace addendum reconciling the fixture alias from exact text equality and recording the source-backed system-prompt hash; the historical request body/hash was not captured and remains unresolved.
- [x] Wire the local A0–A2 runtime through the merged S-1/S-2 item-scoped contract into `CombinedWorkflowHarness.run_manny_connected` and the actual Knowledge receiver. Synthetic checks cover single/multiple items, unknown/ambiguous routing, stale-source rejection, prompt-injection stop, identity/span/digest joins, mandatory human review, and zero external side effects. Unknown urgency keeps Troubleshooting/Documentation behind the Auditor gate; this is not a production API endpoint or authenticated app flow.
- [x] Define and implement Escalation behavior, must-escalate checks, evidence packet, uncertainty handling, and human routing.
- [x] Validate each owned agent independently against its own prompt, tools, permissions, and failure gates.
- [x] Publish versioned input/output contracts and handoff examples for the connection points.
- [x] Fix agent-internal failures found in this lane; do not modify Shawn-owned agent functionality.

### Manny Phase 2 trace checkpoint — 2026-11-05

- [x] Run one explicitly authorized synthetic Claude adapter smoke trace; record usage, latency, output, and cost.
- [x] Record independent Reviewer A/B reconciliation and scoped SECURITY review.
- [ ] Resolve historical smoke-trace provenance gaps: bind SYN-CASE-01 to SYN-TRACE-001 and record that the original exact request body was not captured; keep it excluded from acceptance evidence. The authorized replacement call ran on 2026-11-06 using the active pinned `claude-sonnet-5-5`; its own prompt/request digests and usage are recorded in `docs/temp/trace/Trace-2026-11-06-Synthetic-Connected-Triage-Smoke.md`. Its Unknown category remains unscored and does not reconstruct the earlier trace.

- [ ] Obtain Manny's approved semantic label for the smoke fixture; until then, its classification correctness remains unverified.
- [x] Draft the Manny-owned connection proposal for Shared Lane review in [TRIAGE-LINKED-ITEM-HANDOFF-PROPOSAL.md](docs/lanes/manny/TRIAGE-LINKED-ITEM-HANDOFF-PROPOSAL.md); this does not change or accept the shared contract.
- [x] Receiver/shared gate: PR #12 receiver findings were fixed; PR #15 merged the S-1.1 contract. The connected harness checks item identity, spans, taxonomy evidence, digest joins, stale-state rejection, Auditor resume, and downstream A4/A5/A6 behavior. Focused combined integration set: 58 passed; no Shawn-owned agent internals were changed.
- [ ] Run and retain the app-wired Coordinator-to-Triage plus downstream integration/security cases after the shared handoff shape is accepted; the one-call Triage smoke did not exercise this workflow.
- [x] Manny adjudicated the live Triage category outputs for SYN-EVAL-068 and SYN-EVAL-070 as failures against the expected “Product how-to / documentation request” category; the observed proposal was “Employment record copy.” This is a case-level decision and does not approve the remaining draft labels.
- [x] Record remediation of SYN-EVAL-068 and SYN-EVAL-070 as deferred until after Phase 2, per Manny's 2026-11-09 direction. Both remain confirmed failures in the immutable trace; deferral is not a pass and does not approve other labels. Excluded from the Phase 2 exit gate; reopen post-Phase-2 with a new trace/version and regression evidence.
- [ ] At project completion, run 100 sequential synthetic-only traces; retain pass and failure evidence and stay within the available $40 budget.
- [x] PR #6 was merged into `developer` (merge commit `8499f85`). The merge itself is the only Antigravity action confirmed by the project lead; do not treat the merge as evidence that Antigravity performed or validated the implementation work described in its handoff.
- [ ] Verify PR #6 checks/review and any claimed conflict-resolution work from source records; the earlier “CONFLICTING / DIRTY” note is historical and is not current status.
- [ ] Fast-forward any remaining non-main branches only after checking ancestry, cleanliness, and the current remote state.

### Manny Phase 3 — Escalation status

- [x] EscalationAgent implementation and focused tests exist. Unknown urgency routes to human Auditor review without assigning a band; attention evidence is preserved only after live A1 registry validation, with pattern ID/span provenance; a verified current Under Investigation fact remains human-managed, with no autonomous status change or third-party contact and P1 precedence preserved. Focused suite: 29 passed; full Python 3.13.15 suite: 615 passed. Integrated Phase 3 acceptance remains open.
- [x] Bind A5 recorded-action evidence to the current synthetic case/version before it can be labeled verified; preserve source references on unresolved questions. This does not establish production authentication or replace Shared review.
- [x] Phase 3 integration check: the combined harness passes an Auditor-resolved item through A3/A4/A5/A6 and verifies same-item provenance, P1 escalation, and safe stop behavior. Focused combined integration set: 58 passed; latest full Python suite: 689 passed. Final phase acceptance review remains recorded separately from this test result.

### Manny Phase 4 — Evaluation status

- [x] Synthetic evaluation runner and generated report/JSON artifacts exist.
- [x] Preliminary runner evidence exists for 9 Coordinator checks, 3 benchmark fixtures, 4 Escalation rules, and 12 downstream fixture cases. The runner now compares every downstream result with its case file expected output; 12/12 fixture assertions match. These are engineering-fixture checks, not approved gold labels. The CLI regression asserts exit code 2 and `not_scored`/not-ready status when only preliminary fixtures pass. Focused evaluation and case-harness tests: 22 passed; the full Python suite: 615 passed. No evaluation labels have been scored.
- [ ] Phase 4 acceptance: a 100-case synthetic draft now exists at `synthetic_data/evaluation_draft/v1/cases.json`; it is not approved or scored. Manny must approve the expected labels/source expectations before the evaluator scores it. The combined harness has synthetic fixture coverage but does not prove real-world performance.

**Snapshot comparison:** commit `3138388` (2026-11-05 15:15) recorded Phase 2 active and Phase 3/4 outstanding. Commit `9a2d3f4` later added Escalation code and the fixture harness; commit `37c01c8` added the evaluation runner/report. Those artifacts are retained; their presence does not by itself satisfy phase acceptance.

### Auditor interface scope

- [x] The local Staff/Admin Auditor form and append-only synthetic decision history are implemented and tested. It does not change ticket status, send external messages, or dispatch a third party.
- [ ] Manual browser/accessibility review remains open. Assigned-case authorization is implemented and API-tested; this does not replace the manual UI review.

## Shawn lane — Knowledge, Troubleshooting, Documentation

> 2026-11-04 status: PR #2 merged into `developer` at `a14bb8d` with code for all three Shawn agents, a lane harness, 12 synthetic cases, 97 tests, and `0.1.0-proposed` contracts/examples; PR #4 merged the follow-up into `developer` at `4deafe7` (110 tests and 12 lane cases passed on Python 3.13.17; 111-case synthetic Knowledge calibration set with 0 critical errors). PR #5 merged into `developer` at `10168a2`: PRD-v3 alignment review (`docs/lanes/shawn/PRD-V3-ALIGNMENT-REVIEW.md`) and B-01 fix (Troubleshooting 0.1.1 with policy 0.1.1; 125 tests pass). PR #7 merged N-02 and N-03 at `ff8dc76`; PR #8 merged the A2 receiver review at `3583508`. Project PR #9 merged into `developer` at `1085d20` on 2026-11-06, adding S-1 (`TriageHandoff.item_scope`), S-2 (`InputRef.content_digest`), Shawn agents `0.2.0`, five synthetic item cases, and 43 item-scope tests. Manny approved S-1/S-2 and chose Q-E Option B; PR validation reports 567 tests passed. This establishes code presence, not final lane acceptance or end-to-end linked-item integration. The calibration labels remain drafts pending Manny's explicit approval. Code presence is tracked separately from authorization, acceptance, and validation below.

- [x] Confirm owner availability and accept the three-agent assignment (Shawn's lane-owner direction is recorded in `docs/planning/DEFERRED-DECISIONS.md`).
- [x] Knowledge implementation files are present in merged PR #2 (`src/cdit_support_mao/agents/knowledge/`); acceptance remains pending.
- [x] Troubleshooting implementation files are present in merged PR #2 (`src/cdit_support_mao/agents/troubleshooting/`); acceptance remains pending.
- [x] Documentation implementation files are present in merged PR #2 (`src/cdit_support_mao/agents/documentation/`); acceptance remains pending.
- [x] Versioned `0.1.0-proposed` contracts and synthetic handoff examples are published in `docs/contracts/`; Shared Lane acceptance remains pending.
- [x] Project lead authorizes this agent implementation phase beyond the local scaffold.
- [ ] Review and accept each agent against PRD A3/A4/A6 and the approved shared contract. The lane review record still marks acceptance pending.
- [x] Validate each agent independently on Python 3.13 against prompts, tools, permissions, evidence, and failure gates.
- [x] Fix agent-internal findings in Shawn's lane; do not modify Manny-owned agent functionality.

## Shared connection and integration work

- [x] Agree blackboard fields, identifiers, versioning, provenance, confidence, uncertainty, and state lifecycle.
- [x] Connect Coordinator → semantic Triage → item-scoped Knowledge and exercise the Auditor-resume path through Troubleshooting, Escalation, and Documentation. The synthetic harness uses fake model output and a human Auditor fixture; it does not claim live model accuracy.
- [x] Exercise Knowledge → Troubleshooting → Escalation/Documentation in the current downstream fixture harness.
- [x] Provide the local Staff/Admin Auditor decision form and append-only synthetic decision history; enforce assigned-case scope for Staff and Admin override reason. Manual browser/accessibility review remains open.
- [x] Verify the current single-case fixture connectors preserve case/run/policy/source versions, evidence labels, timestamps, status, and uncertainty without mutation. This does not test linked-item scope.
- [x] Verify linked-item connectors preserve parent/item IDs, source spans, and per-item evidence/status without mutation; 58 focused connected tests pass.
- [x] Test direct pipeline, permitted joins, stale results, linked-item identity, and safe stop/manual fallback in the connected synthetic harness; 58 focused connected tests pass. Coverage remains fixture-based, not real-world performance evidence.
- [x] Verify cross-lane connectors only; agent prompts, tools, decision logic, and behavior remain with their owners.
- [x] Represent mandatory human review and proposed escalation in the handoff contracts. This is contract/output evidence only; no reviewer UI or notification delivery exists.
- [x] Record integration defects and return agent-internal fixes to the owning lane; no cross-lane functionality edits.

## Pending decisions / unassigned

- [x] Decide whether to add the optional second-reviewer agent; if approved, assign an owner before work begins (retained as unapproved optional per AGENTS.md).
- [x] Confirm whether authenticated client-to-developer platform issue reporting is in project scope; keep disabled/optional until scope is confirmed and all submitters are authenticated (D-17 deferred).
- [ ] Operational urgency bands, routing groupings, thresholds, SLA clocks, and overrides remain open under D-01. The approved P1/P2/P3 elapsed-time values are non-guaranteed follow-up benchmarks, not routing policy or SLA guarantees.
- [x] Resolve future-use items separately before expanding beyond the synthetic read-only prototype: write authority/state transitions, production data and integrations, and applicable storage, retention, and audit controls (D-11, D-12, D-18 recorded in DEFERRED-DECISIONS.md).
- [x] Record CDIT data/source, security, privacy, hosting, model-provider, and production integration approvals as prerequisites before any production or sensitive-data work; no such approval is assumed for this synthetic prototype.
- [x] Assign any new agent or workstream explicitly; unassigned work stays pending or is assigned to the user by explicit direction, never silently shared.

## Release / project completion gate

- [ ] All P0 requirements and safety constraints are implemented and evidenced, or explicitly deferred by the project lead. The evaluation-label approval/scoring gate and manual browser/accessibility review remain open.
- [ ] Agent-level confidence, hallucination, prompt-injection, permission, failure-state, and recovery evaluations pass their approved gates. Synthetic integration tests pass; the 100-case labels remain unapproved and unscored.
- [x] End-to-end synthetic handoffs, linked-item provenance, stale-state stops, and human Auditor resume are exercised by the combined harness. This does not prove production persistence or real-world accuracy.
- [x] App-wired synthetic resume (2026-11-11): an Auditor decision saved in the authenticated app runs Knowledge, Troubleshooting, Escalation and Documentation and shows them on the case-version timeline, including after a Knowledge abstention. 773 tests passed. One live Claude Triage call through the app is still to be recorded; see `docs/planning/ACTIONRELAY-END-TO-END-WIRING-HANDOFF.md`.
- [ ] Documentation, known limitations, open decisions, and lane ownership are current and reconciled before project closeout.
- [ ] Project lead explicitly confirms the project is complete or directs a merge to `main`.
- [ ] Only after that direction, complete the authorized merge/release workflow. Never infer permission from checklist progress alone.

## Cross-lane visual UI allowance

- [ ] Either lane may add or restyle presentation controls such as Submit/Save when they invoke existing approved behavior without changing its semantics.
- [ ] UI updates follow the Consistency Page skill and are checked across the canonical page, related tabs/routes, and responsive viewports.
- [ ] Verify controls preserve existing behavior. Removing or bypassing an agent handoff, capability, policy, permission, state transition, or PRD requirement is prohibited cross-lane functionality work.

## Branch and release checklist

- [ ] Each contributor works and pushes only to their own lane branch.
- [ ] Cross-lane edits are limited to agreed connection/interface work and approved visual-only UI changes.
- [ ] Contributor changes are reviewed into `developer` by pull request.
- [ ] Do not merge to `main` until the project is complete and the user explicitly authorizes the release; if completion is unclear, ask.
- [ ] Keep `developer` and owner lanes current only through verified fast-forward updates; never overwrite unique commits.`n
