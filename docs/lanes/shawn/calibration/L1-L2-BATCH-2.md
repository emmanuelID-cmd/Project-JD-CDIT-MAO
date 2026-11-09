# Second L-1/L-2 batch: courtesy terms and the ineligible-anchor guard

**Status:** Shawn's Lane, 2026-11-09.

- **Written first:** sections 1–4 were written before either change was measured on `SYN-KCAL` v3.0 (held out) or v1.0 (regression). They are not edited afterwards.
- **Results:** §5 records the measurement.
- **Baseline:** Knowledge `0.3.0`, with the v3 baseline in [KNOWLEDGE-CALIBRATION-REPORT-v3.md](KNOWLEDGE-CALIBRATION-REPORT-v3.md).

## 1. Changes

**Change 1 (L-1, padded requests): courtesy terms are not topic terms.**

- A fixed list of greeting, thanks, apology, sign-off, urgency, request-timing, and addressing words is removed from the query before scoring, in the same place where identifiers were removed in `0.3.0`. The list is stemmed with the index's own stemmer.

  ```text
  thank thanks thx appreciate appreciated appreciation grateful kindly kind regards cheers
  wishes sincerely dear sorry apologies apologise apologize bother trouble hope hoping urgent
  urgently asap quick quickly soon today tonight tomorrow morning afternoon week weekend
  earliest chase chasing following follow again someone anyone somebody anybody whoever advise
  assist assistance guidance pointers
  ```

- **Deliberately left out:** words that can name a support topic, such as "possible", "question", "advice", "team", "note", and "support".
- **Unchanged:** article indexing.

**Change 2 (L-2): the ineligible-anchor guard.**

- **Anchor:** the scoring term with the highest IDF that the corpus vocabulary contains.
- **Rule:** if the best eligible section does not contain the anchor, and some ineligible section (stale, not yet effective, draft, or retired) does, Knowledge abstains instead of answering. It uses `stale_source_only` or `unapproved_source_only`, and lists the ineligible sections as excluded.
- **Why:** the request's most specific word points at an article that cannot be used, so a current article on another topic should not answer it. Examples: v2 `SYN-KCAL-1075` and evaluation case 067.

**Unchanged:** the cut-offs (D-08), the contracts, and K-3. Knowledge version goes from `0.3.0` to `0.4.0`.

**Out of scope: reworded requests (synonyms).** Lexical scoring cannot match words an article does not use. Fixing that needs an approved synonym vocabulary owned by the corpus owner, or a different retrieval method, and a model-based method would need D-12 approval. It is a separate design decision.

## 2. Design data

The design used `SYN-KCAL` v2.0 (no longer held out) and two scratch development sets: dev 1, with 32 requests, and dev 2, with 29. The scratch sets contain padded requests, courtesy-only uncovered requests, stale-shadow requests, and answerable requests that share a word with an ineligible article. v3.0, v1.0, and the evaluation draft were not used.

Each cell shows correct / wrong / unsupported / false abstentions / correct abstentions.

| Configuration | v2.0 (65) | dev 1 (32) | dev 2 (29) |
| :--- | :--- | :--- | :--- |
| `0.3.0` | 26 / 1 / 1 / 22 / 15 | 10 / 1 / 0 / 9 / 12 | 8 / 0 / 0 / 9 / 12 |
| Courtesy only | 28 / 1 / 1 / 20 / 15 | 9 / 2 / 0 / 9 / 12 | 13 / 0 / 0 / 4 / 12 |
| Courtesy + guard | 28 / 1 / 0 / 20 / 16 | 9 / 2 / 0 / 9 / 12 | 12 / 0 / 0 / 5 / 12 |

**Known trade-offs on the design data:**

| Change | Effect |
| :--- | :--- |
| Courtesy | One request now passes the gate but lands on the wrong section of the right article ("CRF page refuses to save", `KB-EDC-100#s2`). This is the existing s1/s2 tie. |
| Courtesy | One request now abstains, because the injection-flagged `KB-NTF-050` enters the top 3. This is a safe abstention. |
| Guard | It turns v2's unsupported answer into a correct abstention. |
| Guard | It costs one dev 2 answer: "copy" is the anchor, and it appears only in a draft article. |

The PRD treats unsupported answers as worse than abstentions, so the guard's trade is accepted only under the criteria below.

## 3. Acceptance criteria (fixed before measuring)

| Set | Criterion |
| :--- | :--- |
| v1.0 | 0 critical errors. Correct answers ≥ 51 (baseline 52; at most one loss). Wrong plus unsupported ≤ 2 (baseline). |
| v3.0 | 0 critical errors. Correct answers > 11 (baseline). Wrong plus unsupported ≤ 3 (baseline). All 18 abstain cases still abstain. |
| Evaluation-draft source check | Information only. Report any change. |

## 4. Order of decisions (fixed before measuring)

1. Measure both changes together, once, on v1.0 and v3.0. If every criterion holds, adopt both as `0.4.0`.
2. Otherwise, measure the guard alone, once. Adopt it if v1.0 holds the criteria above and v3.0 has 0 critical errors, at least 10 correct answers, wrong plus unsupported ≤ 3, and all 18 abstain cases still abstaining.
3. Otherwise, adopt nothing and record the result.

After this measurement, v3.0 is no longer held out.

## 5. Result
