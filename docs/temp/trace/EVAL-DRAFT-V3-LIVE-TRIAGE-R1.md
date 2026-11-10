# Synthetic live Triage diagnostic

**Diagnostic only.** This report records real, billable Claude Sonnet 5.5 calls on synthetic cases. It does not approve draft labels or represent full MAO accuracy.

- Batch run: CDIT-LIVE-EVAL-7faa54e3-663d-43f9-bdf1-1c20a94cf9da
- Started/report time: 2026-11-09T22:15:43.964430+00:00
- Dataset: CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v3 (DRAFT_NOT_APPROVED)
- Dataset SHA-256: f3655b62a194ab5045b9f1ab0c79db046948fc02bb9bb9a8096340d00d481c6f
- Label approval flags: approved=False, scoring_authorized=False
- Cases/items selected: 100 / 105
- Validated model responses: 89
- SDK create invocations: 92 (method-invocation count, not provider billing confirmation).
- Safe failure-code counts: {'triage_provider_output_rejected': 3}
- Model / contract: claude-sonnet-5-5 / 0.1.0-proposed
- Input/output tokens: 116675 / 51309

## Observed Triage results

- Category proposals paired with an expected item: 51/68 matched (75.0%); 17 differed from the draft expectation.
- Abstentions with expected outputs: 26; unpaired extra model items: 0; expected items without a validated result: 11.
- Item spans: 94/94 matched (100.0%).

No urgency or destination accuracy is calculated: the A2 contract requires both to remain Unknown until human review. Auditor band/route decisions are also not scored by this run.

| Case | Trace ID | Intake | Triage | Calls | Category matches |
| :--- | :--- | :--- | :--- | ---: | :--- |
| SYN-EVAL-001 | TRACE-c539bc00-feef-4679-9c15-669afb854269 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-002 | TRACE-592ca56e-cf9f-4191-99e5-5503970bb7b4 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-003 | TRACE-1f263b36-4dc4-4265-803e-754c87b741b7 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-004 | TRACE-4b2bbd13-a7e0-4d16-a605-fd76d6fd7f5e | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-005 | TRACE-0faa137e-05f2-4ff6-b877-ff5be12aec21 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-006 | TRACE-d3fc5d3a-a4d2-4f4f-9858-c06c03d69837 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-007 | TRACE-cb6429b1-261e-4d74-affc-3312f26d4095 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-008 | TRACE-db277771-8d88-48de-b538-72dfd61b3fc6 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-009 | TRACE-f4804cf6-9632-48c4-941b-f0291e18a409 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-010 | TRACE-b5286f5e-af2e-48a4-b5a1-1baa50858267 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-011 | TRACE-485bf727-616e-4260-b14c-03387927d623 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-012 | TRACE-11009bfe-e9e6-4763-9a91-b1f50094adbd | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-013 | TRACE-a05b3fdb-1fe1-45d1-88bc-8cadea203ff9 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-014 | TRACE-87db70b8-ff7b-4d09-9751-5810c657a20d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-015 | TRACE-a020cc89-5637-4a2c-8430-4246997cc3df | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-016 | TRACE-ebe8ea01-82d2-4c62-b6e1-6fa63cbc98d7 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-017 | TRACE-c1390859-82fa-4fd4-8082-08f4e932c589 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-018 | TRACE-0ec52d02-19a4-47db-9bc5-458656f34c3f | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-019 | TRACE-d276a094-d0f0-4912-a3be-a0c7b7ac72c2 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-020 | TRACE-8d1665d0-3ccc-46de-82c8-74171857a743 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-021 | TRACE-afad74eb-5e8d-4cd5-a6dc-cd476193a555 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-022 | TRACE-af6ac686-3bd0-4cd5-a6df-a5e67f4caa45 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-023 | TRACE-05897ca3-5834-45a5-93f2-7911eb2daeb6 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-024 | TRACE-d3653323-a6fa-4e36-9402-d0ff2973eaa3 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-025 | TRACE-aa9f2999-5cb1-46f4-bfac-f3b3e56b7f31 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-026 | TRACE-298cfb08-6dbc-4f2f-811d-0bf2dc18a3c9 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-027 | TRACE-85401873-bbae-40e2-a441-bdefc610963d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-028 | TRACE-74d05edd-5fef-4f76-84c2-6cdb52ba6d80 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-029 | TRACE-1d542e10-6095-419c-ae6b-7570239d8eac | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-030 | TRACE-d10c4b03-99f4-43b1-97e8-5d406e670674 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-031 | TRACE-5130ea93-5b5d-418b-b195-45a5fa832113 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-032 | TRACE-f3721bbc-15a8-447c-98ac-40512a721ee8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-033 | TRACE-0dc56eb8-1755-4f40-b025-42ad11ca2ae4 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-034 | TRACE-e4c4c145-7862-43bb-9003-ddc229b49814 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-035 | TRACE-24f7b9e3-fd0f-4a0c-957e-5fbbea260b3d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-036 | TRACE-2b26c8f2-21e8-409c-98b1-b149cdae2a43 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-037 | TRACE-1a4b2f8b-59f8-4506-b7f3-acf621a73696 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-038 | TRACE-8a885aec-65f8-4ceb-a439-9afcc9a3890f | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-039 | TRACE-987f4343-ab33-4c30-9628-7603a01632d7 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-040 | TRACE-a9f33ad0-bc41-4b00-94bf-1e10218e1bf5 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-041 | TRACE-3ba68974-3cb8-419e-a30c-74680937e3c8 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-042 | TRACE-d5414534-6dc2-46d2-a7d2-a71dcb57c8b0 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-043 | TRACE-7864fa49-b01f-42b8-b956-6944af04bc30 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-044 | TRACE-6ae02914-6f55-427b-a80d-5158e50be354 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-045 | TRACE-0eba345d-781e-436c-9bef-c77c8e57c49c | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-046 | TRACE-1072a14e-8017-409f-b3df-456d700aaf50 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-047 | TRACE-d462a654-0ede-45c8-a28e-a1b46fcce787 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-048 | TRACE-3dee17d6-1918-4fa2-be9c-64efede919df | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-049 | TRACE-2e487160-b9ff-4c91-8cd5-eb9d7bbeb3f1 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-050 | TRACE-291a1ce6-f18c-4335-9476-c707c03cf265 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-051 | TRACE-ef94e7c8-b295-4703-b79d-8a0cedcb432f | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-052 | TRACE-c835020c-96c2-45ed-a096-bc8c6b3481b8 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-053 | TRACE-06f7dbce-0b17-45cd-b609-ed8a65f173e1 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-054 | TRACE-4bb48839-7531-42ee-a9e6-313ac6140bfd | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-055 | TRACE-01b8cedb-2502-4cc4-a2a2-5a1b1eb1a05a | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-056 | TRACE-3f68f95a-06e9-4555-b724-9bd80b8c2a54 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-057 | TRACE-9fd0b760-c3c6-4bf5-91d7-459af51e180c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-058 | TRACE-a194d1e9-e4a7-4258-9497-8a7d1ea8f49c | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-059 | TRACE-cd4a9d17-87ca-4bb2-89d4-c54a84dc9bfd | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-060 | TRACE-0e5330c4-3fe0-4917-9edc-e771f2a930e8 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-061 | TRACE-556a9075-bd2e-4b21-96c8-f70d7a3152c6 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-062 | TRACE-20167091-ec6d-423d-ad90-4dd7e38ab0b7 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-063 | TRACE-24c2b7e1-da32-4d15-b0c3-5d988c4f1868 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-064 | TRACE-f517f792-2771-486d-87c8-d8cf5a9811b3 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-065 | TRACE-ae1cc44b-0e01-4f3c-919e-d324f63bc8f1 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-066 | TRACE-2069f0bd-d69e-4d44-91ca-0b92b7991b4e | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-067 | TRACE-c8120e53-0a08-4ac5-8f0f-23f8f011123f | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-068 | TRACE-5e37b763-2798-4d66-a371-319e3417382f | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-069 | TRACE-ad5359ff-92d7-4685-bb7f-44955267e7f7 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-070 | TRACE-0c5ed001-4ae1-47bb-898a-91e67b08c950 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-071 | TRACE-5196be5a-09fe-41c6-8678-a9cb4260cb02 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-072 | TRACE-3075f024-e460-4db4-9378-a954af7605ec | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-073 | TRACE-8c5a767b-7f26-47e1-a2a2-46635138cf17 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-074 | TRACE-295e14ec-019d-4600-bee8-dea9af616141 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-075 | TRACE-1b683da6-dc5c-44ec-8786-4a927a1363aa | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-076 | TRACE-7fd35d5b-f1d5-459d-8bea-6fc540a87d2c | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-077 | TRACE-58980e77-4ee2-4d0c-b4e4-1a29b22fe517 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-078 | TRACE-08887c0c-aeeb-49df-9c06-73974f25e82a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-079 | TRACE-146618e0-788b-4b5a-b4c3-2da283a2d3f4 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-080 | TRACE-0c133340-4831-46a8-a0fd-e27706e3045a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-081 | TRACE-7ff505a2-8532-4ddf-8411-7f8d57f60707 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-082 | TRACE-e92b3acc-52d5-427d-bc01-74d07802e0bb | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-083 | TRACE-175abd5f-ff0b-41cc-af0a-e854eadf4105 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-084 | TRACE-4b8e67e8-712f-449d-9e79-1f8d46d4047e | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-085 | TRACE-28d3b08e-bf6b-4af8-86ea-6a2a84a8dfcc | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-086 | TRACE-718b8e57-bf41-455a-9b7a-8d4554ba8571 | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-087 | TRACE-c2261ec7-6515-4c49-b174-99e44b306427 | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-088 | TRACE-add9a716-ea05-49db-94a6-b96a9951631a | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-089 | TRACE-24e6cc70-98c3-4657-a5d2-2ece90f4ce68 | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-090 | TRACE-1b581476-1828-4087-a91b-10df0919acfd | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-091 | TRACE-322cfe82-9f84-4ca3-ad8f-19e5d6fec676 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-092 | TRACE-702bf9b5-5620-4e32-8a23-4f2afa3c9eec | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-093 | TRACE-7db2c0d1-6a43-4d41-8c32-502d630fef9a | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-094 | TRACE-ace77a5a-9f34-481d-9f37-b4195a1925d0 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-095 | TRACE-bff3bb27-98cf-49b3-8df1-853c0b1d2901 | ready_for_triage | proposal_for_human_review | 1 | 0/0 |
| SYN-EVAL-096 | TRACE-e7bc37fe-722d-4033-a49e-ea2b6c820e1a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-097 | TRACE-de1492c4-a040-4bfa-8ecf-2d9f4701e0bb | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-098 | TRACE-24dae817-45d6-49a2-990e-ca7d70fdbcba | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-099 | TRACE-c0937044-7040-4e44-a36d-891953ab49ab | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-100 | TRACE-a1fa8cd6-ae2c-498c-92c3-fc26a6ebc575 | blocked_checkpoint | not reached | 0 | 0/0 |

## Limits

- knowledge: see separate non-billable Knowledge diagnostic
- auditor_band_and_route: not_scored_by_triage_runtime
- troubleshooting: not_run
- documentation: not_run
- full_mao: not_run
- actual_model_cost: not_calculated

No raw case text, API key, model rationale, or unredacted prompt payload is stored in this report. Input and evidence are identified by hashes.
