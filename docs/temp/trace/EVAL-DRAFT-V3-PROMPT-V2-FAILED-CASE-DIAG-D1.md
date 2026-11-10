# Synthetic live Triage diagnostic

**Diagnostic only.** This report records real, billable Claude Sonnet 5.5 calls on synthetic cases. It does not approve draft labels or represent full MAO accuracy.

- Batch run: CDIT-LIVE-EVAL-b4494692-8540-4578-a3f8-e7c6bd738802
- Started/report time: 2026-11-10T15:14:03.381368+00:00
- Dataset: CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v3 (DRAFT_NOT_APPROVED)
- Dataset SHA-256: f3655b62a194ab5045b9f1ab0c79db046948fc02bb9bb9a8096340d00d481c6f
- Label approval flags: approved=False, scoring_authorized=False
- Cases/items selected: 25 / 30
- Validated model responses: 1
- SDK create invocations: 25 (method-invocation count, not provider billing confirmation).
- Safe failure-code counts: {'triage_provider_response_incomplete': 1, 'triage_provider_output_schema_invalid': 23}
- Model / contract: claude-sonnet-5-5 / 0.1.0-proposed
- Input/output tokens: 1907 / 196

## Observed Triage results

- Category proposals paired with an expected item: 0/0 matched (N/A); 0 differed from the draft expectation.
- Abstentions with expected outputs: 1; unpaired extra model items: 0; expected items without a validated result: 29.
- Item spans: 30/30 observed spans matched (100.0%); 0/30 expected spans were unavailable (observed coverage 100.0%).

No urgency or destination accuracy is calculated: the A2 contract requires both to remain Unknown until human review. Auditor band/route decisions are also not scored by this run.

| Case | Trace ID | Intake | Triage | Calls | Category matches |
| :--- | :--- | :--- | :--- | ---: | :--- |
| SYN-EVAL-034 | TRACE-f31b4563-1ca8-4d49-9d30-e70f55627174 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-036 | TRACE-ed775c2f-16b0-43c8-802f-f7747d2f0fd3 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-047 | TRACE-6762d9e6-ace3-4215-8f63-196d6e406444 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-048 | TRACE-1994c78b-881d-4357-b18b-26946225858c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-049 | TRACE-108416da-510e-42b2-aec8-ecf30e440d50 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-053 | TRACE-f846dd4e-f61d-4585-b1b2-3c878034c351 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-061 | TRACE-0f6c9709-8003-4459-996a-41ce029683b6 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-062 | TRACE-235e4e57-c6da-495d-bb2c-8e3f6469a1bf | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-063 | TRACE-d4b88113-28b7-471a-b438-d6b20d2370c4 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-064 | TRACE-d7926006-a305-4b37-a98c-dd496c12fb3c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-065 | TRACE-4b9578b3-cda9-43e2-bda2-7e10fd22e9c5 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-066 | TRACE-54c42fec-bf2b-47ce-836d-cff81d776af9 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-067 | TRACE-f04a83f8-237a-40b3-9a95-e32b41b5e6c8 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-069 | TRACE-d3a91e80-5784-497e-b981-443921174a52 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-081 | TRACE-dab09958-62eb-4e52-94f7-010bdc2dc656 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-082 | TRACE-60da6765-1f74-48ab-b294-2382f76940f9 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-083 | TRACE-3e3ac4cc-ad14-45f3-92ae-e42ebcde7b5b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-084 | TRACE-56b0ab21-0deb-4f0b-af6f-8bd3e3b3f395 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-085 | TRACE-0daf5efa-21c3-4612-8783-4d9524a08651 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-086 | TRACE-3734b83a-46b8-4d2b-bbf9-e5d30e522a61 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-087 | TRACE-1bd35d1d-d8ad-45a3-8171-caf5687e3382 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-088 | TRACE-aa16992c-6daf-47ba-bd97-4be2e62c175b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-089 | TRACE-1afa8953-88b9-4b7d-b490-37bba913dfb1 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-090 | TRACE-6f385e91-2d5a-457e-b8e5-09f8913babe4 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-094 | TRACE-9b25fa0f-b7c5-46e9-ae72-b47a9089f0bc | ready_for_triage | needs_human_review | 0 | 0/0 |

## Limits

- knowledge: see separate non-billable Knowledge diagnostic
- auditor_band_and_route: not_scored_by_triage_runtime
- troubleshooting: not_run
- documentation: not_run
- full_mao: not_run
- actual_model_cost: not_calculated

No raw case text, API key, model rationale, or unredacted prompt payload is stored in this report. Input and evidence are identified by hashes.
