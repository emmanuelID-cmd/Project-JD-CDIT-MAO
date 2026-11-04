# Runtime Agent Ownership and Lane Plan

This finalized plan divides ownership by the six runtime agents named in the PRD, not by front end/back end or broad task streams. Manny and Shawn own the agents listed below. Each owner controls assigned-agent functionality. Cross-lane access is limited to connecting approved handoffs and shared-state contracts.

| Lane | Runtime agents owned | Owns | Handoffs to agree and connect |
| :--- | :--- | :--- | :--- |
| Manny's Lane (`manny/coordinator-triage-escalation`) | Coordinator, Triage, Escalation | Internal prompts, tools, policy logic, routing and behavior for these agents; their agent-specific implementation and documentation. | Coordinator → Triage; Triage → Knowledge; Triage/Escalation inputs; Escalation → human handoff. |
| Shawn's Lane (`shawn/knowledge-troubleshooting-docs`) | Knowledge, Troubleshooting, Documentation | Internal prompts, retrieval/tools, evidence logic, drafting behavior and implementation for these agents. | Knowledge → Troubleshooting; Knowledge/Troubleshooting → Documentation; Documentation → Coordinator review. |
| Shared / pending | Optional second-reviewer agent (not approved); human review boundary (human role, not an agent) | No unassigned agent functionality is silently shared. If a new runtime agent is approved, assign an owner before implementation; until then it is pending. Both lanes may define the human-review contract and integration acceptance. | Agent-to-human output contract; optional reviewer placement and I/O contract only if approved. |

## Ownership boundary

- An owner may change functionality only inside agents assigned to that owner's lane.
- The other lane may inspect the interface and make only the minimal changes required to connect an approved handoff, shared-state contract, schema, or integration route. It must not alter the sending or receiving agent's internal prompt, tools, decision logic, or behavior.
- Shared state is an integration contract: agree on fields, versions, provenance, confidence, uncertainty, and validation across lanes. Each lane implements its own agent's reads/writes to that contract.
- If a connection cannot be completed without changing another lane's agent functionality, stop at the interface boundary, document the mismatch, and hand it to that agent's owner. Do not patch across the lane boundary.
- The coordinator owns orchestration behavior because it is assigned to Manny's Lane; shared interface decisions do not transfer coordinator implementation ownership.

## Visual UI work across lanes

Either lane may make presentation-layer UI changes, including adding or styling Submit/Save controls, when those controls invoke existing approved behavior. Follow the Consistency Page skill across tabs/routes and responsive layouts. This allowance does not change what an action does. Removing or bypassing an agent handoff, capability, policy, permission, state transition, or PRD requirement is a functional change and remains with its owner.

## Checkpoints: connection work vs lane gate-work

- **Connection work (Shared/connecting lane access):** validate handoff schema/version, required fields, state transition, acknowledgment, provenance preservation, and routing between agents. Checks may observe outputs and confirm the wire contract, but may not change another agent's internal behavior.
- **Lane gate-work (agent owner):** implement that agent's internal validation, confidence thresholds, prompt-injection handling, failure states, retries, abstention, and recovery behavior.
- **Cross-boundary failure:** if one agent rejects an incoming handoff, the receiving owner fixes its own validation or behavior; the connecting lane may fix only a demonstrable transport/schema-mapping defect in the connector. Coordinate the contract change before modifying it.

## Handoff workflow

1. Owners agree the input/output contract and shared-state fields before implementation.
2. Each owner builds and validates only their assigned agents against that contract.
3. The connecting lane validates that packets pass between the agents without loss or mutation of evidence, status, confidence, or version.
4. A failed connection returns to the responsible agent owner or connector owner based on the defect location; no cross-lane functionality edits.
5. Shared integration review verifies the complete path and records unresolved issues; it does not reassign ownership by implication.

## Assignment note

Manny and Shawn are the finalized owners for the six-agent split. Ownership changes require an explicit project-lead decision.
