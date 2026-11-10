# Synthetic live Triage diagnostic

**Diagnostic only.** This report records real, billable Claude Sonnet 5.5 calls on synthetic cases. It does not approve draft labels or represent full MAO accuracy.

- Batch run: CDIT-LIVE-EVAL-58417aca-0150-4dd7-a072-3dfce760156a
- Started/report time: 2026-11-10T15:28:28.435119+00:00
- Dataset: CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v3 (DRAFT_NOT_APPROVED)
- Dataset SHA-256: f3655b62a194ab5045b9f1ab0c79db046948fc02bb9bb9a8096340d00d481c6f
- Label approval flags: approved=False, scoring_authorized=False
- Cases/items selected: 34 / 39
- Validated model responses: 2
- SDK create invocations: 34 (method-invocation count, not provider billing confirmation).
- Safe failure-code counts: {'triage_provider_output_schema_invalid_items': 32}
- Model / contract: claude-sonnet-5-5 / 0.1.0-proposed
- Input/output tokens: 5665 / 709

## Observed Triage results

- Category proposals paired with an expected item: 0/2 matched (0.0%); 2 differed from the draft expectation.
- Abstentions with expected outputs: 0; unpaired extra model items: 0; expected items without a validated result: 37.
- Item spans: 39/39 observed spans matched (100.0%); 0/39 expected spans were unavailable (observed coverage 100.0%).

No urgency or destination accuracy is calculated: the A2 contract requires both to remain Unknown until human review. Auditor band/route decisions are also not scored by this run.

| Case | Trace ID | Intake | Triage | Calls | Category matches |
| :--- | :--- | :--- | :--- | ---: | :--- |
| SYN-EVAL-036 | TRACE-f4538373-8095-4a99-8ec1-5f9c94660766 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-050 | TRACE-a181106e-8526-4772-b489-462f82871edb | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-051 | TRACE-d818dbc0-fc59-495b-9113-c7437553268d | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-052 | TRACE-171763ff-5f8e-4e36-93f4-cab329712bf0 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-053 | TRACE-2db7c15c-8406-45f4-8f4f-d8f2bea7e90e | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-054 | TRACE-14ab0f92-e6db-4848-a8fa-1d06758e005d | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-055 | TRACE-3f6931c5-0500-4337-95f0-8bd28c1251ab | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-056 | TRACE-41b5da1c-d805-4088-afc8-935c53090fbd | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-057 | TRACE-3b9ce003-2fd4-4f5b-9b45-5c8a211f5d8f | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-058 | TRACE-16635cd8-c595-4909-b22a-d59ff6de6728 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-059 | TRACE-e32eef0a-e79e-4f70-b746-b6f07eb92ca4 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-060 | TRACE-76837d8b-045a-4996-a579-814ce9fdc46c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-061 | TRACE-a17c6232-c89c-4885-9706-84379f9e0d0c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-062 | TRACE-ba49809e-9380-46cf-8967-4cb07b32de39 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-063 | TRACE-bd5ed767-4aa8-4d4d-8046-ef6f6d7a13d4 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-064 | TRACE-57d080be-387f-40db-9b0d-11fcd6043e28 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-065 | TRACE-f0052bc1-05e0-4df8-b658-e577dae5cd34 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-066 | TRACE-d71ba69a-3fb0-4840-95df-e37e6af729ab | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-067 | TRACE-9e149c50-0d30-467e-bf34-634e904eab06 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-068 | TRACE-f9707baa-13b7-4814-b779-4191c2a25f7c | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-069 | TRACE-72bdda37-8888-494c-90f2-ccf09e0f5dc9 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-072 | TRACE-eaee5f73-c968-4d03-b552-083664cd1acb | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-073 | TRACE-5f540048-3a87-45ce-bcf9-70e7a8be81ad | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-081 | TRACE-9ad58286-bac7-4a27-b625-30793a4b0f82 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-082 | TRACE-72cdcf7e-0bf4-4b8b-b154-f6c6155507f0 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-083 | TRACE-0f92a2ae-d5be-4d62-8bfc-dee44c327890 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-084 | TRACE-33ed258b-2060-40f8-a4cc-612cbafdaec8 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-085 | TRACE-8ebaf888-a9cc-4bdf-a98b-0e3ad67f546a | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-086 | TRACE-f2c5f3af-ea90-49df-9f9d-4bf5fb9a9037 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-087 | TRACE-3c5ff4bc-1d7e-41a0-8fba-914e0d923312 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-088 | TRACE-668f4048-4132-4dde-ae56-df23efa2a6b2 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-089 | TRACE-37ba027a-e4fb-47d2-a69a-9050b87b5079 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-090 | TRACE-15548adf-b577-448c-9638-e2b94ef5c5ee | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-095 | TRACE-9edf66d5-21bf-47f6-bb07-a5c46ebe106d | ready_for_triage | needs_human_review | 0 | 0/0 |

## Limits

- knowledge: see separate non-billable Knowledge diagnostic
- auditor_band_and_route: not_scored_by_triage_runtime
- troubleshooting: not_run
- documentation: not_run
- full_mao: not_run
- actual_model_cost: not_calculated

No raw case text, API key, model rationale, or unredacted prompt payload is stored in this report. Input and evidence are identified by hashes.
