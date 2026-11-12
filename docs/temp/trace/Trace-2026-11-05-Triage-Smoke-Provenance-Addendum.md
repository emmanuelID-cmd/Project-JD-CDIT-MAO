# Retrospective provenance addendum — Triage smoke trace

**Trace:** `triage-smoke-20261105T144736-0500`
**Recorded:** 2026-11-05
**Purpose:** Reconcile source-backed identifiers and prompt provenance from the frozen artifacts without changing them or making another provider call.

## Reconciled from frozen evidence

- The manifest names the fixture `SYN-CASE-01`; `Evidence.json` names it `SYN-TRACE-001`. Their `reported_text` and `fixture_text` values are byte-for-byte equal as UTF-8 text. The SHA-256 of that shared text is `1a05637006444ede7f60c9a9ca5e25c43b949f04405fb88b0ca35b841000f40f`. For this trace only, record `SYN-TRACE-001` as an alias for `SYN-CASE-01`. This is a retrospective reconciliation, not a contemporaneous fixture-registry record.
- The manifest records `src/cdit_support_mao/agents/triage/anthropic_adapter.py` at SHA-256 `dda307426903e99a1391d0d4848209422e27707164e660d15a42c8c2fa527616`; the current file has the same digest. Its embedded `SYSTEM_PROMPT` has SHA-256 `92dcee2769dbefed8b42e9b8579dd1e929789bd9c340d7d17bdc844225aa996c` (686 characters). This identifies the prompt text in the source file referenced by the manifest. `TRIAGE-PROMPT-v0.md` was not loaded for the call.

## Still unavailable; do not infer

- The canonical serialized request body and a request-body digest were not captured. The source and fixture identify how the request is built, but cannot prove the exact bytes sent in that past call. TR-01 remains unresolved for that run.
- The manifest records one authorized provider request, and the user authorized one synthetic call in the conversation. A separate machine-readable approval record was not included in the frozen bundle.
- No Manny-approved semantic label exists for this fixture. Its category correctness remains unverified.
- The trace still does not exercise app-wired Coordinator-to-semantic-Triage, linked-item receiver acceptance, or the six-agent workflow.

No frozen trace artifact was rewritten. No model/API call was made. This addendum does not assign an aggregate score or change the trace's `INCOMPLETE` disposition.
