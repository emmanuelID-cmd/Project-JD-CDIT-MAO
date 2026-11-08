# Phase 4 — Manny Lane Validation and Handoff

**Status:** Runner and preliminary report exist; Phase 4 is not accepted or complete. The evaluator reports 12 downstream fixture cases using a stand-in Triage handoff, zero Manny-approved labeled cases scored, and not-ready integration status.

## Current progress — 2026-11-06

- Drafted [`EVALUATION-PROTOCOL-DRAFT.md`](../../lanes/manny/EVALUATION-PROTOCOL-DRAFT.md) with synthetic-only case lifecycle, label approval, metric definitions, safety gates, over-reliance checks, retrieval freshness, confidence, latency/cost, and reproducibility.
- Implemented Phase 4 Synthetic Evaluation Runner in `src/cdit_support_mao/manny_evaluation.py`.
- Evaluated Coordinator checks, benchmark fixtures, and Escalation rules separately; exercised the downstream combined harness on 12 synthetic cases using prebuilt Triage handoffs. The combined harness does not run Coordinator into semantic Triage.
- Generated evaluation report in [`docs/lanes/manny/evaluation/MANNY-EVALUATION-REPORT.md`](../../lanes/manny/evaluation/MANNY-EVALUATION-REPORT.md) and JSON results in [`docs/lanes/manny/evaluation/manny-evaluation-v1.results.json`](../../lanes/manny/evaluation/manny-evaluation-v1.results.json).
- The generated report records zero violations on its tested fixtures. This result applies only to that 12-case set and does not establish PRD-wide evaluation completion or full workflow safety.
- The revised evaluator tests pass; the full Python 3.13.15 suite passes 565 tests after the case-evaluation update and developer fast-forward. Test success does not alter `scoring_status=not_scored` or Phase 4 not-ready status.
- Connected the evaluator to the existing per-case `check_expectations` contract. Every downstream harness run is now compared with its case-file expected tool outputs; the current 12/12 declared fixture expectations match. These outputs remain engineering expectations, not approved gold labels or holdout scoring. The JSON report records per-case pass/failure and mismatch details.
- Added a CLI regression test: preliminary fixture assertions still exit with status 2 and emit `phase_exit_ready=false`, `scoring_status=not_scored`, and zero Manny-approved labeled cases. Focused test passes; this prevents fixture checks from appearing as Phase 4 completion.
- CLI convention: exit code 2 means the runner produced preliminary fixture evidence but Phase 4 is not ready; it is not a passing evaluation or a CLI usage-error claim.

## Evidence currently implemented

- The runner separately evaluates Coordinator intake fixtures, three elapsed-time benchmark fixtures, four handcrafted Escalation rule cases, and 12 downstream cases using a stand-in TriageHandoff.
- Each gate reports its actual check count and violations. The no-dispatch/write gate is explicitly `not_tested` because this harness has no dispatch surface.
- The generated report marks fixture checks as preliminary, sets scoring to `not_scored`, records 0 of 100 Manny-approved labeled cases, and reports integration as `not_ready`.
- The runner cannot claim Phase 4 readiness. It does not exercise Coordinator-to-semantic-Triage, measure semantic accuracy, or validate all PRD safety gates.
## Preliminary evidence (not phase exit)

The current fixture results can be reproduced with the command below. Until the 100-case labeled evaluation set, Manny-approved labels, and Coordinator-to-semantic-Triage integration are present, this report is preliminary and does not close Phase 4.
```bash
python -m cdit_support_mao.manny_evaluation --report docs/lanes/manny/evaluation/MANNY-EVALUATION-REPORT.md --results docs/lanes/manny/evaluation/manny-evaluation-v1.results.json
```
These results describe the asserted checks over the current fixture set only. They do not prove the approved evaluation gates over the required labeled set or the missing integrated Triage path.

## Boundaries

This phase validates the synthetic agent workflow. It does not close PRD-v4 local database, authentication, role-interface, or no-auth showcase acceptance; those checks belong to the separate local app workstream.


This preliminary report records component and downstream fixture evidence only. It does not verify Coordinator-to-semantic-Triage, item-scoped compatibility, or full cross-lane integration; Shared receiver acceptance remains pending. Real data and production integrations remain out of scope.
