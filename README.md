# Project-JD-CDIT-MAO

Planning workspace for a human-supervised multi-agent orchestration (MAO) assistant supporting Tier 1 customer support for a clinical-trial-management SaaS platform.

## Project status

The planning package is established. The project lead has authorized the local shared foundation scaffold only: Python 3.13, FastAPI, Pydantic, and SQLite on Manny's lane. Agent workflows, retrieval, model-provider integration, authentication, and external systems remain unimplemented and require their owners/approvals. The supplied job description is the source for role duties. No CDIT system, Salesforce instance, private knowledge base, customer ticket, credential, or PHI access is authorized.

## Documents

- `docs/requirements/PRD.md` — Agent Build PRD, including user needs, proposed workflow, metrics, tool boundaries, blast radius, and evaluation cases.
- `docs/planning/TASK-SPLIT.md` — proposed Manny, Shawn, and Shared lane responsibilities.
- `AGENTS.md` — local collaboration and repository guidance.
- `docs/templates/PRD Template.md` — original user-supplied template; preserve unchanged.

## Recommended prototype direction

Python 3.13, FastAPI, Pydantic, local SQLite, a local document retrieval index, and one model adapter. Start with synthetic tickets and mock knowledge articles. The initial prototype has no live Salesforce integration, outbound messages, credential resets, permission changes, or production authentication. Production services and any handling of PHI require CDIT review and approval first.

## Suggested evaluation

Use labeled synthetic cases to measure triage accuracy, evidence grounding, must-escalate recall, note factuality, handling-time change, and data-boundary behavior. The PRD marks thresholds as provisional until CDIT baseline data and pilot criteria are available.

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

Requires Python 3.13. The scaffold uses FastAPI and Pydantic, with Python's built-in `sqlite3` module for a local database. No external service or credentials are required.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
Copy-Item .env.example .env
uvicorn cdit_support_mao.main:app --reload --app-dir src --env-file .env
```

The API health endpoint is `http://127.0.0.1:8000/health`; interactive API documentation is at `http://127.0.0.1:8000/docs`. SQLite is created on first health check at `data/cdit_support.db` by default. Set `CDIT_DATABASE_PATH` to change the local path. Only synthetic data is permitted. The database helper intentionally defines no ticket, user, role, audit, or agent tables yet; those schemas need an approved design.

The current scaffold establishes the API/runtime and database connection foundation only. Coordinator, Triage, and Escalation functionality belongs to Manny's lane; Knowledge, Troubleshooting, Documentation, retrieval, and the model adapter belong to Shawn's lane. Shared state and handoff contracts require coordination before implementation.
