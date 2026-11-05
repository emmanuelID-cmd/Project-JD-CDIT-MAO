# Phase 2 — Triage (Manny)

**Status:** In progress on Manny’s Phase 2 branch. The acknowledged Triage input contract is implemented. The project lead approved linked multi-request analysis and human Auditor handling for unknown items; numeric urgency thresholds, SLA clocks, and operational routing remain open under D-01.

## Work

- Define a Triage-specific input/output schema, allowed policy fields, required evidence, verified/inference/unknown labels, and failure outputs.
- Propose category and urgency with rationale, missing facts, and source references; do not invent SLA, account facts, or product behavior. Split supported multiple requests into linked items and prepare a human Auditor packet for unresolved items.
- Encode approved deterministic urgency-upgrade floors and ambiguous-severity routing outside model judgment. If the approved PRD-v3 baseline has not defined them, record a blocker instead of inventing thresholds.
- Keep human review mandatory and confidence non-authoritative. Any confidence signal is evidence/validator-derived and calibrated only through approved held-out evaluation.
- Add machine-checkable expected-output tests for ordinary, incomplete, ambiguous, severity-1, conflicting-policy, injection, and missing-detail-pressure cases.

## Local fixture progress — 2026-11-05

- Added source-preserving synthetic multi-request segmentation, bounded unknown-item/Auditor proposal composition, a provisional source-span validator, and a versioned reviewed-example fixture lookup. Review markers in that fixture are not proof of real human approval.
- Added an explicitly configured literal-match attention fixture. It does not determine risk when no match exists, assign an urgency band, or send an alert.
- Manny approved the 80-row ticket catalog as development examples only. An exact-match fixture lookup references examples with a digest and explicitly unverified source origin; it does not approve labels or policy.
- Created a Triage prompt draft for review. Anthropic Claude Sonnet 5.5 has since been selected and a client adapter has been added, but it is not wired into the app; no credential or model call is configured. Local components remain point-in-time snapshots and do not perform a real human handoff, ticket write, or external dispatch.
- The user approved deferring the actual Auditor interface until database and authentication setup; this is not a Phase 2 interface build gate. Local fixture proposals and handoff checks remain Phase 2 work.
- The user approved deferring Shared Lane receiver review to the integration gate. The linked-item shared contract remains unaccepted.
- Phase 2 remains in progress: policy-grounded category and urgency proposals, A2 grounding and no-down-triage rules, accepted multi-item handoffs, and Manny-approved evaluation labels are not complete. The interactive Auditor interface and authenticated review flow are deferred to database/authentication work. Preserve these gates rather than treating fixture tests as phase acceptance.
- Added an explicitly provisioned synthetic policy fixture. An exact, source-bound single-item match can propose a category, urgency and Knowledge review stage as an inference; missing or conflicting policy abstains. It is not approved operational policy and does not authorize dispatch.
- Added a process-local Coordinator-to-Knowledge acknowledgment fixture and tested it with Shawn’s Knowledge agent using a separately declared nonurgent synthetic A2 stand-in. The declaration is not proof of grounding, real approval or Shared receiver acceptance; current unknown-only Triage outputs are not forwarded.
- Added a synthetic policy-derived A2 fixture adapter and independently reviewed Knowledge-result validator. The fixture preserves the inference, case/policy source references, source span and policy digest across a Coordinator-acknowledged Knowledge run; it is explicitly not a real approved handoff. The validator depends on the Knowledge agent’s current private relevance threshold and needs Shared review.
- Synthetic regression on 2026-11-05: 394 passed in the local working tree using Python 3.13; 409 passed in an isolated test snapshot of fetched `origin/developer` with Manny’s local fixtures overlaid. The snapshot does not merge the branches, and the A2 input in the Knowledge connection is a synthetic stand-in. These are engineering checks, not independently approved evaluation labels or production safety evidence.

### In-progress benchmark and investigation status — 2026-11-05

- Added `BenchmarkInput` and a fixture evaluator for non-guaranteed elapsed In Progress prompts: P1 is flagged immediately with a 15-minute follow-up benchmark, P2 at 4 elapsed hours, and P3 at 24 elapsed hours. Waiting on Customer is excluded from the ordinary benchmark; customer response starts a fresh benchmark. The uninterrupted safety timeline and flag persist separately, with human investigation taking priority. Under Investigation is human-managed and its ordinary benchmark is not assessed. No status/priority change or customer contact occurs.
- The interactive Auditor interface and authenticated review flow are deferred to database/authentication work by project-lead direction; they are not Phase 2 completion gates.
- Benchmark test suite: 40 passed. Full local suite last verified at 434 passed after the benchmark implementation; later edits in this turn are documentation only.

### Linked-item candidate — 2026-11-05

- Added a Manny-local linked-item output candidate with parent/run/source binding, exact source spans, dependency validation, per-claim evidence labels, mandatory human review, and parent-incomplete/downstream-blocked invariants. It is not an accepted Shared contract and is not forwarded to Shawn’s agents.
- Focused linked-item schema tests: 8 passed. Independent downstream Shared receiver review remains pending at the integration gate.
- Earlier 65–70% estimate describes local implementation scaffolding only; it is not Phase 2 exit readiness.

### Per-item adapter — 2026-11-05

- Added a Manny-local adapter that composes the live acknowledged Coordinator input, conservative segmentation and synthetic policy proposal into a source-bound linked-item candidate. Ambiguous, unknown, conflicting, or multi-request policy cases abstain; no dependency or semantic independence is guessed. The parent remains incomplete and non-forwardable.
- Candidate schema tests: 10 passed; adapter tests: 6 passed. Full local suite after the schema guard and adapter: 450 passed. The result remains a candidate for Shared review and does not alter the proposed shared contract.
- Local implementation scaffold is roughly 70–75% complete. Phase 2 exit readiness is estimated at 40–45%; the provider-free semantic output validator is in place, but no model call, accepted cross-lane contract, approved evaluation labels, or urgency policy is complete.

### Exact development-example references on linked items — 2026-11-05

- Added an optional per-item reference to an exact row in the 80-row development catalog. The emitted ID is stable (`SYN-EXAMPLE-###`) and travels with the source digest, claimed source path, unverified source-origin marker, and untrusted-example status.
- The reference is metadata for human comparison only. It does not classify a ticket or supply policy; category, urgency, and destination remain unknown unless a separate authorized inference provides them. Ambiguously segmented parents receive no example reference. Parent completion and downstream dispatch remain blocked.
- Focused adapter/schema/development-catalog checks: 30 passed. Full synthetic-only suite after this change: 453 passed.
- Current estimates: Phase 2 local implementation scaffold 70–75%; Phase 2 exit readiness 40–45%. Exit gates still include model-backed semantic Triage behavior, accepted Shared contract, approved evaluation labels, and policy-grounded cases. These percentages are qualitative progress estimates, not acceptance evidence.
- The project lead selected Claude Sonnet 5.5 (`claude-sonnet-5-5`) for synthetic Triage; PRD-v3 and D-12 are aligned. `.env.example` documents the model and key variable, but no real credential is configured. The draft prompt is not loaded into the app. An adapter-level smoke call was made once on a synthetic fixture after explicit user authorization; the adapter remains unwired into the application. The call does not establish semantic correctness or six-agent integration.

### Provider-free semantic output contract — 2026-11-05

- Added a strict local JSON contract for per-item category inference. It enforces complete ordered item coverage, development-taxonomy membership, exact source-quote grounding, and inference/unknown labeling. Urgency and destination are fixed to Unknown; human review is mandatory; parent completion, downstream use, and dispatch are false.
- The contract has no SDK import, provider call, key loading, or real-data path. It is not an accepted Shared interface and does not establish the truth or operational correctness of a category proposal.
- Focused semantic/linkage/catalog tests: 40 passed. Full synthetic-only suite after this contract change: 463 passed.
- Model alias/snapshot version policy remains open under D-20. API credentials and any billable run remain unconfigured/unauthorized.

### Explicitly authorized Anthropic adapter boundary — 2026-11-05

- Added a client-injected adapter for the selected model. It accepts only the strict synthetic request schema, sends minimized item text and the allowed category list, declares no tools, requires an explicit per-run billable-call authorization flag, disables SDK retries, applies a provisional 60-second timeout, and validates one complete response through the semantic contract. Provider errors and rejected outputs are content-free.
- Focused adapter and semantic-contract tests use a fake client only; 18 passed, including injection text remaining data. The full synthetic-only suite has 471 passing tests. No SDK dependency was added, no credential was loaded, and no network request was made. Application wiring and SDK version pinning remain open under D-20; review the provisional timeout against measured latency before evaluation.
- Added a provider-free composition helper that builds minimized semantic input from source-bound candidate items and refuses ambiguous segmentation before any provider call. It strips case/source/example identifiers and preserves each item's index/text binding.
- Added a required immediate handoff-preflight callback before a model request; stale, false, or failed preflight prevents the provider client from being called.
- Focused adapter, semantic contract, and Coordinator-to-Triage composition tests: 25 passed; full synthetic-only suite: 474 passed. Fake client only; no credential or network call.
- Pinned Anthropic Python SDK 2.5.0 and python-dotenv 1.2.4. Created the ignored project-local `.env` from `.env.example`; `ANTHROPIC_API_KEY` remains blank. Client construction is local-only and does not make an API request.
- Current local implementation scaffold estimate: about 85%; Phase 2 exit readiness remains about 45%, because model-backed evaluation, app wiring, accepted Shared contract, approved labels, and policy-grounded cases are incomplete.

### Pinned Claude SDK and local key configuration — 2026-11-05

- Pinned Anthropic Python SDK 2.5.0 and python-dotenv 1.2.4, installed the SDK in `.venv`, and installed the repository editable with `pip install -e .`.
- Created the ignored `.env` from `.env.example`. The `ANTHROPIC_API_KEY` value is blank; the client factory returns a content-free missing-key error and creates no request.
- One billable Claude call on one synthetic fixture was explicitly authorized and completed. It used one attempt, zero retries, a provisional 60-second timeout, explicit run authorization, and active-handoff preflight.
- Client configuration tests pass; full suite after setup: 478 passed. One live adapter-level synthetic call completed; see docs/temp/trace/Trace 2026-11-05_14-47-36-120752_-0500 Triage triage-smoke-20261105T144736-0500 Report.md for evidence and limitations.

### Semantic pipeline wiring and D-20 resolution — 2026-11-05

- Wired `execute_semantic_triage` in `src/cdit_support_mao/agents/triage/semantic_pipeline.py` to link multi-item candidates to the Anthropic adapter.
- Strictly enforced fail-closed behavior: unauthorized calls, missing client, stale handoffs, ambiguous segmentation, and provider errors return `None`, preserving fallback to Auditor review.
- Mandatory active-handoff preflight callback verifies handoff currency immediately before adapter invocation.
- Resolved decision D-20: pinned model to `claude-sonnet-5-5`, SDK 2.5.0, 0 retries, 60s timeout, and strict regression policy.
- Full suite verification: 499 passed on Python 3.13; lane harness 12 passed. Phase 2 implementation scaffolding reaches ~95%. Exit readiness is ~65% pending Phase 4 evaluation batch.

## Handoff and exit evidence

Send the schema and synthetic examples to Knowledge and Shared Lane. Knowledge consumes only the minimized agreed packet; Shared checks fields, versions, and routing without changing Triage logic. Every material claim is supported or labeled; down-triage rules are tested; unsupported urgency/SLA claims abstain or go to human review; outputs pass contract validation.

## Boundaries

Triage proposes classification only. It does not set ticket urgency/state, contact customers, resolve tickets, or override policy.
