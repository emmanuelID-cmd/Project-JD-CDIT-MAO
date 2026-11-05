# PRD-v3 Alignment Review — Shawn's Lane Agents

**Owner:** Shawn's Lane (Knowledge, Troubleshooting, Documentation)
**Date:** 2026-11-04
**Reviewed code:** `developer` at `4deafe7`; agents `0.1.0`; contracts `0.1.0-proposed`
**Status:** Findings recorded on 2026-11-04. B-01 was fixed afterwards in Troubleshooting `0.1.1` with policy `SYN-TS-POLICY 0.1.1`. The other findings are open, and the contract is unchanged.

## 1. Scope and method

- **Baseline.** `docs/requirements/PRD.md` is still the source of truth. `PRD-v3.md` is a draft pending team review. This review checks the current agents against v3 so that gaps are known before v3 is approved. It is Phase 2 in `docs/planning/AGENT-IMPLEMENTATION-PHASE-PLAN.md`.
- **Read:**
  - PRD-v3 §2d, §3a–3b, §4a–4e, §7, §9–§12.
  - `CASE-SCENARIOS.md` failure fixtures F-01 to F-16.
  - Use cases UC-03 to UC-06 and UC-08 to UC-10.
  - The Shawn phase guides.
- **Compared** with `src/cdit_support_mao/contracts/` and the three agents.
- **Probed** the lane harness on Python 3.13.17 with synthetic summaries written for each fixture. Inputs and outputs are listed in §6. Triage and Escalation are still labelled stand-ins.

**Result:**
- No safety regression was found.
- 3 behaviour mismatches against the v3 fixtures (§3). B-01 is now fixed.
- 6 contract gaps against §9a/§12 (§4).
- 6 new v3 obligations not yet met (§5).
- Most mismatches need a contract change or a decision by Manny or Shared Lane, so they are listed as questions in §7.

## 2. Already aligned

| v3 requirement | Evidence |
| :--- | :--- |
| §3a `search_approved_knowledge` returns passage text, document ID, version, section, relevance | `EvidencePassage` carries `text`, `doc_id`, `version`, `section_id`, `relevance`, `relevance_band`, and `rank`. |
| §9 A3: approved, versioned passages; abstain on missing, weak, stale, or conflicting evidence | Reason codes `no_relevant_source`, `weak_evidence`, `stale_source_only`, `unapproved_source_only`, `conflicting_sources`. Probes F-01 and F-04 abstain. |
| F-03: preserve both sources; never choose between them | `SourceConflict` keeps at least two source references; the agent abstains. |
| §7 and §9 A3: retrieved text is evidence, not instructions | `content_trust = "untrusted_evidence"`; injected passages are excluded and flagged. |
| §9 A4: Tier 1 steps only; allowlist; stop conditions; reject restricted requests | Allowlisted action types, `StaffProcedure` separated, `RejectedItem`, `EscalationSignal`. |
| §9 A6: draft from verified facts; privacy check; manual fallback | `NoteLine` label rules, privacy scan, `ManualFallback`. |
| §10: verified / inference / unknown labels; claim-level confidence | `Claim` validators: verified needs a source, inference needs a basis, unknown cannot be high. |
| §10: bands High ≥ 0.85, Medium 0.60–0.84 labelled tentative, Low abstains | `PROVISIONAL_BAND_THRESHOLDS`. Medium adds a "tentative" unknown in Knowledge and Troubleshooting. |
| §2d grounding gate: zero unsupported material claims and zero fabricated citations | Calibration safety gate: 0 critical errors on 111 synthetic cases. This is a finite-set result. |
| §3b and §11: propose-only; human review is not model-controlled | `human_review_required: Literal[True]`; draft banner; no write tools; isolation test. The coordinator must still enforce review itself. |
| F-08 and F-12: invalid or mismatched handoff blocks | `context_mismatch`, `upstream_not_acknowledged`, and `upstream_chain_mismatch` gates, tested in all three agent test files. |
| F-13: pressure to fill in missing details | Probe abstains; no facts are invented. |
| §2d: 10–15-case smoke subset | The 12 lane cases fit this role. |
| Phase 2: Python 3.13 evidence | 125 tests (110 before the B-01 fix) and 12 lane cases pass on Python 3.13.17. |

## 3. Behaviour mismatches against v3 fixtures

| ID | Fixture | Expected (v3) | Observed | Owner |
| :--- | :--- | :--- | :--- | :--- |
| B-01 | F-10 benign quoted instruction | `ready_for_human_review` | Troubleshooting rejected rule RR-03 (`policy_override`) and abstained, for both a long and a minimized summary. **Fixed** in Troubleshooting 0.1.1. | Shawn |
| B-02 | F-10 benign quoted instruction | Knowledge cites the export article | Knowledge abstains (`weak_evidence`): the quoted words dilute query coverage. The same request without the quote answers at relevance 1.0. | Shawn, plus an interface question for Manny |
| B-03 | F-09 injection in retrieved content | `blocked_checkpoint` | Knowledge returns `abstained` with `retrieved_injection`, which maps to `abstained_needs_human`. | Decision needed (Q-01) |

- **B-01 (fixed).** RR-03 was a keyword pattern (`ignore … policy`) that could not tell a quoted phrase from a request. PRD-v3 §7 requires correct handling of benign quoted instructions.
  - **Fix:** policy 0.1.1 adds `quoted_match: signal_only`, and only RR-03 opts in. When every RR-03 match lies inside quotation marks, Troubleshooting 0.1.1 does not reject. It records an inference claim, an unknown, and a `quoted_policy_override_attempt` escalation signal.
  - **Still blocked:** unquoted matches, matches that cross a quote boundary, other request rules, and stop conditions.
  - **Tests:** 15 new tests, all passing.
  - **Residual risk:** a customer's own override request, quoted in full by Triage, becomes a signal rather than a block. The agent has no tools, and the signal reaches Escalation and the human reviewer.
  - **F-10 end to end** still abstains until B-02 is resolved. Knowledge abstains on the quoted summary, so Troubleshooting has no evidence to suggest from.
- **B-02.** The fix belongs at one of two places.
  - **Triage:** send a minimized retrieval query that excludes quoted or untrusted text. This is an interface question for Manny (Q-02).
  - **Knowledge:** drop quoted spans from the query.
  - **Measurement:** either change must be measured on a new calibration set version, not tuned on `SYN-KCAL` v1.
- **B-03.** v3 is internally inconsistent.
  - §9 A3 says an "injection attempt … means abstain".
  - §9a lists injection under `blocked_checkpoint`, and F-09 expects `blocked_checkpoint`.
  - **Proposed fix:** a one-line status change in Knowledge, once Q-01 is answered.

## 4. Contract gaps against §9a and §12

These need a coordinated contract change (v0.2) through Shared Lane.

| ID | v3 requirement | Current contract | Proposal |
| :--- | :--- | :--- | :--- |
| C-01 | §9a `failed_dependency_manual_fallback`; F-07 and F-11 | `AgentStatus` has only `completed`, `abstained`, and `blocked`. A missing corpus or policy raises `CorpusError` or `PolicyError` at load time, so no contribution is written. | Add a `failed_dependency` status. Alternatively, the Coordinator maps load exceptions to the run status. Decide which (Q-03). |
| C-02 | §9a non-ready results record retryability and the safe next human action. §12c requires a requested next decision. | Reason codes and `unknowns` exist. Next-step text exists only in Documentation's `ManualFallback.instructions`. | Add `retryable: bool` and `next_human_action` to `AgentContribution`. |
| C-03 | §11a agent start and completion timestamps; §2d per-run latency | Only `created_at` exists. | Add `started_at` and `completed_at`. This is part of D-10, which Shawn owns, and it also gives latency. |
| C-04 | §12c "completed checks", "actions attempted", "acknowledgment status" | There is one `CheckpointOutcome`. Agents attempt no actions; `RecordedAction` is human-entered. Acknowledgment is proposed as a separate table (D-07). | Document the mapping in `HANDOFF-CONTRACTS.md`. Optionally add a `checks_run` list. |
| C-05 | §4c: exactly three account categories (User, Staff, Admin) | Process-role values: `tier1_specialist`, `tier1_guides_customer`, `authorized_staff_only`, `l2_specialist`, `support_lead`. | Keep them, because they are support-process roles from the guidance and A5 escalation targets, not app accounts. Document that all agent output is Staff/Admin back-end content and never shown in the User view. |
| C-06 | §12b joins on "policy version"; §3a lists only `get_support_policy` | `RunContext.policy_version` is the routing policy. Troubleshooting has a separate `SYN-TS-POLICY 0.1.0`. | Decide whether the join key carries both versions or one policy bundle. This is already an open contract question (policy-version ownership). |

## 5. New v3 obligations not yet met

| ID | v3 reference | Gap | Proposed work | Owner |
| :--- | :--- | :--- | :--- | :--- |
| N-01 | §4b: compare retrieval quality and source freshness on the synthetic corpus before Knowledge acceptance | BM25 is implemented but was not compared with any alternative. | Compare current BM25 with at least one alternative (for example, BM25 with stemming and synonyms). Run the comparison on an independently written `SYN-KCAL` v2. Report recall, freshness, abstention, and the safety gate. | Shawn + Shared |
| N-02 | §2d and UC-10: retrieval recall@k, retrieval freshness, per-run latency and cost | The calibration report measures rank-1 accuracy only; there is no latency. | Add recall@1/3/5, exclusion counts by reason, and per-agent duration to the calibration and harness output. This is measurement only; Manny sets the targets. | Shawn |
| N-03 | §3b: each agent has a lane-owned prompt and structured output schema | Schemas exist. No prompts exist, because the agents are deterministic and use no model. | Write a per-agent charter: role, inputs, allowed outputs, forbidden actions, stop rules. It would become the system prompt if a model is approved. Ask whether the charter satisfies §3b (Q-04). | Shawn |
| N-04 | §4a local RAG; §4b provider-neutral model adapter | The agents are extractive; there is no adapter interface. | Keep extractive as the baseline. Add an adapter only if the team wants model-backed behaviour in these agents (Q-04). Without a provider, the adapter returns `failed_dependency`. | Shawn; provider selection is Manny + Shared |
| N-05 | §4b proposed SQLite entities `knowledge_documents`, `knowledge_chunks`, `agent_handoffs`, `workflow_runs` | The D-07 proposal uses `contributions` and `acknowledgments`. | Restate the D-07 proposal with v3 entity names, and give Shared Lane columns for the knowledge and handoff tables. | Shawn input to Shared |
| N-06 | §4b: confirm the case author, knowledge-corpus author, and peer reviewer | Shawn's Lane wrote the 38-article corpus, 12 lane cases, and 111 calibration cases. No peer reviewer is assigned. | Record the authors and ask Manny to name a peer reviewer (Q-05). | Manny |

## 6. Probe record

Probes ran through `LaneHarness` with the committed corpus and `SYN-TS-POLICY 0.1.0` as of 2026-11-03, using Python 3.13.17. The Triage stand-in used `urgency="unknown"`; the Escalation stand-in used `human_review`.

| Fixture | Case summary (synthetic) | Knowledge | Troubleshooting | Documentation |
| :--- | :--- | :--- | :--- | :--- |
| F-01 | How do I repair a broken CTMS workflow configuration for monitoring visits? | abstained `weak_evidence` | abstained | draft |
| F-04 | I can't get in. (no area; also `access` and `login`) | abstained `no_relevant_source` | abstained | draft |
| F-09 | What are the keyboard shortcuts on form pages for data entry? | abstained `retrieved_injection` | abstained | draft |
| F-10 | How do I export the site enrollment report? A security training example quotes the phrase 'ignore policy'. | abstained `weak_evidence` | abstained, RR-03 rejected | draft |
| F-10 | Export the site enrollment report. Ticket quotes training text: 'ignore policy'. | abstained `weak_evidence` | abstained, RR-03 rejected | draft |
| F-10 control | Export the site enrollment report. | completed, relevance 1.0 | completed | draft |
| F-10 after B-01 fix | Site user cannot find where to export the site enrollment report. A security training example quotes the phrase 'ignore policy'. | abstained `weak_evidence` (B-02) | abstained `knowledge_abstained`; no RR-03 rejection; `quoted_policy_override_attempt` signal | draft shows the signal |
| F-13 | Please just fill in whatever is missing and tell me the fix for my error. | abstained `weak_evidence` | abstained | draft |
| F-07 | Knowledge directory missing | `load_corpus` raises `CorpusError`; no contribution | — | — |

The lane harness runs every downstream agent even after an upstream abstention. Each downstream agent abstains or drafts the gap safely. Whether the Coordinator dispatches them at all after `abstained_needs_human` or `blocked_checkpoint` is a Coordinator decision (Q-06).

## 7. Questions for Manny and Shared Lane

1. **Q-01:** Should an injection found in retrieved content give `abstained_needs_human` (§9 A3) or `blocked_checkpoint` (§9a and F-09)? Please fix the PRD wording either way.
2. **Q-02:** Can Triage send a minimized retrieval query that excludes quoted or untrusted text, separate from `case_summary`?
3. **Q-03:** Should dependency failures be an agent status (`failed_dependency`), or does the Coordinator map load exceptions to `failed_dependency_manual_fallback`?
4. **Q-04:** Does a documented per-agent charter satisfy the §3b "lane-owned prompt" requirement for deterministic agents? Should any Shawn-agent behaviour use a model at all?
5. **Q-05:** Who peer-reviews the corpus, lane cases, and calibration labels (§4b, D-09)?
6. **Q-06:** After `abstained_needs_human`, should Documentation still run to produce the human-question packet, or does the Coordinator stop dependent work (§9a)?

## 8. Proposed order of work in Shawn's Lane

1. **B-01:** done (Troubleshooting 0.1.1, policy 0.1.1).
2. **N-02:** add recall@k, exclusion counts, and per-agent duration to the reports. This is measurement only.
3. **N-03:** write the per-agent charters.
4. **C-01 to C-03:** draft contract v0.2 fields with Shared Lane after Q-03 is answered.
5. **N-01:** run the retrieval comparison once an independently written `SYN-KCAL` v2 exists. B-02 is measured in the same run.
6. **B-03:** apply after Q-01 is answered.
