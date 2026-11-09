> **Superseded summary:** The original denominator counted unpaired rows. Use `EVAL-DRAFT-V1-LIVE-TRIAGE.corrected.results.json` and the `Trace ... Manny-Triage Live100-001 coordinator.md` report for reconciled metrics and Manny’s case-level adjudications.

# Synthetic live Triage diagnostic

**Diagnostic only.** This report records real, billable Claude Sonnet 5.5 calls on synthetic cases. It does not approve draft labels or represent full MAO accuracy.

- Batch run: CDIT-LIVE-EVAL-4b7dfc48-532a-4c9a-b92d-63cdd590ba37
- Started/report time: 2026-11-09T19:34:02.111323+00:00
- Dataset: CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v1 (DRAFT_NOT_APPROVED)
- Dataset SHA-256: a4d6d2b6e6bbb21584ae2a9b86da13c32b62e30c3a047a1bc4c53f08f72d7c82
- Label approval flags: approved=False, scoring_authorized=False
- Cases/items selected: 100 / 114
- Calls: 45 (authorized=True, sequential=True, retries=0)
- Model / contract: claude-sonnet-5-5 / 0.1.0-proposed
- Input/output tokens: 58906 / 25579

## Observed Triage results

- Category proposals: 30/54 matched (55.6%); 60 items did not return a validated model proposal.
- Item spans: 36/45 matched (80.0%).

No urgency or destination accuracy is calculated: the A2 contract requires both to remain Unknown until human review. Auditor band/route decisions are also not scored by this run.

| Case | Trace ID | Intake | Triage | Calls | Category matches |
| :--- | :--- | :--- | :--- | ---: | :--- |
| SYN-EVAL-001 | TRACE-e1225c33-3ec8-40d7-8fb2-f60b5a97a9e9 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-002 | TRACE-7dc75998-fd36-49f0-8449-5bb77dc83b1f | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-003 | TRACE-66642b28-2871-44f7-ba6a-54e4b01c5b55 | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-004 | TRACE-629ed468-3a1a-4975-9472-e4393806ae68 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-005 | TRACE-266bbd03-9762-4012-bf72-c11fd9373a60 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-006 | TRACE-6019ab43-721d-4b6f-a421-15bbed09136b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-007 | TRACE-4eae6b13-016f-485f-99f8-96e110222892 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-008 | TRACE-4ad2b900-1d4c-4b0a-996c-2c70d09d07f2 | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-009 | TRACE-1f2f3db4-8e53-40bc-840a-5d84008badae | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-010 | TRACE-a094b2f7-6c75-4198-9d4e-83b5fc5e63bf | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-011 | TRACE-d3e1fda3-14f2-4390-b9da-309246420a1d | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-012 | TRACE-e71c9eb4-91a0-4a51-bc0d-2ba38e0e3d26 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-013 | TRACE-c360180f-04a4-414a-a33a-9e0557dfb57e | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-014 | TRACE-70e10f4c-a6fa-4719-938c-96481c94040d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-015 | TRACE-ed0a6407-c2a4-494b-ae5f-d10acc4b2ad2 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-016 | TRACE-75cf39ed-e586-4c02-b224-f6b1c9a2cf2c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-017 | TRACE-04be5e6f-19b1-4645-915a-f60091c7bd66 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-018 | TRACE-99365fd0-80f2-456c-990e-a3cbbc8703a1 | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-019 | TRACE-c7e811f0-ae49-464d-bf95-fe0d9ca3102a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-020 | TRACE-3752a212-39d9-4bed-89c0-a7ea78fa701c | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-021 | TRACE-b9abba95-5f4f-4faf-94ce-11b942ab2f13 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-022 | TRACE-cd7b0684-9f31-4f16-bec8-a8ab37330eb6 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-023 | TRACE-be113a2c-5b2c-43d0-89a5-b65afcffea74 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-024 | TRACE-4f0b6b22-0f42-4545-ae4a-fb1a4d21bb00 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-025 | TRACE-c953c6c2-b76b-47ef-a51f-2b8d0ba8fe38 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-026 | TRACE-559484f1-851a-4d8f-82fa-6271307d13ee | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-027 | TRACE-feac2e8e-d05a-4458-be1b-d16700c6c348 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-028 | TRACE-9b8efbc6-65fc-44e3-a7c1-9725d831f921 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-029 | TRACE-9ce84ced-f32e-446a-a87b-c4df0e80d0e4 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-030 | TRACE-21c9e884-8287-4850-857d-24c20fb9fbbe | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-031 | TRACE-fb58e1d5-fd02-464b-8c4e-603d4c313438 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-032 | TRACE-69cd077e-26c8-4373-a8f6-be77cdeccb1a | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-033 | TRACE-03ac8619-1d43-409f-95cc-c2e7592a23d8 | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-034 | TRACE-e596187a-c811-40fd-bfc4-fffd63803353 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-035 | TRACE-bfeeb363-2df7-4952-a696-dc7045cf4e3e | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-036 | TRACE-cd4da482-8e9a-46d8-9a99-026b9956861b | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-037 | TRACE-e82310ae-c3c3-4d7b-9a92-efa9dde6c0d5 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-038 | TRACE-628faadc-ae1e-498c-9428-9d4862a1e2f0 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-039 | TRACE-6e712446-6f4d-4022-b9b1-4d5fad1f94a7 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-040 | TRACE-9001b63e-89bf-4ddd-b79a-1dc3df3fe71a | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-041 | TRACE-2410c92a-58f9-4c1d-aece-8b98141a6270 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-042 | TRACE-ec9f75ad-b668-4d52-8009-6aa97fcb4e4c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-043 | TRACE-733ff504-dd40-4412-8423-a70df0ec4ed2 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-044 | TRACE-a4b92b07-9ae3-4142-91a7-0bb80b5bd385 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-045 | TRACE-8afe9268-a65d-4577-9900-6e98c0e05ba9 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-046 | TRACE-b0cd4c5c-6161-4b38-b6ac-3180e7454deb | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-047 | TRACE-8f2676b8-ee81-4353-af7a-a4611dba3059 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-048 | TRACE-09cf3b61-5129-4438-9a5d-d3f85f701184 | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-049 | TRACE-acf90213-aa0e-49e5-b96d-09b3c70a7851 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-050 | TRACE-02945c47-6cd7-436e-9060-ccaf39c5e91b | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-051 | TRACE-828d917f-8ddb-4f75-ab2d-9c23460ea37e | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-052 | TRACE-9245bdbf-7a39-46c4-8f5c-6b5dcb0397fa | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-053 | TRACE-51cd740d-a03f-463f-b878-622ae1ca52ba | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-054 | TRACE-97643e92-0d83-4696-97b8-a817ff92f4ca | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-055 | TRACE-17150a2b-74b0-4412-88a4-7a6a953942d5 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-056 | TRACE-7060f338-7226-4a16-b1db-98a561cce875 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-057 | TRACE-766197f4-be0c-45b6-930b-c8ca5934a760 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-058 | TRACE-9b13bc14-2da0-45b4-8deb-31669eb90e67 | ready_for_triage | proposal_for_human_review | 1 | 1/2 |
| SYN-EVAL-059 | TRACE-bc673039-1a4f-4b56-8269-e6c26bb79733 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-060 | TRACE-1a27ece6-100e-46df-b789-1c394236ef4b | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-061 | TRACE-8e66203c-da20-4c11-9639-2db06bc663d0 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-062 | TRACE-734d0565-e3c3-4d9c-a225-f19bb9c77c20 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-063 | TRACE-93e65c56-4e98-4a2b-848e-cfd7ce8caa97 | ready_for_triage | proposal_for_human_review | 1 | 0/2 |
| SYN-EVAL-064 | TRACE-3b89ec4e-5be5-4d65-8775-dd5bb9421953 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-065 | TRACE-233c8958-9020-47df-b30e-233abb978608 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-066 | TRACE-60502d4d-5e94-48c2-8772-7815c1f02fe0 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-067 | TRACE-c7662f24-e9f8-4681-bfc8-ca2ec1f1085f | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-068 | TRACE-9aa5dff2-24da-4755-a9a4-2db7f0be5eb4 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-069 | TRACE-2ed72e34-35de-422c-9f50-3fd065ec62d4 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-070 | TRACE-dae5c9c7-7603-42b3-a9fe-67e3c65c25c0 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-071 | TRACE-628775e1-d9d1-4a32-aa49-92e548bf3c2d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-072 | TRACE-5fbfb98c-a87f-47f1-a62f-e5d3409548e9 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-073 | TRACE-e93876e2-29fa-4b93-bfef-c52d8162aeb8 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-074 | TRACE-d88b9ca5-8e6f-4cef-83d1-ac6dc090522d | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-075 | TRACE-70c67418-11d3-4574-aa60-dd5c84c29796 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-076 | TRACE-e01e945f-43c1-414a-beb7-e861b60e0c9d | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-077 | TRACE-25f678a7-75fa-4be1-a391-4a72ca74346c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-078 | TRACE-6b08037a-b302-4e8c-8c44-84c7953d5c6b | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-079 | TRACE-39d15ade-e13a-4eb6-a27d-7e810796c84c | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-080 | TRACE-86c448cc-6e96-4844-b83e-0ce74ca37951 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-081 | TRACE-167e53d0-b449-497b-a278-d0ffbacffed6 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-082 | TRACE-7d1a890c-751a-48b0-90c4-8b56b1b9068e | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-083 | TRACE-8c05f3af-f80b-4402-b3a6-fe32c2351ea9 | ready_for_triage | proposal_for_human_review | 1 | 0/2 |
| SYN-EVAL-084 | TRACE-13b62c78-6de0-404b-b8d9-7049b31d6c25 | ready_for_triage | proposal_for_human_review | 1 | 0/1 |
| SYN-EVAL-085 | TRACE-058988ea-c00e-4aed-82f5-9b3486fde319 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-086 | TRACE-3e273225-e051-42c5-922d-4a0077e2ad71 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-087 | TRACE-70e99ac8-a053-431a-9c02-39b10c5c2ead | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-088 | TRACE-10b2e67b-2718-44fe-82bb-30fa60c412e9 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-089 | TRACE-1acec28b-4034-4e64-bc79-23e3145f5175 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-090 | TRACE-0a55d24c-cc0c-4769-9d80-eb424423d0a3 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-091 | TRACE-56d6d481-239c-42b2-b149-b29cd8701b64 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-092 | TRACE-11bf41bd-9ec7-4db6-ac22-9c331de8c089 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-093 | TRACE-db86ffdc-7c17-4565-b552-f9885837955a | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-094 | TRACE-c829a401-0fb3-478e-806a-55a20477aefe | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-095 | TRACE-8fae191e-42c9-4362-b874-5cb2e8161065 | ready_for_triage | needs_human_review | 0 | 0/0 |
| SYN-EVAL-096 | TRACE-19fa03d7-d93f-4ad1-b4a1-7cf7a0dd1361 | ready_for_triage | proposal_for_human_review | 1 | 1/1 |
| SYN-EVAL-097 | TRACE-9fb08cb2-3289-470e-bc66-35f6942876b7 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-098 | TRACE-c68e7e0e-8940-404e-9fcb-b6aea880f44a | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-099 | TRACE-1ad8e814-a190-4831-bdfb-cabdb0b5aed8 | blocked_checkpoint | not reached | 0 | 0/0 |
| SYN-EVAL-100 | TRACE-c92e4be9-333a-4498-82b8-5d73a7a1d4de | blocked_checkpoint | not reached | 0 | 0/0 |

## Limits

- knowledge: see separate non-billable Knowledge diagnostic
- auditor_band_and_route: not_scored_by_triage_runtime
- troubleshooting: not_run
- documentation: not_run
- full_mao: not_run
- actual_model_cost: not_calculated

No raw case text, API key, model rationale, or unredacted prompt payload is stored in this report. Input and evidence are identified by hashes.
