# Synthetic evaluation draft v1

**Status: DRAFT / NOT APPROVED / NOT SCORED.** This is a 100-case synthetic label-review draft for Manny. It is not gold data, an operational routing policy, or evidence of agent accuracy.

## Approval and use

Manny is the single label author, reviewer, and approver for this assignment. The category vocabulary, three-band scheme (Low/Medium/High), Urgent-as-High/P1 attention flag, Unknown-to-Auditor handling, and propose-only boundary were already agreed; this draft does not ask Manny to decide those policies again. Before scoring, Manny reviews this draft's application of those rules to each case, including segmentation, category, Auditor band/route, evidence expectations, and gate outcomes. Do not score this draft. The deferred evaluator agent is not part of the product workflow.

The cases are synthetic and contain no real names, tickets, PHI, credentials, or company records. Marker strings such as `SYNTHETIC-SSN-0000` are test tokens, not real identifiers.

## Relationship to current behavior

Current A2 contract output fixes urgency and destination to `unknown` while a human Auditor remains responsible for assigning the band and route. Each case keeps this runtime expectation separate from a draft `auditor_decision_proposal`. The proposals do not establish low/medium/high/urgent thresholds, SLA guarantees, or operational rules. Unknown categories remain unknown until human assignment.

The 80-row `CASE-SCENARIOS.md` catalog is a development resource, not evaluation truth. Its rows, outcomes, urgency examples, and rationale were not copied as expected labels. Category names are drawn from the approved synthetic vocabulary; the per-case expected outcomes are new and need review. The case validator checks text for exact duplicate overlap with existing case suites and the catalog.

## Coverage and limitations

The draft includes prompt-injection attempts in retrieved knowledge and attachment contexts, plus a separate benign-quoted-instruction control, benign quoted instructions, synthetic sensitive-data markers, stale and conflicting sources as separate cases, ambiguous severity, a major outage, clinical-advice request, tool/model outage, role-denial, missing-detail pressure, linked multi-item requests, source/claim grounding, and no-write authority. The file includes a computed per-gate challenge/control count; these are coverage counts only, not pass rates. All 17 proposed source IDs are currently absent from the local synthetic knowledge/policy corpus; map them to approved synthetic passages or build those passages before scoring grounding/retrieval gates.

No model was called and no result was scored. The manifest records only draft expectations. Existing evaluator and harness artifacts were not changed.
