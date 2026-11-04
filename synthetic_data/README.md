# Synthetic data (prototype only)

Everything in this folder is invented for local testing. Every knowledge article must declare `"data_classification": "synthetic"`, and the loader rejects any file that does not. Case IDs must match `SYN-…`.

Never place real customer tickets, PHI, credentials, Salesforce exports, or CDIT-private documents here. That requires an approved data-handling path (see `AGENTS.md` and PRD "Data sources and constraints").

| Folder | Contents | Used by |
| :--- | :--- | :--- |
| `knowledge/` | 11 versioned KB article files (approved, retired, draft, stale, conflicting, injected, and governance-error examples) | Knowledge agent |
| `policy/` | Proposed Tier 1 troubleshooting policy (`SYN-TS-POLICY` 0.1.0) | Troubleshooting agent |
| `cases/` | 12 lane cases, each with Triage and Escalation stand-ins and expected outcomes | `cdit_support_mao.lane_harness`, tests |

Some fixtures are unsafe on purpose so the agents can prove they handle them:

- `KB-NTF-050` contains instruction-like text.
- `KB-AUD-080` contains a forbidden account action.
- `KB-UPL-030` and `KB-UPL-031` conflict.
- `KB-RPT-040` is stale.
- `KB-DRAFT-060` is unapproved.
- Case 07 contains a synthetic PHI-like date.

Do not "fix" these fixtures without updating the tests that depend on them.
