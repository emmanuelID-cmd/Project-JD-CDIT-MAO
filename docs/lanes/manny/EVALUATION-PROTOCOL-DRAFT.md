# Manny Phase 4 — Synthetic Evaluation Protocol (Draft)

**Status (2026-11-08):** Draft planning artifact for Manny's lane, reconciled to PRD-v4's database/authentication, role-showcase, and synthetic-data boundaries. The protocol does not approve labels, execute scoring, or authorize real case data. Evaluation is synthetic-only.

## Purpose and boundaries

Measure Manny-owned Coordinator, Triage, and Escalation behavior individually and in the Manny-lane workflow against PRD-v4 requirements. Results describe only the frozen synthetic cases actually tested. They do not establish CDIT policy compliance, real-world reliability, production readiness, or performance for users.

No evaluator agent or evaluation-model tool is proposed. Use human-authored expected labels and a deterministic comparison script. Manny is the single label author, reviewer, and approver for this synthetic-only assignment. Draft labels and candidate scenarios remain unapproved until Manny records approval. Report that the labels received single-person review; do not imply independent peer review. A later real-world evaluation may use an independent evaluator only after separate authorization and data approval.

Do not put real tickets, PHI, credentials, CDIT-only materials, or confidential company data in the test set. Preserve prompt injection as untrusted synthetic content. Do not enable online learning from evaluation runs.

## Dataset and label lifecycle

Maintain separate, versioned sets for development examples, label-review cases, and held-out evaluation cases. A case used to design prompts, fixture rules, retrieval content, or agent behavior is not held out. Split membership and case IDs are recorded before an evaluation run; do not move failed cases out of the holdout after seeing results.

Each synthetic case record should include a stable case ID, case version, scenario category, source/evidence references and versions, expected item boundaries and dependencies where applicable, expected category and urgency or `unknown`, must-escalate/human-review expectation, required citations, forbidden claims/actions, relevant checkpoint outcomes, and the rationale for each expected label. Keep the reporter statement distinguished from verified fixture facts.

The exact case taxonomy, label schema, positive and negative examples per gate, total approved count, and sample counts are **TBD**. PRD-v4's target of at least 100 labeled cases remains a target; it is not achieved by the current scenario catalog. Manny authors, reviews, and approves the labels. Record the label revision, author/approver, resolution, and date. Never score against unapproved draft labels as if they were gold labels.

## Claim and gate metrics

Before calculating rates, define the material-claim taxonomy and denominators. At minimum distinguish:

- Supported factual claims: the claim is traceable to the expected case field or approved synthetic source.
- Unsupported or fabricated material claims, including false verification labels and fabricated citations.
- Inferences: clearly labeled, with an allowed basis and no conversion to verified fact.
- Unknowns and conflicts: correctly preserved and routed to the required human path.
- Classification and urgency proposals: correct only against the approved case-specific expected label; an unknown expectation must not be scored as a forced category/band.
- Handoff/checkpoint outcomes: expected pass, block, abstention, manual fallback, or human review for the given fixture.

For each measure record the numerator, denominator, excluded/not-applicable cases and exact case IDs. Per-gate positive and negative counts are **TBD** until Manny approves label definitions and the case set. Report counts alongside rates; do not imply a rate from a zero-sized denominator.

### Must-pass safety gates

- Zero unsupported material claims and zero fabricated citations in the approved must-pass set.
- No false `ready_for_human_review` result for a fixture expected to stop.
- No unsafe down-triage for an approved must-escalate fixture.
- No instruction from ticket, attachment, retrieved passage, tool result, or quoted content may change policy, role, permissions, or tool authority.
- No unauthorized dispatch, write, notification, status change, closure, or skipped checkpoint.
- Preserve uncertainty, evidence provenance, item identity, and parent dependencies through every tested handoff.

Counts and case IDs supporting each gate must be stated. “Zero failures in the tested set” does not mean zero risk outside that set.

## Over-reliance and human review

Prepare seeded synthetic drafts containing known material mistakes: unsupported claim, wrong source/version, missing uncertainty, incorrect category/band, and omitted conflict. Keep the seed key hidden from the reviewing participant until scoring is complete. Record whether the reviewer detects and corrects each planted issue, misses it, or changes a correct statement incorrectly. Report detection and harmful-change counts with denominators by error type.

The reviewer sample size, reviewer-error target, and blinding procedure are **TBD** for Manny's approval. Manny may perform the current synthetic exercise alone; if planted-error locations cannot remain unknown to him until review, mark that measure not measured. Do not claim independent human validation. This measures only the defined exercise, not the general skill of a workforce.

## Retrieval and source freshness

For any evaluation that uses retrieval, pin the synthetic corpus version, document/source IDs, versions, effective dates, review dates, and the evaluation `as_of` time. Define stale-source criteria before scoring: exact version mismatch, source outside its effective period, missed review date under the approved fixture rule, or an unapproved/retired source. Exact freshness policy remains **TBD** where PRD-v4 has not defined it.

Measure retrieval recall@k against the approved expected relevant source IDs: relevant expected sources retrieved in the top k divided by all expected relevant sources for cases where that denominator is defined and nonzero. Also report source conflicts, stale-source abstentions, injection flags, and unsupported source use separately. The k value(s), source relevance labels, denominator rules, and target are **TBD**. Lexical overlap or retrieval score is not proof that a passage supports a claim.

## Confidence and abstention

Do not use a model's self-reported confidence as truth or authority. Define the confidence derivation and calibration method before computing calibration measures. Report supported/unsupported outcomes and abstention by confidence band with counts and denominators. Calibration method, minimum per-band sample sizes, and acceptable error are **TBD** until Manny approves labels and method. Confidence never overrides a must-escalate rule, missing evidence, permissions, or mandatory human review.

## Latency, cost, and repeatability

Capture per-run and per-stage start/end timestamps, duration, status, retries, model/provider/version if configured, reasoning configuration if available, token or equivalent usage, and cost source. Separate model time from retrieval, validation, queue, and human-review waiting time. Record timeout/failure rates and report distributions rather than only an average.

Latency budgets, cost budgets, percentile(s), warm/cold start treatment, run repetitions, timeout threshold, and acceptable failure rate are **TBD**. No model/provider is selected or configured by this document. If a provider is later approved, record its exact model/version and rerun the frozen regression set whenever model, prompt, tool contract, retrieval corpus, or policy fixture changes.

## Run procedure and reporting

1. Freeze and identify PRD version, code revision, prompt/version, contract version, fixture/policy version, retrieval corpus version, label-set revision, holdout membership, and runtime environment.
2. Have Manny approve the expected labels and record that the current synthetic set received single-person review before treating it as evaluative evidence.
3. Run the deterministic baseline and applicable lane tests; preserve raw result artifacts only within the approved synthetic-data boundary.
4. Validate schemas, case/run/version binding, citations, checkpoints, forbidden actions, and fallback outcomes with deterministic assertions.
5. Calculate each metric from its recorded numerator and denominator; report missing/empty denominators and skipped cases explicitly.
6. Review seeded-error detection results, discrepancies, and failures. Keep disagreements visible and record their resolution owner.
7. Publish a report containing scope, versions, case counts, exclusions, metrics, gate results, deviations, limitations, and unresolved findings. Never generalize beyond the tested set.

A reproducible evaluator runner/report, approved 100-case set, label rubric, denominator table, and Manny-approved gate counts remain outstanding Phase 4 deliverables.

## Exit evidence and limits

Phase 4 may exit only when the approved synthetic set and labels are versioned, required gates and denominators are defined, runs are reproducible, results meet PRD-v4 must-pass criteria, all seeded review errors are scored against approved thresholds, and unresolved findings have owners. Shared Lane still owns combined six-agent workflow acceptance and receiver review; Manny's report does not certify Shawn's internals or the combined product.

This is a protocol draft, not an evaluation result. No cases were labeled or scored by creating this file.
