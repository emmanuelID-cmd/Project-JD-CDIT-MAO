# Render Free synthetic demo

This setup runs the existing FastAPI app on a Render Free web service with a
temporary SQLite database. It is for demonstrations with synthetic data only.
Render Free has no persistent disk or service Shell, and its filesystem is
discarded on restart, spin-down, and redeploy. Ticket edits and account changes
will therefore reset. The service also spins down after 15 minutes without
traffic.

## Render service settings

- **Repository:** `emmanuelID-cmd/Project-JD-CDIT-MAO`
- **Branch:** `developer`
- **Root directory:** leave blank
- **Runtime:** Python 3
- **Build command:** `python -m pip install .`
- **Start command:** `python -m cdit_support_mao.render_free_bootstrap && uvicorn cdit_support_mao.main:app --app-dir src --host 0.0.0.0 --port $PORT`
- **Health check path:** `/health`

Set these environment variables in the Render service:

| Key | Value |
| --- | --- |
| `PYTHON_VERSION` | `3.13.5` |
| `CDIT_DATABASE_PATH` | `/tmp/cdit_support.db` |
| `ACTIONRELAY_RENDER_FREE_BOOTSTRAP` | `1` |
| `ACTIONRELAY_DEMO_USER_PASSWORD` | A unique synthetic demo password, 12–128 characters |
| `ACTIONRELAY_DEMO_STAFF_PASSWORD` | A unique synthetic demo password, 12–128 characters |
| `ACTIONRELAY_DEMO_AUDITOR_PASSWORD` | A unique synthetic demo password, 12–128 characters |
| `ACTIONRELAY_DEMO_ADMIN_PASSWORD` | A unique synthetic demo password, 12–128 characters |
| `CDIT_TRIAGE_MODEL` | `claude-sonnet-5-5` |
| `ACTIONRELAY_ENABLE_LIVE_TRIAGE` | `1` only when live synthetic Triage is wanted; otherwise `0` |
| `ANTHROPIC_API_KEY` | Optional Render secret; required for live Claude calls |

The startup command applies packaged migrations, seeds the synthetic catalog,
and sets credentials for `user.demo`, `staff.demo`, `auditor.demo`, and
`admin.demo`. It does not print password values. Keep passwords and the API key
in Render environment secrets, never in Git or in this document.

The Claude adapter uses Render environment variables first, with the ignored
local `.env` as a development fallback. Each live Triage run still requires
explicit in-app authorization, and the current integration accepts only its
approved synthetic examples. A successful deployment does not mean the full
six-agent workflow is connected.

## What resets

Render Free deletes local filesystem changes on service restart, spin-down, and
redeploy. The startup command recreates the example data and reactivates the
four demo accounts on each boot; ticket edits, account changes, sessions, and
agent-run history are not durable. Do not enter CDIT, employee, customer, or
other personal data. This is not a production deployment.
