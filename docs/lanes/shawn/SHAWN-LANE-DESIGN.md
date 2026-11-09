# Shawn's Lane — Knowledge, Troubleshooting, Documentation Agents

**Branch:** `shawn/knowledge-troubleshooting-docs`
**Owner:** Shawn (finalized six-agent split, `docs/planning/TASK-SPLIT.md`)
**Version:** Knowledge `0.3.0`, Troubleshooting `0.2.0`, Documentation `0.2.1`; contracts `0.1.0-proposed` with S-1, S-2, and S-1.1 (item scope `0.2-proposed`)
**Status:** Implemented on synthetic data and merged into `developer` through PRs #2, #4, #5, #7, and #8 (2026-11-04 and 2026-11-05). Manny's combined six-agent harness runs these agents with his Coordinator, Triage, and Escalation agents. Linked-item support (shared drafts S-1 and S-2; Shawn changes K-1 to K-7) is on the lane branch, pending review (2026-11-06; [A2-ITEM-HANDOFF-RECEIVER-REVIEW.md](A2-ITEM-HANDOFF-RECEIVER-REVIEW.md) §8).

## 1. Authorization and scope

- On 2026-11-04 Shawn, the lane owner, directed this implementation in a working session.
- `Checklist.md` now marks the project-lead authorization of this phase and the per-agent acceptance items as done. Manny's 2026-11-05 integration commits made that update. The agent charters and contracts are still `proposed`, and team-wide review of PRD-v3 is pending.
- Inside scope: Shawn-owned agent behaviour for Knowledge (A3), Troubleshooting (A4), and Documentation (A6). Also a synthetic knowledge set and troubleshooting policy, proposed handoff contracts, tests, and a lane-only validation harness.
- Outside scope, not touched: the Coordinator, Triage, and Escalation agents (Manny's Lane), the API routes in `main.py`, authentication, database schemas, model-provider integration, Salesforce, outbound messages, real or CDIT data.
- **No language model is used.** No model provider is approved (D-12), so all three agents are deterministic and extractive. They quote approved text verbatim and never generate product guidance. This removes fabricated claims by construction. A model adapter remains future work and needs approval.

## 2. Components

| Path | Purpose |
| :--- | :--- |
| `src/cdit_support_mao/contracts/` | Proposed v0.1 envelope, claim labels, bands, reason codes, and handoff payloads ([HANDOFF-CONTRACTS.md](../../contracts/HANDOFF-CONTRACTS.md)). |
| `src/cdit_support_mao/agents/_gates.py` | Receiving-side input gates: context match, acknowledgment, blocked upstream, provenance chain by ID and content digest, linked-item eligibility, same-item joins, and the Auditor hold. |
| `src/cdit_support_mao/agents/knowledge/` | Corpus loader (fails closed; synthetic-only), BM25 lexical index, retrieved-text injection scanner, Knowledge agent. |
| `src/cdit_support_mao/agents/troubleshooting/` | Versioned Tier 1 policy loader and Troubleshooting agent. |
| `src/cdit_support_mao/agents/documentation/` | Privacy scanner and Documentation agent. |
| `src/cdit_support_mao/lane_harness.py` | Lane validation harness and CLI. **Not the coordinator.** It builds labelled Triage and Escalation stand-ins from case files and times each lane agent call. |
| `src/cdit_support_mao/lane_calibration.py` | Calibration runner and CLI that produces lane evidence for D-08: band accuracy, abstention, cut-off sweep, retrieval recall@k, source exclusions, and a critical safety gate over every case (§9). |
| `docs/lanes/shawn/AGENT-CHARTERS.md` | Per-agent charters: role, inputs, outputs, forbidden actions, stop rules (N-03). Accepted with the schemas as the behaviour specification (Q-04); the prompt drafts are not runtime prompts. |
| `synthetic_data/knowledge/` | 38 synthetic KB article versions (see §6 and `synthetic_data/README.md`). |
| `synthetic_data/policy/troubleshooting-policy_v0.1.2.json` | Synthetic Tier 1 action allowlist, staff-only and forbidden action types, request rules, stop conditions. 0.1.2 adds the privilege-escalation flag to RR-06; `_v0.1.1.json` stays for callers that still name it. |
| `synthetic_data/cases/` | 12 synthetic lane cases, each with its expected outcome written before the run. |
| `synthetic_data/item_cases/` | 5 synthetic linked-item cases (two items of one parent, an item held for the Auditor, an ambiguous parent, instruction-like item text). Kept apart so Manny's evaluation set is unchanged. |
| `synthetic_data/calibration/` | Held-out calibration set `SYN-KCAL` v1.0: 111 cases with draft labels, written before the first run and not yet human-approved. |
| `docs/lanes/shawn/calibration/` | Generated calibration report and per-case results. |
| `tests/` | 175 tests in the lane's test files, including one Escalation contract test Manny added to `test_contracts.py` and 43 linked-item tests in `test_item_scope.py`. The full project suite has 567. |

## 3. Knowledge agent (A3 — retrieval handoff)

1. **Input gate.** Triage must be `completed`, acknowledged, and in the current `RunContext`. Otherwise the result is `blocked` and no retrieval runs.
2. **Retrieve.** BM25 over every article section (title, heading, text, keywords, step text). The triage `case_summary` is used only as a bag of query terms. Instructions in ticket text therefore cannot change behaviour.
3. **Evidence strength.** `relevance` is the IDF-weighted share of query terms found in a section, banded with the provisional PRD thresholds. A candidate needs relevance ≥ 0.60 and at least 2 matched terms.
4. **Eligibility.** Only `approved` articles within `effective_date ≤ as_of ≤ review_due` may ground guidance. Draft, retired, stale, and not-yet-effective matches are listed in `excluded_sources` (IDs and reason only).
5. **Product area.** Prefer sources in the triage `product_area`. If the only evidence is outside it, the result says so in `unknowns`.
6. **Injection.** Scan the selected sections, including steps and stop conditions, for instruction-like text. Any hit means abstain (`retrieved_injection`). Flags hold pattern IDs, never the injected text.
7. **Conflicts.** Two approved, current documents on the same topic (`conflicting_sources`), or two approved versions of one document (`multiple_approved_versions`), mean abstain. Both sources are cited and neither is chosen.
8. **Output.** Up to 3 passages, verbatim, marked `untrusted_evidence`. Each carries verified metadata claims and inferred relevance claims. Confidence is the top passage's band.

## 4. Troubleshooting agent (A4 — troubleshooting boundary)

1. **Input gate.** Same checks as Knowledge, plus the Knowledge result must have been built from the same Triage contribution.
2. **Restricted requests** in the untrusted summary are matched against policy rules. Blocking rules mean no steps plus escalation signals: bulk account actions, cross-site data, policy override, clinical or eligibility questions. Flag rules (password reset, access change) are recorded in `rejected` ("the assistant will not do this") but still allow approved self-service guidance.
   - **Quoted text (policy 0.1.1, PRD-v3 fixture F-10).** A rule marked `quoted_match: signal_only` treats a match as quoted case data when every match lies inside quotation marks, for example a training example quoting "ignore policy".
     - Such a match is not rejected. The agent records an inference claim, an unknown, and a `quoted_<signal>` escalation signal so a human still sees it.
     - Only RR-03 (policy override) opts in. Unquoted matches and matches that cross a quote boundary still block.
     - Other request rules and all stop conditions ignore quotes, so a quoted "suspicious login" still halts.
     - Residual risk: a customer's own override request quoted in full by Triage is downgraded to a signal. The agent has no tools, and the signal keeps the request visible to Escalation and the human reviewer.
3. **Policy stop conditions:**
   - Access or identity concerns are flagged and only collection steps are allowed.
   - Privacy and security concerns halt all routine steps.
4. **Knowledge abstained** means abstain, with an `insufficient_approved_evidence` signal.
5. **Steps** come only from the top passage and keep their order and wording. Each action type is classified by the policy:
   - `tier1` steps are suggested.
   - `staff_only` steps go to `staff_only_procedures`.
   - `forbidden` or unknown action types mean the whole guidance is rejected, because partial procedures are unsafe. This raises a `guidance_step_outside_tier1` signal.
6. **Information needed:** knowledge items not already verified in the case facts, plus triage-reported gaps with triage provenance.
7. **Confidence** is never higher than the Knowledge confidence. An output check asserts that no suggested step escaped the Tier 1 allowlist.

## 5. Documentation agent (A6 — draft assembly)

1. **Gate.** All four upstream inputs (Triage, Knowledge, Troubleshooting, Escalation) must be present, current, acknowledged, chained, and not blocked. Otherwise the result is `blocked` with a `manual_fallback`. Abstained upstream results are still documented, because "no approved guidance" is a valid factual record.
2. **Note sections**, every line labelled:

   | Section | Label |
   | :--- | :--- |
   | Case facts | Verified fields only |
   | Triage proposal | Inference |
   | Approved guidance consulted | Verified citations, or unknown |
   | Suggested Tier 1 steps (not performed) | Verified, quoted |
   | Steps reserved for authorized staff | Verified, quoted |
   | Actions taken | Staff-recorded, verified only |
   | Information still needed | Unknown |
   | Stop conditions and escalation | Inference / verified |
   | Unverified or unresolved | Unknown |

3. **Privacy.** Every line and the final rendered text are scanned for PHI-like or credential-like strings. A hit suppresses the draft. Findings store category and location only; the value is never stored.
4. **Banner and IDs.** The banner states the draft is not saved, not sent, and changed no ticket state. `draft_id` is deterministic, so retries are idempotent. `save_reviewed_result` is not implemented (disabled until approved).

## 6. Synthetic evaluation set

| Case | What it proves | Result |
| :--- | :--- | :--- |
| 01 Golden report export | Cited, verbatim, allowlisted steps; retired v1.0 excluded | K, T, D completed |
| 02 Access after role change | No access change advised; staff-only steps separated; access signals | completed, 2 steps + 2 staff-only |
| 03 Adversarial override | Untrusted text cannot widen tools; restricted requests rejected; escalation signals | K, T abstained; D documents escalation |
| 04 Conflicting upload limits | Conflict preserved, not resolved; no "25 MB / 50 MB" claim | abstained |
| 05 Stale source only | Stale article never used | abstained |
| 06 Injection in retrieved source | Indirect injection → abstain; injected text never echoed | abstained |
| 07 PHI-like value in facts | Draft suppressed; value absent from all output | D blocked |
| 08 Session loop + staff action | Only verified staff actions shown as performed | completed |
| 09 Forbidden step in guidance | `modify_account` step rejected; whole guidance rejected | T abstained |
| 10 Password self-service | Reset request flagged; only self-service steps | completed |
| 11 Cross-site data exposure | Privacy stop halts routine steps | T abstained |
| 12 Triage blocked | Downstream agents refuse to run | all blocked |

## 7. Validation evidence (2026-11-04)

Run from the repository root in the project `.venv` (Python 3.13.17, pydantic 2.14.2, pytest 9.2.0, FastAPI 0.162.0, uvicorn 0.54.0), installed with `python -m pip install -e ".[dev]"`:

```text
python -m pytest -q -p no:cacheprovider
125 passed

python -m cdit_support_mao.lane_harness synthetic_data/cases
12 passed, 0 failed

python -m cdit_support_mao.lane_calibration synthetic_data/calibration/knowledge-calibration-v1.json
111 cases | answered 54 | accuracy 96.3% | coverage 74.3% | abstention recall 95.1% | critical errors 0 | label problems 0

python -m cdit_support_mao.lane_calibration synthetic_data/calibration/knowledge-calibration-v2.json --knowledge-dir synthetic_data/knowledge
65 cases | answered 28 | accuracy 92.9% | coverage 53.1% | abstention recall 93.8% | critical errors 0 | label problems 0

uvicorn cdit_support_mao.main:app --app-dir src  ->  GET /health  200 {"status":"ok","database":"ok"}
```

- **Python versions.** The suite also passes on Python 3.12.0 (125 passed).
- **Quoted-instruction fix (B-01).** Troubleshooting 0.1.1 with policy 0.1.1 adds 15 tests: benign quotes, unquoted and boundary-crossing overrides, other rules, stop conditions, and quote detection. The 12 lane cases and all 111 calibration cases keep their outcomes; only version fields changed in the report and examples.
- **Corpus growth.** The knowledge set grew from 11 to 38 article versions for calibration. All 12 lane cases kept their expected outcomes without any agent change. Contract examples were regenerated for the new source set.
- **Isolation.** A static test asserts that the agent packages import no network or process modules.
- **Measurement (N-02, 2026-11-05).** Run on Python 3.13.17 after pulling Manny's integration (`developer` at `6bdad27`):

  ```text
  python -m pytest -q
  524 passed

  python -m cdit_support_mao.lane_harness synthetic_data/cases
  12 passed, 0 failed  (plus per-agent duration summary)

  python -m cdit_support_mao.combined_harness synthetic_data/cases
  12 of 12 cases PASS

  python -m cdit_support_mao.lane_calibration synthetic_data/calibration/knowledge-calibration-v1.json
  111 cases | answered 54 | accuracy 96.3% | coverage 74.3% | abstention recall 95.1% | ranking recall@3 100.0% | critical errors 0 | label problems 0
  ```

  - The calibration report adds ranking recall@1/3/5 (98.6% / 100% / 100%), returned recall (74.3%), and exclusions by reason. All 111 case outcomes are unchanged.
  - Both CLIs print the median, p95, and maximum duration per agent. `--timing PATH` writes the calibration timings to JSON. On Shawn's machine the median lane total was about 1 ms per case, with 0 model calls and $0 provider cost.
  - Durations are machine-dependent, so they are kept out of `LaneRun.as_json()`, the committed report, and the results file.

## 8. Known limitations

- Lexical retrieval misses paraphrases and synonyms. The calibration set measures this: 8 of 25 paraphrased cases were answered, and the other 17 abstained safely (§9). Recall@k shows the ranking itself is not the problem: in 16 of those 17 cases the acceptable section was ranked first, but its relevance stayed under the 0.60 gate. A long, chatty `case_summary` also lowers coverage. Triage should send a minimized summary. Replacing or augmenting retrieval needs evaluation and a decision.
- Injection, request, and privacy patterns are regex risk signals tuned on synthetic text. They are a backstop, not a guarantee. Real PHI must never enter the prototype.
- Confidence thresholds are still provisional. Calibration evidence now exists (§9), but adopting new cut-offs is the D-08 decision, which belongs to the evaluation owner (Manny).
- The lane harness and calibration runner still use labelled Triage and Escalation stand-ins, so lane evidence stays independent of Manny's agents. Manny's `combined_harness` runs the same 12 cases through all six agents. The v0.1 contracts are still `proposed`.
- Nothing is persisted. Blackboard storage (D-07) and audit events (D-10) are proposals only (§9).

## 9. Proposals for Shawn-owned deferred decisions (not decided)

- **D-07 Blackboard storage.**
  - SQLite table `contributions(contribution_id PK, run_id, case_id, case_version, stage, contract_version, status, created_at, payload_json)`, insert-only with no updates.
  - Acknowledgments in a separate `acknowledgments(contribution_id, acknowledged_by, acknowledged_at)` table.
  - Retention and access controls remain open.
- **D-08 Calibration (lane evidence only).**
  - Ownership: the 2026-11-04 planning agreements in `DEFERRED-DECISIONS.md` assign D-08 and D-09 to Manny as evaluation owner. Shawn's Lane supplies agent outputs and this evidence; the method, gate, and acceptance follow Manny's protocol.
  - Method, done 2026-11-04:
    - Labelled 111 held-out synthetic cases (`synthetic_data/calibration/`) before the first run: 70 answerable and 41 that should abstain.
    - The labels are drafts written in Shawn's lane with AI assistance. D-09 requires human-approved labels, so a human must review them before the results count toward a gate.
    - The abstain cases cover no coverage, near misses, ineligible-only sources, conflicts, and injection.
    - The runner reports accuracy per band, abstention precision and recall, a reliability table, and cut-off sweeps.
    - Report: [KNOWLEDGE-CALIBRATION-REPORT.md](calibration/KNOWLEDGE-CALIBRATION-REPORT.md).
  - Results:
    - Critical safety gate: 0 errors across all 111 cases.
    - High band: 29/29 correct (95% CI 88–100%).
    - Medium band: 23/25 correct. Both errors are unsupported answers at relevance 0.61 and 0.63, just above the 0.60 cut-off. There were no wrong-source answers.
  - Sweep reading (single author, small sample):
    - Raising the answer cut-off to 0.65 removes both unsupported answers. The cost is coverage of answerable cases, which falls from 74% to 70%.
    - Lowering the high cut-off to 0.75 would still have been 43/43 correct.
  - Proposal, **not decided**:
    - Keep 0.60/0.85 for now.
    - Before adopting 0.65 and 0.75, confirm both on a held-out set written by someone else. Changing them against this set would overfit it. `SYN-KCAL` v2.0 (below) is single-author and measures L-1/L-2 instead, so it does not meet that condition.
    - The bigger gap is paraphrase recall, which is a retrieval design question. No threshold fixes it.
  - Bands stay qualitative until the evaluation owner accepts a report under the D-09 protocol.
  - **`SYN-KCAL` v2.0 baseline (2026-11-09, L-1/L-2).**
    - The set: 65 new cases with labels written before the first run. It uses the runtime corpus, `product_area` null as on the linked-item path, and `as_of` 2026-11-10.
    - Results with the current agent (0 critical errors):

      | Kind | Result |
      | :--- | :--- |
      | Short requests | 18/26 correct, 1 wrong (`SYN-KCAL-1012`, "How do I change study?" answered by `KB-ACC-010`), 7 false abstentions |
      | Padded requests | 2/12 correct |
      | Numeric requests | 1/11 correct |
      | Stale-shadow | 8/9 abstain; 1 unsupported answer (`SYN-KCAL-1075` answered by `KB-NAV-001#s2`), which reproduces L-2 |
      | No coverage | 6/6 abstain |

    - **Main finding:** ranking recall@3 is 95.9%. The right section is usually ranked, but the coverage gate rejects it. L-1 is a gate design problem, not a ranking problem.
    - **How the set is used:** measure one retrieval change against v2.0; any further change needs a new set version.
    - **The change measured on it:** Knowledge `0.3.0` ([L1-IDENTIFIER-TERMS.md](calibration/L1-IDENTIFIER-TERMS.md)) drops identifier tokens from the query. The design and acceptance criteria were fixed before the run.
      - v2.0 correct answers went 21 → 26 (numeric requests 1 → 6), with the same 2 wrong or unsupported answers.
      - v1.0 is unchanged.
      - v2.0 is no longer held out.
    - Report: [KNOWLEDGE-CALIBRATION-REPORT-v2.md](calibration/KNOWLEDGE-CALIBRATION-REPORT-v2.md).
- **D-10 Timestamps and audit.**
  - UTC ISO-8601 with microseconds from the host clock in the prototype.
  - Audit fields: run, case, contribution ID, stage, status, reason codes, and source/policy versions. No ticket text in audit events.

## 10. Handoff record

- **Artifacts and versions:**
  - Knowledge, Troubleshooting, and Documentation agents `0.2.0` (linked-item support, 2026-11-06). Documentation `0.2.1` adds the S-1.1 attention check line (2026-11-08). Knowledge `0.3.0` stops counting identifier tokens as topic terms (L-1, 2026-11-09).
  - Contracts `0.1.0-proposed`, with S-1 (`TriageItemScope`), S-2 (`InputRef.content_digest`), and S-1.1 (`attention_check` and the taxonomy citation; item scope `0.2-proposed`).
  - Source set `SRC-61C4A35E96CF`.
  - Calibration sets `SYN-KCAL` 1.0 and 2.0. 2.0 records the L-1/L-2 baseline (2026-11-09).
  - Troubleshooting policy `SYN-TS-POLICY 0.1.2` (proposed, 2026-11-09). 0.1.1 is kept for callers that still name it.
- **Completed:** the three Shawn-owned agents, their gates, synthetic data, harness, tests, and contract proposal with examples. Also calibration evidence for D-08 (draft labels) and a Python 3.13 / `/health` run.
- **Evidence:** §7, plus `docs/contracts/examples/`.
- **PRD-v3 alignment:** [PRD-V3-ALIGNMENT-REVIEW.md](PRD-V3-ALIGNMENT-REVIEW.md) (2026-11-04, updated 2026-11-05). It lists findings and open questions. B-01 is fixed (§4), N-02 is done (§7), and N-03 is accepted under Q-04 ([AGENT-CHARTERS.md](AGENT-CHARTERS.md)). The other findings are open.
- **Linked items:** [A2-ITEM-HANDOFF-RECEIVER-REVIEW.md](A2-ITEM-HANDOFF-RECEIVER-REVIEW.md) §8 records Manny's answers, the S-1 and S-2 drafts, and K-1 to K-7. Q-E is open.
- **Escalation interface note:** Troubleshooting can emit `quoted_policy_override_attempt`. Manny's Escalation agent routes it to human review (rule 6).
- **Assumptions:**
  - Triage supplies the minimized summary, per-field verification flags, and acknowledgment IDs.
  - Escalation consumes `escalation_signals`.
  - Synthetic policy values stand in for CDIT policy (D-01 to D-04).
- **Open questions:** see `HANDOFF-CONTRACTS.md` §5.
- **Requested decisions:**
  1. Project-lead confirmation of this implementation phase.
  2. Shared Lane review of the v0.1 contracts.
  3. Manny's Lane acknowledgment of the Triage and Escalation fields Shawn's agents read.
