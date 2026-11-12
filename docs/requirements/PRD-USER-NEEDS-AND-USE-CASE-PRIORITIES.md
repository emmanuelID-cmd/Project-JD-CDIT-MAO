# CDIT Support MAO — User Needs and Use Case Priorities

> Companion artifact to [`PRD-v4.md`](./PRD-v4.md). User needs derive from the supplied job description and remain hypotheses, not validated CDIT research. Priorities describe the synthetic project prototype, not approved CDIT service commitments.

## User Needs — design anchor

The product should help support staff prepare accurate, timely work while keeping decisions and customer-impacting actions with authorized humans. Every use case below maps to one or more needs; a workflow that does not meet these needs should not be treated as successful merely because it generated an answer.

| ID | User | Need | Why it matters | Success evidence |
| :--- | :--- | :--- | :--- | :--- |
| UN-01 | Staff | As Staff, I need a concise synthetic-case summary and policy-based classification because I need to understand the request and proposed attention path. | Helps support staff review synthetic requests efficiently. | Reviewer accepts the summary and policy rationale on labeled synthetic cases. |
| UN-02 | Staff | As Staff, I need relevant synthetic support guidance with its source because I need to verify proposed instructions. | Prevents unsupported product claims and makes evidence review practical. | Claims are supported by cited, current passages from the approved synthetic knowledge set. |
| UN-03 | Staff | As Staff, I need bounded troubleshooting suggestions and explicit stop conditions because I need to see when a human escalation is required. | Supports consistent recommendations inside the prototype's read-only boundary. | Suggestions match supplied synthetic policy; all must-escalate test cases are flagged. |
| UN-04 | Staff | As Staff, I need a draft note based on verified synthetic case facts because I need a complete, reviewable record without an agent writing to a ticketing system. | Reduces repetitive drafting while protecting record quality. | Required fields are complete; no unsupported material claims appear. |
| UN-05 | Staff | As Staff, I need escalations to include the issue, evidence, proposed steps, and unresolved questions because a human reviewer needs an actionable handoff. | Makes a simulated handoff reviewable. | Handoff contains required evidence and no invented details. |
| UN-06 | Admin | As Admin, I need to inspect and manage synthetic account permissions because privileged access changes must be visible and accountable. | Supports local role/access administration without creating multiple staff tiers. | Admin-only grant/update/promote/demote/suspend/deactivate/remove actions are authorized and recorded; unauthorized attempts are denied. |
| UN-07 | User | As User, I need to submit and track only my own synthetic support requests, edit them before review begins, and cancel my own unresolved request because I need control over my client-side submissions. | Defines the client view without including the separate platform-to-developer issue-reporting feature. | User can submit and view only their own request; edit only while Submitted; after In Progress, see In Review and no edit action; cancel own unresolved requests; access to another user's and development-example data is denied. |
| UN-08 | Product Health | As Product Health, I need minimal synthetic/system metadata about runs, status, versions, errors, performance, and access changes because I need to investigate, correct, or improve the prototype without retaining ticket content. | Enables project-level investigation while minimizing retained data. | Required metadata is queryable; ticket bodies, attachments, direct identities, and actual records are absent. |
| UN-09 | Project reviewer | As a project reviewer, I need linked static User, Staff, and Admin previews without signing in because I need to compare the intended views without receiving application access. | Makes the three role views easy to inspect without distributing demo accounts or granting app access. | Three previews load without login or protected API/database access; privileged actions are inert. |

## Priority definitions

- **[P0] Must ship:** Required for a safe, coherent MVP. Omitting it blocks MVP acceptance.
- **[P1] Important:** Strong value, but the MVP can operate safely without it using a documented manual process.
- **[P2] Nice to have:** Useful enhancement that can follow after core workflow evidence exists.

## Prioritized use cases

| ID | Priority | Use case | Primary user | Need IDs | MVP acceptance signal |
| :--- | :---: | :--- | :--- | :--- | :--- |
| UC-01 | [P0] | User submits a synthetic support request, sees only their own request/status, may edit only while Submitted, sees In Progress as In Review, and can cancel their own unresolved request. | User | UN-07 | Own-request scope, pre-review edit, post-review lock, and unresolved cancellation work; another user's requests and Staff/Admin development examples are denied. This is not platform issue reporting to developers. |
| UC-02 | [P0] | Summarize a permitted synthetic case and propose a policy-based category and attention rationale. | Staff | UN-01 | Labeled synthetic-case triage meets the PRD target; report finite-set counts and must-escalate outcomes. |
| UC-03 | [P0] | Retrieve relevant versioned synthetic guidance and show source IDs/sections; abstain when evidence is missing, stale, or conflicting. | Staff | UN-02 | Grounding meets the defined supported-claim measure; zero unsupported material claims and fabricated citations in the must-pass set. |
| UC-04 | [P0] | Suggest bounded support steps, identify missing facts, and flag stop/escalation conditions. | Staff | UN-03 | All defined must-escalate synthetic cases are flagged; false escalations are reported. |
| UC-05 | [P0] | Prepare a draft note from verified synthetic case facts with uncertainty visible and human review enforced. | Staff | UN-04 | Required-field completeness meets target; no unsupported material claim; no external write occurs. |
| UC-06 | [P0] | Assemble an escalation packet with issue summary, evidence, proposed steps, and unresolved questions. | Staff / human reviewer | UN-05 | Required handoff fields are present; no unsupported material claims. |
| UC-07 | [P0] | Authenticate synthetic User, Staff, and Admin accounts and enforce their view/actions. Admin shares the Staff back end and has privileged synthetic account/access controls. | User / Staff / Admin | UN-06, UN-07 | Positive and negative tests cover account creation/access administration, own-request visibility, staff workflow, and denial of unauthorized operations. No extra staff tiers or interfaces. |
| UC-08 | [P0] | Keep agents propose-only/read-only; enforce human review and safe failure/manual fallback for invalid, unavailable, or conflicting inputs. | Staff | UN-01–UN-05 | No agent write tool, external message, ticket-state mutation, resolution, or closure; synthetic fallback cases pass. |
| UC-09 | [P0] | Record and inspect minimal Product Health metadata and synthetic evaluation results. | Product Health / project team | UN-08 | Synthetic run/event IDs, timestamps, status/category, component/version, errors/performance, and access-change metadata are queryable; case content and real identities are excluded. |
| UC-10 | [P0] | Evaluate agent and combined-workflow behavior against human-approved synthetic labels and a deterministic script. | Project team | UN-01–UN-08 | Results report gate counts, denominators, uncertainty, grounding, escalation, injection/permission, fallback, latency/cost, and peer review on the tested set. |
| UC-11 | [P2] | Consider a second reviewer/model only in a separately approved future comparison. | Project team | UN-02–UN-05 | Remains deferred; not part of the six-agent runtime. |

| UC-12 | [P0] | Inspect linked static User, Staff, and Admin previews without signing in; preview controls do not perform actions. | Project reviewer | UN-09 | 3/3 previews load without login; no authenticated API/database request occurs; privileged controls are inert. |

## Priority rationale and dependencies

- P0 use cases define the safe synthetic-data MVP: useful preparation, source grounding, role boundaries, human control, and safe escalation.
- UC-06 is an authorization requirement, but production identity-provider integration remains out of scope. The prototype should model permissions and prove denial behavior locally.
- UC-07 is a boundary, not permission to automate external actions; it is P0 because the prototype must show safe behavior.
- P1 items improve persistence, measurement, or recovery but have manual or evaluation-workflow alternatives.
- P2 items are deferred until the core workflow demonstrates value and data governance permits further work.
- The prototype uses synthetic account categories and policy/knowledge. CDIT-specific role matrices, product sources, and operating SLAs are not assumed; any future production use requires separate approved sources and controls.
- Client-to-developer platform issue reporting remains out of scope, unconfirmed, and disabled under D-17; it is not a prioritized use case in this companion.
- A single-call comparison is optional synthetic evaluation only; it is not a product use case or an additional runtime agent (D-19).

| UC-13 | [P0] | Staff/Admin manage the local synthetic case queue, including labeled development examples, human case-detail edits, and permitted status changes. | Staff / Admin | UN-01, UN-07 | Staff and Admin can operate the synthetic case controls; User cannot see development examples; human case writes are audited; agents have no write path. |