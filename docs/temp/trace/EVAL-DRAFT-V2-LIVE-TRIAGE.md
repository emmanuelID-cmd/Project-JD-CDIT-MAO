# Synthetic live Triage diagnostic

**Diagnostic only.** This report records real, billable Claude Sonnet 5.5 calls on synthetic cases. It does not approve draft labels or represent full MAO accuracy.

- Batch run: CDIT-LIVE-EVAL-0b64472b-7dde-4a5b-a772-746d51104344
- Started/report time: 2026-11-09T21:48:28.374238+00:00
- Dataset: CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v2 (DRAFT_NOT_APPROVED)
- Dataset SHA-256: f3e40a8d940e5066a0a09145a2dd434fbc40485f5aa5dbc32e12fc77e421fd74
- Label approval flags: approved=False, scoring_authorized=False
- Cases/items selected: 100 / 105
- Validated model responses: 46
- SDK create invocations: 47 (method-invocation count, not provider billing confirmation).
- Safe failure-code counts: {'ambiguous_segmentation_requires_auditor': 45, 'triage_provider_output_rejected': 1}
- Model / contract: claude-sonnet-5-5 / 0.1.0-proposed
- Input/output tokens: 60099 / 25896

## Observed Triage results

- Category proposals paired with an expected item: 30/32 matched (93.8%); 2 differed from the draft expectation.
- Abstentions with expected outputs: 14; unpaired extra model items: 0; expected items without a validated result: 59.
- Item spans: 46/46 matched (100.0%).

No urgency or destination accuracy is calculated: the A2 contract requires both to remain Unknown until human review. Auditor band/route decisions are also not scored by this run.

| Case | Trace ID | Intake | Triage | Calls | Category matches |
| :--- | :--- | :--- | :--- | ---: | :--- |
| SYN-EVAL-001 | TRACE-68d6fc4e-c931-482d-8a08-e7857f5c2ced | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-002 | TRACE-35623d37-7335-4ebe-bd7e-42c92606bcda | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-003 | TRACE-15410089-4a04-4c5f-bb32-879cdb7064e5 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-004 | TRACE-2db50a5d-ed4f-43c6-b75a-5dce6f95905a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-005 | TRACE-c19ba5d1-1021-481c-b0b3-7da8617024e5 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-006 | TRACE-9e6f69fd-d840-47b2-bdfd-5962aed1602e | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-007 | TRACE-51345ac6-6913-4de0-a808-8fa17ed05d28 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-008 | TRACE-d9eb7df6-6a54-4026-9e0b-9d8eaf3c7085 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-009 | TRACE-fdbaf554-cf52-4cf1-b6c4-b2e9ecf7b574 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-010 | TRACE-009afd84-966b-4f14-b438-6924216dea30 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-011 | TRACE-7588acd2-2661-4baf-8db1-5b9527d08a7b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-012 | TRACE-941fa104-4686-414b-bcc9-91e514ab8945 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-013 | TRACE-496bd775-9836-472b-96d1-78d09623b265 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-014 | TRACE-c4913ffd-cb07-4a2e-a2a6-6383b429896b | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-015 | TRACE-02405349-e96a-48fa-871f-ecba7a935c70 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-016 | TRACE-0b35dc8a-544b-4fac-9780-3eea18bf4d5e | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-017 | TRACE-51ce8a18-144f-4f46-b150-60d6ead02f9d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-018 | TRACE-db9176c5-0b1d-4538-aa49-1f69a82a6b82 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-019 | TRACE-fd4ac8d4-f003-4fc2-bee3-2e34a65c4705 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-020 | TRACE-87f688a1-fdb5-49fc-9324-88efeab64621 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-021 | TRACE-df7693db-da8f-45b3-8be0-466f4dc61b1f | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-022 | TRACE-fabd3b18-94ae-4f20-863b-dc9a5889733a | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-023 | TRACE-37965340-38b9-404a-abcf-41c3f0f56ea6 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-024 | TRACE-96c58348-9178-4055-a92a-620f5d3238dd | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-025 | TRACE-c9c7f68b-97c3-4bea-a319-5a7ad5d179f1 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-026 | TRACE-e1b04250-8d27-448b-81d5-d422d94964cc | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-027 | TRACE-43e2bfd7-d503-494c-965d-20289c30357b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-028 | TRACE-beabb2f5-5013-4fd1-a901-bf6384f45f7f | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-029 | TRACE-e7297dad-b218-4438-a37b-b7cd3e3ef493 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-030 | TRACE-392eb2f8-9f68-4c5f-97e3-518e38830643 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-031 | TRACE-ef1f4cd3-0484-4b74-9c7d-5cfb0132df73 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-032 | TRACE-ebad36b5-0955-44e8-9a29-effb19f50609 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-033 | TRACE-68ca3b5e-ecac-498b-90c7-ed22e25fbe2f | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-034 | TRACE-42e08ba3-1979-4187-b3e5-fbc0db782cc2 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-035 | TRACE-a349d690-1ff6-4fd8-a1e2-2f7928a22859 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-036 | TRACE-127f375a-5a70-481d-a153-17193aac6f71 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-037 | TRACE-e75b3f61-1bd3-4ccf-9d6a-2e2e51723d77 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-038 | TRACE-8c6e3cb5-7fb8-4f5f-ba12-779d103b0eea | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-039 | TRACE-720a4d22-04ac-4daa-8d7e-2a83c449fdfc | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-040 | TRACE-5a13daa7-37f0-4bb3-9b50-28b2e735fe82 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-041 | TRACE-703c49a0-f185-488d-aa37-cf1a91217452 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-042 | TRACE-82fb1964-908d-4cb5-b527-565fd84a1573 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-043 | TRACE-ec7f4a88-b358-4303-a8bf-c395d989d1be | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-044 | TRACE-1678cb44-be45-4053-aae3-215b7e58d09e | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-045 | TRACE-61586129-ab6d-4c34-9168-fbd59a3f27b0 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-046 | TRACE-9367d606-a361-4d2a-b1c1-050cee2a2674 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-047 | TRACE-3c66a875-77f5-4cbc-b9a7-3c531f78bb5f | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-048 | TRACE-32e035ae-ed07-45cf-aa40-d7834b3ce092 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-049 | TRACE-17842f7b-cb9d-4be9-bb8c-a5204707e838 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-050 | TRACE-ac6b0320-37a3-4a74-a15b-4fd57c162eb2 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-051 | TRACE-8d51216f-bdb3-4b04-a46a-19fa47eaadc6 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-052 | TRACE-717da110-c73d-4daf-b192-1f2c3ee43a88 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-053 | TRACE-1e957273-e084-41bc-869a-5eaa7e3220a4 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-054 | TRACE-1e1eb9a9-4491-4878-8878-aa62d3025c8c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-055 | TRACE-e7ecc909-e369-4432-bc16-2718636d0df6 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-056 | TRACE-1f3af46b-7e9e-4400-a456-61895f9b9e52 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-057 | TRACE-010aaed0-712d-40b1-b0c2-43a16c5ddd24 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-058 | TRACE-3ba91e94-1acf-4a7a-bf5e-60e351727882 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-059 | TRACE-744c42ed-f498-44fb-a334-de9b9d0fbc42 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-060 | TRACE-0fea13e2-1d5d-4fb2-bd5c-c2b171bb943c | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-061 | TRACE-4abb46c4-12fe-4015-84e3-13f11e92cbb1 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-062 | TRACE-d08984ae-0b25-4f4f-bfd8-8bf983f8a028 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-063 | TRACE-29d65bb4-7e7b-4f5f-b8cb-8d9ec11638e2 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-064 | TRACE-02d46cc2-4164-4def-864c-020c5fecf5e3 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-065 | TRACE-4839a7e3-3b41-4d9c-aa61-97068e5aa4d9 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-066 | TRACE-2f1118aa-0bff-4477-9213-ba203fe6cbfe | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-067 | TRACE-b8aa1907-96b3-4f8b-b18c-98521df7bb5e | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-068 | TRACE-3d6f2b26-30a5-41e0-b989-6f4774861ba2 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-069 | TRACE-6f2fe7b3-705a-46ba-ad38-6d6fd2a1b6b5 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-070 | TRACE-d44e30e7-0da9-4ba5-aa82-4a64c0fb0f0c | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-071 | TRACE-54263983-47c4-4817-8d47-d76202b1b621 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-072 | TRACE-900f9abc-a704-4532-a962-4b371b944dbe | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-073 | TRACE-8237b796-536e-4e73-96c3-7f32ade22508 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-074 | TRACE-d4289217-e40d-4afe-b4f5-ca1f55ecb8fa | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-075 | TRACE-c1b2394b-8ec3-44be-9b8b-1ab7726c2f1f | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-076 | TRACE-ac933c1f-dc0e-40c9-a1f3-25443f0bc0aa | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-077 | TRACE-ab2f4097-b108-4ff4-97d6-e443d5026514 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-078 | TRACE-098e6df1-46d9-4e84-b8ab-3a992721f945 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-079 | TRACE-a985aba0-b813-4879-bbb8-f7c560fce23d | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-080 | TRACE-55833169-5356-4589-af9a-5a29e4cb6f9a | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-081 | TRACE-df04ada5-ce37-458d-8bbb-caf8c013463b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-082 | TRACE-3d4e844b-4c3d-4ca0-826e-71683cdd7e40 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-083 | TRACE-77b9b998-3b4d-4725-a00f-dee9616a75a8 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-084 | TRACE-990adc59-9892-4dbc-9de1-864784208409 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-085 | TRACE-ee6b76a8-7b99-4910-8537-6c6e17061d70 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-086 | TRACE-5402a7e5-be41-459a-9863-abb250528251 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-087 | TRACE-819c78b9-e45e-4ba1-aa2d-19aef6e11494 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-088 | TRACE-4e5ed896-8e8a-4be8-ae78-b5e4523e5cf8 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-089 | TRACE-cfe391cc-8cfc-40bc-a855-d19311bf9bc0 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-090 | TRACE-be0c48a7-8a30-49b0-8e9a-5a45de6c6413 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-091 | TRACE-c7628b60-2040-4d29-9e5b-4944a28b00aa | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-092 | TRACE-676314a8-c567-40b8-bf54-7ae1521f6b52 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-093 | TRACE-92833e75-35bd-4669-b11e-5248e026c8af | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-094 | TRACE-673cfa84-8088-4568-a9eb-9500065213db | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-095 | TRACE-ace8576a-2c92-4a1c-b6f7-cae81fc2926f | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-096 | TRACE-f622e054-bf11-4c9f-a756-6854b05bb18a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-097 | TRACE-008bc3cf-f770-4bf3-b7b0-29ba8bf51676 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-098 | TRACE-c81c205b-cd84-4313-9c9a-415623cfeda3 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-099 | TRACE-c6032ce0-2c51-4d3f-8e24-3c8d2be73aab | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-100 | TRACE-9df10e55-febf-4ae6-99f4-e8e093054862 | blocked_checkpoint | not reached | 0 | 0/0 |

## Limits

- knowledge: see separate non-billable Knowledge diagnostic
- auditor_band_and_route: not_scored_by_triage_runtime
- troubleshooting: not_run
- documentation: not_run
- full_mao: not_run
- actual_model_cost: not_calculated

No raw case text, API key, model rationale, or unredacted prompt payload is stored in this report. Input and evidence are identified by hashes.
