# Linked-Item A2 Handoff — Manny Connector Plan

**Status:** Updated 2026-11-06 after project PR #9. Manny approved S-1 (`TriageHandoff.item_scope`) and S-2 (`InputRef.content_digest`); both were merged into `developer`. This document describes the Manny-owned connector and integration work that remains. It does not claim that the connected path has passed receiver acceptance.

**Receiver and ownership:** Shawn’s Knowledge agent receives eligible A2 item handoffs. Manny owns Coordinator/Triage production, item eligibility, and the connector. Shawn owns any changes inside Knowledge, Troubleshooting, or Documentation. Shared Lane checks only the connection contract, versions, acknowledgments, and routing.

## Purpose and current gap

Manny’s Triage runtime can segment clearly separated requests and preserve their original source spans. PR #9 added item scope and content-digest support to the shared contracts and Shawn’s receiver agents. Manny’s item-aware connector is still missing. The existing `CombinedWorkflowHarness` starts from a fixture-created Triage handoff, so it does not prove the Coordinator-to-semantic-Triage or multi-item path.

## Accepted handoff behavior

Emit a separate `TriageHandoff` for each eligible linked item. Keep the parent case, run, case version, policy version, and parent message source common; bind each child with its own run-scoped item ID, index/count, exact source span, and content digest. `case_summary` contains that item’s text only.

The item scope carries segmentation/dependency state, category label/basis/sources, source evidence span, pending Auditor state, the item attention reference, and parent attention summary. The shared model validates item identity and provenance before Knowledge runs.

- Every material proposal retains verified/inference/unknown status and its evidence or basis. Category remains an inference; the model must provide an exact quote from that item and a value in the approved synthetic category vocabulary.
- Unknown category, ambiguous segmentation, conflict, invalid source binding, or blocked dependency goes to the human Auditor and is not sent to Knowledge.
- **Approved Q-A:** an item with an inferred category and Unknown urgency may go to Knowledge for read-only retrieval while the Auditor reviews urgency. Troubleshooting and Documentation remain blocked until the Auditor determines band and route.
- The model always returns `downstream_allowed=false`. Only Manny’s deterministic connector may prepare an eligible handoff after validating the current case/run/policy, item scope, category evidence, and accepted contract. Preparing a packet does not change the ticket or dispatch externally.
- An unknown or blocked item does not suppress a clearly independent sibling. Keep all child outcomes joined to the parent, keep the parent incomplete, and never average confidence.
- No ticket write, customer message, priority change, external dispatch, resolution, or closure is authorized.

For a single-request case, keep the existing `item_scope=None` path. Do not change Shawn-owned agent internals from Manny’s lane.

## Synthetic example

Parent `SYN-CASE-041` / run `RUN-041` contains two clearly separated requests.

- Item 1 has an exact source span and a supported category inference; urgency remains Unknown. It may reach Knowledge for retrieval while Auditor review is pending. Troubleshooting and Documentation wait for the Auditor’s band-and-route decision.
- Item 2 has an unknown category or ambiguous boundary. It goes to the Auditor and is not sent to Knowledge.
- Both items retain the parent/run identity and exact source spans. The parent remains incomplete and requires human review.

This is a contract example, not an operational routing rule or an evaluation label.

## Fail-closed rules

- Reject any item whose source span does not exactly reproduce its text from the current parent message.
- For ambiguous segmentation, keep one intact parent for human review; do not emit partial children.
- Stop on a stale case, policy, handoff, or run version.
- Stop on duplicate/missing item identities, invalid dependencies, or a downstream result with mismatched item scope.
- Treat ticket text, retrieved content, model output, and tool results as untrusted data. None can change policy, roles, tools, or permissions.
- Preserve a blocked item and its independent siblings separately; keep the parent open.

## Decisions already recorded

- **S-1/S-2:** optional item scope and canonical content digest were approved and merged in PR #9.
- **Q-A:** inferred-category items with Unknown urgency may reach Knowledge; later agents wait for Auditor determination.
- **Q-B:** attention is item-scoped with a parent summary; when segmentation is ambiguous, keep the attention signal at parent level.
- **Q-C:** use the approved run-scoped item ID formula from the shared schema.
- **Q-E:** a separate immutable Auditor decision record (Option B) is deferred follow-on work; it is not a prerequisite for read-only Knowledge retrieval.

## Manny implementation and Shared review still open

- [ ] Build the Manny-owned bridge from the validated Triage candidate/runtime result to one item-scoped `TriageHandoff` per eligible item.
- [ ] Make the connector item-aware: recheck the live parent and exact span, reject stale/mutated content, track item identity/digest in the receipt, and prevent conflicting duplicate acknowledgments.
- [ ] Preserve the attention reference for each matching item and a parent-level summary without passing raw match text to Knowledge.
- [ ] Wire the actual A0–A2 result into the combined workflow; keep fake-client execution for ordinary tests and do not call the paid provider without explicit per-run authorization.
- [ ] Shawn reviews Knowledge as the receiver after the connected path exists. Shared Lane verifies contract/version integrity, acknowledgment, item joins, stale-state rejection, failure routing, and that the correct item text is queried.
- [ ] Fix defects by ownership: Manny changes Coordinator/Triage/connector code; Shawn changes Shawn-owned behavior. No production database, authentication, real data, ticket write, notification, or Auditor UI is part of this phase.

## Evidence boundary

The current Checklist records 565 full-suite tests, but that is regression evidence, not Phase 2 acceptance. The combined harness still begins from a stand-in Triage handoff, and the prior synthetic Claude smoke trace has an unapproved semantic label and incomplete prompt/request/fixture provenance. Neither proves the connected item path or model accuracy. The 80-row catalog remains development examples, not approved labels or operational policy.