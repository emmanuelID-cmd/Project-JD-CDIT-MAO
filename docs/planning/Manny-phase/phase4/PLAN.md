# Phase 4 — Manny Lane Validation and Handoff

**Status:** Planned; follows Phases 1–3 and accepted contracts.

## Work

- Map Manny A0/A1/A2/A5 requirements to tests, deterministic assertions, and synthetic fixtures.
- Own the synthetic evaluation definitions/protocol: claim classes and denominators, per-gate positive/negative counts, confidence calibration, retrieval freshness/recall, latency/cost, reviewer-error thresholds, and deterministic metric/reporting rules. Use human-approved expected labels and the deterministic script baseline; a project teammate peer-reviews disputed labels and a sample. No external evaluator, customer, or specialist participant is required.
- Preserve the zero unsupported material-claim safety gate and report results as applying to the tested set; do not let model-reported confidence alone establish truth or authority.
- Run owner-lane checks on the approved Python 3.13 environment; record exact command, environment, counts, and failures.
- Cover unsupported claims, citation mismatch, abstention, stale/malformed packets, permission denial, retries, cancellation, and safe fallback.
- Publish contract-compatible examples and a handoff with versions, evidence, limitations, and unresolved findings.
- Return interface mismatches to Shared Lane; keep agent-internal fixes in Manny's lane.

## Exit evidence

Results are reproducible by an independent reviewer. The approved must-pass set has zero critical fabricated claims/citations, unsafe down-triage, injection bypass, unauthorized dispatch, or lost uncertainty; all open findings have explicit owners.

## Boundaries

This lane report does not accept Shawn's agents or certify the combined workflow. Shared Lane and independent review own those checks.
