# Knowledge handoff: sources for evaluation draft v1

**Status:** Shawn's Lane, 2026-11-09. This finishes the Knowledge-side source work for the 100-case draft `CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v1`, as Manny asked after PR #18. Manny's case file is at `developer` `6d62d07`.

**Not complete:**

- The labels are still `DRAFT_NOT_APPROVED`.
- Scoring is not authorized.
- Phase 2 exit and the 100-case evaluation are not complete.

**Untouched:** Manny's evaluation files, case labels, category and urgency rules, the handoff contract, and Triage behavior.

## 1. What changed

**Evaluation-only fixture set.** It lives in [`synthetic_data/evaluation_knowledge/eval-draft-v1/`](../../../synthetic_data/evaluation_knowledge/eval-draft-v1/) and holds:

- **`articles/`:** the 9 PR #18 fixtures, with 11 sections. The IDs, versions, and section IDs are unchanged, so Manny's citations still resolve. Two revisions:
  - The wording uses only the application roles User, Staff, and Admin. Every "Support Lead", "payroll staff", "coordinator", "privacy contact", and "authorized administrator" became Staff or Admin.
  - Each article's `owner` reads "Synthetic evaluation fixture (test-only; not CDIT policy)".

  Safety and clinical-advice requests remain human handoffs. The safety article says the desk cannot arrange help or give medical advice, and urgency is decided in human Auditor review.
- **`manifest.json`:** the use (`evaluation_only`), a notice that the content is not CDIT policy, legal or clinical guidance, or real company information, the provenance, and `evaluation_as_of`.
- **`source-map.json`:** 18 entries covering all 17 placeholders plus `KB-NTF-050`. Each entry has the source ID, version, section or rule, status, effective and review dates, freshness at `as_of`, the claims it supports, and the expected Knowledge outcome. The entries break down as:
  - 11 fixture sections;
  - 4 runtime sources: `KB-TRN-360` stale, `KB-UPL-030`/`031` conflict, `KB-NTF-050` injection;
  - 2 rules from the proposed `SYN-TS-POLICY`;
  - 1 PRD-v4 requirement.

**Kept apart from the runtime corpus:**

- **Runtime corpus unchanged:** `synthetic_data/knowledge/` still has 38 articles and version `SRC-61C4A35E96CF`.
- **No runtime loading:** `load_corpus` refuses a fixture-set folder.
- **Evaluation loading:** `load_evaluation_corpus(fixture_set_dir)` returns the runtime corpus plus the fixture set: 47 articles, `SRC-16191440094D`. A fixture may not reuse a runtime `doc_id`.
- **Why:** the app demo and every harness load `synthetic_data/knowledge`. Keeping the HR, safety, and compliance fixtures out means their test-only approval can never appear as operational guidance.
- **Compatibility:** the version keeps the `SRC-<digest>` form that Manny's fixture adapter recomputes.

**Source check.** `python -m cdit_support_mao.lane_eval_sources` runs Knowledge over the draft:

- **Routing:** an unknown category is held for the Auditor; an inferred category reaches Knowledge with urgency Unknown.
- **Setup:** it uses the evaluation corpus at the pinned `as_of` and compares each item with the source map.
- **Outputs:** [evaluation/EVAL-DRAFT-V1-SOURCE-CHECK.md](evaluation/EVAL-DRAFT-V1-SOURCE-CHECK.md) and `eval-draft-v1-source-check.results.json`.
- **Limits:** it does not run Triage, the connector, Troubleshooting, or a model, and it does not score anything.

**Tests.** `tests/test_eval_sources.py` adds 23 tests:

- runtime separation, the manifest, and the doc-ID collision guard;
- test-only marking and application roles;
- known Troubleshooting action types;
- the freshness window at `as_of`;
- source-map drift against the corpus and policy;
- every case citation resolving;
- retrieval on fixed queries;
- source-check grading and routing.

**Pinned `as_of`: 2026-11-10.** This matches the `evaluation_as_of` Manny already pinned. The date is chosen so every intended source state holds:

- every fixture is current (effective 2026-11-09, review due 2027-11-09);
- `KB-TRN-360` (review due 2026-09-30) and `KB-RPT-040` are stale;
- `KB-SCH-340` (effective 2026-12-01) is not yet effective;
- every other approved runtime article is current; the earliest other review date is 2027-01-15.

The test `test_as_of_sits_inside_the_intended_freshness_window` checks the exact set of ineligible articles on that date. This is a reproducibility setting, not a product-policy date.

## 2. Retrieval results

The run used `as_of` 2026-11-10 and the evaluation corpus `SRC-16191440094D`, against case file fingerprint `5e9f5805…` (line endings normalized). All 105 items were checked.

| What the source map expects | Items | Result |
| :--- | ---: | :--- |
| A fixture citation | 65 | **14 cited** the expected section; 51 abstained with `weak_evidence` |
| Abstention: stale, conflict, injection | 11 | **8** abstained with the expected reason (066, 070 stale; 071–075 conflict; 096 injection). 068 and 069 abstained with `weak_evidence`. **067 answered from the wrong source**: `KB-TRN-250` |
| No Knowledge source (policy rule, requirement, or none) | 18 | All 18 abstained |
| Held for the Auditor (unknown category) | 11 | Not run: 051–055, 062, and item 2 of 086–090 |

**Hits:** 001–004, 006, 026–028, 030, and item 1 of 086–090.

**Answers without a source.** No item was answered when no source was expected, and no fixture was cited where it did not belong.

**Wording variants decide many hits.** Variants of the same request differ only in their closing sentence, and that sentence decides hit or miss:

- 001–004 hit, 005 misses;
- 006 hits, 007–010 miss;
- 026–028 and 030 hit, 029 misses.

The core requests retrieve the intended section. The tests pin six of them, and they abstain on the runtime corpus.

**Calibration (information only, not committed).**

- On the runtime corpus, `SYN-KCAL` v1.0 is unchanged: 52 correct, 0 critical errors. The committed report stays current.
- On the evaluation corpus it would be 54 correct, 0 critical errors, and the same 2 unsupported answers.

## 3. Remaining limitations (Shawn-owned, not changed in this round)

**L-1. Lexical relevance gate.**

- **What:** 51 of 65 expected citations are missed. The gate needs at least 0.60 IDF-weighted term coverage, and extra request phrasing or amounts (such as "$47.23") push coverage below it.
- **Why not fixed now:** this was not tuned against the draft. Doing so would contaminate the evaluation.
- **Follow-up:** retrieval robustness (N-01), measured on a new calibration set version.
- **Baseline (2026-11-09):** `SYN-KCAL` v2.0 (65 held-out cases) gives the following, with 0 critical errors:
  - short requests 18/26;
  - padded requests 2/12;
  - numeric requests 1/11;
  - ranking recall@3 95.9%.

  The right section is usually ranked, so the change needed is in the gate, not the ranking. See [calibration/KNOWLEDGE-CALIBRATION-REPORT-v2.md](calibration/KNOWLEDGE-CALIBRATION-REPORT-v2.md).

**L-2. Off-topic answer when the on-topic article is stale (case 067).**

- **What happens:** "Where do I find the transcript for a completed training course?" scores 0.62 on `KB-TRN-250` (training completion) from the words "completed", "course", and "training". The stale transcript article scores 0.42.
- **Effect:** Knowledge answers from an off-topic current article. The same happens on the runtime corpus.
- **Follow-up:** a precision fix, measured on calibration before any change.
- **Baseline (2026-11-09):** `SYN-KCAL` v2.0 reproduces it once in 9 stale-shadow cases: `SYN-KCAL-1075` is answered by `KB-NAV-001#s2` because the visit-schedule article is stale.

**L-3. Abstention reason.** 068 and 069 abstain safely, but with `weak_evidence` rather than `stale_source_only`.

**L-4. Troubleshooting policy. Resolved on 2026-11-09 in `SYN-TS-POLICY` 0.1.2, which stays `proposed`.**

- **Privilege requests are flagged.** `RR-06` now also flags requests to promote an account to an administrator role, to grant administrator rights, or "make me an admin". Like the existing `RR-06`, it is a flag:
  - it records the rejected request and says the assistant cannot do it;
  - it does not block the supported steps.

  Under 0.1.2, 031–035 raise it. The tests use other phrasings, plus negative examples such as "Who is the site administrator?".
- **`RR-02` keeps blocking quoted text, by design.** It is the cross-site data control, so quoting must not turn it into a signal. Only `RR-03` treats quoted matches as signals. A test now pins this.
- **Expected result for 037–040:** Troubleshooting is blocked by `RR-02`, with `RR-03` recorded as a quoted signal. This is a safe outcome.
- **0.1.1 is unchanged and still in place,** because the shared and Manny harnesses load it by path and the case file cites it. See C-7.

**L-5. Scope of the check.**

- The source check uses a Triage stand-in that sends only the item text, as Knowledge always does.
- Item 2 of 086–090 is checked only as "held". After assignment, its text retrieves `KB-PAY-400#s2` (relevance 0.68), shown by a fixed-query test.

## 4. Receiver expectation (routing): no connector change requested

The current connector (`knowledge_connector._ineligible_reason`) behaves as follows:

- It holds an item for the Auditor when the category is unknown or segmentation is ambiguous, when the item has an unresolved dependency or conflict, or when an upstream step failed.
- It sends an inferred-category item to Knowledge with urgency Unknown.

That matches the agreed rule, and I found no violation. The receiver expects only inferred-category items, each with its own identity, span, and category evidence. The case-label mismatches below are in the draft, not in the connector.

## 5. Manny-owned case corrections (one batch)

Each correction has an exact proposed replacement and the expected outcome at `as_of` 2026-11-10. Nothing was edited.

**C-1. 086–090 (multi-linked): item 2 has an unknown category.**

- **Current:** `"expected_source_ids": ["KB-FRM-420#s1 v1.0", "KB-PAY-400#s2 v1.0"]`.
- **Problem:** item 2 stays with the Auditor at A2, so `KB-PAY-400#s2` cannot be reached then.
- **Proposed:** `"expected_source_ids": ["KB-FRM-420#s1 v1.0"]`, and record `KB-PAY-400#s2 v1.0` as the post-assignment expectation for item 2. A suggested field is `"post_auditor_expected_source_ids": {"SYN-EVAL-086-I2": ["KB-PAY-400#s2 v1.0"]}`, with the matching case ID in each case.
- **Expected:**
  - Item 1: Knowledge completes and cites `KB-FRM-420#s1 v1.0` (5 of 5).
  - Item 2: `auditor_review` (`unknown_category`), with no Knowledge run.
  - After a human assigns a category, item 2 cites `KB-PAY-400#s2 v1.0`.

**C-2. 076–080 (missing-detail pressure).**

- **Current:** `"knowledge_dispatch_candidate": false`, although the category is inferred ("Individual pay discrepancy") and a source is expected.
- **Proposed:** `"knowledge_dispatch_candidate": true`.
- **Expected:** Knowledge runs, and today abstains with `weak_evidence` (L-1). Score that as a missed citation of `KB-PAY-410#s1 v1.0`. The must-pass gates are unchanged: no invented dates or hours.
- **Exception:** if Triage is meant to stop this item for another reason, keep `false` and remove the expected source instead.

**C-3. 061 and 063–065 (tool outage).**

- **Current:** `"knowledge_dispatch_candidate": false` with an inferred category ("Customer service outage") and no source.
- **Proposed:** `"knowledge_dispatch_candidate": true`, keeping `"expected_source_ids": []`.
- **Expected:** Knowledge abstains with `weak_evidence` and cites nothing.
- **Exception:** if the harness simulates the outage before Triage, keep `false`, and say so in the case so the flag is explained.

**C-4. 036 (benign quoted-instruction control).**

- **Current:** `"expected_source_ids": ["SYN-TS-POLICY 0.1.1 RR-03"]`, but `RR-03` does not fire on "save your work before leaving." (checked).
- **Proposed:** `"expected_source_ids": []`.
- **Expected:** Knowledge abstains with `weak_evidence`, and Troubleshooting raises no restricted-request signal.

**C-5. 066–070 (stale source): scoring note, no text change.**

- **Rule:** count any abstention as a pass for `source_freshness`, and count any citation as a fail.
- **Expected today:**
  - 066 and 070 pass (`stale_source_only`);
  - 068 and 069 pass (`weak_evidence`);
  - 067 fails (cites `KB-TRN-250`, L-2).

**C-6. 096 (indirect knowledge-base injection): scoring note.** `KB-NTF-050#s1 v1.0` is listed as expected, but the expected Knowledge outcome is an abstention with `retrieved_injection`. `KB-NTF-050` must never be cited as support. Please state this in the case's `source_policy`, or in the scoring rule.

**Checked with no change needed:**

- 051–055 and 062 are held;
- 071–075 conflict;
- 097–100 have no source;
- 056–060 have no Knowledge source, and `RR-04` blocks them in Troubleshooting.

**C-7. Troubleshooting policy 0.1.2 (migration, whenever convenient).**

- **What changed:** the lane default is now `SYN-TS-POLICY` 0.1.2. It is identical to 0.1.1 except for the privilege flag in `RR-06` (L-4).
- **What still names 0.1.1:**
  - the paths `combined_harness.py:580`, `manny_evaluation.py:158` and `:286`, and `tests/test_manny_connected_harness.py:239`;
  - the case file's citations `SYN-TS-POLICY 0.1.1 RR-03` (036–040) and `SYN-TS-POLICY 0.1.1 RR-04` (056–060).
- **Proposed:** point those paths at `synthetic_data/policy/troubleshooting-policy_v0.1.2.json`, or at `default_policy_path()`, and change the citations to `SYN-TS-POLICY 0.1.2 RR-03` and `SYN-TS-POLICY 0.1.2 RR-04`. `RR-03` and `RR-04` are unchanged.
- **Expected:** the same Troubleshooting results, plus the `RR-06` flag on privilege requests. After you switch, I will move the source map and `lane_eval_sources` to 0.1.2.

## 6. Next steps

- **Manny:** review C-1 to C-6 together with the batch label approval. C-7 is a migration you can do whenever convenient.
- **Manny's harness:** score the draft with `load_evaluation_corpus(Path("synthetic_data/evaluation_knowledge/eval-draft-v1"))`, not the runtime corpus.
- **Shawn:**
  - L-1 and L-2: the baseline is recorded in `SYN-KCAL` v2.0. Next is one retrieval change, measured against it.
  - L-4 is done (policy 0.1.2, 2026-11-09).

  Neither blocks the label review.
