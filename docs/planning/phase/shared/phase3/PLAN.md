# Shared Phase 3 — Integrated Evaluation and Independent Review

**Status (2026-11-08):** The 100-case draft and integrated synthetic harness are available. Evaluation remains unscored because Manny must approve the draft expected labels/source expectations first. The 686 passing Python tests and 5 passing draft-validator checks establish engineering checks only; they do not establish PRD accuracy gates or real-world performance. Current acceptance requirements are in PRD-v4.

## Work

- Run frozen synthetic holdout cases across component, lane, connection, and full-workflow paths; retain fixture and policy/source versions.
- Report per-agent and end-to-end factual precision, fabricated citations, evidence attribution, abstention, conflict handling, confidence calibration, uncertainty propagation, injection/permission outcomes, retrieval recall@k, source freshness, latency/cost, and failure recovery.
- Measure human detection/correction of planted draft errors. Handling-time comparisons require an accepted participant/protocol design; otherwise report exploratory/not measured.
- Report per-gate sample counts/uncertainty. A finite-set pass is evidence for that set, not a population-wide guarantee.
- Provide PRD, contracts, assertions, traces, and results to independent REVIEWER and SECURITY. Owners fix internal findings in their lanes; Shared fixes connection defects; re-review affected evidence.

## Exit evidence

Every P0/safety claim has an observable result or explicit project-lead deferral. The approved must-pass set has zero critical unsupported claims, fabricated citations, unsafe non-abstention, injection bypass, sensitive disclosure, unauthorized dispatch, or state corruption. Missing evidence is PARTIAL/NOT TESTED, never PASS.
