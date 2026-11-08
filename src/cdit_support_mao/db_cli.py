"""Explicit command-line entry points for the local synthetic SQLite database."""
from __future__ import annotations

import argparse
from getpass import getpass

from cdit_support_mao.config import database_path
from cdit_support_mao.database import initialize_database, purge_expired_metadata, reset_synthetic_data, seed_synthetic_data
from cdit_support_mao.web import provision_synthetic_password


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "seed", "purge", "reset", "set-password"))
    parser.add_argument("account_id", nargs="?")
    parser.add_argument("--confirm-synthetic-only", action="store_true")
    args = parser.parse_args()
    path = database_path()
    if args.command == "init":
        version = initialize_database(path)
        print(f"Initialized local SQLite schema version {version} at {path}")
    elif args.command == "seed":
        print(f"Seeded: {seed_synthetic_data(path)}")
    elif args.command == "purge":
        print(f"Purged expired metadata rows: {purge_expired_metadata(path)}")
    elif args.command == "reset":
        if not args.confirm_synthetic_only:
            parser.error("reset requires --confirm-synthetic-only")
        print(f"Reset synthetic rows: {reset_synthetic_data(path)}")
    else:
        if not args.account_id:
            parser.error("set-password requires a synthetic account_id")
        first = getpass("Synthetic local password (12-128 characters): ")
        second = getpass("Repeat password: ")
        if first != second:
            parser.error("passwords did not match")
        try:
            provision_synthetic_password(args.account_id, first)
        except ValueError as exc:
            parser.error(str(exc))
        print(f"Local synthetic credential configured for {args.account_id}. No password was displayed or stored in plaintext.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
