# Synthetic live Triage diagnostic

**Diagnostic only.** This report records real, billable Claude Sonnet 5.5 calls on synthetic cases. It does not approve draft labels or represent full MAO accuracy.

- Batch run: CDIT-LIVE-EVAL-1fbd739a-333a-41ad-9857-c401493afca0
- Started/report time: 2026-11-10T15:23:10.882425+00:00
- Dataset: CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v3 (DRAFT_NOT_APPROVED)
- Dataset SHA-256: f3655b62a194ab5045b9f1ab0c79db046948fc02bb9bb9a8096340d00d481c6f
- Label approval flags: approved=False, scoring_authorized=False
- Cases/items selected: 100 / 105
- Validated model responses: 58
- SDK create invocations: 92 (method-invocation count, not provider billing confirmation).
- Safe failure-code counts: {'triage_provider_output_schema_invalid': 34}
- Model / contract: claude-sonnet-5-5 / 0.1.0-proposed
- Input/output tokens: 165544 / 14594

## Observed Triage results

- Category proposals paired with an expected item: 57/58 matched (98.3%); 1 differed from the draft expectation.
- Abstentions with expected outputs: 0; unpaired extra model items: 0; expected items without a validated result: 47.
- Item spans: 97/97 observed spans matched (100.0%); 8/105 expected spans were unavailable (observed coverage 92.4%).

No urgency or destination accuracy is calculated: the A2 contract requires both to remain Unknown until human review. Auditor band/route decisions are also not scored by this run.

| Case | Trace ID | Intake | Triage | Calls | Category matches |
| :--- | :--- | :--- | :--- | ---: | :--- |
| SYN-EVAL-001 | TRACE-96009fcf-c026-4d09-ac0a-e108a9d096e3 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-002 | TRACE-e6a120b2-c0c3-4b95-9fce-1add82097d8a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-003 | TRACE-bc03c197-9ac6-4a05-8b65-2c1e25f817d4 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-004 | TRACE-e2befd6b-d1fd-49b4-853b-a19c64969928 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-005 | TRACE-db9e02de-a4ab-40e2-80f4-2c13c13b2a02 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-006 | TRACE-ef797a0f-f1b7-41b6-b176-d248ff51936d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-007 | TRACE-e34f237a-106b-411b-842f-2d7895eed0f8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-008 | TRACE-ca171089-6429-4545-8bf5-6d73d4cce255 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-009 | TRACE-bbde6a79-464e-4b0e-b8c1-dbb2c35132a5 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-010 | TRACE-4fb0fdc1-d8c5-44d0-888e-a2ffe067eb9a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-011 | TRACE-c6812fed-0e4b-41f3-acb8-2ed9ce027fda | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-012 | TRACE-98184f2d-9e21-449a-ba00-ca2d3f347d03 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-013 | TRACE-f3a2d12e-9c79-4a4c-8063-889ab493285d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-014 | TRACE-dffaad6c-4d87-4f48-9592-cab0ed074ec4 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-015 | TRACE-7ffcf465-6c51-40eb-a765-9e6bb8ff7ab3 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-016 | TRACE-c5917665-fe88-4e32-a247-848dbb9c6738 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-017 | TRACE-b985d632-29b4-47c5-be82-461f2b43a06c | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-018 | TRACE-d3c3b537-029c-4ef8-9b9d-6f47c6229991 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-019 | TRACE-d5ad26b3-5dcf-4163-bcd7-d042970bd085 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-020 | TRACE-80b8672e-1996-4d43-88fa-fe99ee15ca79 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-021 | TRACE-4c567435-91e3-44f5-9cbf-10e63d5e1afa | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-022 | TRACE-32c4513c-6fe9-4571-bd80-1ef84eeea8f8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-023 | TRACE-2a3e4252-b507-47d0-bbf0-c658c8c81524 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-024 | TRACE-ed1c01ce-98f3-40d9-a9d7-30b259ad00d4 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-025 | TRACE-688df9d5-8326-4002-8e1e-3bae693475e8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-026 | TRACE-a8382c5b-25d3-48f6-9adc-d6e04d5b8d90 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-027 | TRACE-59a6eed3-4bcd-453e-a4d8-76a829638d6e | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-028 | TRACE-ae4dfe98-084e-4c28-a72f-cc486de26e72 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-029 | TRACE-52574b05-2c9d-4f72-92f6-c59e9c857fda | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-030 | TRACE-86a8610b-3461-48f5-976c-402cc6c0ec7c | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-031 | TRACE-bd09a5c9-e26b-4369-9759-40a095c2fb25 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-032 | TRACE-19b2cdd3-ac27-49fc-b980-0f97a70210e8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-033 | TRACE-11c84c87-5c7a-4025-acc8-b2de65670ded | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-034 | TRACE-6fa7421c-b1b8-40bf-ad4a-b071202e2d95 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-035 | TRACE-40bcb347-270c-4214-a100-2bc4bedd95ab | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-036 | TRACE-358e8ab3-412c-4fb7-81fa-c18a574fa17a | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-037 | TRACE-ddd83a24-1c7a-47c1-8a0d-a066a6c17286 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-038 | TRACE-b5a21699-5190-498c-aec7-fcbfbc3b55da | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-039 | TRACE-7e6c63d9-6370-47ed-bbbf-606712acd9d4 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-040 | TRACE-4f526e49-3870-4a05-bd65-018cc03d3f4b | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-041 | TRACE-4e5ba132-9961-4353-a53b-e08d5dd3babc | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-042 | TRACE-7d92ac6f-c274-40ce-ab43-7d3febc23890 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-043 | TRACE-8c05506b-757e-4ba5-8f5d-55eeca3ea5ad | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-044 | TRACE-5b75e9d8-2ed9-4b57-82ac-f2023ffb7e90 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-045 | TRACE-5bb0b811-a272-410f-9fc4-3f31b276a6c5 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-046 | TRACE-d185cff7-5240-44ca-9b88-8b4e01afaa09 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-047 | TRACE-200d3d78-5b94-4cf1-b96c-78d4793c3854 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-048 | TRACE-143193db-3d9f-4b58-a504-d3829109f3ae | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-049 | TRACE-2797ae3d-ce25-41e0-ac9f-9765a2a81250 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-050 | TRACE-8e2375c2-b034-4379-9367-2c9e22378e00 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-051 | TRACE-7060af7a-4afa-485e-8746-2dbb34450450 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-052 | TRACE-9005a998-20cc-419e-9925-1333cf9ca925 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-053 | TRACE-0d7c0ad1-0a52-4e96-82ac-8701205ac89c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-054 | TRACE-45b83821-5b17-4632-937c-dfc828be2c97 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-055 | TRACE-6b75e34f-02b8-4671-b57e-f8f833471bff | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-056 | TRACE-594ff204-e68d-4123-b262-b63eb07a2734 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-057 | TRACE-c970b875-d3f8-4a72-b69a-e102402ea903 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-058 | TRACE-67778c44-5e76-4d02-b5a2-90193e3dbcea | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-059 | TRACE-70790641-55da-4b93-9d94-0575db935fff | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-060 | TRACE-8cbd1757-901b-4f27-9540-567379860e80 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-061 | TRACE-83318cbc-7329-4243-b753-a7677f6a3711 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-062 | TRACE-d7665222-735d-4b41-b6d2-b9234eaac2f5 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-063 | TRACE-52c8108d-eea1-4c65-8527-5768114f1092 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-064 | TRACE-214f7e5a-629c-45f4-a21c-a58f9b681fed | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-065 | TRACE-c6cf9d26-83bb-4ee0-8ed8-b673b2c70585 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-066 | TRACE-fd20c434-b6b8-4e64-9786-f9f41f1dee88 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-067 | TRACE-7c8c123f-051a-4a07-ac87-0674509cb578 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-068 | TRACE-78d8c3e6-3a42-48ae-b122-cbedce6ede70 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-069 | TRACE-f041ef71-e033-4fd8-b0d6-825f142e8a43 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-070 | TRACE-973a1b8a-5f42-4bfa-b475-4725b1997793 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-071 | TRACE-d60ad43d-9000-4589-b3e1-b26dc956ec63 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-072 | TRACE-03d73524-52f9-4b73-804c-c38946ec5877 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-073 | TRACE-47ba7dab-32e8-49ba-acab-4993b5870ce8 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-074 | TRACE-364092fa-2bea-4e9e-86b7-4d2df89a382f | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-075 | TRACE-9366eb1a-b123-4a4e-b847-779da66cfdf8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-076 | TRACE-7c4e67fc-6fb5-47d1-895e-d2d70c4c3294 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-077 | TRACE-51cb12bc-319b-4319-8792-50149f006084 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-078 | TRACE-82e48855-2667-4a52-b5aa-f0ef04a777b0 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-079 | TRACE-d7239d08-e591-40e6-aa68-ad846cd2d8ef | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-080 | TRACE-4f54846b-834a-4e70-bb4b-a96e834fa5c8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-081 | TRACE-d4f5e1ad-9406-4064-a2de-7cfd5082f983 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-082 | TRACE-825eb131-a2a5-412f-9073-47389d450801 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-083 | TRACE-9859768f-dc05-406c-b2b3-288a2d01c486 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-084 | TRACE-546c9fb1-61d3-49b9-b8aa-1e7f133f9e1b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-085 | TRACE-875da4c8-8593-4315-bc63-a87a45798052 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-086 | TRACE-c196b4ea-ca8a-48b5-85c5-f44a2890a91a | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-087 | TRACE-69e2fc3d-5028-49d3-ad93-8f8b360cff8a | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-088 | TRACE-e87d0774-efca-480e-acce-3f655f1c53d7 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-089 | TRACE-78143c54-b21a-4470-8ccb-dc0487ca6120 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-090 | TRACE-cf9a0a13-967d-41ef-8f77-e78a90cd22c1 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-091 | TRACE-7fb6eef0-1dc7-4523-aa20-0836ce5687be | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-092 | TRACE-081f4b3a-9886-4501-b3fb-cfde15fd09c6 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-093 | TRACE-d88a2f54-af48-4425-b529-caa6f7c96250 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-094 | TRACE-df89142d-0b44-4f53-8514-3f7b190e8c88 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-095 | TRACE-3707f541-6c41-44d1-88b2-94ed24ddac58 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-096 | TRACE-9058e0c3-fea6-4ea7-8b9d-58c26a918c01 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-097 | TRACE-aee8bacf-4975-4cbb-98db-4d18b8070ed9 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-098 | TRACE-0ea9cf47-d093-4c78-9a27-f3ac163f051e | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-099 | TRACE-9675e78d-34c5-42b0-aad2-95ef424432a7 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-100 | TRACE-a3039860-7a81-4a45-b2dc-35a0caa215c3 | blocked_checkpoint | not reached | 0 | 0/0 |

## Limits

- knowledge: see separate non-billable Knowledge diagnostic
- auditor_band_and_route: not_scored_by_triage_runtime
- troubleshooting: not_run
- documentation: not_run
- full_mao: not_run
- actual_model_cost: not_calculated

No raw case text, API key, model rationale, or unredacted prompt payload is stored in this report. Input and evidence are identified by hashes.
