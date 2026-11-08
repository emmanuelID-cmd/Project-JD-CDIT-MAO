"""SQLite connection, migration, synthetic seed, and retention helpers."""
from __future__ import annotations

import hashlib
import sqlite3
from contextlib import closing
from datetime import datetime, timezone, timedelta
from pathlib import Path

from cdit_support_mao.config import database_path


class MigrationError(RuntimeError):
    """Raised when local schema history is inconsistent with packaged migrations."""


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    """Open a local SQLite database with foreign-key enforcement enabled."""
    target = database_path() if path is None else Path(path)
    if str(target) != ":memory:":
        target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(target), timeout=5.0)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


def _timestamp(value: datetime | None = None) -> str:
    instant = value or datetime.now(timezone.utc)
    if instant.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return instant.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _migration_files() -> list[tuple[int, str, bytes]]:
    root = Path(__file__).with_name("migrations")
    migrations = []
    for path in sorted(root.glob("[0-9][0-9][0-9][0-9]_*.sql")):
        version = int(path.name.split("_", 1)[0])
        migrations.append((version, path.stem, path.read_bytes()))
    if not migrations:
        raise MigrationError("no packaged SQL migrations were found")
    if [row[0] for row in migrations] != list(range(1, len(migrations) + 1)):
        raise MigrationError("migration versions must be contiguous and start at 1")
    return migrations


def initialize_database(path: str | Path | None = None) -> int:
    """Apply pending packaged migrations; reject edits to already-applied migrations."""
    with closing(connect(path)) as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                checksum_sha256 TEXT NOT NULL CHECK(length(checksum_sha256) = 64),
                applied_at TEXT NOT NULL
            )"""
        )
        connection.commit()
        migrations = _migration_files()
        known = {row[0] for row in migrations}
        applied = {row[0] for row in connection.execute("SELECT version FROM schema_migrations")}
        unknown = applied - known
        if unknown:
            raise MigrationError(f"database has unknown migration versions: {sorted(unknown)}")

        for version, name, data in migrations:
            checksum = hashlib.sha256(data).hexdigest()
            row = connection.execute(
                "SELECT name, checksum_sha256 FROM schema_migrations WHERE version = ?",
                (version,),
            ).fetchone()
            if row is not None:
                if row["name"] != name or row["checksum_sha256"] != checksum:
                    raise MigrationError(f"applied migration {version} differs from packaged source")
                continue
            try:
                connection.executescript("BEGIN IMMEDIATE;\n" + data.decode("utf-8"))
                connection.execute(
                    "INSERT INTO schema_migrations(version, name, checksum_sha256, applied_at) VALUES (?, ?, ?, ?)",
                    (version, name, checksum, _timestamp()),
                )
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        return max(known)


def seed_synthetic_data(path: str | Path | None = None, *, now: datetime | None = None) -> dict[str, int]:
    """Create idempotent, non-login-ready sample accounts and clearly synthetic fixtures."""
    initialize_database(path)
    created = _timestamp(now)
    accounts = (
        ("SYN-USER-001", "user.demo", "user"),
        ("SYN-STAFF-001", "staff.demo", "staff"),
        ("SYN-ADMIN-001", "admin.demo", "admin"),
    )
    with closing(connect(path)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        for account_id, username, role in accounts:
            connection.execute(
                """INSERT OR IGNORE INTO synthetic_accounts
                   (account_id, username, role, status, password_hash, created_at, updated_at)
                   VALUES (?, ?, ?, 'setup_required', NULL, ?, ?)""",
                (account_id, username, role, created, created),
            )
        connection.execute(
            """INSERT OR IGNORE INTO synthetic_cases
               (case_id, owner_account_id, subject, request_text, status, urgency_band,
                is_synthetic, created_at, updated_at)
               VALUES (?, ?, ?, ?, 'submitted', 'unknown', 1, ?, ?)""",
            (
                "SYN-CASE-001", "SYN-USER-001", "Synthetic report-export question",
                "SYNTHETIC FIXTURE: I cannot locate the report export control in the demo application.",
                created, created,
            ),
        )
        connection.execute(
            """INSERT OR IGNORE INTO product_health_events
               (event_id, occurred_at, event_type, component, component_version,
                status_code, error_code, duration_ms)
               VALUES (?, ?, 'database_seeded', 'database', '0.1.0', 'ok', NULL, 0)""",
            ("SYN-EVENT-SEED-001", created),
        )
        connection.commit()
    return {"accounts": len(accounts), "cases": 1, "product_health_events": 1}


def _subtract_months(instant: datetime, months: int) -> datetime:
    month_index = instant.year * 12 + instant.month - 1 - months
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    next_month = datetime(year + (month == 12), 1 if month == 12 else month + 1, 1, tzinfo=timezone.utc)
    last_day = (next_month - timedelta(days=1)).day
    return instant.replace(year=year, month=month, day=min(instant.day, last_day))


def purge_expired_metadata(path: str | Path | None = None, *, now: datetime | None = None) -> dict[str, int]:
    """Apply approved metadata retention using an injectable clock for fast tests."""
    initialize_database(path)
    instant = now or datetime.now(timezone.utc)
    if instant.tzinfo is None:
        raise ValueError("retention clock must be timezone-aware")
    instant = instant.astimezone(timezone.utc)
    detailed_cutoff = _timestamp(instant - timedelta(days=30))
    audit_cutoff = _timestamp(instant - timedelta(days=90))
    summary_cutoff = _timestamp(_subtract_months(instant, 12))
    with closing(connect(path)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        counts = {
            "product_health_events": connection.execute(
                "DELETE FROM product_health_events WHERE occurred_at < ?", (detailed_cutoff,)
            ).rowcount,
            "account_access_events": connection.execute(
                "DELETE FROM account_access_events WHERE occurred_at < ?", (audit_cutoff,)
            ).rowcount,
            "product_health_summaries": connection.execute(
                "DELETE FROM product_health_summaries WHERE window_ended_at < ?", (summary_cutoff,)
            ).rowcount,
        }
        connection.commit()
    return counts


def reset_synthetic_data(path: str | Path | None = None) -> dict[str, int]:
    """Delete only allowlisted synthetic application rows, preserving schema history."""
    initialize_database(path)
    tables = (
        "session_extension_alerts", "account_access_events", "sessions",
        "synthetic_cases", "product_health_summaries", "product_health_events",
        "synthetic_accounts",
    )
    with closing(connect(path)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        counts = {}
        for table in tables:
            counts[table] = connection.execute(f"DELETE FROM {table}").rowcount
        connection.commit()
    return counts


def check_database() -> bool:
    """Check that the configured local SQLite database accepts a simple query."""
    with closing(connect()) as connection:
        connection.execute("SELECT 1").fetchone()
    return True
