# CDIT Tier 1 Support MAO - PRD v4

*Product Requirements Document: synthetic prototype planning baseline*

**Product name:** ActionRelay by CDIT (CDIT Support Desk Assistant)
**Owners:** Manny (Manny's Lane), Shawn (Shawn's Lane), Shared Lane
**App/auth/UI owner:** Manny, confirmed 2026-11-08; this remains within Manny's lane unless he explicitly redirects or requests Shawn's participation.
**Date:** 2026-11-10
**Status:** PRD-v4 remains the synthetic-prototype baseline approved on 2026-11-08, amended by the project lead on 2026-11-10 for bounded automatic routine fulfillment, Auditor capability, and oversight. Implementation acceptance and production authorization remain separately tracked.

**Version note:** This amendment supersedes the earlier blanket draft-only restriction for the local synthetic application only. A complete approved routine request may receive an automatic in-ticket reply and Resolved transition through the trusted application gate in §11. Six runtime agents and lane ownership are preserved. Earlier PRDs and the original field guide remain historical. Production writes, external messaging, real CDIT data and billable model calls retain their separate approvals.

# 1. PROBLEM

The supplied Customer Support Specialist job description describes varied intake, triage, approved troubleshooting, documentation, and escalation work. It does not establish which task causes the greatest delay, how much time it costs, or how often errors occur. The specific problem this project tests is whether a Tier 1 specialist can review a synthetic support case with its category proposal, current approved guidance, and factual draft note in one evidence-linked workflow instead of assembling those pieces separately. This is a job-description-derived hypothesis; no CDIT-specific pain, baseline, or productivity gain has been verified.

### Supporting Context

- The supplied CDIT job description names Salesforce case work, phone and email intake, SLA monitoring, Tier 1 troubleshooting, escalation to L2 or Support Lead, customer training, knowledge-base contributions, and possible PHI access.
- No CDIT-specific operational metrics or authorized product documents have been provided; impact claims and targets below are pilot hypotheses.
- Public clinical-trial information may support synthetic examples, but it is not a substitute for CDIT product documentation.

## 1a. Opportunity

A bounded MAO prototype can fulfill a verified routine request directly in its ticket. Exceptions give Staff an evidence-linked packet with category and urgency, approved sources, supported steps and a factual draft. Evaluation measures correctness, grounded fulfillment, safe routing, fallback behavior and run cost using synthetic cases. Real-world time savings and CDIT service outcomes require an authorized baseline.

### Size of the Opportunity

- Baseline ticket volume, time per ticket, SLA performance, first-contact resolution, and escalation rates: **unknown; establish before claiming savings**.
- Handling-time savings are unvalidated and are not a current success claim. Measure model/run latency and cost on synthetic cases; a human handling-time study is outside this project assignment.

## 1b. Users & Needs

**Primary product user:** User, who accesses the client-facing view. Within the synthetic support workflow, Staff uses the back-end work view to review cases and drafts. These role labels are prototype account categories, not CDIT job titles.

**Secondary users:** Staff handles assigned support work. A dedicated Auditor demo account is a Staff account with the Auditor capability, using the shared back-end layout with limited writes. Admin oversees all cases, assignments and accounts. Product Health is a metadata viewing purpose. The presentation has four sign-ins across three dashboard layouts. Auditor is a capability, not a fourth base role or a seventh agent.

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

ActionRelay by CDIT is a local multi-agent support prototype with synthetic data. User submits and tracks own requests. Ordinary Staff works assigned cases. Auditor-capable Staff reads all tickets in the general Queue and classifies or revises assigned cases only. Admin oversees all cases, manages assignments and accounts, and reviews Auditor activity. Coordinator routes six runtime agents. Verified routine results reach an application write gate that may post an in-ticket reply and mark the case Resolved without per-case human approval. Exceptions return a source-linked human handoff. An isolated presentation simulates these workflows. Model tools cannot grant arbitrary ticket, account, database or external-system access.

## 2a. Value Proposition

ActionRelay provides an approved resource directly to a requester when its complete routine case qualifies. For exceptions, the same workflow assembles evidence, supported steps and a reviewable handoff. Its differentiator is a traceable path from intake to authorized action or human review. The supplied job description motivates the hypothesis, not a verified CDIT productivity claim.

## 2b. Top 3 MVP Value Props

**The Vitamin:** Each case receives a structured summary, suggested category, urgency rationale, and source-linked response guidance.
**The Painkiller:** Staff can review relevant approved instructions and prior troubleshooting steps without manually searching multiple knowledge documents.
**The Steroid:** The workflow fulfills an eligible routine request inside the ticket or prepares an evidence-linked human handoff with uncertainty and missing information visible.

## 2c. Goals and Non-Goals

**Goals:** demonstrate six-agent orchestration on synthetic cases, fulfill approved routine patterns without per-case human review, route exceptions safely, enforce roles/capabilities and assignment, preserve versions and provenance, and evaluate safety, grounding, recovery and action measures.

**Non-goals:** assert CDIT behavior without approved sources, claim measured real-world productivity, process real tickets/PHI, send email/phone/SMS, obtain personal records, submit government applications, close tickets autonomously, change accounts through agents, deploy production identity/integrations, or introduce a second reviewer agent.

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

| Enforce local role and case-assignment boundaries | Authenticated page and API access matches the User/Staff/Admin and assigned-case policy | Allowed/denied results for own, assigned, unassigned, reassigned, and Admin-override cases | 100% correct decisions in the synthetic matrix; zero unauthorized protected-data responses |
| Minimize persistent data | Local storage contains only approved synthetic fixtures and allowlisted metadata | Prohibited-field persistence checks | Zero ticket-body, attachment, real-identity, credential, or arbitrary model-prompt fields in Product Health records |
| Audit privileged account changes | Local synthetic-account role/status changes are attributable | Admin changes with matching audit event | 100% of successful privileged changes have an actor, target, action, timestamp, and before/after role/status record |
| Separate the public role showcase | All three previews are visible without login without exposing authenticated app resources | Showcase route coverage and protected-resource requests | 3/3 preview routes load; zero authenticated API/database calls; all privileged controls are isolated simulations |

# 3. AGENT REQUIREMENTS

## 3a. Tools

Prototype tools operate on synthetic fixtures and approved local documents only. Production API names and endpoints are **unknown** and must be approved by CDIT.

| Tool name | What it does | API it calls | Data it returns |
| :--- | :--- | :--- | :--- |
| `get_ticket_fixture` | Reads one synthetic case and its authorized fields | Local fixture adapter; no external API | Case ID, synthetic message, channel, timestamps, product area, permitted metadata |
| `search_approved_knowledge` | Retrieves matching passages from the synthetic, versioned prototype knowledge set | Local retrieval interface; retrieval implementation selected in the shared contract phase | Passage text, document ID, version, section, relevance score |
| `get_support_policy` | Reads versioned synthetic routing, SLA, and escalation policy | Local policy file/interface | Category definitions, priority rules, SLA labels, must-escalate conditions |
| `get_synthetic_account_policy` | Reads the local synthetic User/Staff/Admin permissions for authorization checks | Local account/auth adapter | Actor category, allowed view/actions, authorization result |

The model receives no arbitrary write tool. Agents return typed results and bounded candidate actions. The trusted application may execute only approved local synthetic fulfillment operations after the deterministic rechecks in §11. Account administration remains a human Admin action. Ticket content and model output cannot change the operation allowlist.

## 3b. System boundary charter

This is the authority charter for the six lane-owned agent prompts and schemas. Runtime policy selects either authorized routine fulfillment or human handling. Eligible routine cases may be fulfilled automatically only through §11. All other cases require a human review or safe stop. Every consequential automatic-action claim must be verified with current evidence. Case text, attachments, retrieved passages, metadata, model outputs and tool results remain untrusted. Confidence cannot grant authority. Never send external messages, reset credentials, change accounts, give clinical advice or write to production systems.

## 3c. Blast Radius

**Worst-case scenario:** The assistant fabricates product guidance, mishandles untrusted content, or fails to route a synthetic high-impact case for human attention. Admin access controls could also be misused to change a synthetic account's permissions. Prototype safeguards limit the system to synthetic cases, fixed tools, visible sources, deterministic action checks, human handling of exceptions and auditable local account administration. Real data and production use require separate approval and scoped review.

### Failure Modes & Safeguards

| Failure mode | Worst-case impact | Safeguard |
| :--- | :--- | :--- |
| Wrong triage or priority | SLA breach or delayed attention to an urgent support issue | Deterministic policy checks, labeled evaluation, rationale display, staff confirmation, and must-escalate rules |
| Hallucinated or stale product instructions | Customer may follow incorrect steps or waste time | RAG only over approved versioned content; show exact sources; abstain on weak/conflicting evidence |
| PHI or identifiers enter an unapproved model/log | Privacy and regulatory exposure | Synthetic data by default; approved minimization/redaction boundary; vendor and data-flow review before production |
| Prompt injection in ticket or document | Agent ignores policy or attempts unauthorized action | Treat content as untrusted; fixed tools and sequence; action allowlist; output checks; injection evaluation cases |
| Unauthorized account or permission change | An account receives inappropriate access | Local synthetic accounts only; Admin-only access controls; explicit action authorization; record each privileged change in minimal synthetic audit metadata |
| Salesforce or model service unavailable | Incomplete or delayed support workflow | Explicit unavailable state, preserve source ticket, no fabricated result, safe manual fallback |
| Duplicate or inaccurate case note | Confusing support history | Human approval for exception drafts; atomic reply/status/audit for authorized routine fulfillment; expected-version checks and unique operation keys prevent duplicate commits |

## 3d. Evaluation scenarios

Use the synthetic case scenarios in [`CASE-SCENARIOS.md`](./CASE-SCENARIOS.md) to evaluate normal handling, edge cases, and adversarial input. The test set must be expanded and approved before it is treated as an acceptance suite.

# 4. PRODUCT REQUIREMENTS AND ARCHITECTURE

## 4a. MAO workflow and role boundaries

1. **Coordinator:** validates request shape, chooses allowed workflow, tracks state and budgets, and enforces stop conditions; cannot grant permissions.
2. **Triage agent:** proposes issue category, urgency, and SLA risk using ticket facts and versioned policy.
3. **Knowledge agent:** retrieves passages from approved, versioned support materials and returns source references.
4. **Troubleshooting agent:** proposes supported Tier 1 steps and identifies information needed; has no account-action tools.
5. **Escalation agent:** checks must-escalate rules and prepares the L2 / Support Lead handoff.
6. **Documentation agent:** assembles the source-linked response/note and typed candidate action. The application gate determines automatic eligibility or human routing.
7. **Human Staff/Admin:** reviews drafts and proposals within assigned-case permissions; Admin can assign/reassign cases, oversee all cases, and administer synthetic accounts. Admin Auditor overrides require a recorded reason.

Use Anthropic Claude Sonnet 5.5 (`claude-sonnet-5-5`) as the selected model for synthetic Triage. A local client adapter now requires a per-run billable-call authorization flag and an immediate active-handoff preflight, disables SDK retries, applies a provisional 60-second timeout, and validates outputs; the local runtime callable has been added, but CombinedWorkflowHarness/app wiring remains open; Anthropic SDK version pinning is complete. Review the timeout against measured latency before model-backed evaluation. Keep provider calls behind an adapter; store the API key only in an ignored local `.env`, never in source control, prompts, or ordinary logs. Model calls are billable and require explicit run authorization. A second reviewer or multi-model path is deferred. A single-call comparison is optional, synthetic-only, and not a required feature or runtime agent (D-19). Use local retrieval-augmented generation over the synthetic, versioned knowledge set; retrieval implementation is selected during the Shared contract phase. Retrieved content is evidence, not trusted instructions.
### Core workflow and worked synthetic examples

1. User submits a synthetic request or Staff opens an assigned case. Coordinator validates identity, scope, schema and synthetic data, then creates a versioned minimized packet.
2. Triage proposes broad category, specific issue, band, source spans and missing facts for each supported item. Unknowns retain their uncertainty and route for classification.
3. Knowledge retrieval and deterministic Escalation checks run in parallel when inputs permit. Coordinator joins acknowledged results for matching case/run/policy versions and individually current source versions.
4. Troubleshooting validates supported steps and prerequisites. Documentation assembles cited response text, factual note and a typed candidate action. Each stage checks its output schema, evidence and stop conditions.
5. The outcome gate returns human review, a safe stop or a candidate for the separate application write gate. Automatic candidates require verified consequential facts and complete supported outcomes for all items.
6. The application rechecks authority, procedure, evidence and current versions. It atomically commits the in-ticket reply, Resolved transition and minimal audit/operation record, or applies none of those effects and enters recovery.
7. A human correction creates a new case/decision version and run linked to its parent. Coordinator revalidates scope and reruns affected stages and downstream dependencies, preserving prior outputs.

**Routine example.** A synthetic requester needs the blank IDNYC application. The approved resource registry points to the official application materials page with age/language options. The complete case matches the public-resource procedure. Knowledge validates the registry version, Escalation finds no stop trigger, and the response includes the approved link. The application posts that answer inside the ticket and marks it Resolved without per-case Staff approval. This fulfills the resource request, not an ID application or eligibility decision. The presentation simulates the operation. Backend write integration remains acceptance work.

**Exception example.** “I need my W-2” seeks a personal record. A blank form or public guidance does not fulfill it. Keep the case open with supported guidance and an authorized human handoff. Automatic assignment in the presentation is scripted demo behavior. Runtime assignment remains an Admin action.

**Correction example.** An Auditor initially classifies a withholding change as Payroll. New synthetic evidence indicates unchanged settings with a different calculation. Auditor records a reasoned Technical Issues revision, retaining the prior decision. Admin can comment or flag the exact version. Feedback alone does not change classification, status or execution.

### Multi-request triage and human Auditor

- Preserve each item, parent case and source span. Automatic whole-case resolution requires supported authorized outcomes for every item. Unknown or blocked dependent items keep the entire case open. Supported independent guidance may be visible with the overall case still incomplete.
- Unknown category, band or destination yields `abstained_needs_human`. A plausible high-impact concern also carries a potential-urgent flag without inventing a confirmed band.
- Auditor is a Staff capability. Its general Queue reads all synthetic tickets, including unassigned cases. Its worklist and classification writes are assigned-only. Read access does not grant lifecycle, assignment or account-write authority.
- Classifications record item/case IDs, category, band, proposed destination, reason, evidence references, conditions/exceptions, actor, timestamp and version. Compare the expected previous version on save. Stale submissions refresh rather than overwrite.
- An Auditor may revise their own latest assigned-case decision with a new explicit reason. The current decision stays outside earlier history. Closed cases are read-only. An Auditor cannot supersede an Admin override. Admin can review any case and records an override reason.
- Admin activity groups decisions by case and highlights the current version. Optional notes and flags target one version and reach its author. Feedback does not compel acknowledgment or revision and does not alter classification, assignment, status or a run. Clearing a flag retains its event history and notes.
- A human correction submitted for processing starts a new versioned run. It does not overwrite the old run or promote a learned rule. Similarity to another case does not establish identical facts or authority.
- Store synthetic decision/feedback text with the permitted case records. Product Health receives allowlisted operational metadata only, not free-text requests, reasons, notes or direct identities.

### Synthetic in-progress attention benchmarks

Urgency is based on the case’s actual reported conditions, impact and contingencies, not the passage of a benchmark alone. A relevant baseline example may inform a proposal, but similarity does not establish a case’s facts, its resolution, or an approved policy. An already resolved issue must be distinguished from an ongoing one; disposition follows an approved routine gate or an authorized human action.

For synthetic development, use suggested elapsed **In Progress** attention benchmarks of **15 minutes for High [P1]**, **4 hours for Medium [P2]**, and **24 hours for Low [P3]**. High/P1 receives immediate human attention and its local flag without waiting for 15 minutes. These are review prompts, not guaranteed response or resolution deadlines, service-level commitments, or CDIT policy. A flag includes a concise evidence-linked reason such as “In Progress for 4 hours; review current impact.” A benchmark alone does not change urgency, make it Unknown, resolve a ticket, or establish a breach. Unknown urgency follows the human Auditor path; a plausible immediate harm or major impact receives a potential-urgent flag without asserting a verified band.

Exclude time in **Waiting on Customer** from the In Progress benchmark. A customer response starts a fresh In Progress benchmark except where an ongoing safety concern requires continuing attention; preserve the safety flag and the original safety timeline across customer replies until an authorized human reviews them. Track the safety timeline separately from the paused In Progress benchmark; it records elapsed context and is not a deadline for investigation, emergency care, or legal action. Keep timestamps and prior periods for audit rather than erasing them. A future authorized customer notification may remind the customer of the specific outstanding response, form or correction. Include a submission deadline only when an authorized case record or policy actually supplies one; never invent it. **Under Investigation** is a distinct case status for a human-led investigation, including a possible third-party response. An authorized human sets and manages this status and decides whether to involve a third party; the status alone does not prove that anyone has been contacted. The agent may preserve and display authorized context and prepare a draft handoff for human review, but must not autonomously investigate, interfere with the response, contact outside parties, or change case status. The ordinary In Progress benchmark applies only while the case is In Progress; a separate ongoing-safety timeline and attention flag remain visible during an investigation until authorized human review. The local prototype transition map is defined in §4e; production role workflows remain pending.

For a plausible safety, emergency, or legal concern, prepare a minimized evidence-linked packet for an authorized human to assess and decide whether to involve the appropriate external responder, medical provider, emergency service, legal authority or other third party. The agent must not invent an incident, choose an unverified contact, claim contact was made, or autonomously dispatch. Investigation and emergency or legal response take precedence over benchmark timing. The local synthetic prototype does not send external messages. Customer-visible reminders and delivery channels remain subject to their own implementation and access decisions.

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
| SQLite logical entities | Proposed tables: synthetic_accounts, synthetic_cases, knowledge_documents, knowledge_chunks, policy_versions, workflow_runs, agent_handoffs, evaluation_cases, evaluation_results, product_health_events, and account_access_events. The local account/case/session/assignment/Auditor foundation is recorded separately below. This inventory does not claim that workflow, action-ledger, feedback or operational-event tables are implemented. | Manny owns the SQL foundation; Shared reviews only cross-agent event fields/versions. Approve columns, keys, versioning, migrations, and retention before persistence work. Product Health and access events exclude ticket bodies, credentials, and direct user identity. |
| Synthetic data ownership | At least 100 labeled cases remain the final evaluation target; candidate examples in CASE-SCENARIOS.md are not themselves a completed labeled set. | Manny owns the evaluation protocol and is the single author, reviewer, and approver of labels for this synthetic assignment. Record that the labels did not receive independent peer review. |
| Interface | Authenticated local app with a client-facing User view and shared Staff/Admin back end, plus a separate no-auth role showcase with three static/mock views. | Approved product direction; production identity provider and Salesforce integration remain excluded. |

Implementation status requires code and test evidence. Earlier scaffold descriptions are historical. PRD-v4 records local authentication/session/case/assignment/Auditor foundations. Routine writes, all-case Auditor reads with limited writes, feedback persistence and event-based analytics remain implementation and acceptance work. The presentation simulates these newer flows.

Alternative considered: begin with hosted PostgreSQL, hosted vector search, and live Salesforce integration. Rejected for MVP because requirements, credentials, vendors, environment, and PHI boundaries are unconfirmed.

## 4c. Account categories and access

The base categories remain User, Staff and Admin. Four presentation accounts demonstrate their permissions across three layouts.

| Account / capability | Dashboard and read scope | Allowed writes |
| :--- | :--- | :--- |
| User (`user.demo`) | Own permitted request/status only | Create a synthetic request and edit while Submitted. Classified unresolved cancellation uses an explicit reason under §4e. |
| Ordinary Staff (`staff.demo`) | Assigned cases and scoped operational views | Assigned-case review notes and permitted human lifecycle changes. No account or assignment writes. |
| Auditor capability on Staff (`auditor.demo`) | Shared back-end/Admin-style layout. General Queue reads all cases, including unassigned cases. Worklist is assigned-only. Account directory is read-only. | Classify assigned cases and revise own latest decision with a reason. No lifecycle, assignment, suspension, promotion/demotion, removal or Admin-override writes. |
| Admin (`admin.demo`) | All cases, assignments, accounts, versioned Auditor activity and deeper Product Health | Authorized account/assignment actions, human case controls, reasoned overrides, and optional version-specific notes/flags. |

- Check role, capability, active account, assignment and case version server-side on every page/API/record action. Reassignment, suspension or capability revocation immediately removes write eligibility. Hidden controls do not establish authorization.
- Auditor is a human responsibility, not an additional runtime agent or base role. Product Health is a metadata purpose, not a login.
- Use one shared login page. Authenticated User has no Staff/Admin/Auditor navigation. The isolated showcase may expose role previews without accessing protected app data.
- Admin permissions do not delegate model authority. Automatic routine writes use the separately bounded application capability in §11.
- This matrix records 2026-11-10 product intent. Presentation controls simulate it. Backend acceptance requires positive/negative tests for reads and every type of write.

## 4d. Data sources, Product Health, and privacy

- Use fabricated support tickets, fabricated/versioned knowledge articles, deterministic synthetic policies, and public clinical-trial metadata for scenario context only. Public metadata is not CDIT product guidance.
- No CDIT-specific product/module or workflow behavior may be asserted without a supplied, approved source. When evidence is missing, label the point unknown/simulated and abstain from product claims.
- Product Health may retain only minimal synthetic/system metadata needed for investigation, correction, and change planning: synthetic run/event IDs, timestamps, status/category, component/version, bounded error/performance codes, and access-change metadata. Retention is 30 days for detailed synthetic run/error metadata, 90 days for synthetic account/access-change audit events, and up to 12 months for aggregated non-identifying performance/evaluation summaries. Provide an explicit reset/purge path. Verify expiration using an injected/accelerated test clock so the full lifecycle test completes in under two minutes; this test clock must not change configured retention durations. Do not retain ticket bodies, attachments, arbitrary free-text payloads, credentials, direct user identity, customer records, or confidential information. The local database may contain fabricated fixtures required for the prototype; it must not import or retain real case content.
- Real customer tickets, PHI, credentials, CDIT-private documents, and production service data are excluded. Reassess data, provider, privacy, security, and regulatory requirements before any later scope change to real data or operational integration.

## 4e. Authenticated app and role-view showcase

### Authenticated application

- After local synthetic login, route User to the client-facing view, Staff to the support back end, and Admin to that same back end with privileged synthetic-account controls.
- Enforce authorization on the server for every page, API, and record lookup. Hiding a navigation item is not authorization. User records are scoped to that synthetic account; Staff and Admin access follows the approved local permission matrix.
- User reads own requests only and edits while Submitted. In Progress displays as In Review and locks editing. Classified unresolved cancellation closes with requester_cancelled_unresolved. Unknown category/band must be classified before resolution or closure, including cancellation. Resolved/Closed requests are not editable or cancellable. Catalogue development examples are excluded from authenticated User scope.
- Enforce the capability matrix in §4c on every route. Auditor reads all cases, including unassigned cases, but classifies assigned cases only and cannot alter lifecycle, assignment or accounts. Ordinary Staff works assigned cases only. Admin oversees and assigns all cases. Demo permissions are not evidence of backend authorization.
- For the local prototype, Staff/Admin status changes follow this application transition map: Submitted -> In Progress or Closed; In Progress -> Waiting on Customer, Under Investigation, Escalated, Resolved, or Closed; Waiting on Customer -> In Progress, Under Investigation, Escalated, Resolved, or Closed; Under Investigation -> In Progress, Escalated, Resolved, or Closed; Escalated -> In Progress, Under Investigation, Resolved, or Closed; Resolved -> In Progress or Closed; Closed is terminal. These are prototype UI/data-integrity rules, not CDIT policy or an SLA.
- Human edits, status changes and cancellation create minimal audit metadata with actor, case, action, before/after status, changed-field flags, reason code and timestamp. The bounded automatic operation has its own reply/status/audit transaction under §11. Audit events do not copy request or note text.
- Admin may inspect synthetic account roles/status and perform the locally approved grant, update, promote, demote, suspend, deactivate, or remove actions. Successful changes create an audit event. Auditor may view a minimal account directory but cannot perform any account write.
- The Admin view may present the Product Health metadata summary. Product Health is a viewing purpose within the existing account model, not another account category. Never expose raw ticket text, credentials, or unrestricted model content through this view.
- Use a 30-minute idle timeout and an 8-hour absolute session limit. Warn the user 15 minutes and 5 minutes before whichever limit will expire first; let the user continue the session within those limits. Session extension beyond the 8-hour maximum is deferred. Keep the approved alert path for a user requesting an extension and record the request timestamp for Admin review; do not extend automatically or send email. Invalidate sessions on logout, account suspension/deactivation/removal, or role change.
- Provide login, logout, unauthorized/forbidden, expired-session, empty-data, database-unavailable, and safe-recovery states. A failed or invalid authentication attempt does not reveal whether a protected account exists.

### Unauthenticated role-view showcase

- Provide User, Staff and shared Admin-layout previews with four synthetic sign-ins including the Auditor capability. The no-login showcase uses isolated fabricated data.
- Isolated presentation controls may simulate requests, decisions, feedback, assignments and account status in memory. They make no authenticated API/database/model calls and cannot affect protected application records. Refresh clears demo state. The presentation does not establish backend authorization or integration correctness.
- The showcase must remain a separate presentation surface; it cannot be used to bypass authentication or prove that the authenticated permission boundary works.

## 4f. Prioritized MVP requirements

The companion priority matrix remains a mapping for unchanged needs. The amended requirements here and in the new field guide govern routine fulfillment and Auditor/oversight behavior, including conflicts with historical draft-only UC-08.

| Priority | User journey | Requirement | Minimum evidence |
| :--- | :--- | :--- | :--- |
| [P0] | Submit, view, and manage own request | User creates/reads own requests and edits Submitted content only. Unknown category/band blocks resolution/closure. Qualified routine fulfillment posts a reply and Resolved status. | Own-record, locked-edit, classification, cancellation and eligible fulfillment visibility checks. |
| [P0] | Assigned Staff case management | Ordinary Staff works assigned cases. Auditor-capable Staff reads all cases, classifies assigned cases and views account roles/status read-only. | Separate positive and negative tests for reads, classifications, lifecycle, assignment, account actions, suspension and reassignment. |
| [P0] | Admin case assignment and oversight | Admin manages active Staff assignments, reasoned overrides, and version-specific optional feedback/flags. Current decision stays outside earlier history. | Expected-version conflicts prevent overwrite. Feedback reaches the targeted version author without changing classification or requiring revision. |
| [P0] | Access the prototype | User sees the client-facing view; Staff sees the support back end; Admin shares that back end with privileged synthetic account/access controls. | Synthetic role tests verify allowed access and deny unauthorized account/access changes; all three categories are exercised. |
| [P0] | Persist synthetic prototype data | The local SQLite store persists approved fabricated fixtures, run/evaluation metadata, and minimal Product Health events using versioned schemas. | Schema/version and reset tests pass; prohibited real-data, credential, raw-ticket, and arbitrary-prompt fields are absent from Product Health records. |
| [P0] | Authenticate and route by account category | Local synthetic User, Staff, and Admin accounts reach only their authorized app view and APIs. | Full defined role-route-action matrix passes; every forbidden direct page/API request is denied server-side. |
| [P0] | Administer synthetic access | Admin can inspect and manage synthetic account roles/status; each successful change is auditable. | All successful grant/update/promote/demote/suspend/deactivate/remove operations have a matching audit event; non-Admin attempts are denied. |
| [P0] | Preview role views without login | Project reviewers can navigate among static/mock User, Staff, and Admin view previews without an account. | All three previews load without login and make zero authenticated API/database requests; controls cannot affect authenticated application records. |
| [P0] | Process a synthetic case | The Coordinator and six assigned agents use the approved direct workflow, structured handoffs, source evidence, uncertainty, and stop conditions. | Each agent and the combined workflow pass the approved synthetic must-pass set; no fabricated citations or unsupported material claims. |
| [P0] | Review and disposition | The outcome gate routes approved routine candidates to §11 and exceptions to authorized humans. Model output cannot authorize itself. | Zero unauthorized writes or false automatic eligibility in tested must-stop cases. Allowed commits are atomic and duplicate-safe. |
| [P0] | Protect inputs and permissions | Untrusted case/knowledge/tool content cannot change policy, widen tool access, cause disclosure, or bypass checkpoint gates. | Direct, indirect, stored-content, role-denial, and cross-agent synthetic tests pass with zero unauthorized actions/disclosures. |
| [P0] | Recover from failure | Invalid inputs, missing/stale/conflicting sources, unavailable components, or failed handoffs stop safely and show a truthful manual fallback. | Defined synthetic failure cases pass; no fabricated result advances downstream. |
| [P0] | Evaluate the workflow | The project can score synthetic cases using human-approved labels, deterministic comparisons, safety gates, and a combined workflow harness. | Results include counts per gate, claim denominators, tested-set scope, latency/cost, retrieval measures, and an explicit single-person review limitation for this assignment. |
| [P0] | Inspect Product Health | Authorized Staff/Admin can use minimal synthetic/system metadata to investigate or correct prototype behavior. | Metadata records synthetic run/event IDs, status/category, component/version, error/performance, and access changes; no underlying ticket content or real identity is retained. |

## 4g. Explicit assumptions and deferred dependencies

### Amendment implementation status

The 2026-11-10 amendment records approved intent, not implementation, tests passed, production readiness or CDIT data approval. Older companion/deferred records are historical where they conflict with this amendment. D-02, D-03 and D-11 are superseded only for the bounded local routine operation. Backend integration, concrete source/procedure/schema versions, retry budgets and calibrated evidence thresholds require acceptance work.

- SQLite is the approved local database choice. The synthetic account/session/case, Product Health, access-audit, session-alert, and case-catalog schemas are implemented as versioned local migrations with seed/reset/retention paths. Cross-agent workflow and evaluation persistence remains logical until lane/Shared boundaries, concrete schema, and recovery behavior are approved.
- Local authentication is for synthetic prototype accounts only. Use seeded accounts, no public registration, synthetic password hashes, the session lifecycle in §4e, and the approved Admin action matrix. Do not use production credentials.
- Product Health metadata fields are allowlisted and content-minimized. Apply the retention periods in §4d and an explicit reset/purge path; verify them with the sub-two-minute accelerated test clock. Never store real records to test the metadata path.
- The role showcase is a separate no-login visual deliverable with fabricated content; it is not the authenticated application and does not demonstrate authorization correctness.
- The existing backend stack is Python 3.13/FastAPI/Pydantic. The presentation uses standalone HTML/CSS/JavaScript with isolated synthetic memory. Its integration into the application remains to be selected and implemented without changing API or database permission boundaries.

- The exact CDIT CTMS modules, support channels, internal procedures, and source documents are not provided. The prototype therefore uses a generic synthetic CTMS-support scenario and makes no CDIT-specific product claims.
- Synthetic evaluation uses the current proposed numeric targets in this document; Manny defines claim classes, per-gate counts, confidence calibration, reporting, retrieval freshness, latency/cost budgets, and reviewer-error protocol before evaluation acceptance. For this synthetic assignment, Manny is the single label author, reviewer, and approver; report that no independent peer review occurred. No evaluator agent, external evaluator, or working-specialist participant is required.
- CASE-SCENARIOS.md currently contains a candidate ticket taxonomy and synthetic failure fixtures; these are not a completed 100-case labeled evaluation dataset. Before build acceptance, Manny records case IDs, expected category/band/run state, evidence labels, gate-specific positive/negative counts, and single-person review status for the actual labeled set.
- On 2026-11-05, the project lead selected Anthropic Claude Sonnet 5.5 (`claude-sonnet-5-5`) as the single model path for synthetic Triage. Keep API use synthetic-only, document model/config versions and per-run cost/latency, and do not make billable calls without explicit run authorization. The 80-row catalog remains development examples, not approved evaluation labels or operational policy. See [Anthropic model ID documentation](https://platform.claude.com/docs/en/models/sonnet-5-5/overview).
- An optional single-call baseline may process the same synthetic case/evidence as MAO for a comparative evaluation. It is not a required deliverable, a user-facing feature, or an additional agent (D-19).
- Live CDIT/Salesforce integration, production authentication, production knowledge sources, actual customer data, and any applicable legal/regulatory controls require a separate future authorization and scoped review. This planning PRD makes no regulatory applicability finding.
- The six runtime agents and lane ownership are already assigned in `docs/planning/TASK-SPLIT.md`. The optional second reviewer remains deferred. Admin account controls are synthetic-only and do not grant agent ticket-write authority.
- Client-to-developer platform issue reporting remains scope-unconfirmed, excluded, and disabled (D-17). It is not described as a support workflow or acceptance requirement here.

## 4h. Supporting references

- [Local app, SQL foundation, authentication, and role showcase plan](../planning/phase/undecided/unassigned/LOCAL-APP-DATA-AUTH-PLAN.md).

- Supplied Customer Support Specialist job description (user-provided attachment; needs derived from it remain hypotheses).
- [User needs and prioritized use cases](./PRD-USER-NEEDS-AND-USE-CASE-PRIORITIES.md).
- [Synthetic case scenarios](./CASE-SCENARIOS.md); only the bounded procedures in §11 authorize local prototype fulfillment.
- [Expanded ActionRelay field guide](../architecture/actionrelay-field-guide.html).
- [Technical architecture and contracts](../architecture/ActionRelay-Architecture.md).
- [Standalone diagram](../architecture/actionrelay-architecture.svg).
- [Historical architecture JPEG](../artifacts/cdit-support-mao-architecture-prd-v2.jpg).
- [Deferred decisions](../planning/DEFERRED-DECISIONS.md).
- HHS Security Rule: https://www.hhs.gov/hipaa/for-professionals/security/index.html
- HHS cloud computing and ePHI guidance: https://www.hhs.gov/hipaa/for-professionals/special-topics/health-information-technology/cloud-computing/index.html
- HHS de-identification guidance: https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html
- ClinicalTrials.gov Data API: https://clinicaltrials.gov/data-api/about-api
- CDISC standards: https://www.cdisc.org/standards
## 4i. Queue, analytics and presentation behavior

- Share the Staff/Admin visual system. User sees own-request tasks. Auditor uses the shared layout with restricted writes.
- Filter by band, broad category, status and dates. Support date, A–Z and attention sorting. Specific issues and duplicate/paraphrased requests belong within broad categories.
- Show High/P1 Urgent, Needs classification and evidence-linked attention flags. Unknown cases stay open. The 15-minute/4-hour/24-hour synthetic benchmarks are review prompts, not CDIT SLAs.
- Use one status-color mapping across year-comparison wheels. Status-at-cutoff counts are mutually exclusive snapshots including carryover. Matched-period received/resolved/closed figures count activity during the same dates in each year and can overlap. Open backlog belongs to the snapshot.
- Chart outcome activity from recorded lifecycle transition dates. Never infer historical resolution dates from a current status. Show exact counts, shares and changes. When the prior denominator is zero, show no prior baseline rather than an invented relative percentage.
- The timeline supports day/month/year views, date pinning, weekly/monthly browsing and horizontal scrolling. The interval from a marker up to the next marker selects the earlier date. Year view fits up to ten years. Keyboard and touch access remain required.
- Presentation fixtures expand 80 development examples into 960 variations plus session requests with illustrative 2023–2026 dates. These are not CDIT distributions, independently labeled evaluation cases or measured productivity results.
- The continuous and clicker-controlled demonstrations share the same synthetic workflow, visible role handoffs and targeted split screens. Pause/Resume and 1×/0.75×/0.5× controls apply to the walkthrough. Refresh clears in-memory demo state. Simulated processing does not establish backend auth/integration correctness.
- Presentation files are in [docs/presentations/ActionRelay](../presentations/ActionRelay/actionrelay-demo.html). A CDIT-data version requires approved real inputs, authoritative knowledge and separately approved integrations.


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
- Use a fixed coordinator workflow and narrow tool allowlist. Agents may read only fields needed for their task; no model-callable tool can grant roles, send external messages, change accounts or write to Salesforce.
- Validate tool arguments and structured outputs against schemas and role policy. Reject unexpected fields, tool requests, destinations, or action types; do not treat model-generated text as authorization.
- Use parameterized database queries and fixed repository methods; never execute model-generated SQL or let ticket, metadata, or showcase content choose tables, predicates, or authorization scope.
- Require source citations for product claims. Abstain and request human review when sources conflict, are stale, are missing, or contain instructions that conflict with policy.
- Add adversarial synthetic evaluations for direct prompt injection, indirect injection in retrieved content/attachments, data-exfiltration requests, tool misuse, policy override, and benign quoted instructions. Confirm no unauthorized tool invocation or sensitive-data disclosure.
- Log minimally using synthetic IDs. Human review is mandatory for exceptions and operations outside §11. Product Health excludes free-text ticket/review content, secrets and arbitrary prompts.

# 8. OUT OF SCOPE

- Production deployment/authentication, live Salesforce/telephony/email integrations and production record writes. Local synthetic fulfillment is bounded by §11.
- Real customer tickets, PHI, credentials, CDIT-private documents, or external model processing of sensitive data before documented CDIT approval.
- Autonomous external communication, closure, SLA decisions, account/permission changes, password resets, clinical advice or identity-verification bypass. Only the bounded local reply/Resolved operation is permitted automatically.
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
| A6 — Draft assembly and review | Documentation agent / coordinator | Build draft note from verified facts only; validate required output schema, source references, privacy minimization, and explicit outcome/eligibility fields. A routine candidate must still pass the live application gate; exception output remains a human-review draft. | Unsupported claims, sensitive-data leakage, invalid output, or unavailable dependency suppresses the draft and provides a safe manual fallback. |
| A7 — Authorized outcome | Application gate or authorized human | Recheck procedure, verified facts, case/source/policy versions, all-item completion, scope and capability. Otherwise require human review. | Allowed local reply/Resolved operation commits atomically. Denial, conflict or uncertain commit enters safe recovery. Autonomous closure, account writes and external sends remain excluded. |

For evaluation, capture checkpoint reached, pass/fail reason, agent/tool calls attempted, policy/source versions, and human disposition using synthetic identifiers. Do not log unnecessary ticket text, secrets, or PHI. Required adversarial cases must prove injection cannot skip a checkpoint, widen tool access, suppress escalation, or cause disclosure. These are local synthetic acceptance requirements. Operational CDIT policy and production use require separate review.

## 9a. Run outcome and failed-state contract

These statuses describe the assistant run, not the business ticket state. A failed or abstaining run is never represented as a resolved ticket or a successful answer.

| Run status | Use when | Required result and next step |
| :--- | :--- | :--- |
| `ready_for_human_review` | Required checkpoints pass and every material claim is supported, explicitly labeled as inference, or marked unknown. | Present the proposal and its sources to Staff for review. This means only that the draft is reviewable; it does not mean the ticket is resolved or the answer is approved. |
| `ready_for_authorized_action` | The complete approved routine candidate has passed output checks. | Recheck the live application write gate. Candidate readiness does not establish a committed action. |
| `action_committed` | The application verifies reply/status/audit persistence or finds the same operation already committed. | Return the recorded operation and final case version. Backend implementation and acceptance evidence remain pending. |
| `abstained_needs_human` | The issue cannot be determined from available facts; evidence is missing, stale, conflicting, or below the approved evidence threshold; or severity remains materially ambiguous. | Do not invent an answer or force a category. Return known facts, unknowns, evidence gap, and the specific human question or decision needed. Do not continue dependent agent work. |
| `blocked_checkpoint` | Input/output schema, provenance, citation, permission, injection, version, or policy validation fails. | Stop downstream work. Return the failed checkpoint and safe reason code; require authorized human review or corrected input. Never treat model-generated text as permission to bypass the gate. |
| `failed_dependency_manual_fallback` | A required model, retrieval, storage, or orchestration dependency is unavailable or times out after the approved bounded retry policy. | Mark the run incomplete, preserve only permitted synthetic run metadata and last completed checkpoint, and direct Staff to the manual process. Do not present partial output as a completed answer. |
| `rejected_input` | The request is malformed, unauthorized, outside prototype scope, or uses disallowed data. | Stop at intake; explain the safe reason and the permitted next step. Do not dispatch specialist agents. |

Every non-ready result records a synthetic run ID, status, stage, last passed checkpoint, reason code, relevant source/version references (when available), missing or conflicting facts, retryability, and safe next human action. Keep sensitive or disallowed input out of Product Health metadata. Retry only transient dependency failures under a bounded policy; a retry cannot convert missing evidence, a source conflict, or a failed safety check into approval. The retry limit and exact confidence/evidence thresholds must be set and tested before implementation. A human correction or decision starts a new versioned run; it does not overwrite the failed result.

The must-pass evaluation asserts the expected status for each fixture, no false ready/action-committed result on any must-stop case, zero downstream agent/tool calls after a blocking state, and 100% correct fallback status on the defined synthetic must-pass set. Report the tested cases and counts; this is not a real-world reliability guarantee.

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

### Scope and implementation status

The project lead approved local automatic routine fulfillment on 2026-11-10. A complete Low-band request must match a versioned approved procedure and pass every deterministic application check. Urgency and confidence alone never grant write authority. The model returns an action candidate. The trusted application executes the bounded operation. Presentation behavior is simulated in memory. Backend authorization, transactional persistence and recovery remain implementation/acceptance work. Earlier broad deferrals, including D-02, D-03 and D-11, are superseded only for this local synthetic scope.

### Procedure and authority matrix

| Pattern | Permitted application result | Stop or human route |
| :--- | :--- | :--- |
| Exact, complete request for an approved public blank form or resource link | Post the current source-backed answer and approved link inside the synthetic ticket, then set Resolved atomically without per-case human approval. Initial demo uses the official IDNYC application-materials page. | Ambiguity, private/restricted resource, stale source, unsupported claim, mixed-item unknown, safety trigger or denied capability. |
| Request for “my W-2” or another personal record | Supported general guidance may be prepared for human review. Keep the request open. | A public blank form or guidance does not fulfill a personal-record request. |
| Customer must supply missing information | Prepare the supported clarification and a Waiting on Customer proposal for human approval. | The public-resource procedure does not authorize automatic requests for information or other transitions. |
| Unknown band/category/destination, policy exception or disputed requirement | Abstain and route to assigned Auditor/human review with a potential-urgent flag if justified. | No inferred classification, automatic resolution or closure. |
| Closed ticket | Read the recorded result and history only. | No reopen or automated amendment. |

### Deterministic application write gate

1. Authenticate the caller and resolve the bounded workflow capability. Recheck active identity, case scope and assignment where applicable. The gate cannot create permissions or assign cases.
2. Match the complete request against a versioned approved procedure. Bind the exact permitted action, resource and destination. Every item must qualify before whole-case resolution.
3. Recheck verified facts, current resource/source and policy versions, case version, category and Low band, schema, privacy and safe output. Inference, unknowns, unresolved disputes and must-escalate triggers deny automatic fulfillment.
4. Bind an operation key to case/version, approved procedure, source/policy versions and candidate-response digest. Execute a fixed parameterized repository method. Model output cannot supply SQL, table names, executable instructions or arbitrary destinations.
5. In one local transaction, compare the expected case version, enforce operation-key uniqueness, insert the cited reply, set Resolved, increment the case version and insert the minimal audit/operation record. All effects commit together or none do.
6. Repeated submissions with the same validated key return the recorded result. Concurrent candidates using an old case version conflict and require revalidation. A source/policy/permission change before commit denies stale execution.
7. After a timeout or uncertain acknowledgement, query the operation ledger before retrying. Never replay an uncertain write blindly. An inconclusive lookup requires recovery/human handling and cannot be reported as success.
8. Show Resolved only after verified persistence or recognition of the same completed operation. Denied/failed writes leave the ticket open with a bounded reason and safe next action.

### Resolution and closure

Resolved means the fulfilled issue can be reopened by authorized Staff/Admin if further work is needed. Closed is terminal and remains a human action. A routine reply never closes a case automatically. Unknown category/band must be classified before any Resolved/Closed transition, including requester cancellation. Cancellation of a classified unresolved request records withdrawal and does not claim fulfillment.

### Acceptance evidence

Test finite synthetic eligible and must-stop cases, including missing/stale evidence, personal W-2, unrelated ID request, mixed items, injection, suspended actor, reassignment, duplicate requests, concurrent candidates, expected-version conflicts, transaction rollback and lost commit acknowledgement. Targets are zero unauthorized writes, zero unsupported automatic replies and one consistent reply/status/audit result per accepted operation. These are required targets, not claimed results.

## 11a. ROUTING AND STATUS SIGNAL

Display an in-app Urgent flag for immediate human attention on High [P1] cases; Low [P3], Medium [P2], and High [P1] are the three proposed synthetic bands. The candidate case defaults and override guidance are in [CASE-SCENARIOS.md](./CASE-SCENARIOS.md). These examples do not establish CDIT policy, operational urgency thresholds, or SLA clocks; those remain open under D-01 in [DEFERRED-DECISIONS.md](../planning/DEFERRED-DECISIONS.md) and must be approved before routing implementation. Email and other outbound alerts are out of scope. Record synthetic intake/run timestamps, agent start/completion, source/policy versions, proposal, human decision, and final synthetic disposition using minimal metadata.

# 12. BLACKBOARD SHARED STATE AND HANDOFF CONTRACTS

Use a coordinator-owned, case-scoped blackboard as the authoritative run state. It stores versioned contributions; agents do not overwrite another agent's result. Each contribution includes run/case/stage IDs, actor/agent, input version, timestamp, status, output schema version, evidence/source IDs and versions, claim labels (verified/inference/unknown), confidence and rationale, uncertainty, proposed action, and validation result. Store only the minimum permitted data; use synthetic IDs for prototype/evaluation.

## 12a. Validated path and return loops

Coordinator validates scope and the minimized packet. Triage produces item/category/band proposals. Knowledge and Escalation run in parallel where permitted. Coordinator joins acknowledged compatible results before Troubleshooting, Documentation and the outcome gate. The result reaches either the application write gate or a scoped human handoff.

Each stage validates input fields and versions, acknowledges the accepted artifact, performs its work, validates the output, and appends provenance to the case-scoped blackboard. A transport acknowledgement is not evidence approval. Invalid, stale, missing or unacknowledged results block dependent work. The expanded field guide exposes inputs, internal checks, outputs, and return paths for every stage.

A correction retains original case, decision and run outputs. Create a new case/decision version and run ID linked to its parent, recheck scope, and invalidate affected stages and all downstream dependencies. Reuse unaffected evidence only with valid source/policy versions and dependency proof. Category/band changes revalidate Triage and affected downstream work. Source changes rerun Knowledge and its downstream dependencies. Prompt/model/policy changes require relevant regression gates.

Transient dependency failures may retry the same idempotent checkpoint under an explicit finite attempt budget, delay and timeout policy. Record attempt number and reason. The approved model client disables hidden SDK retries. No implicit retry or unapproved billable call is allowed. Evidence/schema/permission/injection/policy failures do not take this loop. Numeric retry budgets remain a pre-implementation decision.

Write recovery queries the ledger using the original operation key before considering a retry. Human classification revision and Admin feedback are separate loops. Feedback alone does not invalidate a run. An independently submitted reasoned correction starts the correction loop.

## 12b. Parallel analysis

After validated intake and triage, Knowledge retrieval and the deterministic Escalation policy check may run in parallel when inputs permit. Troubleshooting waits for required policy and retrieval results. Documentation waits until the Coordinator reconciles outputs. The second-reviewer agent is deferred and absent from this workflow. Join by run ID, case version, policy version, and source version. Preserve disagreements; never average confidence or silently choose one interpretation. Missing, stale, or materially conflicting results route to a human.

## 12c. Combined workflow harness

Shared Lane owns a test-only end-to-end harness that exercises all six runtime agents through approved public contracts, in addition to Shawn's lane-only component harness. It records correlated synthetic run and handoff events and tests the direct pipeline plus approved parallel join. It is test infrastructure, not a seventh agent, production router, or write tool. Shared may fix connectors only; findings inside an agent or lane harness return to that lane's owner. Test malformed, missing, stale, unacknowledged, duplicate, conflicting, late, timed-out, and rejected handoffs; retries, cancellation, service failure, human pause/resume, and safe fallback. Include seeded draft errors to measure whether project reviewers detect them.

Every handoff contains artifact/result ID and version, completed checks, evidence, verified facts, inferences, unknowns, confidence rationale, actions attempted, unresolved questions, requested next decision, and acknowledgment status. Stale or unacknowledged outputs cannot advance the run.
