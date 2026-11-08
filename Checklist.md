# Project Completion and Lane Checklist

Use this checklist as the live project status record. Check an item only when its evidence is present and reviewed. Planning completion is not implementation completion; an unchecked item blocks a completion claim unless the project lead explicitly marks it out of scope or deferred.

**Current phase:** Manny Phase 2 — Triage in progress; Phase 2 exit gates remain open.
**Planning deadline:** November 11, 2026
**Current implementation status:** The Python 3.13.15 full synthetic-only suite passes 618 tests (2026-11-08). Phase 2 connects Coordinator to Triage to item-scoped Knowledge in `CombinedWorkflowHarness.run_manny_connected` while preserving item identity/span/digest, inference evidence, Unknown urgency, human review, and parent-incomplete status. Shawn's PR #12 receiver review accepted with findings; Manny fixed F-1 (CRLF-sensitive source hash) and F-2 (attention limited to the first matching item) in commit `122d44b`, with focused regression coverage. Updated PR review remains pending. N1-N3 are complete at an estimated 85% Phase 2 exit readiness. Shared connection acceptance, Manny-approved evaluation labels, and complete Phase 2 evidence remain open. The replacement Sonnet 5.5 smoke call returned Unknown for Auditor review and remains unscored. Phase 3 integration and Phase 4 full evaluation acceptance remain pending; the Auditor interface/auth flow remains deferred.
**Antigravity provenance:** The project lead confirms Antigravity only merged PR #6; all other completion/work claims in its handoff are false. Existing repository artifacts are tracked separately and are not attributed to Antigravity.
**Completion status:** In progress; do not claim project completion or begin release workflow.

## Shared project baseline

- [x] PRD is the current requirements source and includes milestones, agent gates, confidence/factuality, prompt-injection controls, case authority, blackboard state, and handoffs.
- [x] PRD-v2 is retained for history; the project lead selected PRD-v3 as Manny’s lane baseline.
- [x] The project lead approved `PRD-v3.md` as Manny’s synthetic-lane build baseline; team-wide review remains pending.
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
- [x] Phase 2 local Triage input boundary, conservative linked-item segmentation, unknown/Auditor proposals, and source-span checks are implemented; these components do not constitute Phase 2 exit. Human dispatch and UI remain deferred to database/auth setup.
- [x] Add exact 80-row development-example references to linked items as unverified IDs; the match does not classify category or urgency, and ambiguous segmentation receives no reference. Focused checks: 30 passed; full synthetic-only suite after current Phase 2 changes: 463 passed.
- [x] Select and document Anthropic Claude Sonnet 5.5 (`claude-sonnet-5-5`) for synthetic Triage. The local ignored `.env` was configured by the user. Two one-attempt authorized synthetic smoke calls are recorded; the 2026-11-06 call uses the connected harness and its output remains unscored. No key value is stored in this checklist.
- [x] Add a provider-free semantic output validator for category inference, exact source quotes, and forced Unknown urgency/destination; no model call or shared-contract change. Full synthetic-only suite: 463 passed.
- [x] Add a synthetic-only Anthropic client adapter boundary with per-run billable authorization, immediate handoff preflight, retry disabled, provisional 60-second timeout, injection-as-data handling, and strict output validation; prepare minimized item requests and block ambiguous segmentation before provider use. Pin/install Anthropic SDK 2.5.0 and python-dotenv 1.2.4; the ignored `.env` is local-only. One synthetic API smoke call is recorded; see its trace report for limits.
- [x] Decide the model alias/snapshot and regression policy with Shared Lane before model-backed evaluation (D-20); SDK 2.5.0 and dotenv 1.2.4 are pinned.
- [x] Define and implement Coordinator behavior, tools, schemas, internal validation, stop conditions, retries, and recovery from the current PRD.
- [ ] Complete implementation of the already-approved Triage behavior: classify separable requests independently, preserve exact source spans, keep categories as inference, route Unknown/ambiguous items to the Auditor, and attach a reasoned attention flag when plausible urgency warrants it. The runtime loads the category-only vocabulary from an exact SHA-256-pinned synthetic source, validates it at the call boundary, and joins each proposal to its exact item quote. The item-scoped Connector/Knowledge path is now implemented and tested; the fixture-only attention signal remains a review cue, not a live risk detector or operational urgency policy. F-1 and F-2 are fixed in Manny commit `122d44b` with regression tests; updated PR review is pending. Remaining Phase 2 gates: Shared connection acceptance, Manny-approved evaluation labels, and full evaluation evidence. Operational urgency/destination remain Unknown pending Auditor review.
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
- [ ] Receiver/shared gate: Shawn reviewed PR #12 and accepted with findings; Manny's F-1/F-2 fixes are in commit `122d44b` and await updated PR verification. Shared Lane still needs to check schema/version integrity, acknowledgements, item joins, stale-state rejection, failure routing, and the end-to-end handoff. Do not change Shawn-owned agent behavior. Follow the [ordered Phase 2 exit checklist](docs/planning/Manny-phase/phase2/EXIT-CHECKLIST.md).
- [ ] Run and retain the app-wired Coordinator-to-Triage plus downstream integration/security cases after the shared handoff shape is accepted; the one-call Triage smoke did not exercise this workflow.
- [ ] At project completion, run 100 sequential synthetic-only traces; retain pass and failure evidence and stay within the available $40 budget.
- [x] PR #6 was merged into `developer` (merge commit `8499f85`). The merge itself is the only Antigravity action confirmed by the project lead; do not treat the merge as evidence that Antigravity performed or validated the implementation work described in its handoff.
- [ ] Verify PR #6 checks/review and any claimed conflict-resolution work from source records; the earlier “CONFLICTING / DIRTY” note is historical and is not current status.
- [ ] Fast-forward any remaining non-main branches only after checking ancestry, cleanliness, and the current remote state.

### Manny Phase 3 — Escalation status

- [x] EscalationAgent implementation and focused tests exist. Unknown urgency routes to human Auditor review without assigning a band; attention evidence is preserved only after live A1 registry validation, with pattern ID/span provenance; a verified current Under Investigation fact remains human-managed, with no autonomous status change or third-party contact and P1 precedence preserved. Focused suite: 29 passed; full Python 3.13.15 suite: 615 passed. Integrated Phase 3 acceptance remains open.
- [x] Bind A5 recorded-action evidence to the current synthetic case/version before it can be labeled verified; preserve source references on unresolved questions. This does not establish production authentication or replace Shared review.
- [ ] Phase 3 acceptance: connect and validate the actual A2-to-A5 path against the accepted Phase 2/shared handoff, including uncertainty and failure behavior. Phase 3 is not marked complete while this dependency remains open.

### Manny Phase 4 — Evaluation status

- [x] Synthetic evaluation runner and generated report/JSON artifacts exist.
- [x] Preliminary runner evidence exists for 9 Coordinator checks, 3 benchmark fixtures, 4 Escalation rules, and 12 downstream fixture cases. The runner now compares every downstream result with its case file expected output; 12/12 fixture assertions match. These are engineering-fixture checks, not approved gold labels. The CLI regression asserts exit code 2 and `not_scored`/not-ready status when only preliminary fixtures pass. Focused evaluation and case-harness tests: 22 passed; the full Python suite: 615 passed. No evaluation labels have been scored.
- [ ] Phase 4 acceptance: the 12-case run is not the PRD target of at least 100 labeled synthetic cases; Manny label approval is pending; and the CombinedWorkflowHarness uses a stand-in TriageHandoff rather than Coordinator-to-semantic-Triage. Do not describe the six-agent workflow or evaluation gate as complete.

**Snapshot comparison:** commit `3138388` (2026-11-05 15:15) recorded Phase 2 active and Phase 3/4 outstanding. Commit `9a2d3f4` later added Escalation code and the fixture harness; commit `37c01c8` added the evaluation runner/report. Those artifacts are retained; their presence does not by itself satisfy phase acceptance.

### Deferred interface scope

- [x] The Auditor UI, authenticated reviewer workflow, and live human-dispatch interface do not exist and remain deferred until database/authentication work. They are not part of the current phase-status correction.

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
- [ ] Connect Coordinator → semantic Triage → Knowledge and the approved parallel Escalation check after runtime wiring and linked-item contract acceptance. The current CombinedWorkflowHarness begins with a stand-in Triage handoff.
- [x] Exercise Knowledge → Troubleshooting → Escalation/Documentation in the current downstream fixture harness.
- [ ] Connect Documentation → Coordinator/human review; the harness produces a draft but has no Coordinator receiver or reviewer interface.
- [x] Verify the current single-case fixture connectors preserve case/run/policy/source versions, evidence labels, timestamps, status, and uncertainty without mutation. This does not test linked-item scope.
- [ ] Verify linked-item connectors preserve parent/item IDs, source spans, and per-item evidence/status without mutation after Shared accepts the proposal.
- [x] Test direct pipeline, permitted parallel joins, retries with new input versions, missing handoffs, stale results, conflicts, and safe stop/manual fallback within the downstream stand-in harness; this does not validate Coordinator-to-semantic-Triage or linked-item integration.
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

- [ ] All P0 requirements and safety constraints are implemented and evidenced, or explicitly deferred by the project lead. Phase 2 integration and evaluation gates remain open.
- [ ] Agent-level confidence, hallucination, prompt-injection, permission, failure-state, and recovery evaluations pass their approved gates. Current unit tests pass; the approved semantic label and integrated workflow evidence are still missing.
- [ ] End-to-end handoffs, blackboard consistency, parallel joins, timestamping, and human escalation are verified. Coordinator-to-semantic-Triage and linked-item downstream integration have not been exercised.
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
- [ ] Keep `developer` and owner lanes current only through verified fast-forward updates; never overwrite unique commits.
