# Synthetic connected Triage smoke — 2026-11-06

**Disposition:** Provider response validated; safe abstention; not an accuracy score.

## Execution

- **Case:** `SYN-CASE-PR2-20261106` (synthetic local fixture; no customer/employee data)
- **Trace:** `TRACE-40d06553-8baa-4fe8-bd26-73cccb711995`
- **Run:** `RUN-83651959-2dc3-4e21-ae76-b38df5be1899`
- **Path:** Coordinator A0/A1 → Triage A2 → item connector → Auditor review
- **Model:** `claude-sonnet-5-5`
- **Prompt ID:** `manny-triage-system-v1`
- **System prompt SHA-256:** `92dcee2769dbefed8b42e9b8579dd1e929789bd9c340d7d17bdc844225aa996c`
- **Serialized request SHA-256:** `58e0732115234c6573c2e370175b6b28f2ebb81f1ddcae6b0e24c4f51faf2e02`
- **Usage:** 1,282 input tokens; 451 output tokens; 5,099 ms
- **Calls/retries:** one call; zero retries
- **Estimated token cost:** $0.007074 USD at the published $2/MTok input and $10/MTok output rates, excluding any account-specific adjustments.

## Result and safety

- The response passed the local structured-output and source-validation contract but returned `category: null`, `category_label: unknown`; urgency and destination remained Unknown.
- The connector retained the item for the human Auditor. Knowledge was not called because category was Unknown.
- Human review remained required; parent completion remained false.
- Ticket writes: 0. External dispatches: 0. Customer notifications: 0.
- This call is not scored: the expected label for this fixture has not been approved by Manny. Do not count this output as a correct or incorrect classification until that label is approved.

## Evidence limits

- The full serialized request and raw model response are not stored; only the adapter's request and prompt hashes, validated category disposition, usage, timing, and workflow status are retained.
- The provider request ID is not retained by the current adapter.
- The older 2026-11-05 smoke trace remains incomplete; this replacement does not reconstruct its missing request body.

Model lifecycle status: [Anthropic model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations). Published token rates: [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing).
