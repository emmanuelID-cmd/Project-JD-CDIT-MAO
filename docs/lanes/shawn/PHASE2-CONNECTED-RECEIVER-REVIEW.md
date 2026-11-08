# Knowledge receiver review: Manny's N1–N3 connected path (PR #12)

**Status:** Shawn's Lane Phase 2 receiver review, 2026-11-07. Review only. No Manny-owned file, shared contract, or Shawn agent was changed.
**Reviewed:** PR #12 (`manny/coordinator-triage-escalation` → `developer`), head `a0373c4`, base `47371ed`. It was run in a detached scratch worktree on Python 3.13.17.
**Scope:**

- The files reviewed:
  - `agents/triage/knowledge_connector.py`
  - `manny_connected_harness.py`
  - `CombinedWorkflowHarness.run_manny_connected`
  - `MannyA0A2Harness.source_is_current`
  - `tests/test_manny_connected_harness.py`
  - the PR's Checklist and Phase 2 exit-checklist text
- The settled decisions are not reopened: S-1, S-2, Q-A to Q-C, Q-E deferred, categories, and urgency.

## 1. Verdict: accept with findings

The connected path delivers what the Knowledge receiver needs.

- Each eligible linked item reaches Knowledge with its own identity, parent link, exact span, category evidence, digest, and attention reference.
- Knowledge queries only that item's text.
- Unknown, ambiguous, dependent, conflicting, and failed-upstream items stay with the Auditor.
- A stale source fails closed.
- Troubleshooting and Documentation stay held, because every item carries `urgency = unknown` and `auditor_review = pending`.

**Merge.** No finding lets wrong-item, unsafe, or unacknowledged data reach Knowledge. Every failure seen fails closed, so the findings do not block merging PR #12. Before Phase 2 exit:

- F-1 and F-2 should be fixed.
- F-3 and F-4 need a small shared follow-up to S-1, which Shawn can draft.

## 2. What was checked, and the evidence

The probes ran against the PR code with the real Coordinator, Triage runtime, a fake model client, and Shawn's agents.

| Receiver requirement | Result | Evidence |
| :--- | :--- | :--- |
| Parent, run, and item identity | Pass | `knowledge_connector.py:76-86`. Probe: `item_id` equals the approved formula, and the parent source is this case message at this case version. |
| Exact source span | Pass | Probe: for both items of "I cannot find the report export; I cannot access MFA", `case_summary == parent[start:end]`. |
| Category evidence | Pass | `knowledge_connector.py:96-114` and `multi_item.py:80` (the quote must be inside the item). Probe: the evidence span lies inside the item span and equals the model quote. |
| Digest | Pass | Probe: `knowledge.input_refs == (handoff.as_input_ref(),)`; PR test at `test_manny_connected_harness.py:121`. |
| Attention reference | Partial | It works when a literal is in one item: locator offsets only, no text, and Knowledge carries nothing. It misses later items that contain the same literal (F-2). It cannot show "not assessed" (F-3). |
| Knowledge queries only the item text | Pass | Probe: every matched query term comes from the item, and no other item's text appears in the Knowledge output. |
| Unknown and ambiguous items stay on the human path | Pass | `knowledge_connector.py:197-212`. PR tests at lines 125-138 (unknown category) and 179-192 (ambiguous). No handoff is built, so Knowledge never sees the text. |
| Stale source | Pass, with a status issue (F-6) | The source is rechecked before building, for each item, before Knowledge, and after Knowledge. Probe: a case version bump mid-run gives `source_stale` with no items. Probe: staleness after Knowledge gives `discarded_stale_result` with the result withheld. |
| Downstream held for the Auditor | Pass | Probe with the real handoff: Troubleshooting returns `blocked` with `missing_dependency`; Documentation returns a manual fallback with `missing_dependency`. |
| Injection, billing, external effects | Pass | PR tests at lines 208-220 (the Coordinator blocks direct injection before Triage) and 164-176 (no model call without authorization). Writes, dispatches, and notifications are fixed to 0. |
| Acceptance records | Pass | The PR's Checklist and `EXIT-CHECKLIST.md` Step 2 keep the Shawn and Shared receiver gates open. |

**Test run.** On the PR head in a Windows checkout, 602 tests pass and 14 fail, all from F-1. With the taxonomy file restored to its LF bytes in the scratch worktree, all 616 pass.

## 3. Findings

| # | Severity | Finding | Evidence (PR head `a0373c4`) | Fix and owner |
| :--- | :--- | :--- | :--- | :--- |
| F-1 | Medium | The taxonomy pin fails on checkouts that convert line endings. `load_project_category_taxonomy` hashes the raw bytes of `CASE-SCENARIOS.md` against a pin of the LF version. With `core.autocrlf=true`, as on Shawn's Windows machine, the file has CRLF endings, so the taxonomy is "changed". Triage then routes every item to the Auditor, and 14 tests fail, 4 of them in PR #12. It fails closed, but the connected path cannot be reproduced on Windows. It has been on `developer` since before PR #12, and the PR's "616 tests pass" holds only on LF checkouts. | `development_examples.py:27`, `:109`. Working copy SHA-256 `432c9208…`; pin and git blob `010077c5…`. | **Manny:** normalize line endings before hashing. **Or Shared:** add a `.gitattributes` rule, `docs/requirements/CASE-SCENARIOS.md text eol=lf`. |
| F-2 | Medium | Attention attaches only to the first item that contains a literal. The signal records the first occurrence of each literal, and the connector attaches only matches that overlap an item. Probe: in "The report export broke in the outage; I cannot access MFA since the outage", item 1 gets `attention_ref`, and item 2 gets none even though it contains "outage". The parent summary flag is still true. Q-B asks for the flag on the relevant item. | `attention.py:5`, `:119`; `knowledge_connector.py:115-125` | **Manny:** record every occurrence, or rescan each item span. |
| F-3 | Low–medium | "Attention not assessed" looks the same as "no flag". Attention runs only when fixture patterns are configured. Otherwise `attention_signal` is `None`, and the handoff carries `parent_attention_flagged = False` and no reference, which reads as "checked, nothing found". Every item here has Unknown urgency, where Q-B says the flag applies. No PR test configures attention patterns. | `runtime.py:128`; `knowledge_connector.py:69-72`; `runtime_harness.py` (`fixture_patterns` is optional) | **Shared (S-1 follow-up):** add an attention status, `flagged`, `none_found`, or `not_assessed`. **Manny:** fill it. **Shawn:** Documentation shows "attention not assessed". |
| F-4 | Low–medium | The category citation names the policy version, not the taxonomy. The real taxonomy source is `SYN-TICKET-CATEGORY-TAXONOMY vsha256-…`, kind `policy_rule`. S-1 requires every `policy_rule` source to carry the run's policy version, so the connector drops the real source and cites `<policy_version> v<policy_version> #category-taxonomy-sha256:<hash>`. The taxonomy hash survives, but the cited source ID is wrong. The cause is partly our S-1 rule. | `knowledge_connector.py:127-139`; `development_examples.py:199-204`; S-1 rule at `contracts/handoffs.py:215-216` | **Shared (Shawn drafts):** let S-1 accept a versioned taxonomy reference, through a separate source kind or a scoped exemption. **Then Manny:** cite `result.category_taxonomy.source`. |
| F-5 | Low | The harness does not validate the Knowledge result before recording `knowledge_completed`. It acknowledges its own handoff and checks neither the echo, the input digest, the context, nor the source-set version. The older fixture adapter checked these. Shawn's agent returns correct values (probe), so this is defence in depth only. | `manny_connected_harness.py:115-133`; compare `fixture_adapter.py:197-202` | **Manny** |
| F-6 | Low | The run status can be mislabelled. If every item is discarded as stale, the run reports `stopped_for_human_review` instead of `source_stale` (probe). Every `HandoffError` from the bridge is reported as `source_stale`, including integrity failures: an invalid result, a parent mismatch, or an attention context mismatch. | `manny_connected_harness.py:95-102`, `:135-140`; `knowledge_connector.py:55-71` | **Manny** |
| F-7 | Low | The item Triage contribution ID is not tied to content. `stable_id("TRI", run_id, item_id, "A2")` leaves out the model, agent version, and proposal. A retried model call in the same run can produce different content under the same ID, and the Knowledge ID, which is derived from it, repeats too. S-2 digests catch the mismatch downstream. | `knowledge_connector.py:161` | **Manny:** include a digest of the item proposal, or the model, in the ID. |
| F-8 | Low | Several tests are weak. Line 110 accepts `knowledge_abstained_or_blocked`, so a receiver gate rejection would pass unnoticed. Lines 153-160 check items only when they were dispatched, and line 156 uses a substring instead of an exact span. Nothing tests attention, staleness after Knowledge, or a case version bump. | `tests/test_manny_connected_harness.py` | **Manny:** assert Knowledge is not `blocked`, check exact spans, and add the attention and staleness cases above. |
| F-9 | Nit | The fallback to `"unavailable"` cannot run, because a proposal-status result must carry a taxonomy. | `knowledge_connector.py:133`; `runtime.py:64-66` | **Manny:** raise instead of using a placeholder citation. |

## 4. Shawn-owned observation (not a PR defect)

**Short item text retrieves less.** In the probe, "I cannot access MFA" made Knowledge abstain with no candidate above the relevance gate, although `KB-MFA-200` exists.

- Splitting a message into items shortens each query. The gate needs coverage of at least 0.60 and at least 2 matched terms, so short items may abstain more often than whole messages do.
- This matches the earlier finding that the gap is the relevance gate, not ranking.
- N-01 should include linked-item-length queries. Until then, Knowledge stays safe and abstains rather than guessing.

## 5. Questions

- **For Manny:** Should F-1 be fixed by normalizing in code or by `.gitattributes`? The second touches a repository-wide file, so it needs Shared agreement.
- **For both lanes:** For F-3 and F-4, should Shawn draft one small S-1.1 contract PR, an attention status plus a taxonomy citation rule, for joint review?
