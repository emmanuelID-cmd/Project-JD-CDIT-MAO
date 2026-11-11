# ActionRelay build checkpoint

The local app and the presentation are two runnable deliverables. The presentation illustrates the complete workflow using synthetic data and simulated processing. The live app stores tickets, human decisions, feedback and actual Coordinator/Triage run results in SQLite.

## Run the local app

From the project root in PowerShell, use the project's existing Python environment and an isolated database:

```powershell
$env:PYTHONPATH = "src"
$env:CDIT_DATABASE_PATH = "data/actionrelay-local.db"
.venv\Scripts\python.exe -m cdit_support_mao.db_cli seed
.venv\Scripts\python.exe -m cdit_support_mao.db_cli set-password SYN-USER-001
.venv\Scripts\python.exe -m cdit_support_mao.db_cli set-password SYN-STAFF-001
.venv\Scripts\python.exe -m cdit_support_mao.db_cli set-password SYN-AUDITOR-001
.venv\Scripts\python.exe -m cdit_support_mao.db_cli set-password SYN-ADMIN-001
$env:ACTIONRELAY_ENABLE_LIVE_TRIAGE = "1"
.venv\Scripts\python.exe -m uvicorn cdit_support_mao.main:app --host 127.0.0.1 --port 8000
```

Open [the local sign-in](http://127.0.0.1:8000/login). Use the four seeded usernames, `user.demo`, `staff.demo`, `auditor.demo`, and `admin.demo`, with the local passwords configured above. The Auditor uses the Staff base role with an additional capability. Keep the existing Anthropic key in the project-local ignored `.env`. Omit the live Triage flag to use account and case features without provider access.

As User, submit one of the displayed synthetic examples. As Admin, expand **Agent activity** on that case, check the authorization box and click **Run live Triage**. Each authorized run sends at most one provider request and the same case version cannot be sent again. The allowlist contains only the three displayed synthetic examples. A blocked or interrupted run remains visible for manual review. An Admin can assign a case to the Auditor, who can record a decision and a reasoned revision. Admin notes and flags attach to a specific version, and only its author and Admin can read them. Staff only see assigned tickets. Auditors can see the full queue and switch to their assigned work.

## Observed live behavior

Two approved synthetic cases were submitted as User and run via the authenticated Admin app API in an isolated database on November 10, 2026. Four separate logins, the assigned/unassigned read boundaries, and duplicate run rejection were observed.

| Case | Persisted run ID | Observed outcome |
| --- | --- | --- |
| IDNYC application | `AR-RUN-6291e7e6cde34d82bd333183c4f5dab0` | One provider attempt and one validated response. Coordinator accepted intake and Triage returned a proposal for human review. Case remained Submitted. |
| Personal W-2 | `AR-RUN-0357db45a4eb44e9839be2f65eb38a83` | One provider attempt. The Triage adapter returned `semantic_result_unavailable`. Case remained Submitted. |

The first staging preflight blocked before provider dispatch because the staging copy lacked the approved taxonomy file. After restoring that source, both attempts above were observed. The smoke script's temporary database cleanup initially reported a Windows file-handle error after the checks. The web handlers now close their database connections explicitly.

## Remaining integration

The live app checkpoint stops at Coordinator and Triage. The existing connected workflow still requires Auditor disposition for downstream handoffs. The next integration must bind that decision to the persisted item and source version, call the existing downstream agents, and record their observed results. The routine action also needs the separate deterministic application gate and atomic PDF reply, status and audit write. Current Triage proposals confer no authority to resolve tickets. Historical analytics and complete presentation layout parity are still pending in the live app.

## Presentation

Use the [continuous edition](ActionRelay-v2/actionrelay-demo.html), [presenter edition](ActionRelay-v2/actionrelay-demo-beats.html), or [180-second MP4](ActionRelay-v2/actionrelay-demo.mp4). Both HTML editions label simulation, include compact playback controls, and show the end-to-end approved story. The IDNYC button targets the official PDF directly and requires internet access. The prior presentation version is retained.
