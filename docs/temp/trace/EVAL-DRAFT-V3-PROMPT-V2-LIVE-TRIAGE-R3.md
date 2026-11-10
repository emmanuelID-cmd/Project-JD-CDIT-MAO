# Synthetic live Triage diagnostic

**Diagnostic only.** This report records real, billable Claude Sonnet 5.5 calls on synthetic cases. It does not approve draft labels or represent full MAO accuracy.

- Batch run: CDIT-LIVE-EVAL-2f2eb04f-36ee-4b89-b10b-ef687bd3586a
- Started/report time: 2026-11-10T15:06:17.506508+00:00
- Dataset: CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v3 (DRAFT_NOT_APPROVED)
- Dataset SHA-256: f3655b62a194ab5045b9f1ab0c79db046948fc02bb9bb9a8096340d00d481c6f
- Label approval flags: approved=False, scoring_authorized=False
- Cases/items selected: 100 / 105
- Validated model responses: 67
- SDK create invocations: 92 (method-invocation count, not provider billing confirmation).
- Safe failure-code counts: {'triage_provider_response_incomplete': 1, 'triage_provider_output_rejected': 24}
- Model / contract: claude-sonnet-5-5 / 0.1.0-proposed
- Input/output tokens: 127091 / 33292

## Observed Triage results

- Category proposals paired with an expected item: 61/63 matched (96.8%); 2 differed from the draft expectation.
- Abstentions with expected outputs: 4; unpaired extra model items: 0; expected items without a validated result: 38.
- Item spans: 97/97 observed spans matched (100.0%); 8/105 expected spans were unavailable (observed coverage 92.4%).

No urgency or destination accuracy is calculated: the A2 contract requires both to remain Unknown until human review. Auditor band/route decisions are also not scored by this run.

| Case | Trace ID | Intake | Triage | Calls | Category matches |
| :--- | :--- | :--- | :--- | ---: | :--- |
| SYN-EVAL-001 | TRACE-037a4555-3578-40d7-9ee7-c097f2f41c8a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-002 | TRACE-0e53bcfd-27fa-45ab-af46-d8be30faedae | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-003 | TRACE-baa6a5d2-77a3-4155-a7e7-09c0965c712f | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-004 | TRACE-2c83d4b4-cad2-48f7-87db-6bbc577b1cdc | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-005 | TRACE-65d84d5e-149c-4688-93eb-ac28b62464c0 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-006 | TRACE-367755bd-dfb1-49f2-b8e3-1d4c47bb3dcb | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-007 | TRACE-8a0feeb4-ed8f-431b-8b35-5412b592f11a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-008 | TRACE-a68d138f-ae91-43ad-89c9-dea9f617daf8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-009 | TRACE-172bea04-90a8-4f5a-af2c-d5a9779dbd6d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-010 | TRACE-a841b7d1-f80e-4808-8c02-88b53d1fbf7e | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-011 | TRACE-fa44d008-535d-4dc8-a9cb-c888bc7ae10e | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-012 | TRACE-965cdce2-7f38-412c-a7ab-b8bbdeb96ec2 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-013 | TRACE-41aa6194-733f-41bc-9fa5-ca285349d289 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-014 | TRACE-fd060c14-754d-420c-838e-1c4e1da70047 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-015 | TRACE-f034c577-d77b-466d-a6f7-9648bf0a3561 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-016 | TRACE-e34ee664-31cf-4030-bceb-6c8a9c9e5878 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-017 | TRACE-16280fab-b733-4604-8114-940859fae4e6 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-018 | TRACE-f5701b76-2b0c-40bb-a45f-aadbcba0b077 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-019 | TRACE-450c9e19-bfdf-40fc-a905-add0f41eaa57 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-020 | TRACE-d1b8bb96-9c07-4036-9afd-8a02788b0551 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-021 | TRACE-bef191e1-6eef-41b7-a87d-3212d937fd52 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-022 | TRACE-6f128a7c-59e2-485a-b197-827f77c2ff50 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-023 | TRACE-c820299b-1408-4fff-ad55-5dca08750b25 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-024 | TRACE-d7b2d4e9-1411-4375-a28b-96b538b02711 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-025 | TRACE-a56c452b-4062-4c4b-b1f7-df8e48ba30cb | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-026 | TRACE-0e51fc3d-5bc3-42de-a503-5ecfe2b716df | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-027 | TRACE-d10de88b-506b-4341-ac15-276dbbd8a3df | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-028 | TRACE-79728581-47ad-4713-87b8-d7c771796872 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-029 | TRACE-002d02ab-f9b5-4aa2-b304-010a4ee61250 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-030 | TRACE-b66b2b17-5849-48b4-8152-d721263de759 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-031 | TRACE-7b2b001a-cd12-42c3-b517-cdebbfe5589b | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-032 | TRACE-f02fc6ae-cc6c-437c-903a-3db3c974645f | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-033 | TRACE-c4e4aa37-f02a-4219-a88e-f0c29fd6e38f | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-034 | TRACE-caf35132-e02e-41a5-a42a-d6262ef6453d | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-035 | TRACE-05289aa8-3f4c-4e28-977d-78d47475e2db | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-036 | TRACE-17ae6c38-a707-4c6b-82b3-726a375e0df3 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-037 | TRACE-26e03857-a38d-48eb-8389-c2136cc8673f | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-038 | TRACE-2f76b24d-b011-43b3-9b8d-5b45f5149028 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-039 | TRACE-5c958c65-0086-4f18-8509-d7d670392d43 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-040 | TRACE-8909274a-7adc-4889-9fc0-cb4adeed5bbb | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-041 | TRACE-8699d5e5-a797-4bfe-9a68-848d002546e3 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-042 | TRACE-0f642d99-57be-46e0-b3d9-35283069c9d2 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-043 | TRACE-b95a1a74-41df-4be7-bb67-5bbd2ec473be | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-044 | TRACE-b49f5536-f528-4cb4-81b1-1432218a5b43 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-045 | TRACE-75041ae7-b6cf-4938-a049-ab378c99a325 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-046 | TRACE-943c5b7d-c4cd-4dce-a0c8-0a76b1ccc080 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-047 | TRACE-7866e431-b7b7-4e17-85f0-b483a05ee069 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-048 | TRACE-3e308760-4075-4aec-bb1d-9715a29b3f51 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-049 | TRACE-33b1201a-c49c-415d-af05-a12dc92d4627 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-050 | TRACE-805dbe09-9525-4c27-aaf3-448ad590bbc8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-051 | TRACE-5dcad053-2a7d-4907-802c-6961c75a0f3b | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-052 | TRACE-d50adc39-1011-4cab-886e-10d3a1f2c509 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-053 | TRACE-5be43e0f-794c-496a-96e8-8a6c07c2f280 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-054 | TRACE-1c12e8f2-f753-41d1-91d1-1792587e0e7c | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-055 | TRACE-667835b7-f831-4e10-826b-82d97ab29260 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-056 | TRACE-3d2c8661-e966-4b91-988c-c3856ca87c6d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-057 | TRACE-10ba2f18-2276-49e2-b0d0-0c7191ccd3ab | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-058 | TRACE-a6e47ca2-eda2-456c-88b5-f275da47e7c8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-059 | TRACE-9fecd97d-096c-4c74-b02f-613116f46711 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-060 | TRACE-a703fd88-ec9a-4e3c-8cbf-f392c8c68225 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-061 | TRACE-71df9e26-833f-4d32-909e-737696ae6fc2 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-062 | TRACE-af8b1233-a9ee-4ee2-95bb-0aed53e86179 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-063 | TRACE-0de10469-759b-4c54-bb11-22eae9c2d353 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-064 | TRACE-0c5e1718-19b5-40c3-8c9c-3d6238c04dc9 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-065 | TRACE-04f3d1d5-2488-4ee8-acfd-f6176c4767d8 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-066 | TRACE-afc3f06d-fb69-4c90-8e57-acb56042fd6b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-067 | TRACE-5ce96c0d-6ff7-4db1-a27c-6715df4bc8dc | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-068 | TRACE-6448ba04-8da9-419f-9a05-24bc6cb440a7 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-069 | TRACE-ed5a8ca8-e29b-4a7a-8115-17252173a2a1 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-070 | TRACE-3ba45599-b94c-4e59-8a37-2b0039283f77 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-071 | TRACE-962a83dd-2b65-460f-a429-c770da685006 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-072 | TRACE-22113175-2a0a-4f77-8ceb-87eb189702b9 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-073 | TRACE-46a2caa5-082b-4f03-ac61-dd84d3123010 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-074 | TRACE-599d45aa-05dd-47d6-8f44-50f356357a9d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-075 | TRACE-90249654-2b25-4a37-a596-16df0c086f5a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-076 | TRACE-e28bd6cd-c40f-4168-aa28-7dd205347f7c | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-077 | TRACE-d4451d24-05b2-4555-9df9-a9fd184993ef | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-078 | TRACE-d8d609f2-24b9-4738-b0c9-826773e46945 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-079 | TRACE-e4a402a9-49d4-47a6-82bf-274279ec05f7 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-080 | TRACE-765a4311-2210-4411-87ea-59d71fc422c5 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-081 | TRACE-426ff42b-827d-40e0-a995-1e272a334472 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-082 | TRACE-0350ead6-81a7-4ba0-8e63-ca04b08f29ca | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-083 | TRACE-be4d4661-6e03-475f-9c28-479e24f202e7 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-084 | TRACE-c04769be-d0d4-4773-8e64-5a80a4795568 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-085 | TRACE-6a8d8bf6-f18e-4fb9-bf1d-5c750d54a0ad | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-086 | TRACE-48374b06-689f-4666-be97-f137f524b497 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-087 | TRACE-065ff891-9015-4563-94d8-fd9aa13edc0a | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-088 | TRACE-b8d0fd2d-7779-4a49-bb62-473561ab4a4f | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-089 | TRACE-ee4554b1-55ee-450c-8927-1c55795951c4 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-090 | TRACE-6405e892-a798-4692-909c-dc9da08e523c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-091 | TRACE-68748de6-91c0-412d-9a89-d3644131a6a3 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-092 | TRACE-b4db3d90-eb07-4f2c-93c4-b9eea734380a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-093 | TRACE-dfe3e35f-a9d9-438b-b60b-03616e74fced | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-094 | TRACE-52304b46-5b02-4b5e-b621-2fe0d156838e | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-095 | TRACE-15db3f6b-e1c1-48dc-a070-05b255fb1944 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-096 | TRACE-07b0d6c0-beec-4ba9-9c65-95a5ba40a60d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-097 | TRACE-fd3948ea-7dce-4e9e-876d-205628792819 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-098 | TRACE-3fa74160-497f-41ad-8c99-152f5f2421c5 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-099 | TRACE-cf97473c-ae39-4c62-8f27-18d8aa53ec10 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-100 | TRACE-41c9f19f-5bd8-460a-ab25-67e99e11e6e0 | blocked_checkpoint | not reached | 0 | 0/0 |

## Limits

- knowledge: see separate non-billable Knowledge diagnostic
- auditor_band_and_route: not_scored_by_triage_runtime
- troubleshooting: not_run
- documentation: not_run
- full_mao: not_run
- actual_model_cost: not_calculated

No raw case text, API key, model rationale, or unredacted prompt payload is stored in this report. Input and evidence are identified by hashes.
