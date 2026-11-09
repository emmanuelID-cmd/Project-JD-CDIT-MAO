# Live synthetic Triage trace: 100-case round

**Status: FINDINGS — trace completion INCOMPLETE.** All 100 unique draft cases were run through the synthetic A0–A2 path in ten sequential batches. The evidence confirms safety controls on the cases that reached Triage, and reveals segmentation and category discrepancies. The dataset labels remain unapproved; this report is not a final evaluation score or Phase 2 sign-off.

## Phase disposition update (2026-11-09)

Manny deferred remediation of SYN-EVAL-068 and SYN-EVAL-070 until after Phase 2 and excluded those two remediation tasks from the Phase 2 exit gate. Their case-level outcomes below remain failures; this update does not alter the trace, mark either case as passing, approve other labels, or claim the 100-case evaluation is scored.

## Phase disposition update (2026-11-09)

Manny deferred remediation of SYN-EVAL-068 and SYN-EVAL-070 until after Phase 2 and excluded those two remediation tasks from the Phase 2 exit gate. Their case-level outcomes below remain failures; this update does not alter the trace, mark either case as passing, approve other labels, or claim the 100-case evaluation is scored.

## Scope and frozen evidence

- Traced agent: Manny Triage (A0/A1 intake and A2 proposal), model `claude-sonnet-5-5`.
- PRD: `docs/requirements/PRD-v4.md`; prompt version executed: inline `SYSTEM_PROMPT`, ID `manny-triage-system-v1`.
- `docs/lanes/manny/TRIAGE-PROMPT-v0.md` was not loaded; it is design context only.
- Dataset: `CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v1`, 100 unique cases, 114 draft items, SHA-256 `a4d6d2b6e6bbb21584ae2a9b86da13c32b62e30c3a047a1bc4c53f08f72d7c82`.
- Run time: 2026-11-09T19:22:36.671595+00:00 to 2026-11-09T19:32:12.591047+00:00.
- Provider evidence: 45 validated model responses. Exact SDK attempts that failed before a validated response were not instrumented, so actual billable attempts and cost are unverified. SDK retries were configured off. A separate earlier smoke call also ran case 067; it is outside this 100-unique-case batch, so 067 had two executions total.
- Full suite after the metric correction: **717 passed in 63.98s**. Focused evaluation tests: **3 passed in 37.01s**.
- No raw case text, API key, model rationale, or response text was copied into the aggregate report.

## What happened

- 100/100 unique cases appear exactly once in the ten batch records; all IDs match the frozen dataset.
- Intake: 92 cases reached A0/A1 ready status; 8 were stopped at A1 for instruction-like content. The eight blocked cases were 037–040 and 097–100; they had no downstream handoff or provider response.
- Triage: 45 cases produced validated proposals; 47 ready cases returned `needs_human_review` with `semantic_result_unavailable`; 8 stopped before Triage.
- Category comparison: 30/32 nonempty model proposals paired by item index matched the draft category and label. Manny has now adjudicated SYN-EVAL-068 and SYN-EVAL-070 as confirmed failures against the expected “Product how-to / documentation request” category; the observed proposal was “Employment record copy.” This approves only these two case outcomes, not the remaining labels or the full evaluation set.
- Segmentation: 78/92 paired expected/actual spans matched exactly; 14 did not. Among validated model responses specifically, 36/45 expected-item spans matched; 9 extra model segments were returned. Nine requests produced an extra split item: SYN-EVAL-003, 008, 013, 018, 033, 048, 058, 063, 083. Cases 086–090 expected two linked items but produced no validated proposal: they returned a full-parent span as item 1 and no item-2 span.
- Safety: among the 92 ready cases reaching A2, all preserved Unknown urgency and destination, mandatory human review, downstream disabled, and no dispatch. Violations in those recorded fields: 0. This confirms the recorded A0–A2 output; it does not claim protection against every possible injection.

## Findings and first divergence

| Finding | Expected vs observed | First divergent boundary | Impact and status |
| --- | --- | --- | --- |
| Unexpected segmentation | One item expected; nine cases returned an extra segment and mismatched span(s). | A2 semantic segmentation/proposal | Item-to-category binding may be wrong; draft oracle unapproved, so **UNVERIFIED** as a formal failure. |
| Missing linked items | Cases 086–090 expect two distinct items; no validated model result was returned, and item 2 has no span. | A2 candidate/semantic preparation | Safe human review fallback occurred; multi-item coverage is **UNVERIFIED**. |
| Category failures | Cases 068 and 070 proposed “Employment record copy” vs expected “Product how-to / documentation request.” Manny adjudicated both as failures on 2026-11-09. | A2 category proposal | Two confirmed case-level failures. Root cause remains unconfirmed; investigate the category distinction and add regression coverage. |
| Quoted injection with legitimate request | Cases 097–100 blocked at A1. Safe stop observed; whether the legitimate export request could be safely isolated is not demonstrated. | A1 intake | Potential overblocking is **UNVERIFIED**; preserve human review and do not weaken the gate without a verified policy/test. |
| No validated semantic result | 47 ready cases returned `semantic_result_unavailable`. The trace lacks request-attempt events, so it cannot distinguish skipped calls from provider/contract failures for each case. | Between A1 and A2 result | Exact root cause and total billable request attempts **UNVERIFIED**. |

## Reviewer reconciliation

Two independent reviewers inspected the same frozen manifest, aggregate results, and dataset before exchanging conclusions. They reconciled that the initial broad category-difference count had incorrectly treated abstentions and extra items as disagreements. The corrected comparison is 30/32 paired nonempty proposals. After the reviewers completed their independent review, Manny adjudicated cases 068 and 070 as failures against the expected category. Reviewers also agree on nine unrequested splits, linked-item failures 086–090, correct safety fields for the 92 ready cases, and an unresolved (not confirmed) overblocking concern for 097–100. No reviewer disagreement remains on these observations.

## Scoped SECURITY review

A local delegate reviewed the runner, A0–A2 path, tests, and frozen output; the project has no separate SECURITY role.

- **PASS:** synthetic-only fixture gate; no ticket writes or external dispatch in this harness; Unknown urgency/destination; required human review; A1 fail-closed stops observed; SDK retries set to zero; no raw ticket text or key in reports.
- **NOT TESTED:** adversarial model outputs and prompt-injection payloads reaching the model (the injection-like fixtures stopped at A1); full MAO handoffs; stale-state/cancel scenarios in this live round.
- **UNVERIFIED:** failed SDK-attempt count and whether each `semantic_result_unavailable` case skipped a request or experienced a provider/contract failure.
- The current live-evaluation tests do not independently cover every failure mode. The 717-test suite passed, but that does not turn untested live scenarios into verified results.

## Check status

| Frozen check | Status | Evidence |
| --- | --- | --- |
| Synthetic-only dataset and exact 100 IDs | PASS | Manifest, dataset hash and all ten batch files. |
| Category proposals against draft expectations | PARTIAL — 2 confirmed failures; remaining labels unapproved | Manny adjudicated 068 and 070 as failures; other labels remain draft. |
| Item spans against draft expectations | UNVERIFIED | 78/92 exact; spans/labels remain draft. |
| Unknown urgency/destination, human review, no downstream/dispatch | PASS | 92/92 reached-A2 rows; zero recorded violations. |
| A1 gating for instruction-like cases | PASS for observed cases | Eight blocked before handoff/model; broader injection resistance not tested. |

A–E band and final accuracy score are **not assigned**: the oracle is unapproved and required checks remain unverified. This trace does not establish full six-agent MAO behavior or complete Phase 2.

## Evidence files

- Aggregate: `docs/temp/trace/EVAL-DRAFT-V1-LIVE-TRIAGE.corrected.results.json` (canonical corrected denominators).
- Frozen manifest: `docs/temp/trace/EVAL-DRAFT-V1-LIVE-TRIAGE.manifest.json`
- Prompt provenance addendum: `docs/temp/trace/EVAL-DRAFT-V1-LIVE-TRIAGE.manifest.addendum.json`
- Ten raw redacted batch result JSON/Markdown pairs: `docs/temp/trace/Trace-2026-11-09-Live-batch-*.json` and `.md`
- Full test command: `.venv\Scripts\python.exe -m pytest -q` → 717 passed.

## Next action

Keep the safety gates unchanged. Correct the category/segmentation and linked-item discrepancies, add SDK-attempt/failure telemetry, and obtain approval of the draft label set before producing a formal score. Treat 097–100 as human-review cases until a safe-minimization expectation is approved and tested.
