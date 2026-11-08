# Synthetic evaluation draft v1

**Status: DRAFT / NOT APPROVED / NOT SCORED.** This is a 100-case synthetic label-review draft for Manny. It is not gold data, an operational routing policy, or evidence of agent accuracy.

## Approval and use

Manny is the single label author, reviewer, and approver for this assignment. No labels become approved until Manny reviews the case wording, item segmentation, category proposal, urgency proposal, Auditor outcome, evidence expectations, and gate expectations and records approval. Do not score this draft. The deferred evaluator agent is not part of the product workflow.

The cases are synthetic and contain no real names, tickets, PHI, credentials, or company records. Marker strings such as `SYNTHETIC-SSN-0000` are test tokens, not real identifiers.

## Relationship to current behavior

Current A2 contract output fixes urgency and destination to `unknown` while a human Auditor remains responsible for assigning the band and route. Each case keeps this runtime expectation separate from a draft `auditor_decision_proposal`. The proposals do not establish low/medium/high/urgent thresholds, SLA guarantees, or operational rules. Unknown categories remain unknown until human assignment.

The 80-row `CASE-SCENARIOS.md` catalog is a development resource, not evaluation truth. Its rows, outcomes, urgency examples, and rationale were not copied as expected labels. Category names are vocabulary only; every proposed label here is newly authored for review. The case validator checks text for exact duplicate overlap with existing case suites and the catalog.

## Coverage and limitations

The draft includes prompt-injection attempts in retrieved knowledge and attachment contexts, plus a separate benign-quoted-instruction control, benign quoted instructions, synthetic sensitive-data markers, stale and conflicting sources as separate cases, ambiguous severity, a major outage, clinical-advice request, tool/model outage, role-denial, missing-detail pressure, linked multi-item requests, source/claim grounding, and no-write authority. The file includes a computed per-gate challenge/control count; these are coverage counts only, not pass rates. Several synthetic source IDs are placeholders and must be checked against the approved fixture corpus before scoring.

No model was called and no result was scored. The manifest records only draft expectations. Existing evaluator and harness artifacts were not changed.
