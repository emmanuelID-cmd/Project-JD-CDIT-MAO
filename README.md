# Project-JD-CDIT-MAO

Planning workspace for a human-supervised multi-agent orchestration (MAO) assistant supporting Tier 1 customer support for a clinical-trial-management SaaS platform.

## Project status

Requirements and architecture are at draft stage. The supplied job description is the source for role duties. No CDIT system, Salesforce instance, private knowledge base, customer ticket, credential, or PHI access is assumed or authorized.

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