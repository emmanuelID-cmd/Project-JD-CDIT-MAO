# Deferred Decisions and Actions

**Project:** CDIT Tier 1 Support MAO
**Planning deadline:** November 11, 2026
**Status:** Open items captured from planning discussion; no item below authorizes implementation or production access.

| ID | Decision / action | Why deferred / dependency | Suggested owner | Needed by / exit evidence |
| :--- | :--- | :--- | :--- | :--- |
| D-01 | Define operational urgency policy: exact impact/time thresholds, SLA clocks, cross-case grouping rules, and who may override a proposed band. | User approved a three-band Low/Medium/High framework with a visible Urgent flag for High [P1]. The 80-row synthetic catalog in CASE-SCENARIOS.md proposes defaults; it is not CDIT policy or validated operational routing. | Project lead + CDIT Support Lead | Before any routing implementation: review the proposed defaults, define thresholds and SLA clocks from authorized policy, and document human override/audit rules. |
| D-02 | Approve case-type-specific agent action allowlist, including response sending and ticket state transitions. | Agent authority must be explicitly delegated per action and case pattern. | Shared Lane + CDIT owner | Before any implementation of writes; role/action matrix approved. |
| D-03 | Decide which routine case types may be fully agent-resolved, which may only receive a sub-action, and which always require a human. | Requires policy, risk, and evidence criteria; urgency alone is insufficient. | Shared Lane + Support Lead | Before build acceptance; case-resolution matrix signed off. |
| D-04 | Define exact distinction and transition policy for In Progress, Waiting on Customer, Escalated, Resolved, and Closed. | Existing workflow states are acknowledged; permitted transitions by role/action remain to be specified. | Manny's Lane + CDIT process owner | Before workflow implementation; transition table reviewed. |
| D-05 | Reconsider whether to add a second reviewer agent; it is deferred and absent from the current six-agent architecture. | No runtime handoff is active. The earlier proposed placement was after A2 Triage, before downstream Troubleshooting/Documentation; a trigger and value evidence were never finalized. Confidence cannot select a “winner.” | Project lead + Shared Lane | Only before adding a reviewer branch; comparative evaluation and a reviewed handoff contract must show value. The approved six-agent path is not blocked. |
| D-06 | Show a visible local P1 status flag for tickets needing immediate human attention. Outbound email remains deferred under D-13. | User approved an in-app flag/badge that signals immediate attention is required. | Shared UI owner | Include the P1 indicator in the approved UI behavior; exact visual treatment follows the UI consistency plan. No outbound message. |
| D-07 | Choose agent shared-state storage and blackboard schema/versioning, retention, and access controls. | Prototype stack suggests SQLite, but run concurrency, audit, and retention needs need confirmation. | Shawn's Lane | Before implementation; schema and lifecycle decision recorded. |
| D-08 | Define and evaluate claim-level confidence derivation/calibration, including whether scores are probabilities or qualitative bands. | Existing bands are provisional; confidence never establishes truth or authority. | Manny (evaluation owner), with agent owners providing their outputs | Before confidence is used as a gate; document method and held-out synthetic results. |
| D-09 | Define the synthetic evaluation protocol: claim classes/denominators, per-gate sample counts, held-out labels, retrieval freshness/recall, latency/cost, and reviewer error-detection thresholds; preserve approved must-pass safety gates. | Evaluation uses synthetic fixtures for this project assignment; no real customers, company records, or operational decisions. Human-approved labels and deterministic comparison are the baseline. | Manny (evaluation owner); peer review uses a project teammate and synthetic fixtures | Before evaluation acceptance; publish the metric rubric, counts, holdout protocol, and reviewed results. |
| D-10 | Define timestamp granularity, clock source, audit fields, retention, and safe alert payload. | Operational/audit requirements and privacy constraints are unknown. | Shawn's Lane + security/privacy reviewer | Before audit/notification implementation; event contract approved. |
| D-11 | Decide conditions for agent-resolved vs. human-resolved status and separate permission for Resolved vs. Closed. | Finalization can have customer/process impact; must be explicitly delegated. | CDIT process owner + Shared Lane | Before any case-state write; transition authority documented. |
| D-12 | Revisit live integration, production authentication, real customer data/PHI, and model/provider approval. | Explicitly outside current planning/prototype scope pending CDIT authorization and safeguards. | Project lead + CDIT security/privacy/legal | Only in separately authorized phase; approvals and data-flow assessment complete. |
| D-13 | Revisit external email alerts and customer-facing autonomous responses. | Requires approved channels, recipients, templates, consent/policy checks, and audit. | CDIT Support Lead + project lead | Separately authorized phase; written policy and acceptance tests complete. |
| D-14 | Decide whether to add an AI-assisted evaluation labeler beyond human-approved expected labels and a deterministic evaluation script. | No evaluator agent/tool is implemented. A hosted API evaluator is online and adds a provider/data-flow/cost dependency; a local LLM would require separate setup. It is not the deferred runtime second reviewer. | Manny (evaluation owner) | Before adding AI-assisted evaluation; specify model/runtime, data boundary, blind-label protocol, and human adjudication. |
| D-15 | Implement the three approved synthetic account categories: User, Staff, and Admin. | User confirmed two work interfaces: client-facing User view; shared back-end for Staff and Admin, with Admin-only privileged controls in that back-end. No rank-based tiers, separate staff interfaces, or access-only zones. | Project lead assigns the platform feature owner before implementation; this assignment does not block PRD v2 review. | Before authentication/RBAC implementation; use the permissions below. Production identity-provider authentication remains D-12. |
| D-16 | Use the generic synthetic CTMS-support default for this prototype; defer claims about specific CDIT products/modules until an approved source is available. | First-party confidential company knowledge is not required for a generic prototype. Use synthetic tickets/knowledge and only public metadata for scenario context; such metadata is not product guidance. | Project lead + synthetic scenario owner (unassigned) | Before any product-specific claim; absent an approved source, label the result simulated/unknown and abstain from asserting CDIT-specific behavior. |
| D-17 | Keep client-to-developer platform issue reporting out of current scope; reconsider only after scope and authentication prerequisites are confirmed. | User direction: remain deferred, scope-unconfirmed, and disabled; it is distinct from ordinary support-ticket reporting. | Project lead | Reopen only after explicit scope approval and confirmation that every intended submitter must authenticate; if approved, define a separate journey and acceptance criteria. |
| D-18 | Keep Product Health limited to minimal synthetic/system metadata for internal investigation, corrections, and change planning; do not retain underlying ticket/customer content in the prototype. | User approved metadata use while excluding underlying records. Project needs and evaluation remain synthetic; no practitioner interview or real-world field activity is required for this assignment. | Shared app/data owners under existing lane rules | Retain only needed synthetic run/event IDs, timestamps, status/category, component/version, error/performance and access-change metadata; exclude ticket bodies, attachments, direct user identity, customer records, and confidential company information. |
| D-19 | A single-call baseline is not a required agent or product feature. It may be used as an optional synthetic-only comparison if the assignment needs evidence for MAO. | User approved the recommendation. One model call receives the same synthetic case/evidence as the MAO workflow; compare results only if useful, without creating a second runtime architecture or contacting real users. | Manny (evaluation owner) | Not a PRD-v2 blocker. If performed, use synthetic fixtures and the already approved model/data boundary. |

## Approved planning agreements — 2026-11-04

- Keep six runtime agents total, with Coordinator included; the human reviewer is not an agent. The second reviewer remains deferred; no handoff to it occurs in the current architecture.
- Include local prototype authentication using exactly three synthetic account categories: **User** (client-facing view), **Staff** (back-end support view), and **Admin** (the same back-end plus privileged account/access controls). Admin can inspect who has what access and grant/update/promote/demote/suspend/deactivate/remove accounts or permissions. Do not create extra staff tiers, separate staff interfaces, or access-only zones. Production identity-provider authentication remains deferred under D-12.
- Use generic synthetic CTMS-support tickets/knowledge as the fallback. Public study metadata may add scenario context but is not CDIT product guidance. Keep synthetic output labeled as simulated; if an actual support case lacks approved evidence, abstain or route to a human.
- Use the three proposed urgency bands and High/P1 Urgent flag documented in CASE-SCENARIOS.md as the synthetic planning taxonomy. Exact thresholds, SLA clocks, real company groupings, and override policy remain open under D-01; do not infer them from this example catalog.
- Keep client-to-developer platform issue reporting deferred, scope-unconfirmed, and disabled until scope and authentication prerequisites are explicitly approved (D-17).
- Keep Product Health limited to synthetic/system metadata useful for internal investigation, correction, and change planning: synthetic run/event IDs, timestamps, status/category, component/version, error/performance, and access-change metadata. Do not retain ticket bodies, attachments, direct user identity, or actual user/ticket records; no working-Specialist interview or real-world field activity is part of this project assignment (D-18).
- Assign Manny ownership of synthetic evaluation definitions and protocol (D-08, D-09, D-14); use human-approved expected labels, deterministic evaluation script, and project-teammate peer review on synthetic fixtures. No external evaluator or real-world participant is required; an AI evaluation labeler remains deferred.
- Keep a single-call baseline out of required implementation scope; any comparison is optional, synthetic-only, and does not add an agent (D-19).
- Treat November 11, 2026 as planning/go-no-go sign-off, not build completion. Keep the prototype synthetic, local, read-only/propose-only, and human-reviewed.

## Approved synthetic account model

- **User:** client-facing front-end for a user's own support requests and permitted client-visible status/details.
- **Staff:** back-end support workspace for ticket review, agent proposals, triage, documentation, escalation, and human disposition under the prototype's read-only/propose-only boundary.
- **Admin:** the same back-end workspace as Staff, plus privileged account/access administration and visibility into who has what permissions. Admin controls may grant/update/promote/demote/suspend/deactivate/remove accounts or permissions. Admin status does not create a separate staff interface or agent authority to write/resolve tickets.

This is the complete synthetic role set for the project: no occupational rank ladder, extra support tiers, per-rank interfaces, or access-only zones. Preserve ordinary user-versus-staff record ownership and authorization checks; these are data-scope protections, not extra interface tiers. Do not infer permission to edit queues, SLAs, knowledge, or ticket state from Admin access unless separately approved.
## Recorded recommendations

- Use case-based action authorization within tier-based routing; urgency selects the path, while case evidence, approved procedure, risk, and explicit permission determine allowed action.
- Permit bounded agent sub-actions (for example, request identified missing documentation and set Waiting on Customer) when explicitly authorized; do not infer missing fields or mark a case Resolved merely because a request was sent.
- Allow full agent resolution only for documented, deterministic, reversible case patterns that pass evidence, policy, permission, and audit checks. Keep Closed separately controlled unless explicitly delegated.
- For parallel analysis, compare evidence and policy fit; do not choose a winner by confidence. Material disagreement or uncertainty goes to a human.
- Timestamp each workflow stage and handoff. Notifications should be minimal and use only an approved channel.
- Keep blackboard entries versioned, attributable, case-scoped, minimally populated, and immutable after handoff; preserve conflict and uncertainty.

## Scoped authorization recorded — 2026-11-03

The project lead authorized starting the local technology-stack foundation scaffold on Manny's active lane. The authorized scope is package metadata/dependencies for Python 3.13, FastAPI and Pydantic; a minimal health endpoint; local SQLite connection support; and local setup documentation. It uses synthetic data only and introduces no domain tables. This authorization does not extend to runtime-agent behavior, retrieval/RAG, model-provider integration, authentication, real or CDIT data, Salesforce, production services, outbound messages, or other deferred decisions. Those require their own lane ownership, approved interfaces, and/or explicit approvals as specified in the PRD.

## Lane-owner direction recorded — 2026-11-04 (project-lead confirmation requested)

Shawn, the Shawn's Lane owner, directed local implementation of the Shawn-owned Knowledge, Troubleshooting, and Documentation agents on `shawn/knowledge-troubleshooting-docs`. The scope is:

- deterministic and extractive agent behavior, with no language model;
- a synthetic knowledge set and a synthetic troubleshooting policy;
- proposed v0.1 handoff contracts (`docs/contracts/HANDOFF-CONTRACTS.md`);
- tests and a lane-only validation harness.

The work uses synthetic data only. It has no model provider, no external I/O, no persistence, and no changes to Manny-owned agents or the API. Details and evidence are in `docs/lanes/shawn/SHAWN-LANE-DESIGN.md`.

Under `Checklist.md`, expansion beyond the local scaffold needs project-lead authorization, so the project lead is asked to confirm or adjust this phase. The work does not decide D-07, D-08, or D-10; it records proposals for them in the lane design document.

## D-08 calibration evidence recorded — 2026-11-04 (not a decision)

Shawn's Lane added a held-out synthetic calibration set (`synthetic_data/calibration/`, 111 cases) and a generated report (`docs/lanes/shawn/calibration/KNOWLEDGE-CALIBRATION-REPORT.md`).

- Critical safety gate: 0 errors.
- High band: 29/29 correct.
- Medium band: 23/25 correct. Both errors are unsupported answers just above the 0.60 cut-off.
- Paraphrased tickets are mostly abstained on (lexical retrieval limit).

The provisional 0.60/0.85 cut-offs are unchanged. D-08 and D-09 belong to Manny as evaluation owner (2026-11-04 planning agreements); this set is lane evidence offered to that protocol. Its expected labels are drafts that need human approval before they count toward a gate. Candidate cut-offs (0.65/0.75) should be confirmed on a second, independently written held-out set first.
