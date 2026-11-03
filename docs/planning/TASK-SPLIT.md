# Recommended task split

The lanes below are proposed areas of ownership, not confirmed assignments. Confirm Manny's and Shawn's availability and strengths before implementation begins.

| Lane | Proposed owner | Responsibilities | Deliverables | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| Manny's Lane | Manny | Convert the job description into support journeys; define synthetic ticket cases, issue categories, priority/SLA examples, Tier 1 limits, and acceptance criteria | Labeled synthetic ticket set; workflow and escalation matrix; requirements review | Shared Lane confirms scope and terminology |
| Shawn's Lane | Shawn | Compare RAG and local retrieval options; map document metadata/version needs; recommend evaluation method and privacy/data-flow questions | Retrieval/data-source note; architecture recommendation; evaluation rubric and risks | CDIT product documents remain unavailable; use mock documents |
| Shared Lane | Manny + Shawn + project lead | Agree on MAO coordinator and role contracts, input/output schema, human approval points, role/access model, and project decisions; integrate lane results and review | Approved PRD, interface contracts, final review checklist | Depends on initial findings from both lanes |

## Suggested sequence

1. Shared Lane freezes prototype boundaries: synthetic data, no live Salesforce, no PHI.
2. Manny's Lane and Shawn's Lane work independently on workflow cases and retrieval/architecture research.
3. Shared Lane reconciles terminology, tool boundaries, evaluation criteria, and unresolved CDIT questions.
4. Only after PRD review, authorize implementation slices and assign confirmed owners.

## Collaboration rules

- Use one shared decision log for cross-lane choices.
- Keep generated examples synthetic and label them clearly.
- Escalate changes to data access, model provider, PHI handling, authentication, or Salesforce scope to Shared Lane before implementation.
- Each contribution should state files changed, rationale, validation, and unresolved questions.