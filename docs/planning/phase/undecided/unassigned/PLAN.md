# Undecided and Unassigned Work Plan

**Status:** PRD-v4 is the current requirements source. This file began as a PRD-v2 planning snapshot; its dated decisions below are historical unless carried forward in PRD-v4 or DEFERRED-DECISIONS.md. Remaining work is not silently owned by Manny, Shawn, or Shared.

## Historical Phase 0 - PRD v2 planning sign-off (superseded by PRD-v4)

1. **Project lead:** accept/revise synthetic, local, propose-only/read-only, human-reviewed prototype scope; preserve six agents unless explicitly changed.
2. **Approved:** use exactly three synthetic account categories—User, Staff, Admin. User has the client-facing view; Staff and Admin share the back-end interface; Admin additionally gets privileged account/access controls. No extra staff tiers, separate staff views, or access-only zones. Production identity-provider auth remains out of scope.
3. **Approved:** show an in-app P1 status flag for immediate human attention. External email remains deferred.
4. **Deferred by user:** keep client-to-developer issue reporting out of scope, unconfirmed, and disabled. Reopen only after scope is explicitly approved and every intended submitter is required to authenticate; then remove the dangling scenario pointer and define any separate journey.
5. **Approved (D-19):** a single-call baseline is one model call given the same synthetic case and evidence that MAO agents process. Comparing results can show whether orchestration adds quality relative to cost/latency. It is not an agent or product feature, and is not a required deliverable; use it only as an optional synthetic comparison if the assignment needs evidence for MAO. No real tickets, participants, or operational decisions.
6. **Historical decision:** PRD v2 was the planning/go-no-go document for Nov 11 at the time; it was superseded when PRD-v4 became the current requirements source on 2026-11-08. The Nov 11 date is not a build-completion commitment.
7. **Historical plan, now superseded:** the urgency-design discussion has since occurred and its prototype guidance is in PRD-v4. D-01 still reserves operational impact/time thresholds, SLA clocks, grouping rules, and override authority for authorized policy.
8. **Approved:** Product Health uses only minimal synthetic/system metadata for internal investigation, correction, and change planning; do not collect or retain actual user/ticket records. No real-world interview or field activity is in scope.


## Approved local app and SQL foundation workstream

The local synthetic database/authenticated app and separate no-auth role showcase are specified in LOCAL-APP-DATA-AUTH-PLAN.md. Scope is approved; Manny owns SQL foundation and app/auth/UI. The local SQL foundation branch is synchronized with Manny's lane using its fast-forward-only rule while Manny is the sole SQL author.

## Phase 1 - Before shared build/evaluation

- **Future production storage (unassigned):** local synthetic SQLite foundation and its version/retention controls are implemented. D-07 production storage, concurrency, audit, and access requirements remain unresolved; do not infer that local SQLite is approved for production.
- **Shared + lane owners:** agree acknowledgment, state/version envelope, policy/source version ownership, vocabulary, and contract promotion.
- **Manny (evaluation owner):** define labeling guidance, human-approved reference-label process, holdout separation, per-gate counts, claim classes/denominators, confidence calibration, retrieval freshness/recall, latency/cost, reviewer-error thresholds, handling-time protocol, and deterministic comparisons. Manny is the single label author, reviewer, and approver for the current synthetic assignment; record the lack of independent peer review.
- Preserve the zero-unsupported-material-claim gate and report the tested set and its counts; do not weaken a gate to fit the available sample.
- **Urgency policy:** the prototype's three-band framework, P1 attention flag, Unknown-to-Auditor behavior, and suggested benchmarks are in PRD-v4. D-01's operational thresholds, SLA clocks, grouping, and override authority remain deferred; prototype benchmarks are not guarantees.

## Phase 2 — Deferred/future use

- Define any case-action/state-transition authority by case type and role; prototype stays read-only with no write tool.
- Approve external alert channel/recipients; assume no outbound alert meanwhile.
- Assign owners for confidence calibration, audit integrity, source-freshness review dates, latency/cost budgets, and model/config regression if a model is later approved.
- Before real user/participant tickets, attachments, PHI, operational support/CTMS integration, or reliance on outputs/records in regulated trial conduct, seek a scoped CDIT compliance/privacy counsel assessment of HIPAA relationships/data, Part 11/GCP, and other controls. This plan makes no applicability finding; synthetic/public-source work does not decide future scope.

## Assignment rule

Every approved workstream receives an explicit owner and acceptance evidence before implementation. Unassigned stays pending; it does not become Shared by default. Non-prerequisite decisions may be deferred with a trigger and review date.
