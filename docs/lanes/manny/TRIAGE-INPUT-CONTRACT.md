# Triage input contract — Manny Phase 2

**Status:** Input boundary in progress. The project lead approved multi-request analysis and a human Auditor for unresolved items; category and urgency behavior are not implemented, and D-01 operational thresholds remain open. This document is not a completed Phase 2 or an accepted Shared Lane integration.

## Purpose and source

Triage consumes a Coordinator handoff only after the receiver acknowledges it. `read_acknowledged_input` asks the process-local registry to recheck the receiver capability, active synthetic session, case scope/version, policy generation, handoff version, and timeout before returning a minimized packet. The packet holds the run context, trace/handoff identifiers, policy generation, case-message source reference, and reported text. It contains no session token or session reference.

The reported text is untrusted case data with claim status `unknown`; its presence in a fixture does not verify that a real-world statement is true. It is not a system instruction. A packet is a snapshot: future Triage execution must revalidate the live handoff immediately before use and prevent a stale/cancelled result from being accepted. Claude Sonnet 5.5 is selected for future synthetic semantic Triage, but no model call, prompt runtime, credential, or external tool is configured by this input contract.

## Output and policy constraints

The existing `TriageHandoff` in `contracts/handoffs.py` is the working `0.1.0-proposed` integration shape approved for Manny’s baseline; its shared schema has not been changed. `validate_triage_structure` checks schema, A2 and case/run context only. Even a structurally valid output remains ungrounded, requires human review, and cannot be handed downstream on that result alone. Triage must attach source references and label verified claims, inferences, and unknowns truthfully. Confidence is provisional and never grants permission or proves a claim. Unsupported classification, missing or conflicting evidence, and uncertain severity must not be invented or silently down-triaged. Human review remains mandatory.

Clearly separable requests may be represented as linked items; unsupported items go to an authorized human Auditor while supported independent items remain reviewable. The 80-row `CASE-SCENARIOS.md` catalog is a candidate synthetic taxonomy, not approved CDIT routing policy. Exact urgency thresholds, SLA clocks and overrides remain open under D-01. This input-only step introduces no classification rule, SLA claim, ticket write, notification, or customer response.

## Engineering checks and handoff

`tests/test_triage_input.py` checks acknowledgment, case/policy freshness, timeout, receiver authorization, minimized data, and source/context consistency with synthetic fixtures. These checks are not human-approved D-09 evaluation labels or evidence of a completed runtime agent. Shared Lane receiver review remains an integration gate.

## Local multi-request and Auditor preparation

`extract_request_parts` conservatively separates some explicit boundaries and preserves exact source spans in the original synthetic message. Quoted separators are preserved, and ambiguous punctuation or conjunctions stop for human review. Segmentation is heuristic: it cannot establish complete semantic or multilingual understanding, independence between requests, or downstream authority. The complete parent message must remain accessible to an authorized human during future review.

`prepare_auditor_review` re-reads the active Coordinator handoff and prepares a local, untrusted item proposal with unknown category, urgency and destination. It neither dispatches a human handoff nor establishes reviewer permissions. It rechecks freshness before return, but its result is a point-in-time snapshot, not durable proof of authorization: future integration must revalidate ownership, access, current context and version immediately before any use. The injectable time parameter is only a trusted fixture hook, never an untrusted caller's clock. Text is excluded from object representations, but serialization still contains it and must not be written to metadata-only logs.

`SyntheticFixtureExampleCatalog` compares opaque, trusted-fixture fact codes against versioned fixture examples and returns inference-only candidates with matched, missing, different and unassessed facts. Its review markers are synthetic test metadata, not proof of an actual human review, approval, sanitization or policy; it does not currently consume Auditor decisions or case text. Instance-local sealing does not prove global catalog-version uniqueness. A future integration requires an authorized review process, a trusted version/digest registry and fresh access checks.

No reviewed-example persistence, classification model, automatic learning, database, urgency rule, customer communication or ticket action is implemented. Shared Lane must review any cross-agent contract or receiver behavior.

## Bounded Phase 2 fixture flow

`prepare_unknown_items` composes source-linked segmentation and one local Auditor proposal per currently unknown item. It checks each proposal's full schema and binding before returning, and rechecks the handoff after composition. All items remain unknown and the parent remains incomplete; the snapshot neither dispatches nor asserts that segmentation captured every request. The independently available `validate_provisional_item` checks candidate shape and exact source-span attribution while keeping notes untrusted and category, urgency and destination unknown. It does not establish factual truth, policy support, entailment or downstream authority. Both are point-in-time fixture results and are not yet joined to an accepted shared multi-item contract or an authorized human-review interface.

## Synthetic attention fixture

`inspect_attention_signal` can identify an exact, case-sensitive occurrence of a literal provisioned by trusted synthetic fixture code. A match is only untrusted reported text that may merit human attention, not an incident, urgency band, dispatched alert or contextual risk assessment. A non-match is `not_assessed`, never safe or low; quoted, negated, historic, paraphrased, multilingual or differently cased input requires contextual human review. No operational risk policy, complete detector, delivered UI flag, trusted cross-instance catalog version or human access interface is implemented.

## Approved development-only example catalog

Manny approved using the 80-row ticket catalog for synthetic development. `DevelopmentExampleCatalog` parses the provided document bytes, checks the numbered 1–80 row set and records a SHA-256 digest. It does not independently verify the claimed source path; the digest identifies bytes, not origin, approval or policy. `lookup_development_examples` returns a reference only for an exact, case-sensitive full-item match when segmentation is not ambiguous. The reference contains the example category and band as unverified synthetic context; the actual case category, urgency and destination remain unknown. Different case context, impact, timing and exceptions are not assessed; non-matches do not mean no risk. This fixture is not an operational classifier, a reviewed-example catalog, an evaluation-label approval or evidence of CDIT coverage.

## Provider-free semantic output contract

`semantic_contract.py` validates model-shaped synthetic category suggestions without importing an SDK or making a model call. Each output item must bind to exactly one supplied item, use an allowed development category, and include a verbatim quote from that item's source text. Unsupported categories, missing or mismatched quotes, unexpected fields, and item-order/binding mismatches fail closed. The schema fixes urgency and destination to `unknown`, requires human review, and blocks parent completion, downstream use and dispatch. Validation is structural only; it does not prove the category is true, approved or operationally correct.
