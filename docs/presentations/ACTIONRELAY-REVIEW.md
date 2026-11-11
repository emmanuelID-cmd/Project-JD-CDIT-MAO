# ActionRelay review build

The working interface runs on the local FastAPI and SQLite application. The
embedded Storyboard explains the CDIT support problem and links the verified
job posting. The adjacent Demo contains the complete synthetic walkthrough in
continuous and presenter editions. Its countdown follows the playback clock.
The previous presentation and MP4 remain available for deadline use.

## Start the app

From the project root in PowerShell, use the existing Python environment:

```powershell
$env:PYTHONPATH = "src"
$env:CDIT_DATABASE_PATH = "data/actionrelay-review.db"
.venv\Scripts\python.exe -m cdit_support_mao.db_cli seed
.venv\Scripts\python.exe -m cdit_support_mao.db_cli set-password SYN-USER-001
.venv\Scripts\python.exe -m cdit_support_mao.db_cli set-password SYN-STAFF-001
.venv\Scripts\python.exe -m cdit_support_mao.db_cli set-password SYN-AUDITOR-001
.venv\Scripts\python.exe -m cdit_support_mao.db_cli set-password SYN-ADMIN-001
.venv\Scripts\python.exe -m uvicorn cdit_support_mao.main:app --host 127.0.0.1 --port 8000
```

Open [local sign-in](http://127.0.0.1:8000/login). The four usernames are
`user.demo`, `staff.demo`, `auditor.demo`, and `admin.demo`. To run billable
Triage, set `ACTIONRELAY_ENABLE_LIVE_TRIAGE=1` before starting the service, keep the
existing key in the ignored project `.env`, and explicitly authorize one call
from the Admin Agent Activity panel for an approved synthetic sample.

## Review the ticket paths

- As User, submit the IDNYC example. The fixed public-resource rule obtains the
  [official NYC PDF](https://www.nyc.gov/assets/idnyc/downloads/pdf/application-materials/IDNYC-1b-IDNYC-14-and-Older-Application-English.pdf).
  The app saves the exact file bytes, reply, audit receipt, and Resolved status
  in a single transaction. The case-scoped download opens as an attachment.
  Find it in Admin using **Flag → Close out or Review**. Close it through the
  status control and confirm the flag clears. If the source is unavailable,
  the app records human review and leaves the case Submitted.
- As User, submit the personal W-2 sample. The reply explains the handoff and
  the ticket remains Submitted. No payroll retrieval or external notification
  runs. If a Claude response fails validation, that outcome appears separately
  in Agent Activity.
- Submit a synthetic case and assign it to Auditor as Admin. Sign in as
  Auditor and save the item decision, including the exact reviewed source span.
  A current whole-ticket, single-item decision starts the downstream stages.
  The workflow records each real agent outcome and stops on missing evidence.
  The enrollment-report example, “Site user cannot find where to export the
  site enrollment report,” completed all four downstream stages with approved
  synthetic knowledge. The case still waits for a human disposition.

## Verification and acceptance

The full regression suite passed 764 tests. Chrome verified the four sign-ins,
matching desktop and mobile sidebar positions, Storyboard and both Demo
editions, pause and countdown, the scoped test PDF download, the W-2 reply,
the flag filter, and human closure after refresh.

- The protected routes, SQLite persistence, decision and case version checks,
  duplicate operations, status flag, and missing file and rollback behavior
  were tested using isolated synthetic databases.
- The primary NYC hostname returned HTTP 403. The same official path at
  [NYC’s alternate hostname](https://home4.nyc.gov/assets/idnyc/downloads/pdf/application-materials/IDNYC-1b-IDNYC-14-and-Older-Application-English.pdf)
  supplied the two-page fillable AcroForm. The isolated authenticated app test
  verified that the actual PDF resolved the request and downloaded byte for byte.
  Start the locally configured app with `.\Start-ActionRelay.ps1`. The launcher
  uses the checksum-pinned PDF under the ignored `data/actionrelay-forms/`
  directory. Other hosts need their own verified copy and the
  `ACTIONRELAY_IDNYC_PDF` and `ACTIONRELAY_IDNYC_SHA256` settings.
- The bounded live W-2 attempt `AR-RUN-480b2b11b7654f77ae09329635ddf5f9` reached
  the provider. The Triage adapter rejected the item schema. The saved ticket
  remained Submitted with a human handoff. No retry was sent.
- The review resume supports current whole-ticket, single-item decisions.
  Split or ambiguous requests remain available for human review.
- Queue analytics use recorded case lifecycle events. Historical dates with no
  recorded activity can display zero. Automatic resolution counts require a
  committed fulfillment receipt.
- The resource catalog now includes a digest-pinned official IDNYC PDF, a
  fillable ActionRelay-only weekly timesheet, a fillable A-D by
  Morning/Evening/Night shift-options matrix, the direct official fillable NYS
  SNAP application PDF, NYC HRA's SNAP forms page, and NY State of Health. The
  two employee PDFs are explicitly labeled
  development samples with no verified employer schedule or policy. Delivery
  resolves only the resource request; actual enrollment, eligibility,
  payroll, or schedule actions remain outside the automated flow. Exact
  allowlist matching, digest checks, the new link-route migration, human
  routing, and User-only attachment scope are covered by the regression suite.
- The local resource endpoint and application API are tested. Browser review
  of the latest flow is still pending because the browser extension UI blocked
  the isolated manual sign-in walkthrough.
- Formal evaluation remains unchanged. Final slides and the final video follow
  review and acceptance of the app.

[Continuous review demo](ActionRelay-review/actionrelay-demo.html) ·
[Presenter review demo](ActionRelay-review/actionrelay-demo-beats.html) ·
[Prior deadline MP4](ActionRelay-v2/actionrelay-demo.mp4)
