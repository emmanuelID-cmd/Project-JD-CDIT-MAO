# Phase 2 — Triage (Manny)

**Status (2026-11-09):** The connected A0–A3 linked-item path and synthetic Auditor-resume path through A6 are implemented and pass focused integration tests (58 passed). PR #15 merged S-1.1; Manny's connector carries item-level attention-check results and taxonomy provenance. The local Staff/Admin Auditor interface, append-only decision history, and assigned-case authorization are implemented. A 100-case live A0–A2 diagnostic ran on 2026-11-09; Manny adjudicated cases 068 and 070 as category failures. Per D-22, fixing those two cases is deferred until after Phase 2 and excluded from its exit gate; they remain failures and are not scored as passes. Forty-seven ready cases lacked a validated semantic result; nine outputs split a single expected item, and five linked-item cases lacked validated proposals. Phase 2 remains open for the other remediation/regression work, remaining label/source approval and scoring gates, and the ordered exit checklist. The previous 95% readiness estimate is stale and should not be used as current status. Benchmarks are suggestions, not guarantees. Operational SLA/routing policy remains open under D-01.

## Ordered exit checklist

See [`EXIT-CHECKLIST.md`](./EXIT-CHECKLIST.md) for the dependency-ordered remaining gates, owners, direct decisions, and cumulative readiness forecasts. The prior 95% Phase 2 exit-readiness estimate remains a planning estimate; the assigned-case permission requirement is implemented, while label approval and scored evaluation remain open. Earlier 70–75% scaffold / 45–50% and 85% readiness estimates are historical.

## Connected Sonnet 5.5 smoke call — 2026-11-06

- One user-authorized call ran through `CombinedWorkflowHarness.run_manny_connected` with the pinned `claude-sonnet-5-5` model. The response passed the structured contract but returned category `unknown`; the connected workflow sent the item to human Auditor review and did not invoke Knowledge, Troubleshooting, or Documentation.
- See [the synthetic trace report](../../../temp/trace/Trace-2026-11-06-Synthetic-Connected-Triage-Smoke.md) for the run/trace IDs, token counts, elapsed time, and prompt/request digests. It contains no API key or raw serialized request.
- The output is a safe abstention, not a scored accuracy result. Manny's expected label is not yet approved.
## Additional Manny-owned work — 2026-11-06

- Added `synthetic_data/manny_triage_cases/unknown-high-impact.json` as a case-specific contract fixture. The actual Coordinator-to-Triage A0–A2 harness, using an injected fake provider response, preserves Unknown category/urgency, records local Auditor-review reasons, requires human review, and carries a potential-attention signal with matching source span. The local review reasons are metadata only; the Shared item contract and Auditor interface remain pending. This tests the agreed fallback/attention behavior, not semantic model accuracy or the 100-case gold set.

- If validated semantic output cannot be bound to the local linked-item candidate, runtime now returns a fail-closed `needs_human_review` result, retains only the unbound candidate, and suppresses the semantic result. Fake-client regression passes; no Shared contract change or provider call was made.
- Future synthetic model results carry a stable prompt ID and SHA-256 digests of the source prompt and exact serialized request body; raw prompt, request text, and key material are excluded from result metadata. Fake-client tests compare the request digest with the exact bytes passed to the provider. This does not backfill the prior smoke call's uncaptured request body.
- Added `docs/temp/trace/Trace-2026-11-05-Triage-Smoke-Provenance-Addendum.md`. It reconciles the two fixture identifiers by exact text match and records the source-backed prompt hash. It explicitly leaves the actual serialized request/hash unresolved because it was not captured during the call.
- Full synthetic suite after this and parallel Phase 3/4 changes: 557 passed. Phase 2 remains open for accepted Shared receiver contract, app/combined workflow wiring, Manny-approved labels, and complete request-trace evidence.

Runtime contract note: a stale/invalid handoff found before candidate creation raises the registry's `HandoffError`; if the handoff becomes stale during semantic preflight, the wrapper returns a human-review result without a provider call. The runtime reads the exact project `CASE-SCENARIOS.md` source only when its SHA-256 matches the reviewed pin, then exposes only its category names and a separate category-list digest. A supplied taxonomy must equal that loaded source before the provider can run. Example ticket text, urgency bands, and conditions are not sent as model examples or treated as labels. Each category inference is joined to its exact item source span and cites the taxonomy digest version. This supports the approved synthetic category behavior; it does not establish CDIT operational urgency/routing policy.

## Manny-local A0–A2 runtime harness contract

- **Owner and boundary:** Manny's tests exercise the Coordinator-acknowledged A0/A1 handoff through semantic A2. They do not dispatch an item to Shawn's Knowledge agent or claim Shared receiver acceptance.
- **Inputs:** synthetic case fixture, current Coordinator handoff/version, the category-only taxonomy from `CASE-SCENARIOS.md`, and an injected fake-compatible client. No credential loading or provider call is part of ordinary test runs.
- **Observable pass path:** one output per clearly segmented item; exact source spans and quotes; allowed taxonomy membership; category remains inference; urgency/destination Unknown; optional source-bound fixture attention signal; human review required; parent incomplete; downstream and dispatch false.
- **Stop/fallback cases:** stale or cancelled handoff, invalid/mutated taxonomy, missing taxonomy, ambiguous segmentation, unauthorized billable call, provider error, or malformed/model-mismatched output must fail closed or return human review without downstream work.
- **Evidence:** `tests/test_manny_triage_flow.py` and `tests/test_manny_triage_runtime_harness.py` cover single and multi-item paths, Coordinator-to-Triage A0–A2 composition, exact source binding, taxonomy provenance/minimization, pinned-source mismatch, missing/mutated taxonomy, stale windows, no-call fallback, fixture attention notes, and fake-provider validation. These are synthetic fixture checks, not semantic accuracy or full six-agent integration evidence.

## Work

- Define a Triage-specific input/output schema, allowed policy fields, required evidence, verified/inference/unknown labels, and failure outputs.
- Propose category and urgency with rationale, missing facts, and source references; do not invent SLA, account facts, or product behavior. Split supported multiple requests into linked items and prepare a human Auditor packet for unresolved items.
- Encode approved deterministic urgency-upgrade floors and ambiguous-severity routing outside model judgment. If PRD-v4 has not defined them, record a blocker instead of inventing thresholds.
- Keep human review mandatory and confidence non-authoritative. Any confidence signal is evidence/validator-derived and calibrated only through approved held-out evaluation.
- Add machine-checkable expected-output tests for ordinary, incomplete, ambiguous, severity-1, conflicting-policy, injection, and missing-detail-pressure cases.

## Local fixture progress — 2026-11-05

- Added source-preserving synthetic multi-request segmentation, bounded unknown-item/Auditor proposal composition, a provisional source-span validator, and a versioned reviewed-example fixture lookup. Review markers in that fixture are not proof of real human approval.
- Added an explicitly configured literal-match attention fixture. It does not determine risk when no match exists, assign an urgency band, or send an alert.
- Manny approved the 80-row ticket catalog as development examples only. An exact-match fixture lookup references examples with a digest and explicitly unverified source origin; it does not approve labels or policy.
- Created a Triage prompt draft for review. Anthropic Claude Sonnet 5.5 has since been selected and a client adapter has been added, but it is not wired into the app; no credential or model call is configured. Local components remain point-in-time snapshots and do not perform a real human handoff, ticket write, or external dispatch.
- The user approved deferring the actual Auditor interface until database and authentication setup; this is not a Phase 2 interface build gate. Local fixture proposals and handoff checks remain Phase 2 work.
- Shared contract fields S-1/S-2 were approved by Manny and merged in project PR #9. Shawn receiver code is present; acceptance of Manny’s connected item-scoped handoff remains a later Shared integration gate, as approved by the user.
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
- Historical estimate at the 2026-11-05 snapshot: local implementation scaffold 70–75%; Phase 2 exit readiness 40–45%. This is superseded by the 2026-11-06 N1–N3 implementation and the current estimate at the top of this plan; it is retained only as dated progress history.
- The project lead selected Claude Sonnet 5.5 (`claude-sonnet-5-5`) for synthetic Triage; PRD-v4 and D-12 are aligned. `.env.example` documents the model and key variable, but no real credential is configured. The draft prompt is not loaded into the app. An adapter-level smoke call was made once on a synthetic fixture after explicit user authorization; the adapter remains unwired into the application. The call does not establish semantic correctness or six-agent integration.

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

### Semantic pipeline helper and D-20 resolution — 2026-11-05

- Added execute_semantic_triage in semantic_pipeline.py to compose multi-item candidates with the Anthropic adapter. Source search found no application/runtime call site; tests call the helper directly with a fake client.
- Strictly enforced fail-closed behavior: unauthorized calls, missing client, stale handoffs, ambiguous segmentation, and provider errors return `None`, preserving fallback to Auditor review.
- Mandatory active-handoff preflight callback verifies handoff currency immediately before adapter invocation.
- Resolved decision D-20: pinned model to `claude-sonnet-5-5`, SDK 2.5.0, 0 retries, 60s timeout, and strict regression policy.
- Historical helper-level verification: 499 tests and 12 lane-harness cases passed on Python 3.13 at that snapshot; that snapshot's full suite passed 518 tests. Neither result demonstrates application wiring, model-backed semantic correctness, or linked-item Shared acceptance. Withdraw the earlier 95% scaffold and 65% exit-readiness estimates; Phase 2 exit remains unverified.

### Triage runtime source-hardening follow-up — 2026-11-05

- Fixed the runtime result validator so category, label, and exact quote binding is checked for every item, not just the final item. Added a negative two-item regression case.
- Category citations now retain the taxonomy digest version instead of reusing the case policy version. The linked-item validator checks the digest-backed taxonomy locator/version pair.
- Added a loader for the exact repository taxonomy source with a pinned whole-file SHA-256. The runtime compares caller-supplied taxonomy to the pinned source and fails closed to human review if the source file is unavailable or changed; a different supplied taxonomy is rejected before any provider call.
- The runtime can include the existing fixture attention signal with exact source offsets and a note requiring human context review. A match does not verify an incident or assign urgency; no match remains `not_assessed`.
- Focused Manny Triage/handoff and attention tests: 103 passed on Python 3.13.15. This pre-harness snapshot's full suite passed 537 tests in 26.78s using pytest `--basetemp` under the authorized writable Codex visualization directory. This is code regression evidence only, not model accuracy, Shared acceptance, or phase exit.

### Manny A0–A2 harness composition — 2026-11-05

- Added `MannyA0A2Harness` to compose synthetic Coordinator intake, sender/receiver handoff acknowledgment, pinned taxonomy loading, optional fixture attention, and `run_triage_runtime` without constructing a client, reading credentials, or writing external state.
- The base harness stops at A2. The new `CombinedWorkflowHarness.run_manny_connected` uses its A0–A2 result to create source-validated item-scoped A2 handoffs and run Shawn's actual Knowledge receiver at A3. Shawn/Shared receiver acceptance remains pending. No FastAPI endpoint was added because the production/authenticated app path remains deferred.
- Focused A0–A2 harness tests pass with both no-call fallback and an injected fake client, including explicit authorization required when a fake client is supplied. Focused Phase 2 suites: 106 passed. Full Python 3.13.15 suite: 540 passed in 19.72s using pytest `--basetemp` under the authorized writable Codex visualization directory. This is regression evidence only; Phase 2 exit and six-agent integration remain open.

## Linked-item A2 contract proposal — 2026-11-05

- Drafted [TRIAGE-LINKED-ITEM-HANDOFF-PROPOSAL.md](../../../lanes/manny/TRIAGE-LINKED-ITEM-HANDOFF-PROPOSAL.md) for Shared Lane review, using existing Manny-owned source-span and linked-item candidate fields.
- The proposal was superseded by project PR #9: Manny approved S-1 (`TriageHandoff.item_scope`) and S-2 (`InputRef.content_digest`), and both were merged to `developer`. Shawn's Knowledge receiver support is present. The remaining gate is acceptance of Manny's actual connected item-scoped handoff after N1–N3 produce a reviewable path.
- The current CombinedWorkflowHarness is not end-to-end Coordinator-to-semantic-Triage evidence: it starts from a fixture TriageHandoff and exercises the downstream agents against that stand-in.
- No Shawn-owned prompt, tool, or agent behavior was changed.

**Current disposition:** This section records the original proposal history. Its former statement that the shared contract was still unaccepted is superseded by PR #9 and must not be used as a current blocker.
## Handoff and exit evidence

Send the schema and synthetic examples to Knowledge and Shared Lane. Knowledge consumes only the minimized agreed packet; Shared checks fields, versions, and routing without changing Triage logic. Every material claim is supported or labeled; down-triage rules are tested; unsupported urgency/SLA claims abstain or go to human review; outputs pass contract validation.

## Boundaries

Triage proposes classification only. It does not set ticket urgency/state, contact customers, resolve tickets, or override policy.
