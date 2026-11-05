# Undecided and Unassigned Work Plan

**Status:** Open decisions and dependencies; not silently owned by Manny, Shawn, or Shared. The canonical D-01–D-19 register is [`DEFERRED-DECISIONS.md`](../../../DEFERRED-DECISIONS.md). This file groups decisions by when they are needed.

## Phase 0 — PRD v2 planning sign-off (by Nov 11, 2026)

1. **Project lead:** accept/revise synthetic, local, propose-only/read-only, human-reviewed prototype scope; preserve six agents unless explicitly changed.
2. **Approved:** use exactly three synthetic account categories—User, Staff, Admin. User has the client-facing view; Staff and Admin share the back-end interface; Admin additionally gets privileged account/access controls. No extra staff tiers, separate staff views, or access-only zones. Production identity-provider auth remains out of scope.
3. **Approved:** show an in-app P1 status flag for immediate human attention. External email remains deferred.
4. **Deferred by user:** keep client-to-developer issue reporting out of scope, unconfirmed, and disabled. Reopen only after scope is explicitly approved and every intended submitter is required to authenticate; then remove the dangling scenario pointer and define any separate journey.
5. **Approved (D-19):** a single-call baseline is one model call given the same synthetic case and evidence that MAO agents process. Comparing results can show whether orchestration adds quality relative to cost/latency. It is not an agent or product feature, and is not a required deliverable; use it only as an optional synthetic comparison if the assignment needs evidence for MAO. No real tickets, participants, or operational decisions.
6. **Approved:** PRD v2 is the planning/go-no-go requirements document for Nov 11, not a build-completion commitment.
7. **Approved:** after initial PRD-v2 finalization, hold the urgency-design discussion and add the decided bands to a reviewed PRD amendment before dependent routing implementation.
8. **Approved:** Product Health uses only minimal synthetic/system metadata for internal investigation, correction, and change planning; do not collect or retain actual user/ticket records. No real-world interview or field activity is in scope.

## Phase 1 — Before shared build/evaluation

- **Project lead + data/infra owner (unassigned):** resolve D-07 storage/version/lifecycle/retention/access; do not assume SQLite suffices for every concurrency/audit need.
- **Shared + lane owners:** agree acknowledgment, state/version envelope, policy/source version ownership, vocabulary, and contract promotion.
- **Manny (evaluation owner):** define labeling guidance, human-approved reference-label process, holdout separation, per-gate counts, claim classes/denominators, confidence calibration, retrieval freshness/recall, latency/cost, reviewer-error thresholds, handling-time protocol, and deterministic comparisons. A project teammate peer-reviews disputed labels and a sample using synthetic fixtures; no external evaluator is required.
- Preserve the zero-unsupported-material-claim gate and report the tested set and its counts; do not weaken a gate to fit the available sample.
- **After initial PRD-v2 finalization:** the project lead and support-process owner define urgency bands, shared case groups, thresholds, SLAs, and override rules in the planned design discussion; record them in a reviewed PRD amendment before dependent routing implementation.

## Phase 2 — Deferred/future use

- Define any case-action/state-transition authority by case type and role; prototype stays read-only with no write tool.
- Approve external alert channel/recipients; assume no outbound alert meanwhile.
- Assign owners for confidence calibration, audit integrity, source-freshness review dates, latency/cost budgets, and model/config regression if a model is later approved.
- Before real user/participant tickets, attachments, PHI, operational support/CTMS integration, or reliance on outputs/records in regulated trial conduct, seek a scoped CDIT compliance/privacy counsel assessment of HIPAA relationships/data, Part 11/GCP, and other controls. This plan makes no applicability finding; synthetic/public-source work does not decide future scope.

## Assignment rule

Every approved workstream receives an explicit owner and acceptance evidence before implementation. Unassigned stays pending; it does not become Shared by default. Non-prerequisite decisions may be deferred with a trigger and review date.
