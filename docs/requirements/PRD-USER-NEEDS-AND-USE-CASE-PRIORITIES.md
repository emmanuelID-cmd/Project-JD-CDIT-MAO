# CDIT Support MAO — User Needs and Use Case Priorities

> Companion artifact to [`PRD.md`](./PRD.md). This makes user needs a first-class design input and assigns explicit MVP priorities to the use cases. Priorities are proposed for review, not approved CDIT commitments.

## User Needs — design anchor

The product should help support staff prepare accurate, timely work while keeping decisions and customer-impacting actions with authorized humans. Every use case below maps to one or more needs; a workflow that does not meet these needs should not be treated as successful merely because it generated an answer.

| ID | User | Need | Why it matters | Success evidence |
| :--- | :--- | :--- | :--- | :--- |
| UN-01 | Tier 1 Support Specialist | As a Support Specialist, I need a concise, prioritized ticket summary because I must respond within the applicable SLA while managing several cases. | Helps staff quickly understand the request and urgency. | Reviewer accepts summary and priority rationale on labeled cases. |
| UN-02 | Tier 1 Support Specialist | As a Support Specialist, I need relevant approved product guidance with its source because I must give accurate instructions in plain language. | Prevents unsupported product guidance and makes verification practical. | Guidance claims are supported by cited, current approved passages. |
| UN-03 | Tier 1 Support Specialist | As a Support Specialist, I need suggested Tier 1 troubleshooting steps and clear stop conditions because I must know when to escalate. | Supports consistent handling within role authority. | Steps match policy; all must-escalate cases are flagged. |
| UN-04 | Tier 1 Support Specialist | As a Support Specialist, I need a draft case note based on verified interaction details because Salesforce records must be complete and accurate. | Reduces repetitive documentation while protecting record quality. | Required fields are complete and factual errors are absent. |
| UN-05 | L2 Specialist / Support Lead | As an L2 Specialist or Support Lead, I need escalations to include the issue, evidence, actions tried, and unresolved questions because I need to continue investigation efficiently. | Makes handoff actionable and reduces repeated discovery. | Handoff contains required evidence and no invented details. |
| UN-06 | Administrator / authorized Upper Tier | As an Administrator / Upper Tier user, I need to manage users, roles, queues, SLA rules, and approved knowledge sources because support operations require controlled configuration. | Enables governed configuration with accountable access. | Only authorized roles can change configuration; changes are auditable. |

## Priority definitions

- **[P0] Must ship:** Required for a safe, coherent MVP. Omitting it blocks MVP acceptance.
- **[P1] Important:** Strong value, but the MVP can operate safely without it using a documented manual process.
- **[P2] Nice to have:** Useful enhancement that can follow after core workflow evidence exists.

## Prioritized use cases

| ID | Priority | Use case | Primary user | Need IDs | MVP acceptance signal |
| :--- | :---: | :--- | :--- | :--- | :--- |
| UC-01 | [P0] | Summarize a permitted ticket and propose category, urgency, and SLA risk with rationale from supplied facts and policy. | Tier 1 Specialist | UN-01 | Labeled synthetic-ticket triage meets the PRD target; no severity-1 miss in evaluation. |
| UC-02 | [P0] | Retrieve relevant approved, versioned guidance and show source IDs/sections; abstain when evidence is missing, stale, or conflicting. | Tier 1 Specialist | UN-02 | Supported-claim rate meets PRD target; no fabricated citations in evaluation. |
| UC-03 | [P0] | Suggest policy-supported Tier 1 steps, identify missing information, and flag explicit stop or escalation conditions. | Tier 1 Specialist | UN-03 | 100% recall on defined must-escalate evaluation cases. |
| UC-04 | [P0] | Prepare a draft case note from verified ticket facts and actions, with uncertainty visible and human approval required. | Tier 1 Specialist | UN-04 | Completeness and factuality meet PRD targets; no external write occurs. |
| UC-05 | [P0] | Assemble an escalation packet with issue summary, evidence, approved guidance consulted, actions tried, and unresolved questions. | L2 Specialist / Support Lead | UN-05 | Reviewer confirms required handoff fields; no unsupported claims. |
| UC-06 | [P0] | Enforce authenticated identity, role-based access, least privilege, and separation of ticket access from configuration privileges. | Specialist / Upper Tier / Administrator | UN-06 | Unauthorized access/configuration attempts are denied in defined tests; audit events are recorded. Prototype may demonstrate roles locally without production auth. |
| UC-07 | [P0] | Keep all case handling synthetic and tools read-only/draft-only in the prototype; require human review for classification, escalation, and notes. | All users | UN-01–UN-06 | No Salesforce writes, outbound messages, account changes, or real customer data in prototype. |
| UC-08 | [P1] | Save a reviewer-approved result and decision audit event in local prototype storage. | Tier 1 Specialist / evaluator | UN-04 | Approved result can be retrieved with reviewer decision and timestamp. |
| UC-09 | [P1] | Provide an evaluation view for accuracy, grounding, escalation recall, note quality, and handling-time comparison. | Project team / Support Lead | UN-01–UN-05 | Evaluation results can be reviewed against the PRD’s proposed gates. |
| UC-10 | [P1] | Provide a safe manual fallback when retrieval, model, or local storage is unavailable. | Tier 1 Specialist | UN-02–UN-04 | User sees unavailable state and can continue through documented manual process without fabricated output. |
| UC-11 | [P2] | Compare a second model or model-review pass against the single-model baseline. | Project team | UN-02–UN-05 | Only considered if evaluation shows a measurable quality gain that justifies cost, latency, and extra data flow. |
| UC-12 | [P2] | Add operational analytics for trends in categories, escalation reasons, and knowledge gaps. | Support Lead / Administrator | UN-01–UN-06 | Requires approved data governance and privacy review before real operational data is considered. |

## Priority rationale and dependencies

- P0 use cases define the safe synthetic-data MVP: useful preparation, source grounding, role boundaries, human control, and safe escalation.
- UC-06 is an authorization requirement, but production identity-provider integration remains out of scope. The prototype should model permissions and prove denial behavior locally.
- UC-07 is a boundary, not permission to automate external actions; it is P0 because the prototype must show safe behavior.
- P1 items improve persistence, measurement, or recovery but have manual or evaluation-workflow alternatives.
- P2 items are deferred until the core workflow demonstrates value and data governance permits further work.
- All priorities require review against CDIT’s actual role matrix, SLA definitions, approved knowledge, and acceptance criteria before implementation.
