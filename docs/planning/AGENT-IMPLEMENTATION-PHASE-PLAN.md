# Agent Build, Security, Harness, and Integration Phase Plan

**Status:** Planner proposal only. This plan does not authorize implementation, new dependencies, live data, external services, or deployment.

**Planning deadline:** November 11, 2026 is the PRD's planning go/no-go deadline, not a build-completion date. Build dates and estimates should be set only after the project lead authorizes the phase and lane owners confirm capacity.

**Authoritative baseline:** `docs/requirements/PRD.md`, with current branch `manny/coordinator-triage-escalation` at `a14bb8d` (same tip as `developer` and Shawn's lane when checked on 2026-11-04). `main` remains at `1a5cf4a`.

## Current state and planning assumptions

- The local Python 3.13, FastAPI, Pydantic, and SQLite scaffold is present.
- Shawn's Knowledge, Troubleshooting, and Documentation code, synthetic fixtures, lane harness, tests, and proposed `0.1.0-proposed` contracts are present in merged PR #2. Their presence is not the same as project approval or acceptance.
- `docs/lanes/shawn/SHAWN-LANE-DESIGN.md` reports 97 tests and 12 lane scenarios passing under Python 3.12. The project targets Python 3.13; this report has not been independently reproduced here. PR #2 shows no GitHub review entries or status checks.
- The Shawn lane design still contains a pre-merge statement that no PR exists. Shawn should correct that lane-owned handoff record before its acceptance review; this plan does not edit Shawn-owned functionality or design.
- Manny's Coordinator, Triage, and Escalation agents and the end-to-end orchestrator are not present yet. Shawn's `lane_harness.py` is a lane harness with Triage/Escalation stand-ins, not the production Coordinator or integrated MAO runtime.
- The cross-lane contracts remain proposals. Their six open questions are listed in `docs/contracts/HANDOFF-CONTRACTS.md`; blackboard storage and lifecycle are deferred under D-07.
- The prototype remains synthetic-only, deterministic unless a model is later approved, read-only with respect to company systems, and human-reviewed. No real tickets, PHI, credentials, private CDIT documents, Salesforce, outbound alerts, or production authentication are in scope.

## Ownership and PRD checkpoint mapping

| PRD checkpoint | Agent or role | Lane | Phase responsibility |
| --- | --- | --- | --- |
| A0 — Intake boundary | Coordinator | Manny | Actor/scope/schema boundary; stop before dispatch on invalid or unauthorized input. |
| A1 — Injection and minimization | Coordinator/input guard plus each receiving agent's owned boundary | Manny for coordinator; Shawn for Knowledge/Troubleshooting/Documentation inputs | Treat all external and stored content as untrusted; minimize, flag, exclude, and safely stop. |
| A2 — Triage handoff | Triage | Manny | Policy-grounded classification, missing facts, evidence, confidence, and uncertainty. |
| A3 — Retrieval handoff | Knowledge | Shawn | Approved/current source selection, provenance, conflict handling, abstention, and retrieved-text risk flags. |
| A4 — Troubleshooting boundary | Troubleshooting | Shawn | Supported Tier 1 suggestions only; enforce allowlists and stop conditions. |
| A5 — Escalation decision | Escalation | Manny | Deterministic must-escalate triggers and evidence-backed human handoff. |
| A6 — Draft assembly and review | Documentation | Shawn | Draft from verified facts and cited evidence; privacy/output checks and manual fallback. |
| A7 — Human disposition | Authorized human staff | Human role, not an agent | Human retains approval, customer communication, closure, and system action authority. |

The checkpoints A0–A7 are per-run workflow gates. The phases below are project work stages. No priority labels are added because the PRD's A-labels identify checkpoints, not P0/P1/P2 priorities.

## Phases and exit gates

### Phase 0 — Authorize and baseline the build

**Lead:** Project lead. **Supporting:** Manny, Shawn, Shared Lane.

**Work:** Confirm the implementation phase and synthetic-only boundary in writing. Confirm the six-agent ownership split. Decide whether Shawn's current proposal is accepted for review or returned for owner changes. Reconcile stale status text in the Shawn lane handoff through Shawn. Identify which deferred decisions are needed now and which can remain explicitly deferred.

**Exit gate:** Project-lead phase authorization is recorded; owner responsibilities and acceptance authority are clear; no unresolved decision is silently treated as policy. If authorization is not given, keep this plan and the current code as review material only.

### Phase 1 — Freeze interfaces and write the harness acceptance plan

**Lead:** Shared Lane. **Contributors:** Manny and Shawn define their sides; neither changes the other's internals.

**Work:** Review `HANDOFF-CONTRACTS.md` v0.1.0-proposed against PRD blackboard and handoff requirements. Resolve or explicitly defer its six open interface questions: verified case-fact shape, acknowledgment representation, Escalation re-check after Troubleshooting signals, controlled product-area vocabulary, policy-version ownership, and contract-version promotion. Decide D-07 state storage/versioning/retention needed for the prototype; specify immutable contributions, acknowledgment, stale-write rejection, and safe recovery before coding shared state. Freeze fixture identifiers, policy/source versions, output schemas, and handoff acknowledgments.

Adapt the Agent Harness plan into this project before evaluations: map each assertion to A0–A7 and synthetic fixtures; write expected behavior before running cases; separate agent-unit tests, lane-harness tests, and integrated orchestration checks. Record observable trace fields, privacy limits, retry/turn budgets, and what the runtime cannot report.

**Exit gate:** Both lanes acknowledge one versioned contract; scope and state lifecycle are decided or documented as a blocker; acceptance cases and expected outputs are reviewed; test commands target Python 3.13. Do not start cross-lane wiring against a still-proposed contract.

### Phase 2 — Review and validate Shawn's existing agents

**Owner:** Shawn's lane. **Reviewer:** Shared Lane for interfaces; project-designated reviewer for acceptance.

**Work:** Review the merged Knowledge, Troubleshooting, and Documentation implementation against PRD A3/A4/A6, approved scope, frozen contracts, and its own design notes. Correct the pre-merge status text in Shawn's lane record. Run the existing tests and 12 synthetic lane cases on Python 3.13; check retrieval citations/current-source rules, abstention and conflict behavior, Tier 1 allowlists, privacy suppression, factual labels, manual fallback, and version/acknowledgment gates. Record failures and fixes in Shawn's lane only.

**Prospective validation commands (not run in this planning task):** `.\.venv\Scripts\python.exe -m pip install -e ".[dev]"`; `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`; `.\.venv\Scripts\python.exe -m cdit_support_mao.lane_harness synthetic_data/cases`.

**Exit gate:** Python 3.13 results and per-agent evidence are recorded; all findings are resolved or explicitly block acceptance; Shared Lane accepts or returns the proposed contracts; project lead records acceptance. Existing Python 3.12 results remain historical evidence, not a substitute.

### Phase 3 — Build Manny's Coordinator, Triage, and Escalation agents

**Owner:** Manny's lane. **Dependency:** Phase 0 authorization and Phase 1 accepted interfaces/fixtures.

**Work:** Implement Coordinator A0/A1 orchestration boundary, run/case identity and stage ownership, minimized context, stop states, and bounded recovery; Triage A2 policy-cited classifications with claim-level evidence/confidence/unknowns; and Escalation A5 deterministic must-escalate rules, trigger evidence, unresolved questions, and human routing. Keep tools local and read-only. Do not build writes, external alerts, production authentication, or a second-reviewer agent. Work only in Manny's owned functionality; expose the agreed versioned handoff contracts.

**Exit gate:** Each owned agent has its own PRD-mapped tests, schema and policy checks, factuality/abstention checks, failure/stop behavior, and owner-reviewed evidence. No cross-lane edits to Shawn agent internals.

### Phase 4 — Enforce and evaluate injection-risk controls

**Owners:** Each lane for its own agent boundaries; Shared Lane for connector integrity and cross-lane evaluation.

**Trust-boundary map:** ticket/request fields and attachments → intake validation/minimization → agent context → retrieved knowledge/policy → handoff/shared state → any local tool dispatch → tool result → structured output/draft → human review. Stored records, metadata, contract examples, and other agents' text remain untrusted data; they never grant authority.

**Work:** Use deterministic code and schemas for field/type/size/identity/version validation, fixed tool allowlists and authorization, output validation, minimal/redacted traces, and safe stop behavior. Keep injection scanners as risk signals, not proofs. Preserve legitimate Unicode and benign quoted instructions. Add synthetic direct and indirect injection, retrieved-source and attachment injection, keyword-free and multilingual variants, exfiltration/tool-misuse asks, forged acknowledgment/ownership records, replayed state, false action-completion claims, and positive benign controls. Verify rejected raw content is excluded from agent context/logs and unauthorized dispatch/effects remain zero. Distinguish prompt injection from SQL/command injection; never execute model or fixture text as SQL, shell, or arbitrary URLs.

**Exit gate:** Owner-authored adversarial cases and expected outcomes exist before execution; every agent and connector boundary has an enforced control and observable result; no unsupported claim of universal detection; critical disclosure, permission, fabricated citation, or bypass failures block progression.

### Phase 5 — Build the shared harness and integrate the MAO

**Lead:** Shared Lane for connectors and end-to-end harness. **Agent owners:** implement only their own agents' sides; Manny owns Coordinator orchestration.

**Work:** Keep Shawn's lane harness as a component/lane harness. Add the shared integration harness around the approved coordinator/runtime and contract. Connect direct pipeline and only the PRD-approved parallel branch after triage (Knowledge retrieval and deterministic Escalation check); Troubleshooting waits for required validated evidence; Documentation runs after reconciliation; A7 pauses at the human reviewer. Do not add the optional second reviewer unless separately approved. Implement coordinator-owned case-scoped versioned state only after Phase 1's D-07 decision. Verify sender/receiver acknowledgment, run/case/policy/source versions, provenance and uncertainty preservation, and no duplicate or stale result acceptance.

Exercise missing/rejected/unacknowledged handoffs, blocked/abstained upstream, stale versions, conflicts, duplicate delivery, timeout/budget exhaustion, cancellation, coordinator failure/reassignment, late results, pause/resume, and bounded-loop recovery. A connection defect returns to the connector owner; agent-internal failures return to that agent's owner.

**Exit gate:** Direct and permitted parallel paths pass contract-level assertions; state and handoffs are version-safe; every stop routes to the defined human/manual fallback; tests prove no bypass, lost uncertainty, duplicate accepted result, or forbidden write.

### Phase 6 — Independent acceptance and phase close

**Lead:** Project-designated REVIEWER; SECURITY reviews the injection/data boundary; owners respond to findings in their lanes.

**Work:** Review requirement-to-test coverage for A0–A7; per-agent and end-to-end confidence/factuality, source attribution, abstention, role boundaries, injection, privacy, traces, recovery, and human disposition. Confirm results on Python 3.13 and synthetic data only. Record remaining decisions, limitations, evidence links, and checklist status. Route findings back to the appropriate owner; do not self-certify from the implementation summary.

**Exit gate:** PRD P0/safety requirements have reviewed evidence or explicit project-lead deferral; critical unsupported claims, false citations, unsafe non-abstention, injection bypass, sensitive-data disclosure, or permission escalation are zero in the approved must-pass set; the project lead explicitly decides next phase. This gate does not authorize merge to `main` or production use.

## Hand-off and progress rules

- After Phase 1, Manny and Shawn can work in parallel on their own agents and tests. Shared Lane owns only contract/schema/routing connections and integrated checks.
- Each handoff carries artifact and version, owner, completed behavior, evidence, assumptions, unknowns, failure/stop state, and requested decision. Receiver acknowledges or returns the mismatch to the responsible owner.
- Track project phase gates in `Checklist.md`; track agent checkpoints A0–A7 inside the runtime/test cases. Never treat one as the other.
- Preserve the PRD's Nov 11, 2026 planning decision deadline; do not compress build, security, or review gates to meet it.
- Keep all work on the existing Manny, Shawn, and developer branches. Use PRs into developer; do not merge to main until completion and explicit project-lead release authorization.

## Open blockers before implementation

1. Project-lead authorization for work beyond the foundation scaffold.
2. Shared Lane acceptance of `0.1.0-proposed` contracts and resolution of required contract questions.
3. D-07 blackboard storage/version/retention decision for integration.
4. PRD decisions D-01–D-04 and D-08–D-10 wherever the chosen prototype behavior depends on them; keep writes, customer messages, authentication and external systems out of scope while unresolved.
5. Python 3.13 test evidence for Shawn's merged implementation and correction of its stale lane status.
6. Confirmed reviewer/security review and synthetic must-pass evaluation criteria.
