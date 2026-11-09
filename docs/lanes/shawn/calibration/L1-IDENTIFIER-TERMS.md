# L-1 retrieval change: identifiers are not topic terms

**Status:** Shawn's Lane, 2026-11-09. Step 2 of the L-1/L-2 work. Sections 1–3 were written **before** this change was measured on `SYN-KCAL` v1.0 or v2.0, and they are not edited afterwards. §4 records the single measurement.

## 1. Change

The Knowledge relevance gate scores lexical coverage: the IDF-weighted share of query terms that a section matches. A section needs a coverage of at least 0.60, and at least 2 matched terms, to answer.

A query term that contains a digit (subject, visit, query, or site numbers; amounts; times; dates) is now dropped from the query before scoring. These are case identifiers and details, not topic words. Today they never match an article, so each one counts as an unseen term at the average IDF. That pushes coverage of the right section below 0.60.

**What does not change:**

- the article index;
- the cut-offs (0.60 answer and medium band, 0.85 high band), which belong to D-08;
- the eligibility, conflict, and injection checks;
- the contracts;
- what Knowledge queries: still the item text only (K-3).

## 2. How the design was chosen

Candidates were compared on a scratch development set of 32 requests. It has 20 that should be answered and 12 that should abstain, and its wording is not used in v1, v2, the evaluation draft, or earlier probes.

| Candidate | Correct (of 20) | Wrong | Unsupported (of 12) |
| :--- | ---: | ---: | ---: |
| Current scoring | 6 | 1 | 0 |
| Drop identifier tokens | 10 | 1 | 0 |
| Score each sentence and keep the best | 6 | 2 | 0 |
| Both | 11 | 2 | 0 |

Sentence-level scoring was rejected: it added one correct answer and one more wrong answer. Courtesy text is not the main cause of misses; most remaining misses are wording mismatches, such as "handset swap" against "phone change". No candidate was tried on v1 or v2.

## 3. Acceptance criteria (fixed before measuring)

The change is adopted only if every criterion holds; otherwise it is reverted and the result is recorded.

| Set | Criterion |
| :--- | :--- |
| `SYN-KCAL` v1.0 | 0 critical errors; correct answers ≥ 52 (baseline); wrong plus unsupported answers ≤ 2 (baseline) |
| `SYN-KCAL` v2.0 | 0 critical errors; correct answers > 21 (baseline); wrong plus unsupported answers ≤ 2 (baseline) |
| Evaluation draft source check | Information only, not a criterion: report any change in wrong-source answers. |

After this measurement, v2.0 is no longer held out. Any further retrieval change needs a new set version.

## 4. Result

Measured once on 2026-11-09 with Knowledge `0.3.0`, Troubleshooting policy 0.1.2, the runtime corpus `SRC-61C4A35E96CF`, and each set's own `as_of`.

| Set | Critical errors | Correct answers | Wrong + unsupported | False abstentions | Criteria |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `SYN-KCAL` v1.0 | 0 | 52 → 52 | 2 → 2 | 18 → 18 | Met |
| `SYN-KCAL` v2.0 | 0 | 21 → 26 | 2 → 2 | 27 → 22 | Met |

**Adopted.**

- **On v1:** every case has the same outcome.
- **On v2:** all five gains are numeric requests, which go from 1 to 6 correct of 11 (`SYN-KCAL-1054`, `1055`, `1058`, `1059`, `1060`). The other kinds are unchanged:
  - short requests 18/26;
  - padded requests 2/12;
  - stale-shadow 8/9 abstain, with `SYN-KCAL-1075` still answered from the wrong source (L-2);
  - no coverage 6/6.
- **Evaluation draft source check (information):** every verdict is unchanged. The one numeric item ("$47.23") still misses, because of its other wording.

**Still open:**

- **Padded and paraphrased requests:** mostly wording mismatch, not identifiers.
- **L-2:** an off-topic current article can answer when the on-topic article is stale.

Both need another design and a new held-out set version, because v2.0 has now been used for this measurement.
