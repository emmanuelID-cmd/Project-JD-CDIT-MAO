# Synthetic data (prototype only)

Everything in this folder is invented for local testing. Every knowledge article must declare `"data_classification": "synthetic"`, and the loader rejects any file that does not. Case IDs must match `SYN-…`.

Never place real customer tickets, PHI, credentials, Salesforce exports, or CDIT-private documents here. That requires an approved data-handling path (see `AGENTS.md` and PRD "Data sources and constraints").

| Folder | Contents | Used by |
| :--- | :--- | :--- |
| `knowledge/` | 38 versioned KB article files (approved, retired, draft, stale, not-yet-effective, conflicting, injected, and governance-error examples) | Knowledge agent |
| `policy/` | Proposed Tier 1 troubleshooting policy `SYN-TS-POLICY`: 0.1.2 is the lane default (adds the privilege-escalation flag to RR-06); 0.1.1 is kept for callers that still name it | Troubleshooting agent |
| `cases/` | 12 downstream lane cases, each with Triage and Escalation stand-ins and expected outputs; not approved gold labels | `cdit_support_mao.lane_harness`, tests |
| `manny_triage_cases/` | Manny-owned A0–A2 contract fixture for Unknown severity, human review, and potential attention; not semantic accuracy or a gold label | Manny triage runtime harness tests |
| `calibration/` | Held-out calibration set `SYN-KCAL` v1.0: 111 cases with draft labels, written before the first run and pending human approval (D-09) | `cdit_support_mao.lane_calibration`, tests |
| `evaluation_knowledge/eval-draft-v1/` | Evaluation-only fixture set `SYN-EVAL-KB-FIXTURES` 1.0: 9 KB articles, a manifest, and the source map for `CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v1` (pinned `evaluation_as_of` 2026-11-10). Not part of the runtime corpus. | `load_evaluation_corpus`, `cdit_support_mao.lane_eval_sources`, tests |

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

## Evaluation-only fixtures

`evaluation_knowledge/` holds synthetic articles written only so an evaluation dataset can be source-grounded:

- **Not policy:** they cover HR, incident, safety, and compliance scenarios as test material. They are not CDIT policy, legal or clinical guidance, or real company information.
- **Not loaded at runtime:** they never enter `knowledge/`. `load_corpus` refuses a fixture-set folder. An evaluation loads `knowledge/` plus one fixture set with `load_evaluation_corpus`.
- **Test-only approval:** `status: approved` inside these articles only makes them retrievable in that evaluation. Each article's `owner` and the set's `manifest.json` say so.
- **Roles:** the application roles User, Staff, and Admin only. Safety and clinical-advice requests stay human handoffs.
- **Provenance:** written by Shawn's Lane on 2026-11-08 (drafts reviewed in PR #18) and revised on 2026-11-09. The wording is original; nothing is copied from CDIT, Product Health, or any real document.

The calibration set is held out. Do not tune agent behaviour or thresholds against it. A change must be measured on a new set version, and the report must be regenerated after any corpus or agent change, because a test checks that it is current.
