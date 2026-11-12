# Shared Phase 1 — Shared State and Connector Agreement

**Status:** Completed and verified; versioned contracts implemented in `src/cdit_support_mao/contracts/`.

## Work

- Agree the Coordinator-owned, case-scoped versioned state envelope: case/run/stage IDs, actor, schemas, policy/source versions, timestamps, status, provenance, claim labels, confidence basis, unknowns/conflicts, proposed action, and validation result.
- Resolve D-07 storage, versioning, retention, and access before implementation. Coordinator owner implements Coordinator/state behavior; each agent owner implements its own reads/writes; Shared checks interoperability.
- Define acknowledgment, stale-result rejection, duplicate/replay handling, immutable handoff artifacts, cancellation, conflict, missing recipient, late result, and stop/manual fallback.
- Validate packet minimization and versions at connectors. Role labels and transfers do not grant field access or tool authority.

## Exit evidence

Both owners approve versioned connection contracts; positive/negative packet tests show no lost/changed evidence or unauthorized fields; unresolved lifecycle decisions are not silently encoded.
