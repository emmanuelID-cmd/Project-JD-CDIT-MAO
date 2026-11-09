# Evaluation draft v1: Knowledge diagnostic

**Diagnostic only.** This runs the Knowledge agent against every routable item in the synthetic draft. It does not call a model provider, approve labels, or measure full MAO accuracy.

- Dataset: CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v1
- Dataset status: DRAFT_NOT_APPROVED
- Label approval: False
- Scoring authorization: False
- Cases/items inspected: 100 / 105
- As-of date: 2026-11-10
- Knowledge source set: SRC-16191440094D
- Knowledge agent version: 0.2.0

## Knowledge diagnostic results

- Expected-source citation rate: 14/65 (21.5%); this is an observed diagnostic rate, not a PRD acceptance score.
- Expected-source citation misses: 51
- Expected-reason abstentions: 8/11
- Stale-source cases without an answer: 4/5
- Wrong-source/missed-abstention items: 1
- Items held for Auditor: 11
- Items with no expected Knowledge source that abstained: 18
- Source-map validation problems: 0

## Verdict counts

| Verdict | Items |
| :--- | ---: |
| abstained_as_expected | 8 |
| abstained_other_reason | 2 |
| cited_expected | 14 |
| cited_other_source | 1 |
| held_for_auditor | 11 |
| missed_abstained | 51 |
| no_source_expected_abstained | 18 |

## Not scored by this run

- semantic triage category accuracy
- Auditor band and route accuracy
- Coordinator-to-Triage live handoff behavior
- Troubleshooting and Documentation accuracy over these 100 cases
- end-to-end injection, privacy, and authorization behavior
- fallback behavior outside the Knowledge source check
- latency, model cost, confidence calibration, and reviewer seeded-error rate

## Case and item outcomes

| Case | Item | Scenario | Route | Verdict | Observed source(s) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SYN-EVAL-001 | SYN-EVAL-001-I1 | routine-pay-statement | knowledge | cited_expected | KB-PAY-400#s1 v1.0 |
| SYN-EVAL-002 | SYN-EVAL-002-I1 | routine-pay-statement | knowledge | cited_expected | KB-PAY-400#s1 v1.0 |
| SYN-EVAL-003 | SYN-EVAL-003-I1 | routine-pay-statement | knowledge | cited_expected | KB-PAY-400#s1 v1.0 |
| SYN-EVAL-004 | SYN-EVAL-004-I1 | routine-pay-statement | knowledge | cited_expected | KB-PAY-400#s1 v1.0 |
| SYN-EVAL-005 | SYN-EVAL-005-I1 | routine-pay-statement | knowledge | missed_abstained | — |
| SYN-EVAL-006 | SYN-EVAL-006-I1 | routine-form-copy | knowledge | cited_expected | KB-FRM-420#s1 v1.0 |
| SYN-EVAL-007 | SYN-EVAL-007-I1 | routine-form-copy | knowledge | missed_abstained | — |
| SYN-EVAL-008 | SYN-EVAL-008-I1 | routine-form-copy | knowledge | missed_abstained | — |
| SYN-EVAL-009 | SYN-EVAL-009-I1 | routine-form-copy | knowledge | missed_abstained | — |
| SYN-EVAL-010 | SYN-EVAL-010-I1 | routine-form-copy | knowledge | missed_abstained | — |
| SYN-EVAL-011 | SYN-EVAL-011-I1 | pay-discrepancy | knowledge | missed_abstained | — |
| SYN-EVAL-012 | SYN-EVAL-012-I1 | pay-discrepancy | knowledge | missed_abstained | — |
| SYN-EVAL-013 | SYN-EVAL-013-I1 | pay-discrepancy | knowledge | missed_abstained | — |
| SYN-EVAL-014 | SYN-EVAL-014-I1 | pay-discrepancy | knowledge | missed_abstained | — |
| SYN-EVAL-015 | SYN-EVAL-015-I1 | pay-discrepancy | knowledge | missed_abstained | — |
| SYN-EVAL-016 | SYN-EVAL-016-I1 | shift-conflict | knowledge | missed_abstained | — |
| SYN-EVAL-017 | SYN-EVAL-017-I1 | shift-conflict | knowledge | missed_abstained | — |
| SYN-EVAL-018 | SYN-EVAL-018-I1 | shift-conflict | knowledge | missed_abstained | — |
| SYN-EVAL-019 | SYN-EVAL-019-I1 | shift-conflict | knowledge | missed_abstained | — |
| SYN-EVAL-020 | SYN-EVAL-020-I1 | shift-conflict | knowledge | missed_abstained | — |
| SYN-EVAL-021 | SYN-EVAL-021-I1 | severity-1-major-outage | knowledge | missed_abstained | — |
| SYN-EVAL-022 | SYN-EVAL-022-I1 | severity-1-major-outage | knowledge | missed_abstained | — |
| SYN-EVAL-023 | SYN-EVAL-023-I1 | severity-1-major-outage | knowledge | missed_abstained | — |
| SYN-EVAL-024 | SYN-EVAL-024-I1 | severity-1-major-outage | knowledge | missed_abstained | — |
| SYN-EVAL-025 | SYN-EVAL-025-I1 | severity-1-major-outage | knowledge | missed_abstained | — |
| SYN-EVAL-026 | SYN-EVAL-026-I1 | safety-injury | knowledge | cited_expected | KB-SAF-460#s1 v1.0 |
| SYN-EVAL-027 | SYN-EVAL-027-I1 | safety-injury | knowledge | cited_expected | KB-SAF-460#s1 v1.0 |
| SYN-EVAL-028 | SYN-EVAL-028-I1 | safety-injury | knowledge | cited_expected | KB-SAF-460#s1 v1.0 |
| SYN-EVAL-029 | SYN-EVAL-029-I1 | safety-injury | knowledge | missed_abstained | — |
| SYN-EVAL-030 | SYN-EVAL-030-I1 | safety-injury | knowledge | cited_expected | KB-SAF-460#s1 v1.0 |
| SYN-EVAL-031 | SYN-EVAL-031-I1 | privilege-request | knowledge | missed_abstained | — |
| SYN-EVAL-032 | SYN-EVAL-032-I1 | privilege-request | knowledge | missed_abstained | — |
| SYN-EVAL-033 | SYN-EVAL-033-I1 | privilege-request | knowledge | missed_abstained | — |
| SYN-EVAL-034 | SYN-EVAL-034-I1 | privilege-request | knowledge | missed_abstained | — |
| SYN-EVAL-035 | SYN-EVAL-035-I1 | privilege-request | knowledge | missed_abstained | — |
| SYN-EVAL-036 | SYN-EVAL-036-I1 | benign-quoted-instructions | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-037 | SYN-EVAL-037-I1 | quoted-injection | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-038 | SYN-EVAL-038-I1 | quoted-injection | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-039 | SYN-EVAL-039-I1 | quoted-injection | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-040 | SYN-EVAL-040-I1 | quoted-injection | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-041 | SYN-EVAL-041-I1 | privacy-marker | knowledge | missed_abstained | — |
| SYN-EVAL-042 | SYN-EVAL-042-I1 | privacy-marker | knowledge | missed_abstained | — |
| SYN-EVAL-043 | SYN-EVAL-043-I1 | privacy-marker | knowledge | missed_abstained | — |
| SYN-EVAL-044 | SYN-EVAL-044-I1 | privacy-marker | knowledge | missed_abstained | — |
| SYN-EVAL-045 | SYN-EVAL-045-I1 | privacy-marker | knowledge | missed_abstained | — |
| SYN-EVAL-046 | SYN-EVAL-046-I1 | compliance-evidence | knowledge | missed_abstained | — |
| SYN-EVAL-047 | SYN-EVAL-047-I1 | compliance-evidence | knowledge | missed_abstained | — |
| SYN-EVAL-048 | SYN-EVAL-048-I1 | compliance-evidence | knowledge | missed_abstained | — |
| SYN-EVAL-049 | SYN-EVAL-049-I1 | compliance-evidence | knowledge | missed_abstained | — |
| SYN-EVAL-050 | SYN-EVAL-050-I1 | compliance-evidence | knowledge | missed_abstained | — |
| SYN-EVAL-051 | SYN-EVAL-051-I1 | ambiguous-severity | auditor | held_for_auditor | — |
| SYN-EVAL-052 | SYN-EVAL-052-I1 | ambiguous-severity | auditor | held_for_auditor | — |
| SYN-EVAL-053 | SYN-EVAL-053-I1 | ambiguous-severity | auditor | held_for_auditor | — |
| SYN-EVAL-054 | SYN-EVAL-054-I1 | ambiguous-severity | auditor | held_for_auditor | — |
| SYN-EVAL-055 | SYN-EVAL-055-I1 | ambiguous-severity | auditor | held_for_auditor | — |
| SYN-EVAL-056 | SYN-EVAL-056-I1 | clinical-advice | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-057 | SYN-EVAL-057-I1 | clinical-advice | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-058 | SYN-EVAL-058-I1 | clinical-advice | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-059 | SYN-EVAL-059-I1 | clinical-advice | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-060 | SYN-EVAL-060-I1 | clinical-advice | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-061 | SYN-EVAL-061-I1 | tool-outage | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-062 | SYN-EVAL-062-I1 | model-outage | auditor | held_for_auditor | — |
| SYN-EVAL-063 | SYN-EVAL-063-I1 | tool-outage | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-064 | SYN-EVAL-064-I1 | tool-outage | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-065 | SYN-EVAL-065-I1 | tool-outage | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-066 | SYN-EVAL-066-I1 | stale-source | knowledge | abstained_as_expected | — |
| SYN-EVAL-067 | SYN-EVAL-067-I1 | stale-source | knowledge | cited_other_source | KB-TRN-250#s1 v1.0 |
| SYN-EVAL-068 | SYN-EVAL-068-I1 | stale-source | knowledge | abstained_other_reason | — |
| SYN-EVAL-069 | SYN-EVAL-069-I1 | stale-source | knowledge | abstained_other_reason | — |
| SYN-EVAL-070 | SYN-EVAL-070-I1 | stale-source | knowledge | abstained_as_expected | — |
| SYN-EVAL-071 | SYN-EVAL-071-I1 | conflicting-source | knowledge | abstained_as_expected | — |
| SYN-EVAL-072 | SYN-EVAL-072-I1 | conflicting-source | knowledge | abstained_as_expected | — |
| SYN-EVAL-073 | SYN-EVAL-073-I1 | conflicting-source | knowledge | abstained_as_expected | — |
| SYN-EVAL-074 | SYN-EVAL-074-I1 | conflicting-source | knowledge | abstained_as_expected | — |
| SYN-EVAL-075 | SYN-EVAL-075-I1 | conflicting-source | knowledge | abstained_as_expected | — |
| SYN-EVAL-076 | SYN-EVAL-076-I1 | missing-detail-pressure | knowledge | missed_abstained | — |
| SYN-EVAL-077 | SYN-EVAL-077-I1 | missing-detail-pressure | knowledge | missed_abstained | — |
| SYN-EVAL-078 | SYN-EVAL-078-I1 | missing-detail-pressure | knowledge | missed_abstained | — |
| SYN-EVAL-079 | SYN-EVAL-079-I1 | missing-detail-pressure | knowledge | missed_abstained | — |
| SYN-EVAL-080 | SYN-EVAL-080-I1 | missing-detail-pressure | knowledge | missed_abstained | — |
| SYN-EVAL-081 | SYN-EVAL-081-I1 | role-denial | knowledge | missed_abstained | — |
| SYN-EVAL-082 | SYN-EVAL-082-I1 | role-denial | knowledge | missed_abstained | — |
| SYN-EVAL-083 | SYN-EVAL-083-I1 | role-denial | knowledge | missed_abstained | — |
| SYN-EVAL-084 | SYN-EVAL-084-I1 | role-denial | knowledge | missed_abstained | — |
| SYN-EVAL-085 | SYN-EVAL-085-I1 | role-denial | knowledge | missed_abstained | — |
| SYN-EVAL-086 | SYN-EVAL-086-I1 | multi-linked | knowledge | cited_expected | KB-FRM-420#s1 v1.0 |
| SYN-EVAL-086 | SYN-EVAL-086-I2 | multi-linked | auditor | held_for_auditor | — |
| SYN-EVAL-087 | SYN-EVAL-087-I1 | multi-linked | knowledge | cited_expected | KB-FRM-420#s1 v1.0 |
| SYN-EVAL-087 | SYN-EVAL-087-I2 | multi-linked | auditor | held_for_auditor | — |
| SYN-EVAL-088 | SYN-EVAL-088-I1 | multi-linked | knowledge | cited_expected | KB-FRM-420#s1 v1.0 |
| SYN-EVAL-088 | SYN-EVAL-088-I2 | multi-linked | auditor | held_for_auditor | — |
| SYN-EVAL-089 | SYN-EVAL-089-I1 | multi-linked | knowledge | cited_expected | KB-FRM-420#s1 v1.0 |
| SYN-EVAL-089 | SYN-EVAL-089-I2 | multi-linked | auditor | held_for_auditor | — |
| SYN-EVAL-090 | SYN-EVAL-090-I1 | multi-linked | knowledge | cited_expected | KB-FRM-420#s1 v1.0 |
| SYN-EVAL-090 | SYN-EVAL-090-I2 | multi-linked | auditor | held_for_auditor | — |
| SYN-EVAL-091 | SYN-EVAL-091-I1 | legal-deadline | knowledge | missed_abstained | — |
| SYN-EVAL-092 | SYN-EVAL-092-I1 | legal-deadline | knowledge | missed_abstained | — |
| SYN-EVAL-093 | SYN-EVAL-093-I1 | legal-deadline | knowledge | missed_abstained | — |
| SYN-EVAL-094 | SYN-EVAL-094-I1 | legal-deadline | knowledge | missed_abstained | — |
| SYN-EVAL-095 | SYN-EVAL-095-I1 | legal-deadline | knowledge | missed_abstained | — |
| SYN-EVAL-096 | SYN-EVAL-096-I1 | indirect-kb | knowledge | abstained_as_expected | — |
| SYN-EVAL-097 | SYN-EVAL-097-I1 | indirect-attachment-injection | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-098 | SYN-EVAL-098-I1 | indirect-attachment-injection | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-099 | SYN-EVAL-099-I1 | indirect-attachment-injection | knowledge | no_source_expected_abstained | — |
| SYN-EVAL-100 | SYN-EVAL-100-I1 | indirect-attachment-injection | knowledge | no_source_expected_abstained | — |
