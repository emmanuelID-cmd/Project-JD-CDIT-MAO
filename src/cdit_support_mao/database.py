"""SQLite connection, migration, synthetic seed, and retention helpers."""
from __future__ import annotations

import hashlib
import json
import random
import sqlite3
from contextlib import closing
from datetime import datetime, timezone, timedelta
from pathlib import Path

from cdit_support_mao.config import database_path


class MigrationError(RuntimeError):
    """Raised when local schema history is inconsistent with packaged migrations."""


_COMPACT_CATEGORY_ROWS = {
    "Safety & Wellbeing": {1, 2, 3, 11, 13, 41},
    "Privacy, Security & Access": {4, 5, 15, 34, 35, 36, 37, 50, 75, 77},
    "Payroll, Benefits & Expenses": {6, 7, 8, 16, 17, 18, 19, 20, 42, 47, 51, 52, 53, 54, 55},
    "Technical Issues & Outages": {9, 14, 33, 74, 76},
    "Scheduling & Leave": {10, 21, 22, 23, 24, 48, 56, 57, 58, 69, 70},
    "Compliance & Legal": {12, 38, 39, 40, 43},
    "HR & Workplace Relations": {25, 26, 27, 28, 29, 30, 44, 59, 60, 63, 65, 66, 67, 68, 79, 80},
    "Customer Service & Feedback": {31, 32, 45, 49, 71, 72, 73, 78},
    "Forms & Documents": {46, 61, 62, 64},
}
_CATEGORY_BY_ROW = {
    row_number: category
    for category, rows in _COMPACT_CATEGORY_ROWS.items()
    for row_number in rows
}
_DEVELOPMENT_STATUS_COUNTS = {
    "submitted": 48,
    "in_progress": 96,
    "waiting_on_customer": 48,
    "under_investigation": 48,
    "escalated": 32,
    "resolved": 88,
    "closed": 40,
}


# One earlier local v2 migration used different source bytes but created this exact schema.
# Accept only that recorded checksum and only after verifying the complete structural signature.
_LEGACY_MIGRATION_CHECKSUMS = {
    2: {"b200a572c5f07a3cf4fbd2108a608582426b8a804fa422c12d2f383da81523d8"},
}


def _matches_legacy_case_catalog_schema(connection: sqlite3.Connection) -> bool:
    required_columns = {
        "synthetic_cases": {"record_kind", "category", "catalog_id", "closure_reason"},
        "synthetic_case_catalog": {
            "catalog_id", "row_number", "category", "example_query", "default_band",
            "rationale", "source_document", "source_version", "is_synthetic",
        },
        "synthetic_case_change_events": {
            "event_id", "case_id", "actor_account_id", "action", "before_status",
            "after_status", "subject_changed", "request_text_changed", "reason_code", "occurred_at",
        },
    }
    for table, expected in required_columns.items():
        actual = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
        if not expected.issubset(actual):
            return False
    required_objects = {
        "synthetic_case_catalog_band_idx", "synthetic_case_change_events_case_time_idx",
        "synthetic_cases_kind_status_idx",
        "synthetic_case_catalog_kind_insert", "synthetic_case_catalog_kind_update",
    }
    actual_objects = {
        row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
        )
    }
    return required_objects.issubset(actual_objects)

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


def _development_case_specs(catalog_rows: list[dict], now: datetime) -> list[dict]:
    """Build 400 reproducible synthetic tickets dated over the prior three years."""
    rng = random.Random(20261111)
    specs = []
    for copy_index in range(5):
        for example in catalog_rows:
            row = example["row_number"]
            sequence = copy_index * len(catalog_rows) + row
            case_id = f"SYN-CASE-EX-{row:03d}" if copy_index == 0 else f"SYN-CASE-EX-{row:03d}-R{copy_index + 1}"
            issue_label = example.get("issue_label", example["category"])
            variants = (
                example["example_query"],
                "Could you help me with this? " + example["example_query"],
                "I need assistance with the following: " + example["example_query"],
                example["example_query"] + " Please let me know the next step.",
                "Can I get help with this? " + example["example_query"],
            )
            specs.append({
                "row": row, "sequence": sequence, "case_id": case_id,
                "issue_label": issue_label, "category": example["category"],
                "catalog_id": example["catalog_id"], "band": example["default_band"],
                "request_text": variants[copy_index],
                "subject": f"Example {row:02d}: {issue_label}" if copy_index == 0
                           else f"Repeat {sequence:03d}: {issue_label}",
            })
    statuses = [status for status, count in _DEVELOPMENT_STATUS_COUNTS.items() for _ in range(count)]
    rng.shuffle(statuses)
    if statuses[0] != "submitted":
        replacement = statuses.index("submitted", 1)
        statuses[0], statuses[replacement] = statuses[replacement], statuses[0]
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    latest_start = now.astimezone(timezone.utc) - timedelta(days=45)
    day_span = max(1, (latest_start.date() - start.date()).days)
    for spec, status in zip(specs, statuses, strict=True):
        unknown_classification = spec["sequence"] % 10 == 0
        if unknown_classification:
            status = "submitted" if spec["sequence"] % 20 == 0 else "in_progress"
            spec["category"] = None
            spec["band"] = "unknown"
        created = start + timedelta(days=rng.randrange(day_span), seconds=rng.randrange(86400))
        spec["created"] = created
        spec["status"] = status
        spec["assignee"] = "SYN-AUDITOR-001" if spec["sequence"] % 2 == 0 else "SYN-STAFF-001"
        spec["history"] = []
        if status == "in_progress":
            path = ["in_progress"]
        elif status == "waiting_on_customer":
            path = ["in_progress", "waiting_on_customer"]
        elif status == "under_investigation":
            path = ["in_progress", "under_investigation"]
        elif status == "escalated":
            path = ["in_progress", "escalated"]
        elif status == "resolved":
            path = ["in_progress", "resolved"]
        elif status == "closed":
            path = ["in_progress", "resolved", "closed"]
        else:
            path = []
        prior = "submitted"
        at = created
        for index, next_status in enumerate(path):
            at += timedelta(days=rng.randint(1, 7), hours=rng.randint(0, 20))
            spec["history"].append((prior, next_status, at, index))
            prior = next_status
        spec["updated"] = at
    return specs


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
                    compatible_legacy = (
                        row["name"] == name
                        and row["checksum_sha256"] in _LEGACY_MIGRATION_CHECKSUMS.get(version, set())
                        and version == 2
                        and _matches_legacy_case_catalog_schema(connection)
                    )
                    if not compatible_legacy:
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
        ("SYN-AUDITOR-001", "auditor.demo", "staff"),
        ("SYN-ADMIN-001", "admin.demo", "admin"),
    )
    with closing(connect(path)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        for account_id, username, role in accounts:
            connection.execute(
                """INSERT OR IGNORE INTO synthetic_accounts
                   (account_id, username, role, status, password_hash, created_at, updated_at, auditor_access)
                   VALUES (?, ?, ?, 'setup_required', NULL, ?, ?, ?)""",
                (account_id, username, role, created, created, int(account_id == "SYN-AUDITOR-001")),
            )
        initial_case = connection.execute(
            """INSERT OR IGNORE INTO synthetic_cases
               (case_id, owner_account_id, subject, request_text, status, urgency_band, is_synthetic, created_at, updated_at)
               VALUES (?, ?, ?, ?, 'submitted', 'unknown', 1, ?, ?)""",
            (
                "SYN-CASE-001", "SYN-USER-001", "Synthetic report-export question",
                "SYNTHETIC FIXTURE: I cannot locate the report export control in the demo application.",
                created, created,
            ),
        )
        if initial_case.rowcount == 1:
            connection.execute(
                """INSERT OR IGNORE INTO synthetic_case_change_events
                   (event_id, case_id, actor_account_id, action, before_status, after_status, reason_code, occurred_at)
                   VALUES (?, ?, ?, 'user_submitted', NULL, 'submitted', 'initial_submission', ?)""",
                ("EV-CASE-001-INIT", "SYN-CASE-001", "SYN-USER-001", created),
            )
        catalog_path = Path(__file__).parent / "catalogs" / "case-condition-catalog-v2.json"
        catalog_rows = json.loads(catalog_path.read_text(encoding="utf-8"))
        for example in catalog_rows:
            connection.execute(
                """INSERT INTO synthetic_case_catalog
                   (catalog_id, row_number, category, example_query, default_band, rationale,
                    source_document, source_version, is_synthetic)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                   ON CONFLICT(catalog_id) DO UPDATE SET
                     category=excluded.category,
                     example_query=excluded.example_query,
                     default_band=excluded.default_band,
                     rationale=excluded.rationale,
                     source_version=excluded.source_version""",
                (
                    example["catalog_id"], example["row_number"], example["category"],
                    example["example_query"], example["default_band"], example["rationale"],
                    example["source_document"], example["source_version"],
                ),
            )
        for spec in _development_case_specs(catalog_rows, now or datetime.now(timezone.utc)):
            case_id = spec["case_id"]
            existing = connection.execute(
                "SELECT status, created_at, updated_at, assigned_staff_account_id FROM synthetic_cases WHERE case_id = ?",
                (case_id,),
            ).fetchone()
            if existing:
                connection.execute(
                    "UPDATE synthetic_cases SET category = ? WHERE case_id = ? AND record_kind = 'development_example'",
                    (spec["category"], case_id),
                )
            event_rows = connection.execute(
                "SELECT event_id, action FROM synthetic_case_change_events WHERE case_id = ? ORDER BY occurred_at, event_id",
                (case_id,),
            ).fetchall()
            pristine_seed = bool(
                existing
                and existing["status"] == "submitted"
                and len(event_rows) == 1
                and event_rows[0]["action"] == "example_seeded"
                and not connection.execute("SELECT 1 FROM synthetic_auditor_decisions WHERE case_id = ? LIMIT 1", (case_id,)).fetchone()
                and not connection.execute("SELECT 1 FROM synthetic_case_responses WHERE case_id = ? LIMIT 1", (case_id,)).fetchone()
            )
            if existing is None:
                connection.execute(
                    """INSERT INTO synthetic_cases
                       (case_id, owner_account_id, subject, request_text, status, urgency_band,
                        is_synthetic, created_at, updated_at, record_kind, category, catalog_id,
                        assigned_staff_account_id, closure_reason)
                       VALUES (?, 'SYN-STAFF-001', ?, ?, ?, ?, 1, ?, ?, 'development_example', ?, ?, ?, ?)""",
                    (case_id, spec["subject"], spec["request_text"], spec["status"], spec["band"],
                     _timestamp(spec["created"]), _timestamp(spec["updated"]), spec["category"],
                     spec["catalog_id"], spec["assignee"], "staff_closed" if spec["status"] == "closed" else None),
                )
                connection.execute(
                    """INSERT INTO synthetic_case_change_events
                       (event_id, case_id, actor_account_id, action, before_status, after_status, reason_code, occurred_at)
                       VALUES (?, ?, 'SYN-STAFF-001', 'example_seeded', NULL, 'submitted', 'synthetic_catalog_seed', ?)""",
                    (f"EV-{case_id}-INIT", case_id, _timestamp(spec["created"])),
                )
                if spec["assignee"]:
                    connection.execute(
                        """INSERT INTO synthetic_case_assignment_events
                           (event_id, case_id, actor_account_id, previous_staff_account_id,
                            assigned_staff_account_id, action, occurred_at)
                           VALUES (?, ?, NULL, NULL, ?, 'seed_assigned', ?)""",
                        ("CASE-ASG-SEED-" + case_id, case_id, spec["assignee"], _timestamp(now)),
                    )
            elif pristine_seed:
                connection.execute(
                    """UPDATE synthetic_cases
                       SET subject=?, request_text=?, status=?, urgency_band=?, created_at=?, updated_at=?,
                           category=?, catalog_id=?, closure_reason=? WHERE case_id=?""",
                    (spec["subject"], spec["request_text"], spec["status"], spec["band"],
                     _timestamp(spec["created"]), _timestamp(spec["updated"]), spec["category"],
                     spec["catalog_id"], "staff_closed" if spec["status"] == "closed" else None, case_id),
                )
                connection.execute(
                    "UPDATE synthetic_case_change_events SET occurred_at = ? WHERE event_id = ?",
                    (_timestamp(spec["created"]), event_rows[0]["event_id"]),
                )
                for before, after, at, transition_index in spec["history"]:
                    connection.execute(
                        """INSERT OR IGNORE INTO synthetic_case_change_events
                           (event_id, case_id, actor_account_id, action, before_status, after_status, reason_code, occurred_at)
                           VALUES (?, ?, 'SYN-STAFF-001', 'staff_status_updated', ?, ?, 'human_status_change', ?)""",
                        (f"EV-{case_id}-{transition_index + 1}", case_id, before, after, _timestamp(at)),
                    )
            # Reassign only previously seeded fixtures. Preserve any later Admin decision.
            assignment = connection.execute(
                "SELECT assigned_staff_account_id FROM synthetic_cases WHERE case_id = ?", (case_id,)
            ).fetchone()[0]
            if existing is not None and assignment == "SYN-STAFF-001" and spec["assignee"] == "SYN-AUDITOR-001":
                latest_assignment = connection.execute(
                    "SELECT action FROM synthetic_case_assignment_events WHERE case_id = ? ORDER BY occurred_at DESC, event_id DESC LIMIT 1",
                    (case_id,),
                ).fetchone()
                if latest_assignment and latest_assignment["action"] == "seed_assigned":
                    assignment_stamp = _timestamp(now)
                    connection.execute(
                        "UPDATE synthetic_cases SET assigned_staff_account_id = ? WHERE case_id = ?",
                        (spec["assignee"], case_id),
                    )
                    connection.execute(
                        """INSERT INTO synthetic_case_assignment_events
                           (event_id, case_id, actor_account_id, previous_staff_account_id,
                            assigned_staff_account_id, action, occurred_at)
                           VALUES (?, ?, 'SYN-ADMIN-001', 'SYN-STAFF-001', ?, 'reassigned', ?)""",
                        ("CASE-ASG-REBALANCE-" + case_id, case_id, spec["assignee"], assignment_stamp),
                    )
        initial_assignments = connection.execute(
            """SELECT case_id FROM synthetic_cases c
               WHERE c.assigned_staff_account_id IS NULL
                 AND (c.case_id = 'SYN-CASE-001' OR c.record_kind = 'development_example')
                 AND NOT EXISTS (
                     SELECT 1 FROM synthetic_case_assignment_events e WHERE e.case_id = c.case_id
                 )
               ORDER BY c.case_id"""
        ).fetchall()
        for row in initial_assignments:
            connection.execute(
                "UPDATE synthetic_cases SET assigned_staff_account_id = 'SYN-STAFF-001' WHERE case_id = ?",
                (row["case_id"],),
            )
            connection.execute(
                """INSERT INTO synthetic_case_assignment_events
                   (event_id, case_id, actor_account_id, previous_staff_account_id,
                    assigned_staff_account_id, action, occurred_at)
                   VALUES (?, ?, NULL, NULL, 'SYN-STAFF-001', 'seed_assigned', ?)""",
                ("CASE-ASG-SEED-" + row["case_id"], row["case_id"], created),
            )
        connection.execute(
            """INSERT OR IGNORE INTO product_health_events
               (event_id, occurred_at, event_type, component, component_version,
                status_code, error_code, duration_ms)
               VALUES (?, ?, 'database_seeded', 'database', '0.1.0', 'ok', NULL, 0)""",
            ("SYN-EVENT-SEED-001", created),
        )
        connection.commit()
    return {"accounts": len(accounts), "cases": 1 + len(catalog_rows) * 5, "catalog_examples": len(catalog_rows) * 5, "product_health_events": 1}


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
        "synthetic_case_assignment_events", "actionrelay_auditor_feedback",
        "actionrelay_runs", "actionrelay_review_runs", "actionrelay_ticket_outcomes",
        "synthetic_auditor_decisions", "synthetic_case_responses",
        "synthetic_case_change_events", "synthetic_cases", "synthetic_case_catalog",
        "product_health_summaries", "product_health_events",
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
