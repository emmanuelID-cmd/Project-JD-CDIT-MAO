# Project-JD-CDIT-MAO

Planning workspace for a human-supervised multi-agent orchestration (MAO) assistant supporting Tier 1 customer support for a clinical-trial-management SaaS platform.

## Project status

PRD-v4 is the current requirements source. Manny owns the SQL foundation and local app/auth/UI work; the Manny agent phases remain separately tracked in Checklist.md. The local app includes four synthetic accounts, 400 reproducible synthetic development tickets dated across 2024–2026, a compact nine-category taxonomy, all-case Auditor queue visibility, and assigned-only Auditor assessments. User accounts see only their own requests, can edit while Submitted, see In Progress as In Review, and may cancel their own unresolved request. Staff/Auditor/Admin cannot rewrite submitted request text; they add responses and permitted lifecycle updates. No real customer or CDIT data is used.

## Documents

- `docs/requirements/PRD.md` — v1 historical requirements; later approved decisions govern Manny’s lane.
- `docs/requirements/PRD-v2.md` — retained planning baseline for traceability; not approved as the current requirements source.
- `docs/requirements/PRD-v4.md` - current project requirements source, approved 2026-11-08; PRD-v3 is retained as historical context.
- `docs/planning/TASK-SPLIT.md` — proposed Manny, Shawn, and Shared lane responsibilities.
- `docs/lanes/manny/COORDINATOR-A0-A1.md` — Manny’s Phase 1 fixture boundary, contract, and harness links.
- `AGENTS.md` — local collaboration and repository guidance.
- `docs/templates/PRD Template.md` — original user-supplied template; preserve unchanged.

## Recommended prototype direction

Python 3.13, FastAPI, Pydantic, local SQLite, a local document retrieval index, and one Anthropic model adapter for synthetic Triage. The prototype uses synthetic tickets and mock knowledge articles. It has no live Salesforce integration, outbound messages, credential resets, permission changes, or production authentication. Production services and any handling of PHI require CDIT review and approval first.

## Suggested evaluation

Use human-approved synthetic labels to measure triage accuracy, grounding, escalation recall, note factuality, data-boundary behavior, latency, and cost. Report finite-set counts; real-world handling-time savings remain unvalidated.

## Local Git

Inspect git status before staging. Approved completed phases may be committed locally; pushes still require explicit authorization and the project lane workflow.
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

The API health endpoint is `http://127.0.0.1:8000/health`; interactive API documentation is at `http://127.0.0.1:8000/docs`. Initialize the versioned local schema explicitly with `python -m cdit_support_mao.db_cli init`, then create the synthetic demo fixtures with `python -m cdit_support_mao.db_cli seed`. The default database path is `data/cdit_support.db`; set `CDIT_DATABASE_PATH` to change it. `/health` checks connectivity only and does not run migrations. `python -m cdit_support_mao.db_cli purge` applies approved metadata retention. The optional terminal-only `python -m cdit_support_mao.db_cli reset --confirm-synthetic-only` clears synthetic app data and its assignment history while retaining schema and migration history; reseeding restores baseline examples.

### Local synthetic role accounts and interfaces

The application seeds four local accounts with no default passwords: user.demo, staff.demo, auditor.demo, and admin.demo. The Auditor account uses the Staff role with Auditor access enabled. After initializing and seeding the local database, configure a unique local synthetic password for each account from a terminal:

```powershell
python -m cdit_support_mao.db_cli set-password SYN-USER-001
python -m cdit_support_mao.db_cli set-password SYN-STAFF-001
python -m cdit_support_mao.db_cli set-password SYN-AUDITOR-001
python -m cdit_support_mao.db_cli set-password SYN-ADMIN-001
```

The CLI prompts for the password twice and stores only a salted password hash. Run the local app and open http://127.0.0.1:8000/login. User accounts see and submit only their own synthetic requests, can edit them only while Submitted, see In Progress as In Review, and may cancel their own unresolved request. Staff, Auditor, and Admin share the support back end and Product Health view. Staff works assigned cases; Auditor reads all cases and records assessments only on assigned cases. A saved Auditor assessment updates the case’s broad category and urgency band and remains versioned in the decision history. Admin can view all cases, assign/reassign/unassign cases, manage account access, and review assignment history; newly submitted User requests remain unassigned until Admin assigns them. The 400 synthetic development tickets are split between the Staff and Auditor demo queues to show their different scopes. Admin Auditor decisions require a recorded override reason. Staff/Auditor/Admin responses are stored separately; none can rewrite the original submitted request. Every protected page and API checks role and case assignment on the server.

The unauthenticated showcase is separate: /preview/user, /preview/staff, and /preview/admin. Those pages contain fabricated examples and disabled illustrative controls. They make no authenticated API or database requests and cannot create a session or change account access. This is a local synthetic prototype, not production authentication or a deployment-ready security system.

The repository ignores `.env`; a blank local copy is present for `ANTHROPIC_API_KEY`. Add the key locally to that file and never commit or send it in chat. The pinned Anthropic client factory reads deployment environment variables first, then falls back to the local file. It makes no request during import or app startup. A model request requires explicit per-run authorization and a fresh handoff preflight.

### Free Render demo deployment

The repository includes an opt-in Render Free startup bootstrap for the synthetic SQLite demo. It uses `/tmp/cdit_support.db`, recreates sample data and four local demo accounts on each boot, and does not preserve tickets or account changes across restarts, spin-downs, or redeploys. Follow [`docs/deployment/RENDER-FREE-DEMO.md`](docs/deployment/RENDER-FREE-DEMO.md) for exact Render settings. This is not a production deployment and must not receive real CDIT or personal data.

The local prototype now includes the API/runtime, SQLite foundation, synthetic role authentication, and role-specific views. Coordinator, Triage, Escalation, and the Claude Triage adapter belong to Manny's lane; Knowledge, Troubleshooting, Documentation, and retrieval belong to Shawn's lane. Shared state and handoff contracts require coordination before integration.

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
