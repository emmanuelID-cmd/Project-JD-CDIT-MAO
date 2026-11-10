# Synthetic live Triage diagnostic — failed aggregation attempt

**Status: INCOMPLETE.** The 100-case synthetic batch completed its case loop but failed while aggregating segmentation availability, before writing report/results artifacts. No accuracy or coverage result is available for this attempt. It must not be treated as a pass or merged with another run.

- Attempt: `CDIT-PHASE2-V3-PROMPT-V2-LIVE-TRIAGE-20261110-R2`
- Frozen manifest: `EVAL-DRAFT-V3-PROMPT-V2-LIVE-TRIAGE-R2.manifest.json` (SHA-256 `af865c0e90301cc76aa01caf462b8c3056a00b029670e173a58e96bdffa1a219`)
- Dataset: synthetic v3, 100 cases / 105 expected items
- Failure boundary: result aggregation after all case executions; `evaluation_live.py` attempted to read `case_id` from an item comparison row.
- Confirmed effect: process exited with `KeyError: 'case_id'`; no R2 `.results.json` or normal report was written.
- Provider-call count and actual provider billing are **unavailable** because this run did not persist per-case telemetry before the aggregation error. Provider retries were configured off; no ticket writes or external dispatch are in scope.
- Remediation: aggregate unavailable case IDs from their parent case records; added a regression test for a case stopped at A1; full suite passed 743 tests before the replacement run.

This record is retained as an incomplete attempt. The replacement run has a new manifest and trace ID; this attempt is not overwritten or counted as a completed trace.
