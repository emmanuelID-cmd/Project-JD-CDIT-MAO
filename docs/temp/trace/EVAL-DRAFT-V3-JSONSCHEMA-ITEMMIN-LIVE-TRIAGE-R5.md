# Synthetic live Triage diagnostic

**Diagnostic only.** This report records real, billable Claude Sonnet 5.5 calls on synthetic cases. It does not approve draft labels or represent full MAO accuracy.

- Batch run: CDIT-LIVE-EVAL-41e9f624-c66c-4a3a-9e5e-f6b76726d1f1
- Started/report time: 2026-11-10T15:35:40.513262+00:00
- Dataset: CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v3 (DRAFT_NOT_APPROVED)
- Dataset SHA-256: f3655b62a194ab5045b9f1ab0c79db046948fc02bb9bb9a8096340d00d481c6f
- Label approval flags: approved=False, scoring_authorized=False
- Cases/items selected: 100 / 105
- Validated model responses: 59
- SDK create invocations: 92 (method-invocation count, not provider billing confirmation).
- Safe failure-code counts: {'triage_provider_output_schema_invalid_items': 33}
- Model / contract: claude-sonnet-5-5 / 0.1.0-proposed
- Input/output tokens: 168905 / 16159

## Observed Triage results

- Category proposals paired with an expected item: 56/59 matched (94.9%); 3 differed from the draft expectation.
- Abstentions with expected outputs: 0; unpaired extra model items: 0; expected items without a validated result: 46.
- Item spans: 97/97 observed spans matched (100.0%); 8/105 expected spans were unavailable (observed coverage 92.4%).

No urgency or destination accuracy is calculated: the A2 contract requires both to remain Unknown until human review. Auditor band/route decisions are also not scored by this run.

| Case | Trace ID | Intake | Triage | Calls | Category matches |
| :--- | :--- | :--- | :--- | ---: | :--- |
| SYN-EVAL-001 | TRACE-daa69fe8-9cd8-4009-9f89-c7456aacfa51 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-002 | TRACE-3b842cca-8b8a-4aa2-ac91-ce78410c2a97 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-003 | TRACE-261d640b-399f-432b-98b5-ed9a555fe588 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-004 | TRACE-fc9696ff-7d26-443d-a886-0af1eba120bb | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-005 | TRACE-41027752-9e6b-4d4d-bbdd-17bbe8633b33 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-006 | TRACE-97bfc5fa-1b46-458d-b346-a89610a7070d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-007 | TRACE-46916449-1b6c-4314-96ff-26c3a0795d79 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-008 | TRACE-f8632431-ae79-46ee-b44b-1dd3296605ed | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-009 | TRACE-a774bf84-f933-4175-b3a8-80eab1dab072 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-010 | TRACE-721e40af-d57d-4adf-884e-5a55a5d0df9f | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-011 | TRACE-9523252e-8f40-416c-a7a9-b3fba3f9f3b5 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-012 | TRACE-ee487b65-0afb-4b8a-b2ea-e1b6da464ccc | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-013 | TRACE-a4cce769-f5ab-4c5a-b658-55b66c4515ee | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-014 | TRACE-bf3d5ac4-8beb-4ca7-9f7f-c8aa3aa88aa3 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-015 | TRACE-22568660-1f4a-43b0-8ef4-4eb96d2fb366 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-016 | TRACE-a9b021d6-92cd-4f9f-8da7-1d85a98cb00d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-017 | TRACE-e0d598e6-7316-419b-be2b-a7535df9179e | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-018 | TRACE-d6508eee-db55-423d-a49d-0836acb42602 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-019 | TRACE-e0bc61d4-6dd7-4f6f-b3da-c0c917b48246 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-020 | TRACE-e0f42a08-ed9b-4f4d-ac85-7fc8be3cd0aa | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-021 | TRACE-6e6fb8b4-18f8-4b4b-9cb8-92d38dd9002d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-022 | TRACE-7ea2ceed-0636-466a-a8ae-16521b5c78b6 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-023 | TRACE-fd1b6974-6908-4f6c-8f4b-d1654929dcad | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-024 | TRACE-e1a7f617-15de-46b1-b25e-da71f88dcb74 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-025 | TRACE-1b0fbf37-931b-428a-be82-9770be770eb8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-026 | TRACE-0e6c25b5-7fe9-468d-a61c-f9f970099171 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-027 | TRACE-94679322-1ff8-4b2a-b3b7-625708c420eb | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-028 | TRACE-10648d31-492e-4482-956f-7dafbafc6eb6 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-029 | TRACE-e48c2fd5-093f-4f8d-ab86-bc224685a5b3 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-030 | TRACE-cece3bc3-7fd3-48bf-b38b-7564e65705a1 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-031 | TRACE-86cdb0eb-6528-413c-9e48-d791bd0a60e3 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-032 | TRACE-9a4940e9-4422-493b-b2e4-3c2b026feb20 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-033 | TRACE-be1ab925-ada2-4a23-a47a-14533a714179 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-034 | TRACE-58dfa16a-b025-47f7-8013-705da235da12 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-035 | TRACE-a09b7006-c651-4d90-adf7-567714912859 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-036 | TRACE-3fb92e1e-6cd7-4b24-b33a-371844a2c70f | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-037 | TRACE-319caba1-32af-4bb9-a2f6-85a0c046b5e7 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-038 | TRACE-4eb4423a-9fe2-4356-af67-7132c44024eb | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-039 | TRACE-c5a0ee3c-c41d-4787-99f7-484dcbe678a0 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-040 | TRACE-ea18da7c-e6bb-4c3f-8abb-5edd1475fd2f | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-041 | TRACE-f4f0843a-c5bb-4264-87c0-9135bfc70189 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-042 | TRACE-da5c6767-2929-428c-85a1-01cf5ac1df40 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-043 | TRACE-b9c52db8-8162-4e79-be5b-5173febd6c52 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-044 | TRACE-45031008-7e46-4312-b38c-d86e56d0cdd1 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-045 | TRACE-425214f9-0574-49db-b0f4-88173630782c | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-046 | TRACE-f722aa60-9e2a-47b1-91fb-5f5b46ccc425 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-047 | TRACE-3854e917-fa7f-4181-a9f7-51f4bcf338c4 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-048 | TRACE-7a84cd9e-fe60-489e-a81d-f2b0e417ba0b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-049 | TRACE-131eb729-5699-4264-9ca4-8401611809e4 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-050 | TRACE-3f54ab20-fb1f-4361-ad5d-516b5b48115f | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-051 | TRACE-77750cfc-8ad8-4f2e-b952-21d847d9ebdb | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-052 | TRACE-35b6465f-9a45-4b50-90f2-75b3ad61328b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-053 | TRACE-91a85328-8135-404f-9204-c21d45392635 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-054 | TRACE-49ec0e51-647d-4d1b-a027-046f405782d0 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-055 | TRACE-1194007c-dee1-4acd-b8b6-3f31ec5b00bf | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-056 | TRACE-046520e4-9c1e-4973-96a2-b02736192cf4 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-057 | TRACE-20c2dcab-6735-4427-8273-5d7f30674d86 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-058 | TRACE-891ead2e-3264-428e-a974-960cdfd7c650 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-059 | TRACE-8bf54b4e-d489-4a05-a977-595d15e76cfa | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-060 | TRACE-155f93ef-a3ed-4e66-8511-a600a2aacdec | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-061 | TRACE-4dd65579-9f53-41a5-8a79-1a1b7381897d | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-062 | TRACE-3f02552d-c546-42c1-8d90-540d11af2795 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-063 | TRACE-5cc11453-8c72-47b7-94e2-75798c46fea8 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-064 | TRACE-9e5dccc6-632a-4dd5-8ea2-600573bca3a9 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-065 | TRACE-b0d03609-d550-43d5-a486-ada78d76e44d | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-066 | TRACE-ac787191-e312-4289-8132-727ae794b24a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-067 | TRACE-a0879913-97ba-4852-b022-bc22e442b9e2 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-068 | TRACE-6285a89a-e7d8-4f70-86e9-40e12d3fe414 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-069 | TRACE-f3eab9f4-23e2-4c92-b0a2-ee7511255d37 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-070 | TRACE-06868b21-26b3-4577-9ae3-936eea56ae9c | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-071 | TRACE-7549e0d1-806a-4c6e-a5de-0e1ee203a264 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-072 | TRACE-df66a8b6-94dc-45f3-8023-75e01f59ce7c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-073 | TRACE-a4de2c2f-b620-4566-bad3-6c4b6036b95a | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-074 | TRACE-b7ae2479-278d-4cbf-84c9-0509d39e64f2 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-075 | TRACE-ee2c5e08-91ba-4940-92d6-017047dce16b | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-076 | TRACE-86b66a46-a1bd-418a-8dde-eba6af6e80d3 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-077 | TRACE-16f5d242-baa9-4d23-b6c2-10916c232b86 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-078 | TRACE-4c3b09c1-4772-4af9-8d0f-8d17d7ed84ef | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-079 | TRACE-1094f0c8-4ccd-4fd6-996b-fc53c6a6f6dd | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-080 | TRACE-ce41179b-6886-43eb-97d0-cfb87429300b | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-081 | TRACE-93eaef40-a9ae-45dd-b2fc-c9e3779e490c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-082 | TRACE-441bad96-fc18-42f0-b558-b179c0e87bd1 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-083 | TRACE-eae6b74f-3744-4083-9e12-90a932a27280 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-084 | TRACE-ac6586b1-ff6e-445f-b481-6a7de730a890 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-085 | TRACE-d73ff65b-9f64-40f4-88b9-1c3d8c4073d8 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-086 | TRACE-9e71d82f-3be0-4a57-9e12-75e883d2eddf | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-087 | TRACE-afe1f6e2-5fc5-40d0-851b-0461a770c1b1 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-088 | TRACE-474bec1e-87e3-4629-962e-b0e7ee70b41a | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-089 | TRACE-1028c8e2-77e4-416b-8e4b-34cc53119934 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-090 | TRACE-8092632c-a4ce-4bff-9aeb-96d244f69b94 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-091 | TRACE-2d14f48c-cdf4-4e19-87ef-baf73db91e98 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-092 | TRACE-94cb1610-d0cb-481b-b178-e3e304a1101a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-093 | TRACE-da0df10a-4cf8-4b90-913f-1856deae5b2c | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-094 | TRACE-84850a2e-21b6-4a12-be82-73fb35fab18c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-095 | TRACE-187036cd-1f01-4ada-9f87-2c8789b2cf91 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-096 | TRACE-ea2bded8-35e2-424a-993c-74d6a38c7442 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-097 | TRACE-83378e17-10d2-4ad3-b02b-5617742118b0 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-098 | TRACE-45124f37-a784-4ca7-9a07-2486061f8057 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-099 | TRACE-bc941b49-0d5f-4f76-8399-8c7554f9c7a4 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-100 | TRACE-5040344b-16b6-40b2-ada0-2de99d7f178a | blocked_checkpoint | not reached | 0 | 0/0 |

## Limits

- knowledge: see separate non-billable Knowledge diagnostic
- auditor_band_and_route: not_scored_by_triage_runtime
- troubleshooting: not_run
- documentation: not_run
- full_mao: not_run
- actual_model_cost: not_calculated

No raw case text, API key, model rationale, or unredacted prompt payload is stored in this report. Input and evidence are identified by hashes.
