# Project-JD-CDIT-MAO

Planning workspace for a human-supervised multi-agent orchestration (MAO) assistant supporting Tier 1 customer support for a clinical-trial-management SaaS platform.

## Project status

The project lead authorized Manny’s synthetic lane phases. Manny’s Coordinator-to-semantic-Triage runtime is now connected through an item-scoped connector to the Knowledge receiver in `CombinedWorkflowHarness.run_manny_connected`; N1–N3 are complete, with Phase 2 exit readiness estimated at 85%. The full synthetic-only suite most recently passed 616 tests on Python 3.13.15; this is regression evidence, not phase acceptance. Shawn/Shared receiver review, the approved 100-case label/evaluation gates, and complete Phase 2 evidence remain open. One authorized Claude Sonnet 5.5 smoke call is recorded and safely returned Unknown for human Auditor review; it is not an approved or scored label. No live customer or CDIT data is used. The Auditor interface/auth flow and external integrations remain deferred. The supplied job description is the source for role duties. No CDIT system, Salesforce instance, private knowledge base, customer ticket, or PHI access is authorized.

## Documents

- `docs/requirements/PRD.md` — v1 historical requirements; later approved decisions govern Manny’s lane.
- `docs/requirements/PRD-v2.md` — retained planning baseline for traceability; not approved as the current requirements source.
- `docs/requirements/PRD-v3.md` — project-lead-approved synthetic build baseline for Manny’s lane; team-wide review remains pending.
- `docs/planning/TASK-SPLIT.md` — proposed Manny, Shawn, and Shared lane responsibilities.
- `docs/lanes/manny/COORDINATOR-A0-A1.md` — Manny’s Phase 1 fixture boundary, contract, and harness links.
- `AGENTS.md` — local collaboration and repository guidance.
- `docs/templates/PRD Template.md` — original user-supplied template; preserve unchanged.

## Recommended prototype direction

Python 3.13, FastAPI, Pydantic, local SQLite, a local document retrieval index, and one Anthropic model adapter for synthetic Triage. The prototype uses synthetic tickets and mock knowledge articles. It has no live Salesforce integration, outbound messages, credential resets, permission changes, or production authentication. Production services and any handling of PHI require CDIT review and approval first.

## Suggested evaluation

Use human-approved synthetic labels to measure triage accuracy, grounding, escalation recall, note factuality, data-boundary behavior, latency, and cost. Report finite-set counts; real-world handling-time savings remain unvalidated.

## Local Git

Inspect `git status` before staging. Do not commit, push, create remote repositories, or publish until the user approves the concrete files and collaboration plan.
## Planning schedule

The planning deadline is **November 11, 2026**. The planning package defines milestones and exit conditions for scope/roles, synthetic workflows, architecture and security review, integrated PRD review, and planning sign-off. A later, narrow authorization started the local foundation scaffold; this does not authorize production deployment, live integration, or PHI use.

See the PRD sections **Delivery milestones, conditions, and deadline**, **Prompt-injection prevention requirements**, and **Out of scope** for checkpoints, lane handoffs, security gates, and exclusions.

The PRD now distinguishes **MAO agent checkpoints within each case run** from **project delivery milestones**. Agent checkpoints cover intake authorization, injection handling, triage, retrieval, troubleshooting, escalation, draft validation, and human disposition; failures stop downstream automation safely.

The PRD also defines claim-level agent confidence and factuality rules: agents must identify verified facts with sources, label inference, disclose unknowns, and abstain/escalate when evidence is insufficient or conflicting. Confidence thresholds and evaluation gates remain proposed pending calibration on held-out synthetic cases.

## Resolution authority and shared state

The PRD defines case-based agent authorization within tier-based urgency routing, ticket-state boundaries (including In Progress, Waiting on Customer, Resolved, and Closed), and a coordinator-managed blackboard with direct-pipeline and parallel-analysis handoffs. Open policy and implementation decisions are tracked in `docs/planning/DEFERRED-DECISIONS.md`.
- docs/requirements/PRD-USER-NEEDS-AND-USE-CASE-PRIORITIES.md — linked companion detail for prioritized use cases and user needs.
- docs/requirements/CASE-SCENARIOS.md — synthetic evaluation and case-routing examples referenced by the PRD.
- `Checklist.md` — live planning, lane, shared integration, pending-decision, and completion checklist.

- `Checklist.md` — live lane, shared integration, pending-decision, and project-completion checklist.

## Contributor lanes

- `manny/coordinator-triage-escalation` — Coordinator, Triage, Escalation agents.
- `shawn/knowledge-troubleshooting-docs` — Knowledge, Troubleshooting, Documentation agents.
- Contributor work targets `developer` by pull request. Only `developer` opens a release pull request to `main`; release merge waits for project completion and explicit user direction.

## Local development setup

Requires Python 3.13. The scaffold uses FastAPI and Pydantic, with Python's built-in `sqlite3` module for a local database. The health endpoint needs no external credentials. A Claude Triage request requires the local API key in `.env` and a separately authorized synthetic run.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
Copy-Item .env.example .env
uvicorn cdit_support_mao.main:app --reload --app-dir src --env-file .env
```

The API health endpoint is `http://127.0.0.1:8000/health`; interactive API documentation is at `http://127.0.0.1:8000/docs`. SQLite is created on first health check at `data/cdit_support.db` by default. Set `CDIT_DATABASE_PATH` to change the local path. Only synthetic data is permitted. The database helper intentionally defines no ticket, user, role, audit, or agent tables yet; those schemas need an approved design.

The repository ignores `.env`; a blank local copy is present for `ANTHROPIC_API_KEY`. Add the key locally to that file and never commit or send it in chat. The pinned Anthropic client factory reads the local file but makes no request during import or app startup. A model request requires explicit per-run authorization and a fresh handoff preflight.

The current scaffold establishes the API/runtime and database connection foundation. Coordinator, Triage, Escalation, and the Claude Triage adapter belong to Manny's lane; Knowledge, Troubleshooting, Documentation, and retrieval belong to Shawn's lane. Shared state and handoff contracts require coordination before integration.

## Shawn's Lane agents (pending review)

`shawn/knowledge-troubleshooting-docs` contains a local implementation of the Knowledge, Troubleshooting, and Documentation agents. It uses no language model, works on synthetic data only, and is pending team review and project-lead confirmation. The proposed v0.1 handoff contracts are in `docs/contracts/HANDOFF-CONTRACTS.md`. Design, evidence, and limitations are in `docs/lanes/shawn/SHAWN-LANE-DESIGN.md`.

```powershell
python -m pip install -e ".[dev]"
python -m pytest
python -m cdit_support_mao.lane_harness synthetic_data/cases
python -m cdit_support_mao.lane_calibration synthetic_data/calibration/knowledge-calibration-v1.json --report docs/lanes/shawn/calibration/KNOWLEDGE-CALIBRATION-REPORT.md --results docs/lanes/shawn/calibration/knowledge-calibration-v1.results.json
```

The calibration command measures the provisional confidence bands on a held-out synthetic set. Its output is lane evidence for the evaluation owner's D-08/D-09 protocol; the labels are drafts pending human approval, and the command does not change any threshold.

The lane harness is not the coordinator. It uses labelled Triage and Escalation stand-ins from `synthetic_data/cases/` until Manny's Lane agents and the shared contracts are agreed.
