# CDIT Tier 1 Support MAO - PRD v4

*Product Requirements Document: synthetic prototype planning baseline*

**Agent name:** CDIT Support Desk Assistant (working name)
**Owners:** Manny (Manny's Lane), Shawn (Shawn's Lane), Shared Lane
**Date:** 2026-11-08
**Status:** Approved by the project lead as the current synthetic-prototype requirements baseline on 2026-11-08. PRD-v4 supersedes PRD-v3 for current requirements. Shared contract acceptance and implementation-phase gates remain separately tracked. Production authentication, real-data use, and live integration remain outside this approval.

**Version note:** PRD-v3 is retained as the historical prior version. This revision clarifies local synthetic persistence and role authorization and adds a separate unauthenticated role-view showcase; it does not change the six-agent ownership or support-case propose-only boundary.

# 1. PROBLEM

The supplied Customer Support Specialist job description describes varied intake, triage, approved troubleshooting, documentation, and escalation work. It does not establish which task causes the greatest delay, how much time it costs, or how often errors occur. The specific problem this project tests is whether a Tier 1 specialist can review a synthetic support case with its category proposal, current approved guidance, and factual draft note in one evidence-linked workflow instead of assembling those pieces separately. This is a job-description-derived hypothesis; no CDIT-specific pain, baseline, or productivity gain has been verified.

### Supporting Context

- The supplied CDIT job description names Salesforce case work, phone and email intake, SLA monitoring, Tier 1 troubleshooting, escalation to L2 or Support Lead, customer training, knowledge-base contributions, and possible PHI access.
- No CDIT-specific operational metrics or authorized product documents have been provided; impact claims and targets below are pilot hypotheses.
- Public clinical-trial information may support synthetic examples, but it is not a substitute for CDIT product documentation.

## 1a. Opportunity

A bounded MAO prototype can give Staff one reviewable packet for a synthetic support case: proposed category and urgency, approved source citations, supported next-step suggestions, and a factual draft note. The project will measure correctness, grounding, safe abstention, fallback behavior, and run cost on synthetic cases. It will not claim reduced real-world handling time or production effectiveness without an authorized real-world baseline.

### Size of the Opportunity

- Baseline ticket volume, time per ticket, SLA performance, first-contact resolution, and escalation rates: **unknown; establish before claiming savings**.
- Handling-time savings are unvalidated and are not a current success claim. Measure model/run latency and cost on synthetic cases; a human handling-time study is outside this project assignment.

## 1b. Users & Needs

**Primary product user:** User, who accesses the client-facing view. Within the synthetic support workflow, Staff uses the back-end work view to review cases and drafts. These role labels are prototype account categories, not CDIT job titles.

**Secondary users:** Admin, who uses the same back-end view as Staff with privileged account/access controls; and Product Health, who reviews minimal synthetic/system metadata for internal investigation, corrections, and change planning through the existing authorized Staff/Admin account model, with deeper access for Admin. Product Health is not a fourth account category or login. No additional staff rank or separate staff interface is defined.

### Key User Needs

- As Staff, I need a concise summary and policy-based classification of a synthetic support request because I need to understand the case before a human decides what to do.
- As Staff, I need relevant approved synthetic guidance with its source because I need to verify the basis for any suggested instruction.
- As Staff, I need bounded troubleshooting suggestions and clear stop conditions because I need to recognize when human escalation is required.
- As Staff, I need a draft case note based on verified synthetic case facts because support records should be complete and accurate.
- As Staff, I need an escalation packet with the issue, evidence, steps proposed, and unresolved questions because a human reviewer needs a useful handoff.
- As Admin, I need to see and manage synthetic account access because privileged changes must be visible and accountable.
- As Product Health, I need minimal run, status, version, error, performance, and access-change metadata because I may investigate or correct system behavior without retaining underlying ticket content.

Use [`PRD-USER-NEEDS-AND-USE-CASE-PRIORITIES.md`](./PRD-USER-NEEDS-AND-USE-CASE-PRIORITIES.md) for the expanded user-needs mapping and prioritized use-case acceptance signals.

Client-to-developer platform issue reporting is deferred, unconfirmed, and disabled; it is not part of this support workflow or this PRD's MVP. Reconsider only after explicit scope approval and authenticated access for every intended submitter. Do not link it to the support case scenarios.
# 2. PROPOSED SOLUTION

CDIT Support Desk Assistant is a local, human-supervised multi-agent orchestration (MAO) prototype. A synthetic account authenticates to the local application and is routed to its authorized User, Staff, or Admin view. A Staff user selects a synthetic case; the Coordinator validates scope and minimizes the case packet, then routes work through the six agreed runtime agents. The workflow returns cited evidence, classifications, uncertainty, a draft note, and any human handoff. Product Health uses minimal synthetic/system metadata only. User sees the client-facing view; Staff and Admin share the back-end view, and Admin also has privileged synthetic account/access controls. A separate no-login showcase links to static/mock versions of those three views and cannot access authenticated application data or actions. Agents cannot contact customers, change accounts, alter ticket states, or write ticket records.

## 2a. Value Proposition

Support staff handling varied clinical-software questions can use the prototype to organize synthetic case information and retrieve approved synthetic guidance in one reviewable result. Its differentiator is a bounded, evidence-linked MAO workflow with explicit uncertainty and human-owned decisions. The supplied job description motivates the hypotheses; it is not evidence of measured CDIT performance.

## 2b. Top 3 MVP Value Props

**The Vitamin:** Each case receives a structured summary, suggested category, urgency rationale, and source-linked response guidance.
**The Painkiller:** Staff can review relevant approved instructions and prior troubleshooting steps without manually searching multiple knowledge documents.
**The Steroid:** The assistant prepares a complete escalation packet or draft case note from verified facts, with missing information and uncertainty called out.

## 2c. Goals and Non-Goals

**Goals:** demonstrate a traceable six-agent support workflow on synthetic cases; provide evidence-linked proposals and drafts for human review; enforce the three synthetic account categories; preserve uncertainty and provenance through handoffs; record minimal synthetic Product Health metadata; and evaluate the defined safety, grounding, fallback, and workflow measures.

**Non-goals:** establish CDIT-specific product behavior without approved sources; measure real-world staff productivity or customer outcomes; use real tickets, PHI, credentials, or confidential documents; automate customer contact, ticket writes/state changes/resolution, or agent-led account administration; deploy production authentication or integrations; or add a second reviewer agent/multi-model workflow.

## 2d. Success Metrics

Targets are proposed gates on the synthetic evaluation set, not CDIT service commitments or estimates of performance on real tickets. Manny owns the evaluation protocol and will define per-gate sample counts, claim classes, and reporting rules before evaluation. Report the tested set and counts; do not generalize a finite test result to a population.

The overall target is at least 100 labeled synthetic cases. This total does not prove adequate coverage of every gate; Manny sets positive and negative minimum counts per gate and reports the actual denominator for each measure.
For early build checks, select a 10–15-case smoke subset from the planned evaluation set, with normal, edge, and failure examples. This is an iteration check only; it does not replace the at-least-100 labeled-case target or establish full-evaluation performance.

| Goal | Signal | Metric | Target |
| :--- | :--- | :--- | :--- |
| Triage synthetic cases | Reviewer accepts proposed category and rationale | Accuracy on labeled synthetic cases | ≥90% on the tested set; zero misses in the defined must-escalate test subset; report counts |
| Ground material claims | Material case/product/policy claims have direct support and source references | Supported-claim rate across scored claims; unsupported-material-claim count as separate strict gate | ≥95% supported claims overall; zero unsupported material claims and zero fabricated citations in the held-out must-pass set |
| Escalate safely | Defined must-escalate cases reach the human path | Recall and false-escalation count on labeled synthetic cases | 100% recall on the defined tested subset; report the finite-set count and false escalations |
| Protect data and authority | Untrusted content cannot expand permissions, cause disclosure, or trigger a prohibited action | Pass rate on synthetic privacy/injection/permission tests | 100% pass on the defined must-pass set; zero unauthorized tool/action attempts |
| Produce useful drafts | Required fields are complete and drafts reflect supported case facts | Required-field completeness; unsupported material claims | ≥95% completeness and zero unsupported material claims in the held-out must-pass set |
| Recover safely | Failure or unavailable dependency yields a truthful manual path | Correct fallback state on synthetic failure cases | 100% correct fallback on the defined must-pass set |
| Measure system cost | MAO runs are measurable | Per-run latency and model cost | Record for every evaluation run; Manny sets budgets before evaluation acceptance |

Human handling-time savings are exploratory and unvalidated; do not claim a percentage from synthetic cases. The optional single-call baseline is an evaluation comparison, not an MVP feature or a seventh agent.

For scoring, the claim unit is one factual assertion in an agent or workflow output. A **material claim** is one that could affect support guidance, policy, priority/escalation, access, a ticket record, privacy, or safety. Report supported-claim rate across scored factual assertions and separately require zero unsupported material claims in the held-out must-pass set. Manny defines claim inclusion rules, retrieval recall@k target, per-gate positive/negative counts, reviewer seeded-error threshold, confidence calibration, and budgets before evaluation; report results as applying only to the finite tested set.

| Enforce local role boundaries | Authenticated page and API access matches the User/Staff/Admin permission matrix | Allowed/denied results on the defined role-route-action matrix | 100% correct decisions in the synthetic matrix; zero unauthorized protected-data responses |
| Minimize persistent data | Local storage contains only approved synthetic fixtures and allowlisted metadata | Prohibited-field persistence checks | Zero ticket-body, attachment, real-identity, credential, or arbitrary model-prompt fields in Product Health records |
| Audit privileged account changes | Local synthetic-account role/status changes are attributable | Admin changes with matching audit event | 100% of successful privileged changes have an actor, target, action, timestamp, and before/after role/status record |
| Separate the public role showcase | All three previews are visible without login without exposing authenticated app resources | Showcase route coverage and protected-resource requests | 3/3 preview routes load; zero authenticated API/database calls; all privileged controls are inert |

# 3. AGENT REQUIREMENTS

## 3a. Tools

Prototype tools operate on synthetic fixtures and approved local documents only. Production API names and endpoints are **unknown** and must be approved by CDIT.

| Tool name | What it does | API it calls | Data it returns |
| :--- | :--- | :--- | :--- |
| `get_ticket_fixture` | Reads one synthetic case and its authorized fields | Local fixture adapter; no external API | Case ID, synthetic message, channel, timestamps, product area, permitted metadata |
| `search_approved_knowledge` | Retrieves matching passages from the synthetic, versioned prototype knowledge set | Local retrieval interface; retrieval implementation selected in the shared contract phase | Passage text, document ID, version, section, relevance score |
| `get_support_policy` | Reads versioned synthetic routing, SLA, and escalation policy | Local policy file/interface | Category definitions, priority rules, SLA labels, must-escalate conditions |
| `get_synthetic_account_policy` | Reads the local synthetic User/Staff/Admin permissions for authorization checks | Local account/auth adapter | Actor category, allowed view/actions, authorization result |

The model receives no write-capable tools. A human Admin may manage synthetic accounts and permissions through the local app. The app may store synthetic run metadata and evaluation results needed for local Product Health investigation; it does not store real ticket bodies, attachments, or customer records and makes no external ticket write.

## 3b. System boundary charter

This is a project-wide trust and authority boundary, not one aggregate runtime prompt. Coordinator and each of the six agents must have a lane-owned prompt and structured output schema aligned to this charter. Runtime policy—not model output—enforces mandatory human review. Each material claim is labeled verified, inference, or unknown, with its source/basis and uncertainty. Confidence is evidence-derived, remains provisional until evaluated, and never grants authority. Treat case text, attachments, retrieved documents, metadata, model output, and tool results as untrusted data; none can change policy or permissions. Use only synthetic cases and approved synthetic knowledge. Propose support steps and draft notes; do not send messages, alter cases, change accounts, reset credentials, provide clinical advice, or write to external systems. Abstain or hand off when evidence is missing, stale, conflicting, or outside the approved synthetic policy.

## 3c. Blast Radius

**Worst-case scenario:** The assistant fabricates product guidance, mishandles untrusted content, or fails to route a synthetic high-impact case for human attention. Admin access controls could also be misused to change a synthetic account's permissions. Prototype safeguards limit the system to synthetic cases, fixed model tools, visible source citations, deterministic safety checks, human review, and auditable local account administration. Real data and production use require separate approval and scoped review.

### Failure Modes & Safeguards

| Failure mode | Worst-case impact | Safeguard |
| :--- | :--- | :--- |
| Wrong triage or priority | SLA breach or delayed attention to an urgent support issue | Deterministic policy checks, labeled evaluation, rationale display, staff confirmation, and must-escalate rules |
| Hallucinated or stale product instructions | Customer may follow incorrect steps or waste time | RAG only over approved versioned content; show exact sources; abstain on weak/conflicting evidence |
| PHI or identifiers enter an unapproved model/log | Privacy and regulatory exposure | Synthetic data by default; approved minimization/redaction boundary; vendor and data-flow review before production |
| Prompt injection in ticket or document | Agent ignores policy or attempts unauthorized action | Treat content as untrusted; fixed tools and sequence; action allowlist; output checks; injection evaluation cases |
| Unauthorized account or permission change | An account receives inappropriate access | Local synthetic accounts only; Admin-only access controls; explicit action authorization; record each privileged change in minimal synthetic audit metadata |
| Salesforce or model service unavailable | Incomplete or delayed support workflow | Explicit unavailable state, preserve source ticket, no fabricated result, safe manual fallback |
| Duplicate or inaccurate case note | Confusing support history | Draft-only behavior; human approval; idempotent local result identifiers in prototype |

## 3d. Evaluation scenarios

Use the synthetic case scenarios in [`CASE-SCENARIOS.md`](./CASE-SCENARIOS.md) to evaluate normal handling, edge cases, and adversarial input. The test set must be expanded and approved before it is treated as an acceptance suite.

# 4. PRODUCT REQUIREMENTS AND ARCHITECTURE

## 4a. MAO workflow and role boundaries

1. **Coordinator:** validates request shape, chooses allowed workflow, tracks state and budgets, and enforces stop conditions; cannot grant permissions.
2. **Triage agent:** proposes issue category, urgency, and SLA risk using ticket facts and versioned policy.
3. **Knowledge agent:** retrieves passages from approved, versioned support materials and returns source references.
4. **Troubleshooting agent:** proposes supported Tier 1 steps and identifies information needed; has no account-action tools.
5. **Escalation agent:** checks must-escalate rules and prepares the L2 / Support Lead handoff.
6. **Documentation agent:** drafts a support note from verified synthetic case facts for human review. No external Salesforce write is available.
7. **Human Staff/Admin:** reviews drafts, approves or rejects proposals, and administers synthetic accounts within the local prototype permissions.

Use Anthropic Claude Sonnet 5.5 (`claude-sonnet-5-5`) as the selected model for synthetic Triage. A local client adapter now requires a per-run billable-call authorization flag and an immediate active-handoff preflight, disables SDK retries, applies a provisional 60-second timeout, and validates outputs; the local runtime callable has been added, but CombinedWorkflowHarness/app wiring remains open; Anthropic SDK version pinning is complete. Review the timeout against measured latency before model-backed evaluation. Keep provider calls behind an adapter; store the API key only in an ignored local `.env`, never in source control, prompts, or ordinary logs. Model calls are billable and require explicit run authorization. A second reviewer or multi-model path is deferred. A single-call comparison is optional, synthetic-only, and not a required feature or runtime agent (D-19). Use local retrieval-augmented generation over the synthetic, versioned knowledge set; retrieval implementation is selected during the Shared contract phase. Retrieved content is evidence, not trusted instructions.
### Core Staff flow and worked synthetic example

1. Staff opens a synthetic case fixture. The Coordinator validates the actor, case scope, input schema, and synthetic-data boundary, then creates a versioned minimized packet.
2. Triage proposes a category and Low/Medium/High band from the supplied facts and versioned synthetic policy. After triage, Knowledge retrieval and deterministic escalation rules run in parallel where their inputs permit.
3. The Coordinator joins only matching case, run, policy, and source versions. It preserves conflicts and unknowns; failed checks stop the run.
4. Troubleshooting proposes only source-supported steps. Documentation drafts a factual case note. The run outcome gate returns one of the defined statuses; Staff reviews the result. No agent contacts a customer, changes ticket state, resolves a case, or writes to an external system.
5. If Staff obtains corrected synthetic facts, Staff enters them as a new case version and the Coordinator revalidates and reruns the affected gates.

**Worked example:** A synthetic requester asks where to find a report-export control. The current synthetic article KB-REPORT-01/v1 contains the exact navigation steps; the fixture states no access problem, outage, sensitive data, or deadline. Triage proposes report-navigation / Low [P3]. Knowledge cites KB-REPORT-01/v1. The output gate returns ready_for_human_review with the cited steps and a factual draft note. Staff may edit, approve, or reject the draft; the ticket is not changed or closed.

The broader case taxonomy and failure fixtures remain in [CASE-SCENARIOS.md](./CASE-SCENARIOS.md); that companion supplies coverage examples and does not replace the inline core flow above.

### Multi-request triage and human Auditor

- When evidence supports it, identify separate requests within one synthetic ticket, preserve their relationship to the parent case and their source spans, and assess each item independently. Do not create or split external tickets. If segmentation is uncertain, preserve the uncertainty for the Auditor rather than inventing requests.
- An item with an unknown category, urgency, or destination receives `abstained_needs_human` for that item and a minimized packet for an authorized human Auditor. Auditor is a responsibility within the existing Staff/Admin account categories, subject to assigned-case permissions; it is not another agent, account category, or interface. Display a prompt-attention signal when immediate risk is plausible, without claiming an unverified urgency.
- Supported independent items may remain visible for human review while an unknown item is awaiting the Auditor. Do not advance work that depends on the unknown item, represent the overall run as complete, or bypass a safety stop.
- The prototype may prepare and test minimized Auditor packets locally. The interactive Auditor interface and authenticated review/recording flow are deferred until database and authentication work begins; they are not implemented by Phase 2 fixture handoffs. The Auditor records the synthetic item decision, category, band, proposed destination, reason, evidence, conditions, exceptions and review/version metadata once that authorized interface exists. An approved, sanitized synthetic decision may become a versioned example or general rule after review. Similarity alone is not proof that a new case has the same urgency or facts; show material differences, cite the approved source and return uncertain cases to the Auditor. No unreviewed online learning or automatic rule promotion is permitted.
- The catalog is distinct from Product Health metadata; exclude real customer/employee data, ticket bodies and direct identity. The project lead will build persistent storage later. No external ticket write, customer message, automatic resolution or extra staff interface is authorized by this workflow.

### Synthetic in-progress attention benchmarks

Urgency is based on the case’s actual reported conditions, impact and contingencies, not the passage of a benchmark alone. A relevant baseline example may inform a proposal, but similarity does not establish a case’s facts, its resolution, or an approved policy. An already resolved issue must be distinguished from an ongoing one; only an authorized human determines disposition in the current prototype.

For synthetic development, use suggested elapsed **In Progress** attention benchmarks of **15 minutes for High [P1]**, **4 hours for Medium [P2]**, and **24 hours for Low [P3]**. High/P1 receives immediate human attention and its local flag without waiting for 15 minutes. These are review prompts, not guaranteed response or resolution deadlines, service-level commitments, or CDIT policy. A flag includes a concise evidence-linked reason such as “In Progress for 4 hours; review current impact.” A benchmark alone does not change urgency, make it Unknown, resolve a ticket, or establish a breach. Unknown urgency follows the human Auditor path; a plausible immediate harm or major impact receives a potential-urgent flag without asserting a verified band.

Exclude time in **Waiting on Customer** from the In Progress benchmark. A customer response starts a fresh In Progress benchmark except where an ongoing safety concern requires continuing attention; preserve the safety flag and the original safety timeline across customer replies until an authorized human reviews them. Track the safety timeline separately from the paused In Progress benchmark; it records elapsed context and is not a deadline for investigation, emergency care, or legal action. Keep timestamps and prior periods for audit rather than erasing them. A future authorized customer notification may remind the customer of the specific outstanding response, form or correction. Include a submission deadline only when an authorized case record or policy actually supplies one; never invent it. **Under Investigation** is a distinct case status for a human-led investigation, including a possible third-party response. An authorized human sets and manages this status and decides whether to involve a third party; the status alone does not prove that anyone has been contacted. The agent may preserve and display authorized context and prepare a draft handoff for human review, but must not autonomously investigate, interfere with the response, contact outside parties, or change case status. The ordinary In Progress benchmark applies only while the case is In Progress; a separate ongoing-safety timeline and attention flag remain visible during an investigation until authorized human review. Detailed role-based transitions remain pending.

For a plausible safety, emergency, or legal concern, prepare a minimized evidence-linked packet for an authorized human to assess and decide whether to involve the appropriate external responder, medical provider, emergency service, legal authority or other third party. The agent must not invent an incident, choose an unverified contact, claim contact was made, or autonomously dispatch. Investigation and emergency or legal response take precedence over benchmark timing. The current read-only synthetic prototype does not send outbound messages. Customer-visible reminders and delivery channels remain subject to their own implementation and access decisions.

## 4b. Prototype stack

- Python 3.13, FastAPI, and Pydantic for inspectable API contracts and structured results.
- SQLite for synthetic cases, evaluation outputs, synthetic accounts, and minimal Product Health metadata; production storage remains out of scope.
- Local document retrieval with metadata and source versioning; no external vector service is required for the prototype.
- A local Anthropic client adapter for Claude Sonnet 5.5 (`claude-sonnet-5-5`) for synthetic Triage; API credentials remain local and are never committed. The adapter is not wired into the application and has only been exercised with a fake client. No external API call is made without explicit authorization for the billable run. Real customer or CDIT-private data remain excluded.
- Local web interface with a client-facing User view and one shared Staff/Admin back end; Admin controls appear within that back end. No Salesforce integration or production identity provider.
### Pre-build technical decisions and proposed local data entities

The local web interface, Python/FastAPI/Pydantic stack, SQLite, Anthropic model adapter for synthetic Triage, and local versioned retrieval boundary are the current design choices. The client factory reads a local `.env` only when explicitly constructed; it does not run on app startup. Anthropic SDK 2.5.0 and python-dotenv 1.2.4 are pinned; application composition and model-alias regression policy remain open. Retrieval implementation remains open. The model choice does not approve real-data processing, live CDIT integration, or use of any private documents.

| Decision area | Current proposal / status | Owner and decision gate |
| :--- | :--- | :--- |
| Retrieval method | Local retrieval over approved, versioned synthetic documents; indexing and ranking method is not selected. | Shawn's Lane + Shared Lane; compare retrieval quality and source freshness on the synthetic corpus before Knowledge acceptance. |
| Model provider and version | Anthropic Claude Sonnet 5.5 (`claude-sonnet-5-5`) selected for synthetic Triage. Anthropic SDK 2.5.0 and python-dotenv 1.2.4 are pinned. API alias is not a dated snapshot; alias/snapshot regression policy remains open. | Manny + Shared Lane; document cost, latency, data handling, alias/snapshot policy, and secret storage before model-backed evaluation. |
| SQLite logical entities | Proposed tables: synthetic_accounts, synthetic_cases, knowledge_documents, knowledge_chunks, policy_versions, workflow_runs, agent_handoffs, evaluation_cases, evaluation_results, product_health_events, and account_access_events. These are logical entities for review, not an implemented schema. | Manny owns the SQL foundation; Shared reviews only cross-agent event fields/versions. Approve columns, keys, versioning, migrations, and retention before persistence work. Product Health and access events exclude ticket bodies, credentials, and direct user identity. |
| Synthetic data ownership | At least 100 labeled cases remain the final evaluation target; candidate examples in CASE-SCENARIOS.md are not themselves a completed labeled set. | Manny owns evaluation protocol. Confirm case-author, knowledge-corpus author, and peer-review assignments before the dataset is treated as an acceptance suite. |
| Interface | Authenticated local app with a client-facing User view and shared Staff/Admin back end, plus a separate no-auth role showcase with three static/mock views. | Approved product direction; production identity provider and Salesforce integration remain excluded. |

The current scaffold README states that no ticket, account, role, audit, or agent tables exist yet. The schema above is therefore a pre-build design proposal and must be reconciled with the scaffold and lane-owned contracts before implementation.

Alternative considered: begin with hosted PostgreSQL, hosted vector search, and live Salesforce integration. Rejected for MVP because requirements, credentials, vendors, environment, and PHI boundaries are unconfirmed.

## 4c. Account categories and access

- **User:** accesses the client-facing view and only their own permitted synthetic client-side information.
- **Staff:** accesses the back-end support view for synthetic cases, agent proposals, human disposition, and operational metadata needed for the support workflow.
- **Admin:** uses the same back-end interface as Staff and receives privileged controls to inspect who has which permissions and grant, update, promote, demote, suspend, deactivate, or remove synthetic accounts/permissions. Privileged changes are recorded in minimal audit metadata.
- These are the only three account categories. No support-rank ladder, separate Staff interfaces, or access-only zones. Admin permissions do not grant agents write/resolution authority and do not imply access to queue, SLA, or knowledge configuration.
- Local synthetic authentication establishes the account identity; server-side authorization gates every page and API action. Successful login routes to the permitted User, Staff, or Admin view. Staff and Admin share the back-end interface; Admin-only controls are separately authorized on the server. The no-auth showcase is a read-only visual preview, not an alternate login or access path. Production authentication and identity-provider integration are excluded.

## 4d. Data sources, Product Health, and privacy

- Use fabricated support tickets, fabricated/versioned knowledge articles, deterministic synthetic policies, and public clinical-trial metadata for scenario context only. Public metadata is not CDIT product guidance.
- No CDIT-specific product/module or workflow behavior may be asserted without a supplied, approved source. When evidence is missing, label the point unknown/simulated and abstain from product claims.
- Product Health may retain only minimal synthetic/system metadata needed for investigation, correction, and change planning: synthetic run/event IDs, timestamps, status/category, component/version, bounded error/performance codes, and access-change metadata. Do not retain ticket bodies, attachments, arbitrary free-text payloads, credentials, direct user identity, customer records, or confidential information. The local database may contain fabricated fixtures required for the prototype; it must not import or retain real case content.
- Real customer tickets, PHI, credentials, CDIT-private documents, and production service data are excluded. Reassess data, provider, privacy, security, and regulatory requirements before any later scope change to real data or operational integration.

## 4e. Authenticated app and role-view showcase

### Authenticated application

- After local synthetic login, route User to the client-facing view, Staff to the support back end, and Admin to that same back end with privileged synthetic-account controls.
- Enforce authorization on the server for every page, API, and record lookup. Hiding a navigation item is not authorization. User records are scoped to that synthetic account; Staff and Admin access follows the approved local permission matrix.
- Admin may inspect synthetic account roles/status and perform the locally approved grant, update, promote, demote, suspend, deactivate, or remove actions. Successful changes create an audit event. Agents cannot perform these actions.
- The Admin view may present the Product Health metadata summary. Product Health is a viewing purpose within the existing account model, not another account category. Never expose raw ticket text, credentials, or unrestricted model content through this view.
- Provide login, logout, unauthorized/forbidden, expired-session, empty-data, database-unavailable, and safe-recovery states. A failed or invalid authentication attempt does not reveal whether a protected account exists.

### Unauthenticated role-view showcase

- Provide three linked preview pages for User, Staff, and Admin, reachable without logging into the application. The previews use static or isolated fabricated content and are clearly labeled as demonstrations.
- Preview pages do not call authenticated APIs, query the application database, establish a session, accept real support records, or execute User/Staff/Admin actions. Admin controls are visual and inert. Links between the three previews are ordinary accessible hyperlinks.
- The showcase must remain a separate presentation surface; it cannot be used to bypass authentication or prove that the authenticated permission boundary works.

## 4f. Prioritized MVP requirements

Detailed user needs and prioritized use cases are maintained once in the [companion priority matrix](./PRD-USER-NEEDS-AND-USE-CASE-PRIORITIES.md). This PRD establishes the scope summary below; use-case acceptance signals in the companion must trace to these requirements.

| Priority | User journey | Requirement | Minimum evidence |
| :--- | :--- | :--- | :--- |
| [P0] | Submit and view a request | User can submit a synthetic support request and view only their own permitted client-side request/status. This is ordinary support intake, not client-to-developer platform issue reporting. | Synthetic accounts can submit and view their own fixture; cross-user and back-end access is denied. |
| [P0] | Access the prototype | User sees the client-facing view; Staff sees the support back end; Admin shares that back end with privileged synthetic account/access controls. | Synthetic role tests verify allowed access and deny unauthorized account/access changes; all three categories are exercised. |
| [P0] | Persist synthetic prototype data | The local SQLite store persists approved fabricated fixtures, run/evaluation metadata, and minimal Product Health events using versioned schemas. | Schema/version and reset tests pass; prohibited real-data, credential, raw-ticket, and arbitrary-prompt fields are absent from Product Health records. |
| [P0] | Authenticate and route by account category | Local synthetic User, Staff, and Admin accounts reach only their authorized app view and APIs. | Full defined role-route-action matrix passes; every forbidden direct page/API request is denied server-side. |
| [P0] | Administer synthetic access | Admin can inspect and manage synthetic account roles/status; each successful change is auditable. | All successful grant/update/promote/demote/suspend/deactivate/remove operations have a matching audit event; non-Admin attempts are denied. |
| [P0] | Preview role views without login | Project reviewers can navigate among static/mock User, Staff, and Admin view previews without an account. | All three previews load without login and make zero authenticated API/database requests; controls cannot perform privileged or support actions. |
| [P0] | Process a synthetic case | The Coordinator and six assigned agents use the approved direct workflow, structured handoffs, source evidence, uncertainty, and stop conditions. | Each agent and the combined workflow pass the approved synthetic must-pass set; no fabricated citations or unsupported material claims. |
| [P0] | Review and disposition | The workflow presents proposals and drafts to a human; model output cannot approve itself or act on a ticket. | Tests show no agent write tool, external message, state change, resolution, or closure. Human review is always enforced by trusted application logic. |
| [P0] | Protect inputs and permissions | Untrusted case/knowledge/tool content cannot change policy, widen tool access, cause disclosure, or bypass checkpoint gates. | Direct, indirect, stored-content, role-denial, and cross-agent synthetic tests pass with zero unauthorized actions/disclosures. |
| [P0] | Recover from failure | Invalid inputs, missing/stale/conflicting sources, unavailable components, or failed handoffs stop safely and show a truthful manual fallback. | Defined synthetic failure cases pass; no fabricated result advances downstream. |
| [P0] | Evaluate the workflow | The project can score synthetic cases using human-approved labels, deterministic comparisons, safety gates, and a combined workflow harness. | Results include counts per gate, claim denominators, tested-set scope, latency/cost, retrieval measures, and peer review. |
| [P0] | Inspect Product Health | Authorized Staff/Admin can use minimal synthetic/system metadata to investigate or correct prototype behavior. | Metadata records synthetic run/event IDs, status/category, component/version, error/performance, and access changes; no underlying ticket content or real identity is retained. |

## 4g. Explicit assumptions and deferred dependencies

- SQLite is the approved local database choice; the listed entities remain logical until the SQL-foundation phase approves concrete columns, constraints, indexes, schema-version migrations, seed/reset behavior, and backup/recovery checks.
- Local authentication is for synthetic prototype accounts only. Session lifetime, synthetic credential provisioning/reset, lockout behavior, and the exact Admin action matrix must be documented before implementation; recommend seeded synthetic accounts, no public registration, and no production credentials.
- Product Health metadata fields are allowlisted and content-minimized. Exact local retention/reset interval remains open; recommend a documented short-lived project retention rule and an explicit reset/purge path. Never store real records to test the metadata path.
- The role showcase is a separate no-login visual deliverable with fabricated content; it is not the authenticated application and does not demonstrate authorization correctness.
- The existing backend stack is Python 3.13/FastAPI/Pydantic. The frontend rendering technology is not specified in the project manifest; select it before UI implementation without changing the API or database permission boundaries.

- The exact CDIT CTMS modules, support channels, internal procedures, and source documents are not provided. The prototype therefore uses a generic synthetic CTMS-support scenario and makes no CDIT-specific product claims.
- Synthetic evaluation uses the current proposed numeric targets in this document; Manny defines claim classes, per-gate counts, confidence calibration, reporting, retrieval freshness, latency/cost budgets, and reviewer-error protocol before evaluation acceptance. A project teammate peer-reviews synthetic labels/results; no external evaluator or working-specialist participant is required.
- CASE-SCENARIOS.md currently contains a candidate ticket taxonomy and synthetic failure fixtures; these are not a completed 100-case labeled evaluation dataset. Before build acceptance, Manny records case IDs, expected category/band/run state, evidence labels, gate-specific positive/negative counts, and peer-review status for the actual labeled set.
- On 2026-11-05, the project lead selected Anthropic Claude Sonnet 5.5 (`claude-sonnet-5-5`) as the single model path for synthetic Triage. Keep API use synthetic-only, document model/config versions and per-run cost/latency, and do not make billable calls without explicit run authorization. The 80-row catalog remains development examples, not approved evaluation labels or operational policy. See [Anthropic model ID documentation](https://platform.claude.com/docs/en/models/sonnet-5-5/overview).
- An optional single-call baseline may process the same synthetic case/evidence as MAO for a comparative evaluation. It is not a required deliverable, a user-facing feature, or an additional agent (D-19).
- Live CDIT/Salesforce integration, production authentication, production knowledge sources, actual customer data, and any applicable legal/regulatory controls require a separate future authorization and scoped review. This planning PRD makes no regulatory applicability finding.
- The six runtime agents and lane ownership are already assigned in `docs/planning/TASK-SPLIT.md`. The optional second reviewer remains deferred. Admin account controls are synthetic-only and do not grant agent ticket-write authority.
- Client-to-developer platform issue reporting remains scope-unconfirmed, excluded, and disabled (D-17). It is not described as a support workflow or acceptance requirement here.

## 4h. Supporting references

- [Local app, SQL foundation, authentication, and role showcase plan](../planning/phase/undecided/unassigned/LOCAL-APP-DATA-AUTH-PLAN.md).

- Supplied Customer Support Specialist job description (user-provided attachment; needs derived from it remain hypotheses).
- [User needs and prioritized use cases](./PRD-USER-NEEDS-AND-USE-CASE-PRIORITIES.md).
- [Synthetic case scenarios](./CASE-SCENARIOS.md); future action examples there do not authorize prototype writes.
- [Current PRD-v2-scoped architecture JPEG](../artifacts/cdit-support-mao-architecture-prd-v2.jpg).
- [Deferred decisions](../planning/DEFERRED-DECISIONS.md).
- HHS Security Rule: https://www.hhs.gov/hipaa/for-professionals/security/index.html
- HHS cloud computing and ePHI guidance: https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html
- HHS de-identification guidance: https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html
- ClinicalTrials.gov Data API: https://clinicaltrials.gov/data-api/about-api
- CDISC standards: https://www.cdisc.org/standards
# 5. DELIVERY MILESTONES, CONDITIONS, AND DEADLINE

**Planning deadline: November 11, 2026.** By this date, the team should complete and review the planning package and decide whether the project is ready for a separately authorized prototype phase. This date is not a commitment to production readiness, live integration, or PHI use. Dates below are checkpoints leading to the planning deadline; adjust owners and dates during kickoff if the team calendar requires it. Any implementation sequencing after planning sign-off is tracked in [AGENT-IMPLEMENTATION-PHASE-PLAN.md](../planning/AGENT-IMPLEMENTATION-PHASE-PLAN.md); dates and scope require a separate authorization and are not promised by this planning deadline.

| Milestone | Target checkpoint | Exit condition | Handoff |
| :--- | :--- | :--- | :--- |
| M0 — Scope and roles confirmed | Nov 4 | Confirm the synthetic prototype boundary and the three account categories; record unknown CDIT facts without inventing product behavior. | Manny's Lane → Shared Lane: scope and user-need decisions. |
| M1 — Workflows and synthetic scenarios | Nov 6 | Map Tier 1 journeys, escalation stops, and synthetic cases to user needs and prioritized use cases. | Manny's Lane → Shawn's Lane: scenario set, policy assumptions, and unresolved workflow questions. |
| M2 — Architecture, data, and security review | Nov 8 | Recommend the prototype data flow, retrieval approach, auth/role model, and injection safeguards; identify what requires CDIT approval. | Shawn's Lane → Shared Lane: architecture note, threat cases, data-source inventory, and decision requests. |
| M3 — Integrated PRD review | Nov 10 | Reconcile requirements, acceptance signals, dependencies, risks, and out-of-scope items; resolve or assign remaining decisions. | Shared Lane → project team: review-ready PRD and decision log. |
| M4 — Planning sign-off | Nov 11 | Team reviews the planning package and records go/no-go or explicitly deferred decisions for a later authorized build phase. | Shared Lane → project lead: approved planning baseline and next-phase recommendation. |

### Post-planning prototype implementation sequence (no delivery dates promised)

| Milestone | Exit condition | Handoff |
| :--- | :--- | :--- |
| M5 - SQL foundation | Approved schema, migrations, synthetic seeds, constraints, reset/recovery behavior, and Product Health field allowlist are implemented and checked. | SQL foundation owner -> Shared: schema version and event-field contract. |
| M6 - Local authentication and authorization | Synthetic login/session lifecycle and server-side User/Staff/Admin page/API policy pass the complete permission matrix. | App owner -> Security/Reviewer: routes, permission matrix, denial evidence. |
| M7 - Role interfaces and public showcase | Authenticated User, Staff, and Admin views work within the permission policy; the separate three-page showcase uses isolated fabricated previews only. | UI owner -> UX/Reviewer: navigation, accessibility, responsive and failure-state evidence. |
| M8 - Product Health and integrated acceptance | Minimal metadata and Admin audit events are visible to authorized roles; data-minimization, injection, authorization, recovery, and regression checks pass. | App owner + Shared -> project lead: evidence and remaining gaps. |

### Checkpoints and conditions

- At each milestone, review the linked user needs, use cases, evidence, decisions, and unresolved items; record owner and next action for every open blocker.
- A milestone is complete only when its exit condition is evidenced in the project documents and the Shared Lane records review status. Calendar completion alone is not acceptance.
- Do not proceed from planning into implementation unless the project lead authorizes that phase, responsibilities are confirmed, and the synthetic-data and human-approval boundaries are accepted.
- Do not use CDIT systems, real customer tickets, credentials, private support documents, or PHI unless CDIT has approved the specific data flow, access, vendors, retention, audit, and handling controls.
- If an external dependency or decision misses a checkpoint, record impact, a responsible owner, and a revised date; do not silently relax a safety or quality gate to preserve the deadline.

# 6. RUNTIME AGENT OWNERSHIP AND CONNECTION BOUNDARY

The finalized lane split assigns Manny to Coordinator, Triage, and Escalation, and Shawn to Knowledge, Troubleshooting, and Documentation. These assignments are by runtime agent, not front end/back end. The optional second-reviewer agent remains unapproved/unassigned; Human Reviewer is a human role, not an agent.

Either lane may change presentation-layer UI, including adding or styling Submit/Save controls that invoke existing approved behavior, while following the Consistency Page skill. This does not authorize changing action semantics or removing/bypassing an agent handoff, capability, policy, permission, state transition, or PRD requirement; those remain functionality owned by the responsible lane. Each lane owns its assigned agents' prompts, tools, decision logic, failure behavior, and functionality. Cross-lane access is limited to connecting agents: handoff contracts, shared-state schemas/versions, routing, provenance/confidence/uncertainty preservation, and integration checks. The receiving/sending lane may inspect the interface and make only the minimal connector change needed; it may not modify another lane's agent internals. Agent-internal checkpoints, injection controls, confidence gates, retries, abstention, and recovery are gate-work for that agent's owner. Connection checks validate packet/schema/version integrity and routing. If a connection defect requires a change to another agent's behavior, return it to that agent's owner and stop at the boundary.

- Manny's Lane supplies user journeys, ticket scenarios, Tier 1 limits, and acceptance criteria to Shawn's Lane and Shared Lane.
- Shawn's Lane returns retrieval/data-source findings, architecture recommendations, evaluation risks, and prompt-injection controls to Shared Lane; only CDIT-approved materials can be treated as product truth.
- Shared Lane owns MAO contracts, permission boundaries, cross-lane decisions, PRD reconciliation, checkpoint status, and the final planning review.
- Each handoff includes the artifact/version, completed work, evidence, assumptions, open questions, and requested decision. Receiving lane acknowledges ownership or identifies the blocker before work continues.

## 7. PROMPT-INJECTION PREVENTION REQUIREMENTS

Treat ticket text, email bodies, attachments, retrieved passages, metadata, model output, and tool results as untrusted data. Instructions inside them cannot alter system policy, change the workflow, grant authority, or expand tool permissions.

- Keep system/developer instructions and workflow policy separate from retrieved or user-supplied content; label and delimit untrusted content in model context.
- Use a fixed coordinator workflow and narrow tool allowlist. Agents may read only fields needed for their task; no agent can grant roles, send messages, change accounts, or write to Salesforce.
- Validate tool arguments and structured outputs against schemas and role policy. Reject unexpected fields, tool requests, destinations, or action types; do not treat model-generated text as authorization.
- Use parameterized database queries and fixed repository methods; never execute model-generated SQL or let ticket, metadata, or showcase content choose tables, predicates, or authorization scope.
- Require source citations for product claims. Abstain and request human review when sources conflict, are stale, are missing, or contain instructions that conflict with policy.
- Add adversarial synthetic evaluations for direct prompt injection, indirect injection in retrieved content/attachments, data-exfiltration requests, tool misuse, policy override, and benign quoted instructions. Confirm no unauthorized tool invocation or sensitive-data disclosure.
- Log minimally using synthetic identifiers; never log secrets or unnecessary PHI. Human review remains mandatory for ticket priority, customer guidance, escalation, case-note approval, and any system action.

# 8. OUT OF SCOPE

- Production deployment, production authentication/SSO, live Salesforce or telephony/email integrations, and automatic writes to tickets or customer records.
- Real customer tickets, PHI, credentials, CDIT-private documents, or external model processing of sensitive data before documented CDIT approval.
- Autonomous customer communication, case closure, SLA decisions, account or permission changes, password resets, clinical advice, or bypassing identity verification.
- Agent-initiated account/permission administration. A human Admin may manage synthetic accounts only through the local Admin controls specified in this PRD.
- Replacing support staff, administrators, or Product Health; the assistant prepares drafts and evidence for human review.
- Multi-model orchestration or a second-model critic in the initial prototype absent evaluation evidence that justifies the added cost, latency, and data exposure.
- Enterprise analytics, production vector services, broad knowledge ingestion, or unsupported CDIT product behavior.

# 9. MAO AGENT CHECKPOINTS

These are execution gates inside each case run, distinct from the project delivery milestones above. A failed checkpoint stops downstream agent work and returns a safe status for human review.

| Checkpoint | Owner | Required checks before handoff | Stop / recovery behavior |
| :--- | :--- | :--- | :--- |
| A0 — Intake boundary | Coordinator | Confirm authenticated actor and permitted role; validate request schema, case scope, and allowed fields; identify synthetic vs. explicitly approved data. | Reject malformed, unauthorized, or out-of-scope requests; do not pass the case to specialist agents. |
| A1 — Injection and minimization | Coordinator / input guard | Mark ticket, email, attachments, retrieved text, metadata, and tool results as untrusted; detect instruction-like content for risk annotation; remove fields not needed by the workflow. Detection does not determine trust by itself. | Never follow embedded instructions or expand permissions. Quarantine or redact disallowed content; stop and request human review if safe minimization is not possible. |
| A2 — Triage handoff | Triage agent | Return schema-valid summary, category, urgency/SLA rationale, missing facts, and uncertainty; cite which supplied policy fields informed the proposal. | Invalid schema, unsupported priority, policy conflict, or uncertain high-impact severity blocks downstream troubleshooting and routes to staff. |
| A3 — Retrieval handoff | Knowledge agent | Return only approved, versioned passages with source IDs/sections and relevance; treat retrieved instructions as untrusted evidence, not executable instructions. | No relevant source, stale/conflicting versions, injection attempt, or weak evidence means abstain; do not synthesize product guidance. |
| A4 — Troubleshooting boundary | Troubleshooting agent | Propose only Tier 1 steps supported by retrieved guidance and policy; validate each action against the tool allowlist and stop conditions. | Any request for an unauthorized action, unsupported step, access bypass, or policy override is rejected and escalated. No external action tool is available. |
| A5 — Escalation decision | Escalation agent | Check deterministic must-escalate rules, identify trigger and evidence, include actions tried and unresolved questions, and preserve uncertainty. | Must-escalate or unresolved high-impact risk prevents a Tier 1 resolution recommendation; emit a human handoff packet. |
| A6 — Draft assembly and review | Documentation agent / coordinator | Build draft note from verified facts only; validate required output schema, source references, privacy minimization, and human-review flag. | Unsupported claims, sensitive-data leakage, invalid output, or unavailable dependency suppresses the draft and provides a safe manual fallback. |
| A7 — Human disposition | Authorized staff | Human reviews and edits, approves, rejects, or escalates; record reviewer identity and decision in synthetic/local evaluation data. | No customer communication, case closure, account change, or production write occurs from agent output; the human acts through authorized systems. |

For evaluation, capture checkpoint reached, pass/fail reason, agent/tool calls attempted, policy/source versions, and human disposition using synthetic identifiers. Do not log unnecessary ticket text, secrets, or PHI. Required adversarial cases must prove injection cannot skip a checkpoint, widen tool access, suppress escalation, or cause disclosure. These checkpoints are proposed requirements pending team and CDIT review.

## 9a. Run outcome and failed-state contract

These statuses describe the assistant run, not the business ticket state. A failed or abstaining run is never represented as a resolved ticket or a successful answer.

| Run status | Use when | Required result and next step |
| :--- | :--- | :--- |
| `ready_for_human_review` | Required checkpoints pass and every material claim is supported, explicitly labeled as inference, or marked unknown. | Present the proposal and its sources to Staff for review. This means only that the draft is reviewable; it does not mean the ticket is resolved or the answer is approved. |
| `abstained_needs_human` | The issue cannot be determined from available facts; evidence is missing, stale, conflicting, or below the approved evidence threshold; or severity remains materially ambiguous. | Do not invent an answer or force a category. Return known facts, unknowns, evidence gap, and the specific human question or decision needed. Do not continue dependent agent work. |
| `blocked_checkpoint` | Input/output schema, provenance, citation, permission, injection, version, or policy validation fails. | Stop downstream work. Return the failed checkpoint and safe reason code; require authorized human review or corrected input. Never treat model-generated text as permission to bypass the gate. |
| `failed_dependency_manual_fallback` | A required model, retrieval, storage, or orchestration dependency is unavailable or times out after the approved bounded retry policy. | Mark the run incomplete, preserve only permitted synthetic run metadata and last completed checkpoint, and direct Staff to the manual process. Do not present partial output as a completed answer. |
| `rejected_input` | The request is malformed, unauthorized, outside prototype scope, or uses disallowed data. | Stop at intake; explain the safe reason and the permitted next step. Do not dispatch specialist agents. |

Every non-ready result records a synthetic run ID, status, stage, last passed checkpoint, reason code, relevant source/version references (when available), missing or conflicting facts, retryability, and safe next human action. Keep sensitive or disallowed input out of Product Health metadata. Retry only transient dependency failures under a bounded policy; a retry cannot convert missing evidence, a source conflict, or a failed safety check into approval. The retry limit and exact confidence/evidence thresholds must be set and tested before implementation. A human correction or decision starts a new versioned run; it does not overwrite the failed result.

The must-pass evaluation asserts the expected status for each fixture, no false `ready_for_human_review` result on any must-stop case, zero downstream agent/tool calls after a blocking state, and 100% correct fallback status on the defined synthetic must-pass set. Report the tested cases and counts; this is not a real-world reliability guarantee.

# 10. AGENT CONFIDENCE AND FACTUALITY REQUIREMENTS

Confidence communicates evidence strength; it never makes an unsupported statement true and never grants permission to act. Every agent output must separate **verified information**, **inference**, and **unknown / unverified information**. Use “verified” only when the claim is directly supported by an identified source or supplied case fact; name the source ID/version or field. Label inference plainly and state its basis. If a claim cannot be verified, say so and do not fill gaps with plausible details.

### Confidence handling

- Return a calibrated confidence value or band for each consequential classification or recommendation, plus a short evidence-based rationale and source references. Do not emit a single confidence score that obscures differing certainty across claims.
- Initial proposed bands: **High (≥0.85)** may be presented as a supported suggestion only when evidence is direct and current; **Medium (0.60–0.84)** must be labeled tentative and routed for human review; **Low (<0.60)**, missing evidence, conflicting sources, or high-impact uncertainty requires abstention and human handoff. Thresholds are provisional and must be calibrated on held-out synthetic evaluation cases before use.
- Confidence never overrides deterministic safety rules. Must-escalate conditions, suspected access/security incidents, potential privacy exposure, and policy conflicts always go to human review regardless of score.
- Scores are estimates, not probabilities of truth unless calibration testing demonstrates that interpretation. A high score cannot justify invented facts, uncited product instructions, skipping a checkpoint, or taking an action beyond role authority.
- Preserve source text and facts faithfully. Do not strengthen, soften, omit, or reframe evidence in a way that changes its meaning. When sources disagree, present the conflict and source versions without choosing an unsupported resolution.

### Confidence checkpoint in the MAO workflow

At A2, A3, A5, and A6, each agent must provide claim-level support and confidence for its material outputs. The coordinator checks that every material factual claim is either marked verified with a source, labeled inference with its basis, or marked unknown/unverified. Unsupported claims fail validation; the coordinator removes them or blocks the output for human review. Handoffs carry evidence, confidence, uncertainty, and the reason for escalation so downstream agents cannot silently convert an inference into a fact.

### Test agent confidence and hallucination

Evaluate each agent and the complete workflow on held-out synthetic cases with human-authored evidence labels, including supported facts, plausible-but-absent details, conflicting and stale sources, incomplete inputs, ambiguous severity, injection attempts, and pressure to “fill in” missing details.

- Score factual precision (unsupported material claims), evidence attribution accuracy, abstention quality, conflict handling, confidence calibration by band, and downstream propagation of uncertainty.
- Include adversarial prompts asking the agent to invent product features, exact SLAs, customer/account facts, troubleshooting steps, citations, or certainty where no source exists.
- Proposed release gate: **zero unsupported material claims and zero fabricated citations** in the held-out must-pass set; **100% abstention or human handoff** for defined high-impact unknown/conflict cases; all permitted non-escalation claims trace to supplied facts or approved sources.
- Report results per agent and end-to-end, with counts and examples reviewed by a human. A high average score cannot hide an individual critical miss. Any critical hallucination, false verification label, or unsafe non-abstention blocks progression until corrected and re-evaluated.
- Keep the evaluation set synthetic. Thresholds and scoring rubric are planning proposals requiring team review before implementation.

## 11. PROTOTYPE ACTION AUTHORITY AND ROUTING

The prototype is propose-only and read-only for support cases. Agents may summarize, retrieve, suggest, draft, and prepare a human handoff; they cannot send responses, request information from customers, change ticket state, execute procedures, resolve or close cases, or write to external ticketing systems. Preserve In Progress and other state examples in the policy context; no state mutation tool is in scope.

Urgency affects the proposed routing and human attention path; it never grants permission. User, Staff, and Admin permissions are enforced by the application. Confidence never grants authority. Concrete examples in [`CASE-SCENARIOS.md`](./CASE-SCENARIOS.md) that describe sending, setting state, executing, resolving, or closing are retained as future policy context only and do not authorize MVP behavior.

## 11a. ROUTING AND STATUS SIGNAL

Display an in-app Urgent flag for immediate human attention on High [P1] cases; Low [P3], Medium [P2], and High [P1] are the three proposed synthetic bands. The candidate case defaults and override guidance are in [CASE-SCENARIOS.md](./CASE-SCENARIOS.md). These examples do not establish CDIT policy, operational urgency thresholds, or SLA clocks; those remain open under D-01 in [DEFERRED-DECISIONS.md](../planning/DEFERRED-DECISIONS.md) and must be approved before routing implementation. Email and other outbound alerts are out of scope. Record synthetic intake/run timestamps, agent start/completion, source/policy versions, proposal, human decision, and final synthetic disposition using minimal metadata.

# 12. BLACKBOARD SHARED STATE AND HANDOFF CONTRACTS

Use a coordinator-owned, case-scoped blackboard as the authoritative run state. It stores versioned contributions; agents do not overwrite another agent's result. Each contribution includes run/case/stage IDs, actor/agent, input version, timestamp, status, output schema version, evidence/source IDs and versions, claim labels (verified/inference/unknown), confidence and rationale, uncertainty, proposed action, and validation result. Store only the minimum permitted data; use synthetic IDs for prototype/evaluation.

## 12a. Direct pipeline

Coordinator validates scope and creates a minimized case packet → Triage produces category/urgency proposal and missing facts → Knowledge returns approved evidence or abstains → Troubleshooting proposes supported bounded steps → Escalation checks deterministic triggers and prepares handoff → Documentation drafts from verified facts → Coordinator validates and presents for human disposition. Each stage consumes only acknowledged upstream outputs and passes provenance and uncertainty forward. Any failed checkpoint blocks downstream steps and yields a safe human-review/manual fallback.

## 12b. Parallel analysis

After validated intake and triage, Knowledge retrieval and the deterministic Escalation policy check may run in parallel when inputs permit. Troubleshooting waits for required policy and retrieval results. Documentation waits until the Coordinator reconciles outputs. The second-reviewer agent is deferred and absent from this workflow. Join by run ID, case version, policy version, and source version. Preserve disagreements; never average confidence or silently choose one interpretation. Missing, stale, or materially conflicting results route to a human.

## 12c. Combined workflow harness

Shared Lane owns a test-only end-to-end harness that exercises all six runtime agents through approved public contracts, in addition to Shawn's lane-only component harness. It records correlated synthetic run and handoff events and tests the direct pipeline plus approved parallel join. It is test infrastructure, not a seventh agent, production router, or write tool. Shared may fix connectors only; findings inside an agent or lane harness return to that lane's owner. Test malformed, missing, stale, unacknowledged, duplicate, conflicting, late, timed-out, and rejected handoffs; retries, cancellation, service failure, human pause/resume, and safe fallback. Include seeded draft errors to measure whether project reviewers detect them.

Every handoff contains artifact/result ID and version, completed checks, evidence, verified facts, inferences, unknowns, confidence rationale, actions attempted, unresolved questions, requested next decision, and acknowledgment status. Stale or unacknowledged outputs cannot advance the run.
