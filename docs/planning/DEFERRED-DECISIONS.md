# Deferred Decisions and Actions

**Project:** CDIT Tier 1 Support MAO
**Planning deadline:** November 11, 2026
**Status:** Open items captured from planning discussion; no item below authorizes implementation or production access.

| ID | Decision / action to defer | Why deferred / dependency | Suggested owner | Needed by / exit evidence |
| :--- | :--- | :--- | :--- | :--- |
| D-01 | Confirm urgency definitions (Low/Medium/High), thresholds, SLA clocks, and override rules. | CDIT policy and measured impact are not supplied. | Shared Lane + CDIT Support Lead | Before final routing policy; approved definitions documented. |
| D-02 | Approve case-type-specific agent action allowlist, including response sending and ticket state transitions. | Agent authority must be explicitly delegated per action and case pattern. | Shared Lane + CDIT owner | Before any implementation of writes; role/action matrix approved. |
| D-03 | Decide which routine case types may be fully agent-resolved, which may only receive a sub-action, and which always require a human. | Requires policy, risk, and evidence criteria; urgency alone is insufficient. | Shared Lane + Support Lead | Before build acceptance; case-resolution matrix signed off. |
| D-04 | Define exact distinction and transition policy for In Progress, Waiting on Customer, Escalated, Resolved, and Closed. | Existing workflow states are acknowledged; permitted transitions by role/action remain to be specified. | Manny's Lane + CDIT process owner | Before workflow implementation; transition table reviewed. |
| D-05 | Decide whether Medium cases use a second independent agent critique and under what evidence-based arbitration rule. | Confidence-based “winner” is rejected; need to justify latency/cost and define human handling of disagreement. | Shawn's Lane + Shared Lane | Before parallel orchestration; eval shows value and arbitration contract exists. |
| D-06 | Define High urgency alert recipients/channels, message content, escalation timing, and acknowledgment expectations. | Email is not assumed approved; recipient and sensitive-data minimization rules are unknown. | CDIT Support Lead + security/privacy reviewer | Before alerts; channel and routing policy approved. |
| D-07 | Choose agent shared-state storage and blackboard schema/versioning, retention, and access controls. | Prototype stack suggests SQLite, but run concurrency, audit, and retention needs need confirmation. | Shawn's Lane | Before implementation; schema and lifecycle decision recorded. |
| D-08 | Calibrate claim-level confidence thresholds and verify whether scores are calibrated probabilities or qualitative bands. | Current bands are proposed and must be measured; score never establishes truth or authority. | Shawn's Lane + evaluation reviewer | Before gating decisions; held-out synthetic calibration report accepted. |
| D-09 | Approve factuality/hallucination test set and must-pass threshold for each agent and end-to-end workflow. | Proposed zero unsupported material claims/citations on held-out must-pass cases needs rubric and reviewer agreement. | Shared Lane | Before build gate; labeled synthetic set and scoring protocol approved. |
| D-10 | Define timestamp granularity, clock source, audit fields, retention, and safe alert payload. | Operational/audit requirements and privacy constraints are unknown. | Shawn's Lane + security/privacy reviewer | Before audit/notification implementation; event contract approved. |
| D-11 | Decide conditions for agent-resolved vs. human-resolved status and separate permission for Resolved vs. Closed. | Finalization can have customer/process impact; must be explicitly delegated. | CDIT process owner + Shared Lane | Before any case-state write; transition authority documented. |
| D-12 | Revisit live integration, production authentication, real customer data/PHI, and model/provider approval. | Explicitly outside current planning/prototype scope pending CDIT authorization and safeguards. | Project lead + CDIT security/privacy/legal | Only in separately authorized phase; approvals and data-flow assessment complete. |
| D-13 | Revisit external email alerts and customer-facing autonomous responses. | Requires approved channels, recipients, templates, consent/policy checks, and audit. | CDIT Support Lead + project lead | Separately authorized phase; written policy and acceptance tests complete. |

## Recorded recommendations

- Use case-based action authorization within tier-based routing; urgency selects the path, while case evidence, approved procedure, risk, and explicit permission determine allowed action.
- Permit bounded agent sub-actions (for example, request identified missing documentation and set Waiting on Customer) when explicitly authorized; do not infer missing fields or mark a case Resolved merely because a request was sent.
- Allow full agent resolution only for documented, deterministic, reversible case patterns that pass evidence, policy, permission, and audit checks. Keep Closed separately controlled unless explicitly delegated.
- For parallel analysis, compare evidence and policy fit; do not choose a winner by confidence. Material disagreement or uncertainty goes to a human.
- Timestamp each workflow stage and handoff. Notifications should be minimal and use only an approved channel.
- Keep blackboard entries versioned, attributable, case-scoped, minimally populated, and immutable after handoff; preserve conflict and uncertainty.
