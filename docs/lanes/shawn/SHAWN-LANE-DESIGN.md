# Shawn's Lane — Knowledge, Troubleshooting, Documentation Agents

**Branch:** `shawn/knowledge-troubleshooting-docs`
**Owner:** Shawn (finalized six-agent split, `docs/planning/TASK-SPLIT.md`)
**Version:** agents `0.1.0`; contracts `0.1.0-proposed`
**Status:** Implemented on synthetic data and pushed to the lane branch for team review. Not merged into `developer`; no PR opened yet.

## 1. Authorization and scope

- On 2026-11-04 Shawn, the lane owner, directed this implementation in a working session.
- `Checklist.md` still has "Project lead authorizes any expansion beyond the local scaffold before that work begins" unchecked. **Project-lead confirmation of this phase is requested** (recorded in `docs/planning/DEFERRED-DECISIONS.md`). Until then, treat this work as a reviewable proposal.
- Inside scope: Shawn-owned agent behaviour for Knowledge (A3), Troubleshooting (A4), and Documentation (A6). Also a synthetic knowledge set and troubleshooting policy, proposed handoff contracts, tests, and a lane-only validation harness.
- Outside scope, not touched: the Coordinator, Triage, and Escalation agents (Manny's Lane), the API routes in `main.py`, authentication, database schemas, model-provider integration, Salesforce, outbound messages, real or CDIT data.
- **No language model is used.** No model provider is approved (D-12), so all three agents are deterministic and extractive. They quote approved text verbatim and never generate product guidance. This removes fabricated claims by construction. A model adapter remains future work and needs approval.

## 2. Components

| Path | Purpose |
| :--- | :--- |
| `src/cdit_support_mao/contracts/` | Proposed v0.1 envelope, claim labels, bands, reason codes, and handoff payloads ([HANDOFF-CONTRACTS.md](../../contracts/HANDOFF-CONTRACTS.md)). |
| `src/cdit_support_mao/agents/_gates.py` | Receiving-side input gates: context match, acknowledgment, blocked upstream, provenance chain. |
| `src/cdit_support_mao/agents/knowledge/` | Corpus loader (fails closed; synthetic-only), BM25 lexical index, retrieved-text injection scanner, Knowledge agent. |
| `src/cdit_support_mao/agents/troubleshooting/` | Versioned Tier 1 policy loader and Troubleshooting agent. |
| `src/cdit_support_mao/agents/documentation/` | Privacy scanner and Documentation agent. |
| `src/cdit_support_mao/lane_harness.py` | Lane validation harness and CLI. **Not the coordinator.** It builds labelled Triage and Escalation stand-ins from case files. |
| `synthetic_data/knowledge/` | 11 synthetic KB article versions (see §6). |
| `synthetic_data/policy/troubleshooting-policy_v0.1.0.json` | Synthetic Tier 1 action allowlist, staff-only and forbidden action types, request rules, stop conditions. |
| `synthetic_data/cases/` | 12 synthetic lane cases, each with its expected outcome written before the run. |
| `tests/` | 97 focused tests. |

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

Run from the repository root:

```text
py -3.12 -m pytest -q -p no:cacheprovider
97 passed in under 1 second

PYTHONPATH=src py -3.12 -m cdit_support_mao.lane_harness synthetic_data/cases
12 passed, 0 failed
```

- **Python version.** The project targets Python 3.13. This machine only has Python 3.12.0, and 3.13 was not installed. Tests ran on 3.12 using pydantic 2.13.4 and pytest 9.1.1, with `pythonpath=src` from `pyproject.toml`. Re-run on 3.13 after `python -m pip install -e ".[dev]"`.
- **FastAPI.** FastAPI is not installed for 3.12 here. The scaffold `/health` route was not exercised, and these agents do not import FastAPI.
- **Isolation.** A static test asserts that the agent packages import no network or process modules.

## 8. Known limitations

- Lexical retrieval misses paraphrases and synonyms. A long, chatty `case_summary` lowers coverage and causes abstention, which is safe but can be over-cautious. Triage should send a minimized summary. Replacing or augmenting retrieval needs evaluation and a decision.
- Injection, request, and privacy patterns are regex risk signals tuned on synthetic text. They are a backstop, not a guarantee. Real PHI must never enter the prototype.
- Confidence thresholds are uncalibrated (D-08). The knowledge set has 11 articles, too small for calibration.
- Triage and Escalation inputs are stand-ins until Manny's Lane delivers its agents and the contracts are agreed.
- Nothing is persisted. Blackboard storage (D-07) and audit events (D-10) are proposals only (§9).

## 9. Proposals for Shawn-owned deferred decisions (not decided)

- **D-07 Blackboard storage.**
  - SQLite table `contributions(contribution_id PK, run_id, case_id, case_version, stage, contract_version, status, created_at, payload_json)`, insert-only with no updates.
  - Acknowledgments in a separate `acknowledgments(contribution_id, acknowledged_by, acknowledged_at)` table.
  - Retention and access controls remain open.
- **D-08 Calibration.**
  - Label at least 100 held-out synthetic cases for relevance and correctness.
  - Report accuracy per band, plus abstention precision and recall.
  - Adjust the 0.60/0.85 cut-offs only from that report. Bands stay qualitative until then.
- **D-10 Timestamps and audit.**
  - UTC ISO-8601 with microseconds from the host clock in the prototype.
  - Audit fields: run, case, contribution ID, stage, status, reason codes, and source/policy versions. No ticket text in audit events.

## 10. Handoff record

- **Artifacts and versions:**
  - Agents `0.1.0`.
  - Contracts `0.1.0-proposed`.
  - Source set `SRC-9FC8AF62B4B8`.
  - Troubleshooting policy `SYN-TS-POLICY 0.1.0` (proposed).
- **Completed:** the three Shawn-owned agents, their gates, synthetic data, harness, tests, and contract proposal with examples.
- **Evidence:** §7, plus `docs/contracts/examples/`.
- **Assumptions:**
  - Triage supplies the minimized summary, per-field verification flags, and acknowledgment IDs.
  - Escalation consumes `escalation_signals`.
  - Synthetic policy values stand in for CDIT policy (D-01 to D-04).
- **Open questions:** see `HANDOFF-CONTRACTS.md` §5.
- **Requested decisions:**
  1. Project-lead confirmation of this implementation phase.
  2. Shared Lane review of the v0.1 contracts.
  3. Manny's Lane acknowledgment of the Triage and Escalation fields Shawn's agents read.
