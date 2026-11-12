# Synthetic live Triage diagnostic

**Diagnostic only.** This report records real, billable Claude Sonnet 5.5 calls on synthetic cases. It does not approve draft labels or represent full MAO accuracy.

- Batch run: CDIT-LIVE-EVAL-d6e42f86-d288-44bb-899a-4820bc0e0ed6
- Started/report time: 2026-11-09T19:18:00.406589+00:00
- Dataset: CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v1 (DRAFT_NOT_APPROVED)
- Dataset SHA-256: a4d6d2b6e6bbb21584ae2a9b86da13c32b62e30c3a047a1bc4c53f08f72d7c82
- Label approval flags: approved=False, scoring_authorized=False
- Cases/items selected: 1 / 1
- Calls: 1 (authorized=True, sequential=True, retries=0)
- Model / contract: claude-sonnet-5-5 / 0.1.0-proposed
- Input/output tokens: 1288 / 752

## Observed Triage results

- Category proposals: 0/1 matched (0.0%); 0 items did not return a validated model proposal.
- Item spans: 1/1 matched (100.0%).

No urgency or destination accuracy is calculated: the A2 contract requires both to remain Unknown until human review. Auditor band/route decisions are also not scored by this run.

| Case | Trace ID | Intake | Triage | Calls | Category matches |
| :--- | :--- | :--- | :--- | ---: | :--- |
| SYN-EVAL-067 | TRACE-43379b34-cae0-46ca-b362-74c309572a0f | ready_for_triage | proposal_for_human_review | 1 | 0/1 |

## Limits

- knowledge: see separate non-billable Knowledge diagnostic
- auditor_band_and_route: not_scored_by_triage_runtime
- troubleshooting: not_run
- documentation: not_run
- full_mao: not_run
- actual_model_cost: not_calculated

No raw case text, API key, model rationale, or unredacted prompt payload is stored in this report. Input and evidence are identified by hashes.
