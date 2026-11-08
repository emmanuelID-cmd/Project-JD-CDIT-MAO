# Shared Phase 0 - Requirements and Evaluation Baseline (PRD-v4)

**Status (2026-11-08):** PRD-v4 is the current requirements source. Shared contract changes S-1/S-2 and S-1.1 are merged. The evaluation protocol and a 100-case draft with per-gate positive/negative counts exist; the labels remain unapproved and unscored. Connected synthetic integration tests pass, while the assigned-case permission condition and final evaluation acceptance remain open. Earlier phase notes are historical snapshots.

## Work

- Crosswalk current PRD-v4, user needs, A0-A7, scenarios, deferred decisions, lane ownership, and accepted contracts; PRD-v2 is historical context only.
- Agree interface/version promotion criteria and list open contract questions. Each lane owns its agent-side schema/behavior.
- Coordinate with Manny, who owns the synthetic evaluation definitions/protocol: machine-checkable expected outcomes, per-gate positive/negative sample counts, human-approved reference labels, deterministic evaluation script, holdout separation, and metric definitions. For this synthetic assignment, Manny is the single label author, reviewer, and approver; report the lack of independent peer review. No evaluator agent is required, and the AI cross-labeler option remains deferred under D-14.
- Define trace fields/privacy limits, run/case/policy/source versions, test commands on Python 3.13, budgets, and combined-harness acceptance.
- Define material-claim classes/denominators, retrieval recall@k, source freshness, latency/cost, and reviewer over-reliance measures without relaxing quality gates.

## Handoff and exit evidence

Both lanes acknowledge a contract version and evaluation matrix; decisions are assigned or explicitly deferred; no incompatible v1/v2 rules are hidden. Do not wire agents to a still-proposed contract.
