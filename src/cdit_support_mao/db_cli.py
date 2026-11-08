"""Explicit command-line entry points for the local synthetic SQLite database."""
from __future__ import annotations

import argparse

from cdit_support_mao.config import database_path
from cdit_support_mao.database import initialize_database, purge_expired_metadata, reset_synthetic_data, seed_synthetic_data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "seed", "purge", "reset"))
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
    else:
        if not args.confirm_synthetic_only:
            parser.error("reset requires --confirm-synthetic-only")
        print(f"Reset synthetic rows: {reset_synthetic_data(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
