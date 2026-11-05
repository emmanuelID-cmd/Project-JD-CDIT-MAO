# Synthetic data (prototype only)

Everything in this folder is invented for local testing. Every knowledge article must declare `"data_classification": "synthetic"`, and the loader rejects any file that does not. Case IDs must match `SYN-…`.

Never place real customer tickets, PHI, credentials, Salesforce exports, or CDIT-private documents here. That requires an approved data-handling path (see `AGENTS.md` and PRD "Data sources and constraints").

| Folder | Contents | Used by |
| :--- | :--- | :--- |
| `knowledge/` | 38 versioned KB article files (approved, retired, draft, stale, not-yet-effective, conflicting, injected, and governance-error examples) | Knowledge agent |
| `policy/` | Proposed Tier 1 troubleshooting policy (`SYN-TS-POLICY` 0.1.0) | Troubleshooting agent |
| `cases/` | 12 lane cases, each with Triage and Escalation stand-ins and expected outcomes | `cdit_support_mao.lane_harness`, tests |
| `calibration/` | Held-out calibration set `SYN-KCAL` v1.0: 111 cases with draft labels, written before the first run and pending human approval (D-09) | `cdit_support_mao.lane_calibration`, tests |

Some fixtures are unsafe on purpose so the agents can prove they handle them:

- `KB-NTF-050` and `KB-KBD-370` contain instruction-like text.
- `KB-AUD-080` contains a forbidden account action.
- `KB-UPL-030` and `KB-UPL-031` conflict.
- `KB-LANG-220` has two approved, current versions (a governance error).
- `KB-RPT-040` and `KB-TRN-360` are stale.
- `KB-SCH-340` is not yet effective.
- `KB-DRAFT-060` and `KB-EDC-350` are unapproved drafts.
- `KB-NAV-001` v1.0 and `KB-MOB-260` v1.4 are retired.
- Case 07 contains a synthetic PHI-like date.

Do not "fix" these fixtures without updating the tests that depend on them.

The calibration set is held out. Do not tune agent behaviour or thresholds against it. A change must be measured on a new set version, and the report must be regenerated after any corpus or agent change, because a test checks that it is current.
