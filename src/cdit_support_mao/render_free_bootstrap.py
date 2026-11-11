"""Opt-in ephemeral database and synthetic account setup for Render Free."""
from __future__ import annotations

import os
from pathlib import Path

from cdit_support_mao.config import database_path
from cdit_support_mao.database import seed_synthetic_data
from cdit_support_mao.web import provision_synthetic_password


DEMO_ACCOUNTS = (
    ("SYN-USER-001", "ACTIONRELAY_DEMO_USER_PASSWORD"),
    ("SYN-STAFF-001", "ACTIONRELAY_DEMO_STAFF_PASSWORD"),
    ("SYN-AUDITOR-001", "ACTIONRELAY_DEMO_AUDITOR_PASSWORD"),
    ("SYN-ADMIN-001", "ACTIONRELAY_DEMO_ADMIN_PASSWORD"),
)
EXPECTED_DATABASE = Path("/tmp/cdit_support.db")


def main() -> int:
    """Create the demo data only when the explicit Render Free opt-in is set."""
    if os.environ.get("ACTIONRELAY_RENDER_FREE_BOOTSTRAP") != "1":
        raise SystemExit("Render Free bootstrap is disabled; set ACTIONRELAY_RENDER_FREE_BOOTSTRAP=1.")

    configured_database = database_path().resolve()
    if configured_database != EXPECTED_DATABASE:
        raise SystemExit("Render Free bootstrap requires CDIT_DATABASE_PATH=/tmp/cdit_support.db.")

    missing = [name for _, name in DEMO_ACCOUNTS if not os.environ.get(name, "").strip()]
    if missing:
        raise SystemExit("Set these Render demo-password secrets before deploy: " + ", ".join(missing))
    passwords = [os.environ[name] for _, name in DEMO_ACCOUNTS]
    if len(set(passwords)) != len(passwords):
        raise SystemExit("Use a distinct password for each synthetic demo account.")

    seed_synthetic_data(configured_database)
    for account_id, variable in DEMO_ACCOUNTS:
        provision_synthetic_password(account_id, os.environ[variable])

    print("Render Free synthetic database initialized and four demo accounts activated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
