# Project Completion and Lane Checklist

Use this checklist as the live project status record. Check an item only when its evidence is present and reviewed. Planning completion is not implementation completion; an unchecked item blocks a completion claim unless the project lead explicitly marks it out of scope or deferred.

**Current phase:** Manny Phase 2 — Triage input and policy design
**Planning deadline:** November 11, 2026
**Current implementation status:** Shawn agent and calibration work is merged through PR #4; Manny’s Phase 1 synthetic Coordinator fixture boundary is locally implemented and reviewed. Triage input, linked-item examples, and fixture handling are in progress; semantic classification, Escalation, and end-to-end integration remain incomplete.
**Completion status:** In progress

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
- [x] Phase 2 local Triage input boundary, conservative linked-item segmentation, unknown/Auditor proposals, and source-span checks are implemented; human dispatch and the UI remain deferred to database/auth setup.
- [x] Add exact 80-row development-example references to linked items as unverified IDs; the match does not classify category or urgency, and ambiguous segmentation receives no reference. Focused checks: 30 passed; full synthetic-only suite after current Phase 2 changes: 463 passed.
- [x] Select and document Anthropic Claude Sonnet 5.5 (`claude-sonnet-5-5`) for synthetic Triage; `.env.example` contains only the model setting and blank key variable. No credential is configured and no billable API call has been made.
- [x] Add a provider-free semantic output validator for category inference, exact source quotes, and forced Unknown urgency/destination; no model call or shared-contract change. Full synthetic-only suite: 463 passed.
- [x] Add a synthetic-only Anthropic client adapter boundary with per-run billable authorization, immediate handoff preflight, retry disabled, provisional 60-second timeout, injection-as-data handling, and strict output validation; prepare minimized item requests and block ambiguous segmentation before provider use. Pin/install Anthropic SDK 2.5.0 and python-dotenv 1.2.4; create ignored `.env` with blank key. Full synthetic-only suite: 478 passed. No live API call.
- [ ] Decide the model alias/snapshot and regression policy with Shared Lane before model-backed evaluation (D-20); SDK 2.5.0 and dotenv 1.2.4 are pinned.
- [ ] Define and implement Coordinator behavior, tools, schemas, internal validation, stop conditions, retries, and recovery from the current PRD.
- [ ] Define and implement Triage behavior, policy-grounded outputs, claim-level evidence/confidence, unknown handling, and failure behavior.
- [ ] Wire the adapter into the application, resolve model-alias regression policy, review the provisional timeout against measured latency, and validate model-backed semantic proposals. One synthetic call is authorized but waits for the key to be added locally to `.env`.
- [ ] Define and implement Escalation behavior, must-escalate checks, evidence packet, uncertainty handling, and human routing.
- [ ] Validate each owned agent independently against its own prompt, tools, permissions, and failure gates.
- [ ] Publish versioned input/output contracts and handoff examples for the connection points.
- [ ] Fix agent-internal failures found in this lane; do not modify Shawn-owned agent functionality.

### Manny Phase 2 trace checkpoint — 2026-11-05

- [x] Run one explicitly authorized synthetic Claude adapter smoke trace; record usage, latency, output, and cost.
- [x] Record independent Reviewer A/B reconciliation and scoped SECURITY review.
- [ ] Resolve trace provenance gaps, obtain Manny's semantic label, and run the app-wired six-agent integration/security cases.
- [ ] At project completion, run 100 sequential synthetic-only traces; retain pass and failure evidence and stay within the available $40 budget.
- [x] Compare the outgoing Manny work with origin/developer using git merge-tree; PR preflight found content conflicts in Checklist.md and PROJECT-HANDOFF.md.
- [ ] Reconcile those shared-document conflicts, then review PR checks before integration.
- [ ] After an authorized merge, fast-forward only clean branches whose ancestry proves it safe.
## Shawn lane — Knowledge, Troubleshooting, Documentation

> 2026-11-04 status: Shawn’s three agent implementations and lane harness were merged in PR #2; the calibration follow-up was merged into `developer` in PR #4 (`4deafe7`). PR #4 reports 110 tests and 12 lane cases passing on Python 3.13.17 and a 111-case synthetic calibration set with 0 critical errors. Manny accepted the set as candidate D-08/D-09 evidence and will review the draft labels; the labels and project-wide gates are not yet approved. Code presence, phase authorization, and acceptance remain distinct.

- [x] Confirm owner availability and accept the three-agent assignment (Shawn's lane-owner direction is recorded in `docs/planning/DEFERRED-DECISIONS.md`).
- [x] Knowledge implementation files are present in merged PR #2 (`src/cdit_support_mao/agents/knowledge/`); acceptance remains pending.
- [x] Troubleshooting implementation files are present in merged PR #2 (`src/cdit_support_mao/agents/troubleshooting/`); acceptance remains pending.
- [x] Documentation implementation files are present in merged PR #2 (`src/cdit_support_mao/agents/documentation/`); acceptance remains pending.
- [x] Versioned `0.1.0-proposed` contracts and synthetic handoff examples are published in `docs/contracts/`; Shared Lane acceptance remains pending.
- [ ] Project lead authorizes this agent implementation phase beyond the local scaffold.
- [ ] Review and accept each agent against PRD A3/A4/A6 and the approved shared contract.
- [ ] Validate each agent independently on Python 3.13 against prompts, tools, permissions, evidence, and failure gates.
- [ ] Fix agent-internal findings in Shawn's lane; do not modify Manny-owned agent functionality.

## Shared connection and integration work

- [ ] Agree blackboard fields, identifiers, versioning, provenance, confidence, uncertainty, and state lifecycle.
- [ ] Connect Coordinator → Triage → Knowledge and the approved parallel Escalation check.
- [ ] Connect Knowledge → Troubleshooting → Escalation/Documentation and Documentation → Coordinator/human review.
- [ ] Verify connectors preserve case/run/policy/source versions, evidence labels, timestamps, status, and uncertainty without mutation.
- [ ] Test direct pipeline, permitted parallel joins, retries with new input versions, missing handoffs, stale results, conflicts, and safe stop/manual fallback.
- [ ] Verify cross-lane connectors only; agent prompts, tools, decision logic, and behavior remain with their owners.
- [ ] Define the human-review contract and verify escalation/notification routing against approved policy.
- [ ] Record integration defects and return agent-internal fixes to the owning lane; no cross-lane functionality edits.

## Pending decisions / unassigned

- [ ] Decide whether to add the optional second-reviewer agent; if approved, assign an owner before work begins.
- [ ] Confirm whether authenticated client-to-developer platform issue reporting is in project scope; keep disabled/optional until scope is confirmed and all submitters are authenticated.
- [ ] After initial PRD-v2 finalization, define urgency bands, case groupings, SLA thresholds, and overrides; record them in a reviewed PRD amendment.
- [ ] Resolve future-use items separately before expanding beyond the synthetic read-only prototype: write authority/state transitions, production data and integrations, and applicable storage, retention, and audit controls.
- [ ] Confirm CDIT data/source, security, privacy, hosting, model-provider, and production integration approvals before any production or sensitive-data work.
- [ ] Assign any new agent or workstream explicitly; unassigned work stays pending or is assigned to the user by explicit direction, never silently shared.

## Release / project completion gate

- [ ] All P0 requirements and safety constraints are implemented and evidenced, or explicitly deferred by the project lead.
- [ ] Agent-level confidence, hallucination, prompt-injection, permission, failure-state, and recovery evaluations pass their approved gates.
- [ ] End-to-end handoffs, blackboard consistency, parallel joins, timestamping, and human escalation are verified.
- [ ] Documentation, known limitations, open decisions, and lane ownership are current.
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
