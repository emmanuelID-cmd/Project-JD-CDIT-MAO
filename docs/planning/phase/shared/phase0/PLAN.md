# Shared Phase 0 — PRD v2 and Evaluation Baseline

**Status:** Planning prerequisite; no runtime code changes.

## Work

- Crosswalk approved PRD v2, user needs, A0–A7, scenarios, deferred decisions, lane ownership, and contract proposals.
- Agree interface/version promotion criteria and list open contract questions. Each lane owns its agent-side schema/behavior.
- Coordinate with Manny, who owns the synthetic evaluation definitions/protocol: machine-checkable expected outcomes, per-gate positive/negative sample counts, human-approved reference labels, deterministic evaluation script, holdout separation, and metric definitions. A project teammate peer-reviews disagreements and a sample using synthetic fixtures; no external evaluator is required. The AI cross-labeler option remains deferred under D-14.
- Define trace fields/privacy limits, run/case/policy/source versions, test commands on Python 3.13, budgets, and combined-harness acceptance.
- Define material-claim classes/denominators, retrieval recall@k, source freshness, latency/cost, and reviewer over-reliance measures without relaxing quality gates.

## Handoff and exit evidence

Both lanes acknowledge a contract version and evaluation matrix; decisions are assigned or explicitly deferred; no incompatible v1/v2 rules are hidden. Do not wire agents to a still-proposed contract.
