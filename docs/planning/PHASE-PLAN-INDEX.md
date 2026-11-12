# Historical PRD v2 Planning Index

**Status:** Historical planning snapshot from 2026-11-04; superseded for current implementation tracking. PRD-v4 is the current requirements source. For current status, read [`AGENTS.md`](../../AGENTS.md), [`Checklist.md`](../../Checklist.md), [`PRD-v4.md`](../requirements/PRD-v4.md), and the owner-specific phase plans. Historical proposals and dated PRD-v3 decisions are retained as context and do not override PRD-v4.

**Planning decision deadline:** November 11, 2026. This is a planning/go-no-go deadline, not a delivery date for agents, harness, or evaluation.

## Read this first

- **Manny's phase plan is his obligation** to guide and track his assigned work. He should follow it or record an approved change.
- **Shawn's phase plan is optional guidance.** She may follow, change, reorder, or opt out. Using it or checking off its steps cannot block her work, handoffs, review, or acceptance. Her work is judged against the approved PRD and shared contracts, not this guide.
- Shared owns agreed interfaces, state contracts, connectors, and end-to-end test infrastructure, not agent internals. Undecided work is not silently assigned to either contributor.
- PRD requirements, safety constraints, contract acceptance, and evidence-based release decisions remain project gates regardless of use of a phase guide.

## Historical project position — November 4, 2026 (superseded)

- `docs/requirements/PRD.md` remains the current approved requirements source. `docs/requirements/PRD-v2.md` is now a separate planning draft for review and is not yet approved; `PRD-V2-CLAUDE-CRITIQUE-PLAN.md` remains the critique/correction record.
- The local Python 3.13/FastAPI/Pydantic/SQLite foundation is scaffolded. Domain schemas, production authentication, external integrations, and the MAO runtime are not established.
- Shawn's Knowledge, Troubleshooting, Documentation code, fixtures, lane harness, tests, and proposed `0.1.0-proposed` contracts are merged in PR #2 at `a14bb8d`. Presence is not acceptance. Her lane design reports 97 tests and 12 cases on Python 3.12; Python 3.13 results have not been independently recorded. PR #2 has no recorded review or status checks.
- Manny's Coordinator, Triage, Escalation, the combined six-agent harness, and runtime blackboard are not implemented. Shawn's lane harness uses upstream stand-ins and is not an end-to-end harness.
- Existing fixtures do not establish the 100-case target or measured safety gates. Gate counts, independent labels, and several measurement protocols need definition.
- Checklist records implementation expansion as pending project-lead authorization. This plan does not grant that authorization.

## Proposed changes to sequencing

Require a PRD v2 consistency, scope, and approval gate before implementation. Preserve all six agents, A0–A7, blackboard, quality metrics, and proposed safety gates unless the project lead explicitly approves a change. Add Python 3.13 validation, independent evaluation labels, per-gate sample counts, reviewer over-reliance evaluation, retrieval recall@k, latency/cost/source freshness metrics, and a test-only combined workflow harness. Do not adopt Claude's workload or agent-count reduction proposal.

Prototype target remains synthetic-data-only, local, propose-only/read-only, and human-reviewed. No write tool, ticket-state mutation, external alert, live Salesforce/CTMS access, production authentication, or real ticket/PHI use is authorized here. Future case-action examples remain non-MVP policy context. Regulatory review is conditional; this plan makes no HIPAA, Part 11, GCP, or other applicability finding.

## Order of work

1. **Through Nov 11 — initial PRD v2 planning/sign-off:** draft and approve the non-urgency corrections, generic synthetic support default, and three account categories (User, Staff, Admin). Keep evaluation and Product Health limited to synthetic cases/metadata; do not require real-user interviews, records, or operational activity. Manny owns evaluation definitions/protocol. After initial v2 sign-off, hold the Low/Medium/High band-design discussion and issue a reviewed PRD amendment before dependent routing implementation.
2. **After separate authorization — shared baseline:** agree versioned contracts, state lifecycle decisions, fixture outcomes, labels/counts, reviewer protocol, and Python 3.13 commands.
3. **After baseline — lane work:** Manny follows his required Coordinator/Triage/Escalation sequence. Shawn may follow or adapt her voluntary Knowledge/Troubleshooting/Documentation guide; adoption is not a prerequisite.
4. **Integration/acceptance:** Shared builds only approved connectors and test-only combined harness; each owner fixes internal findings in their lane; independent SECURITY/REVIEWER assess evidence; project lead decides next phase.

## Detailed plans

- [Manny — required personal work plan](Manny-phase/README.md)
- [Shawn — optional, non-gating work guide](Shawn-phase/README.md)
- [Shared — connections and combined harness](phase/shared/README.md)
- [Undecided/unassigned work](phase/undecided/unassigned/PLAN.md)
- [PRD v2 critique/correction inventory](PRD-V2-CLAUDE-CRITIQUE-PLAN.md)
- [Existing implementation phase proposal](AGENT-IMPLEMENTATION-PHASE-PLAN.md)

## Handoffs and boundaries

Handoffs identify phase, owner, artifact/contract version, completed checks, evidence, unknowns, failures, and requested decision. Receiver acknowledges or returns a concrete mismatch. Cross-lane work is limited to agreed contracts, shared-state connections, connectors, and end-to-end verification; agent-internal fixes return to that owner. A0–A7 are runtime gates, not project phases. Keep work on existing owner lanes. This plan creates no branches and authorizes no commits, pushes, or `main` merge.
