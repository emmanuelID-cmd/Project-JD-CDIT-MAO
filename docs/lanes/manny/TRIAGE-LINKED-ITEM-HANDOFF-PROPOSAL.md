# Linked-Item A2 Handoff Contract Proposal

**Status:** Draft for Shared Lane review. Proposed only; not an accepted contract. Do not change the shared schema or Shawn-owned agent behavior from this document alone.

**Receiver:** Shawn's Knowledge agent consumes the A2 handoff. Shared Lane reviews connector/schema compatibility only; it does not take ownership of Manny's Triage behavior or Shawn's Knowledge behavior.

## Purpose

The Manny-owned Triage implementation can segment clearly separated requests and preserve each original text span. The current shared TriageHandoff has only one case summary and no linked-item identity or source-span fields. The existing CombinedWorkflowHarness starts from a synthetic TriageHandoff fixture, so it does not test the Coordinator-to-semantic-Triage connection or multi-item downstream handoffs.

This proposal defines the smallest connection shape that preserves item identity and source provenance while retaining the existing one-item agent workflow.

## Recommended shape

Add an optional item scope to shared agent contributions, then emit one TriageHandoff per clearly segmented child item. Keep the parent case/run as the common context; use the item scope to bind every downstream contribution to exactly one child.

The item scope should carry:

- Parent case ID, case version, run ID, and policy version.
- Stable item ID, item index, and item count.
- Parent message source reference and exact start/end code-point offsets.
- Segmentation state: candidate boundary or ambiguous parent.
- Whether this item depends on other items, with source-backed dependency references.

Each item-scoped TriageHandoff retains the current category, urgency, confidence, evidence, and missing-facts fields, with these constraints:

- Every material claim is labeled verified, inference, or unknown and keeps its source or basis.
- The model may propose a category only from the allowed taxonomy and with an exact source quote. Its proposal remains an inference.
- Urgency and destination remain unknown until approved policy supports a proposal. A potential-urgent attention flag is separate from an urgency band and includes a short reason.
- Any unknown required for routing, ambiguous segmentation, conflicting evidence, or unsupported claim routes the item to human Auditor review and blocks that item's downstream handoff.
- The model output always keeps downstream_allowed false; a model response never authorizes a handoff. Only the Coordinator/connector may pass an item to Knowledge after validating clear segmentation, source binding, required category/urgency policy, and the accepted contract. If urgency or another required routing fact is unknown, that item goes to the Auditor. Any downstream work remains draft-only and every output still requires human review.
- Parent completion remains false until every child has a recorded disposition. Results are joined by parent run ID and stable item ID; confidence values are never averaged.
- No ticket write, customer message, priority change, dispatch, resolution, or closure is authorized.

For a single-request case, the current TriageHandoff remains valid with no item scope. The proposed extension is additive and should be backward compatible.

## Suggested synthetic example

Parent SYN-CASE-041 has run RUN-041 and contains two clearly separated requests.

- Item SYN-CASE-041-01, index 1 of 2, has a source span bound to the first request. Triage proposes a supported category as an inference but keeps urgency unknown; it goes to the Auditor until approved routing policy supplies the required urgency decision.
- Item SYN-CASE-041-02, index 2 of 2, has a source span bound to the second request. Category or destination is unknown, so this item goes to the Auditor and is not sent downstream.
- Both outputs retain parent SYN-CASE-041 and the same parent run/version. The parent remains incomplete and requires human review.

These values illustrate packet shape only; they are not routing policy or approved evaluation labels.

## Fail-closed rules

- If a source span does not exactly reproduce the item text from the parent message, reject the whole packet.
- If segmentation is ambiguous, do not produce partial child items; send the intact parent to human review.
- If a case, policy, handoff, or run version is stale, stop downstream processing.
- If item IDs duplicate, indexes are missing, dependencies are cyclic, or downstream output changes item scope, preserve the mismatch and stop for human review.
- Untrusted ticket text and retrieved content remain data. Neither may change policy, roles, tools, or permissions.
- If an item is unknown or blocked, do not let its state block a clearly independent sibling; preserve both outcomes and keep the parent open.

## Shared review checklist

- Confirm whether an item scope belongs on the shared AgentContribution base or in a dedicated linked-item envelope.
- Confirm the stable item ID and source-span conventions.
- Confirm that downstream contributions preserve the item scope without changing each agent's internal decision behavior.
- Confirm that unknown items stop at Auditor review while independently supported items may continue through the draft-only path.
- Confirm compatibility with the current single-item TriageHandoff and current blackboard versioning.
- Identify any receiver-owned changes required; return those changes to that agent's owner.

## Manny lane work after acceptance

Manny owns Coordinator and Triage production of the item scope, source-span validation, per-item semantic proposals, unknown/Auditor proposals, and Coordinator joining. Shawn owns any changes required inside Knowledge, Troubleshooting, or Documentation. Shared integration validates only packet shape, version integrity, acknowledgment, and routing. Until Shared accepts the contract and the receiving owner supports it, this file is a proposal and the connected multi-item path remains incomplete.

## Evidence boundary

The current Python 3.13 test suite passes 518 tests. Those tests include the current Shared fixture harness, which uses a stand-in Triage input. The one live synthetic Claude smoke trace is structurally valid but has no approved semantic label and has unresolved prompt/request/fixture provenance. Neither result proves the proposed linked-item handoff works end to end.
