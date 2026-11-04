# Project Completion and Lane Checklist

Use this checklist as the live project status record. Check an item only when its evidence is present and reviewed. Planning completion is not implementation completion; an unchecked item blocks a completion claim unless the project lead explicitly marks it out of scope or deferred.

**Current phase:** Local foundation scaffold (implementation authorized within the scope recorded in `docs/planning/DEFERRED-DECISIONS.md`)
**Planning deadline:** November 11, 2026
**Current implementation status:** Shared API and SQLite foundation scaffold set up; runtime agents and integrations remain not started
**Completion status:** In progress

## Shared project baseline

- [x] PRD is the current requirements source and includes milestones, agent gates, confidence/factuality, prompt-injection controls, case authority, blackboard state, and handoffs.
- [x] User Needs and prioritized use cases have a linked companion file.
- [x] Synthetic evaluation and routing examples are in `docs/requirements/CASE-SCENARIOS.md`.
- [x] Deferred policy and implementation decisions are tracked in `docs/planning/DEFERRED-DECISIONS.md`.
- [x] Interactive architecture is available in the field guide and standalone artifact.
- [ ] Team reviews and accepts the PRD, agent ownership, interfaces, and current scope.
- [ ] All planning milestone exit evidence and decisions are recorded.
- [x] Project lead explicitly authorized the local technology-stack foundation scaffold on 2026-11-03.
- [ ] Project lead authorizes any expansion beyond the local scaffold before that work begins.

## Shared foundation scaffold

- [x] Python 3.13 package metadata and FastAPI/Pydantic dependencies are configured.
- [x] FastAPI health endpoint and local SQLite connection helper are scaffolded.
- [x] Local setup instructions and synthetic-data configuration example are documented.
- [ ] Agree and implement domain schemas, authentication, and audit/retention behavior before adding those capabilities.
- [x] Install project dependencies in the local Python 3.13 virtual environment.
- [ ] Start the local service and confirm the health endpoint on the contributor machine.

## Manny lane — Coordinator, Triage, Escalation

- [ ] Confirm owner availability and accept the three-agent assignment.
- [ ] Define and implement Coordinator behavior, tools, schemas, internal validation, stop conditions, retries, and recovery from the current PRD.
- [ ] Define and implement Triage behavior, policy-grounded outputs, claim-level evidence/confidence, unknown handling, and failure behavior.
- [ ] Define and implement Escalation behavior, must-escalate checks, evidence packet, uncertainty handling, and human routing.
- [ ] Validate each owned agent independently against its own prompt, tools, permissions, and failure gates.
- [ ] Publish versioned input/output contracts and handoff examples for the connection points.
- [ ] Fix agent-internal failures found in this lane; do not modify Shawn-owned agent functionality.

## Shawn lane — Knowledge, Troubleshooting, Documentation

- [ ] Confirm owner availability and accept the three-agent assignment.
- [ ] Define and implement Knowledge retrieval, approved-source/version handling, citations, conflicts, abstention, and injection handling.
- [ ] Define and implement Troubleshooting behavior, evidence-supported steps, allowlists, stop conditions, and recovery.
- [ ] Define and implement Documentation behavior, verified-fact-only drafts, citations, schema validation, and uncertainty reporting.
- [ ] Validate each owned agent independently against its own prompts, tools, permissions, and failure gates.
- [ ] Publish versioned input/output contracts and handoff examples for the connection points.
- [ ] Fix agent-internal failures found in this lane; do not modify Manny-owned agent functionality.

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
- [ ] Resolve the deferred urgency definitions, SLA thresholds, alerts, state transitions, write permissions, confidence calibration, storage, retention, and audit decisions in the deferred register.
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
