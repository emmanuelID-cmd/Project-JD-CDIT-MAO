# Phase 0 — PRD v3 Baseline and Authorization (Manny)

**Status:** Phase 0 was approved against PRD-v3 on 2026-11-04. PRD-v4 is now the current requirements source and supersedes v3 for ongoing implementation; contract `0.1.0-proposed` and synthetic scope remain subject to their recorded shared acceptance gates.

## Purpose

Build against one internally consistent, approved contract rather than unresolved v1 conflicts.

## Work

1. Review PRD v3 against A0/A1/A2/A5, Manny-owned responsibilities, propose-only/read-only boundary, six-agent ownership, factuality, confidence, and handoffs.
2. Include functional local authentication/accounts using exactly three synthetic categories: User (client-facing view), Staff (back-end view), and Admin (same back-end plus privileged account/access controls). Do not add staff rank tiers or separate staff interfaces. Production identity-provider authentication remains out of scope.
3. Review the accepted handoff contract version, error/stop outcomes, evidence/provenance fields, state-version expectations, and connection points.
4. Record project-lead authorization for the specific build scope. Nov 11, 2026 remains planning/go-no-go only.

## Handoff and exit evidence

Inputs: project-lead-approved PRD v3, `TASK-SPLIT.md`, accepted `HANDOFF-CONTRACTS.md` version, decision register, and written phase authorization. Handoff accepted version IDs and unresolved blockers/deferred items to Phase 1.

Exit only when the project lead approves PRD v3 as Manny’s build baseline; six-agent ownership and read-only synthetic boundary are explicit; scope, reviewer, and contract version are recorded; and no A0/A1 prerequisite is silently assumed.

## Out of scope

Approving decisions on behalf of the project lead; production authentication; live data; write tools; edits to Shawn-owned agent behavior.
