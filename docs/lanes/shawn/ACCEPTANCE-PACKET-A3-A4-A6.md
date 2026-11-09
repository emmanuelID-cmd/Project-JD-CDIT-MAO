# Acceptance evidence: Knowledge (A3), Troubleshooting (A4), Documentation (A6)

**Status:** Shawn's Lane evidence for the open `Checklist.md` item *"Review and accept each agent against PRD A3/A4/A6 and the approved shared contract"*, 2026-11-09, at `developer` `fa6b14f`. **This is evidence, not acceptance**: the reviewer (Manny or the project lead) decides. Requirements source: [PRD-v4](../../requirements/PRD-v4.md) (approved 2026-11-08).

## 1. Summary

| Item | Value |
| :--- | :--- |
| Agents | Knowledge `0.4.0` (updated 2026-11-09, after this packet was first written; see [L1-L2-BATCH-2.md](calibration/L1-L2-BATCH-2.md)); Troubleshooting `0.2.0` with policy `SYN-TS-POLICY 0.1.2` (proposed); Documentation `0.2.1` |
| Contracts | `0.1.0-proposed` with S-1 (linked items), S-2 (input digests), and S-1.1 (item scope `0.2-proposed`). S-1.1 was approved by Manny on 2026-11-08. |
| Design | Deterministic agents with no model calls. Per Q-04 (2026-11-05), each agent's charter plus its structured output schema satisfies PRD §3b ([AGENT-CHARTERS.md](AGENT-CHARTERS.md)). |
| Tests | Full suite 744 passed with Knowledge `0.4.0` (731 at `fa6b14f`). Knowledge 24, Troubleshooting 36, Documentation 8, linked items 78, contracts 19. |
| Lane cases | 12/12 synthetic lane cases pass: golden, edge, adversarial, conflict, stale, injection, privacy, governance, and upstream stop. |
| Integration | Manny's connected-path tests (11) and combined-workflow tests (9) pass with these agents. |
| Calibration | `SYN-KCAL` v1.0 (111 cases), v2.0 (65), and v3.0 (59), each with 0 critical safety errors. The labels are drafts (D-09). |

**Proposed decision:** accept A3, A4, and A6 for the **synthetic prototype**, with the limitations in §5 recorded. This is not an evaluation result: the 100-case evaluation, with approved labels and scoring, is a separate gate owned by Manny.

## 2. Knowledge (A3)

| PRD-v4 requirement | Status | Evidence |
| :--- | :--- | :--- |
| §9 A3: return only approved, versioned passages with source IDs, sections, and relevance | Met | Passages carry the document, version, section, relevance, and band, quoted verbatim. Tests: `test_golden_returns_current_approved_source_with_citations` and `test_every_returned_passage_is_eligible_on_as_of`. The calibration safety gate requires every citation to exist and be eligible: 0 errors on v1 and v2. |
| §9 A3: treat retrieved instructions as untrusted evidence | Met | `test_injection_in_retrieved_source_abstains_without_echoing_text`; lane case 6; evaluation-draft case 096 abstains with `retrieved_injection`. |
| §9 A3 stop: no relevant source, stale or conflicting versions, an injection attempt, or weak evidence means abstain | Met | `test_abstains_without_current_relevant_approved_evidence`, `test_not_yet_effective_source_is_excluded`, `test_conflicting_approved_sources_abstain_and_preserve_both`, `test_multiple_approved_versions_of_one_document_abstain`; lane cases 4, 5, and 6. |
| §7: ticket text cannot change policy or widen results | Met | `test_instructions_in_ticket_text_cannot_widen_results`. The query is the item text only (K-3): `test_item_query_is_the_item_text_only`, `test_instruction_like_item_text_is_only_a_query`. |
| §10: claims labelled verified, inference, or unknown; band derived from evidence; thresholds provisional | Met | Claim validators (`test_verified_claim_requires_source`, `test_inference_requires_basis_and_unknown_cannot_be_high`). The band comes from the top passage's coverage (0.60/0.85, D-08). |
| §10: calibrate on held-out synthetic cases | Partial | v1.0 and v2.0 evidence exists ([report](calibration/KNOWLEDGE-CALIBRATION-REPORT.md), [v2 report](calibration/KNOWLEDGE-CALIBRATION-REPORT-v2.md)). Label approval (D-09) and threshold decisions (D-08) belong to Manny. |
| §4f P0: no fabricated citations or unsupported material claims | Met for citations; open risk for off-topic answers | No fabricated citations: every citation is a real, eligible section. A few answers come from an off-topic section, at medium band, marked tentative, and routed to human review (L-2, §5). |
| Linked items (S-1, S-1.1): item-only retrieval; ineligible items blocked | Met | `test_unknown_urgency_item_is_retrieved_while_the_auditor_reviews`, `test_knowledge_blocks_ineligible_items_without_retrieving`, `test_two_items_of_one_parent_stay_separate`; Manny's connected-path tests. |
| §9a failed states; deterministic IDs | Met | `test_input_gate_blocks_unusable_triage`; lane case 12 (upstream stop); `test_contribution_id_is_idempotent`. |
| Synthetic data only | Met | `test_corpus_rejects_non_synthetic_and_duplicate_articles`. Evaluation-only fixtures never enter the runtime corpus (`tests/test_eval_sources.py`). |

## 3. Troubleshooting (A4)

| PRD-v4 requirement | Status | Evidence |
| :--- | :--- | :--- |
| §9 A4: propose only Tier 1 steps supported by retrieved guidance and policy; check each action against the allowlist | Met | Steps are quoted from the top approved passage and marked `suggested_not_performed`. Tests: `test_golden_steps_are_verbatim_allowlisted_and_cited`, `test_access_case_separates_staff_only_procedures`, `test_forbidden_step_in_approved_guidance_is_rejected`, `test_unknown_action_type_is_rejected`. Lane case 9. The calibration gate requires no step outside Tier 1: 0 errors. |
| §9 A4 stop: an unauthorized action, unsupported step, access bypass, or policy override is rejected and escalated | Met | `test_adversarial_request_is_rejected_with_no_steps`, `test_block_rule_suppresses_steps_even_with_good_evidence`, `test_override_outside_or_across_quotes_still_blocks`, `test_quoting_does_not_exempt_other_request_rules`, `test_privilege_request_is_flagged_without_blocking` (policy 0.1.2). Troubleshooting emits escalation signals; Manny's Escalation agent decides. Lane cases 3 and 11. |
| §9 A4: no external action tool | Met | `test_agents_have_no_network_or_process_access`. The agent has no tools. |
| §7: benign quoted instructions are data; quoting does not bypass controls | Met | `test_quoted_policy_phrase_is_case_data_not_a_request`; `test_only_rr03_treats_quoted_matches_as_signals`. RR-02 (cross-site data) blocks even quoted text, by design. |
| Privacy and security stop conditions halt routine steps | Met | `test_privacy_stop_condition_halts_routine_steps`, `test_quoted_text_does_not_suppress_security_stop_condition`. |
| No steps without evidence; confidence never above Knowledge | Met | `test_knowledge_abstention_means_no_steps`, `test_confidence_never_exceeds_knowledge`. |
| Gates and linked items | Met | `test_gates_block_unacknowledged_or_mismatched_chain`; a linked item waits for the Auditor (`test_troubleshooting_waits_for_the_auditor`); `test_policy_loader_fails_closed`. |

## 4. Documentation (A6)

| PRD-v4 requirement | Status | Evidence |
| :--- | :--- | :--- |
| §9 A6: draft from verified facts only; validate schema, source references, privacy minimization, and the human-review flag | Met | Every line is labelled, and the draft banner says it is not saved, not sent, and changed no ticket state. Tests: `test_golden_draft_uses_only_labelled_cited_content`, `test_recorded_actions_only_verified_ones_count_as_performed`, `test_result_requires_exactly_one_of_draft_or_fallback`. `human_review_required` is always true (`test_contributions_are_frozen_strict_and_always_need_human_review`). |
| §9 A6 stop: sensitive-data leakage or an unavailable dependency suppresses the draft and gives a manual fallback | Met | `test_sensitive_data_suppresses_draft_without_echoing_value`, `test_missing_dependency_suppresses_draft`, `test_unacknowledged_or_stale_inputs_suppress_draft`; lane cases 7 and 12. |
| No unsupported content; abstained upstream documented truthfully | Met | `test_abstained_upstream_still_documents_without_guidance`. The calibration leak checks require no unsafe or ineligible source text in any output: 0 errors. |
| Draft-only, with idempotent identifiers (§3c) | Met | `test_draft_is_idempotent`. Nothing is saved or sent: `save_reviewed_result` stays disabled ([charter](AGENT-CHARTERS.md)). |
| Linked items (S-1.1): attention flag by reference; attention-check information line; no extra hold | Met | `test_documentation_states_the_attention_check`, `test_check_not_run_adds_no_hold` (`tests/test_item_scope_v02.py`). |

## 5. Limitations and open items

| ID | Limitation | Effect | Owner and next step |
| :--- | :--- | :--- | :--- |
| L-1 | **Retrieval recall.** The lexical gate misses many reworded or padded requests. v2.0 answerable coverage is 53.1%, and the evaluation draft cites the expected source for 14 of 65 items. | Usefulness, not safety: a missed answer becomes an abstention and goes to human review. | Shawn. Knowledge `0.3.0` fixed numeric requests and `0.4.0` padded requests ([L1-IDENTIFIER-TERMS.md](calibration/L1-IDENTIFIER-TERMS.md), [L1-L2-BATCH-2.md](calibration/L1-L2-BATCH-2.md)). Reworded requests need a synonym vocabulary or another retrieval method. |
| L-2 | **Off-topic answer when the on-topic article is ineligible.** Examples: v2 `SYN-KCAL-1075`, evaluation case 067, and v1's 2 medium-band unsupported answers (relevance 0.61 and 0.63). | A real but wrong-topic citation, labelled tentative and routed to human review. | Shawn. Mostly fixed in Knowledge `0.4.0` by the ineligible-anchor guard: v1 `SYN-KCAL-0099`, v2 `1075`, and evaluation case 067 now abstain. One v1 medium-band unsupported answer (`SYN-KCAL-0078`) and some wrong-section answers remain. |
| D-08, D-09 | Confidence thresholds are provisional, and the calibration labels are drafts. | The bands are qualitative. | Manny (evaluation owner). |
| D-02, D-03 | `SYN-TS-POLICY` is `proposed`; its patterns are risk signals. | Tier 1 boundary values await CDIT policy. | Shared Lane / CDIT. |
| Evaluation | The 100-case draft is unapproved and unscored. C-1 to C-7 are in [EVAL-DRAFT-V1-KNOWLEDGE-HANDOFF.md](EVAL-DRAFT-V1-KNOWLEDGE-HANDOFF.md). | §4f "approved must-pass set" evidence does not exist yet. | Manny. |
| Q-04, N-04 | The agents are deterministic, with no model adapter. | A model-backed agent would need a prompt, a schema, and provider approval (D-12). | Not planned for this phase. |

## 6. Decisions requested from the reviewer

1. **Acceptance.** Accept Knowledge, Troubleshooting, and Documentation against PRD-v4 A3, A4, and A6 for the synthetic prototype, with §5 recorded, or name the specific gaps to close first.
2. **Shared contract.** Confirm `0.1.0-proposed` with S-1, S-2, and S-1.1 as the "approved shared contract" this checklist item refers to, or list the remaining contract changes.

## 7. Proposed `Checklist.md` wording (for Manny to apply)

`Checklist.md` is shared and Manny maintains it, so Shawn's Lane has not edited it. There are two proposed edits, both in the "Shawn lane" section.

**1. Add a dated status line after the existing 2026-11-04 note, and keep that note unchanged:**

```text
> 2026-11-09 status: PRs #13–#15, #18, and #20–#24 merged into `developer` (latest `fa6b14f`): Phase 2 connected-path receiver review, S-1.1 complete (item scope 0.2, `attention_check` required), evaluation-only Knowledge fixtures and source check for the 100-case draft, Troubleshooting policy 0.1.2 (L-4), the `SYN-KCAL` v2.0 baseline, and Knowledge 0.3.0 (L-1 identifier change). Full suite 731 passed; 12/12 lane cases; calibration v1.0 and v2.0 with 0 critical errors. Acceptance evidence for A3/A4/A6: `docs/lanes/shawn/ACCEPTANCE-PACKET-A3-A4-A6.md`. Acceptance remains pending the reviewer's decision.
```

**2. Point the open item to the evidence, and keep it unchecked until the reviewer decides:**

```text
- [ ] Review and accept each agent against PRD A3/A4/A6 and the approved shared contract. Evidence: `docs/lanes/shawn/ACCEPTANCE-PACKET-A3-A4-A6.md` (2026-11-09); reviewer decision pending.
```

## 8. Reproduce

```text
python -m pytest -q                                   # 744 passed with Knowledge 0.4.0
python -m cdit_support_mao.lane_harness synthetic_data/cases
python -m cdit_support_mao.lane_calibration synthetic_data/calibration/knowledge-calibration-v1.json --knowledge-dir synthetic_data/knowledge
python -m cdit_support_mao.lane_calibration synthetic_data/calibration/knowledge-calibration-v2.json --knowledge-dir synthetic_data/knowledge
python -m cdit_support_mao.lane_eval_sources
```

Synthetic data only. No model calls, ticket writes, or outbound messages.
