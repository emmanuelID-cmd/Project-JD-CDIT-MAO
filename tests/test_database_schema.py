from datetime import datetime
import sqlite3

import pytest

from cdit_support_mao.database import (
    MigrationError,
    connect,
    initialize_database,
    purge_expired_metadata,
    reset_synthetic_data,
    seed_synthetic_data,
)


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def test_migration_is_idempotent_and_enables_required_tables(tmp_path):
    path = tmp_path / "local.sqlite3"
    assert initialize_database(path) == 4
    assert initialize_database(path) == 4
    with connect(path) as db:
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"schema_migrations", "synthetic_accounts", "sessions", "synthetic_cases", "product_health_events", "product_health_summaries", "account_access_events", "session_extension_alerts", "synthetic_case_catalog", "synthetic_case_change_events", "synthetic_auditor_decisions", "synthetic_case_assignment_events"} <= tables
        assert "assigned_staff_account_id" in {r[1] for r in db.execute("PRAGMA table_info(synthetic_cases)")}
        assert "admin_override_reason" in {r[1] for r in db.execute("PRAGMA table_info(synthetic_auditor_decisions)")}
        assert db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 4


def test_seed_is_synthetic_idempotent_and_product_health_has_no_content_fields(tmp_path):
    path = tmp_path / "seed.sqlite3"
    seed_synthetic_data(path, now=instant("2026-11-08T12:00:00Z"))
    seed_synthetic_data(path, now=instant("2026-11-08T12:01:00Z"))
    with connect(path) as db:
        accounts = db.execute("SELECT role, status, password_hash FROM synthetic_accounts ORDER BY role").fetchall()
        assert [(r["role"], r["status"], r["password_hash"]) for r in accounts] == [
            ("admin", "setup_required", None), ("staff", "setup_required", None), ("user", "setup_required", None)
        ]
        case = db.execute("SELECT request_text, is_synthetic FROM synthetic_cases WHERE case_id='SYN-CASE-001'").fetchone()
        assert case["is_synthetic"] == 1 and case["request_text"].startswith("SYNTHETIC FIXTURE:")
        assignments = db.execute(
            "SELECT COUNT(*) FROM synthetic_case_assignment_events WHERE action='seed_assigned'"
        ).fetchone()[0]
        assert assignments == 81
        assert db.execute(
            "SELECT COUNT(*) FROM synthetic_cases WHERE assigned_staff_account_id='SYN-STAFF-001'"
        ).fetchone()[0] == 81
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            db.execute(
                "UPDATE synthetic_case_assignment_events SET action='assigned' WHERE event_id LIKE 'CASE-ASG-SEED-%'"
            )
        db.execute(
            "UPDATE synthetic_cases SET assigned_staff_account_id = NULL WHERE case_id='SYN-CASE-EX-001'"
        )
        db.execute(
            """INSERT INTO synthetic_case_assignment_events
             (event_id, case_id, actor_account_id, previous_staff_account_id, assigned_staff_account_id, action, occurred_at)
             VALUES ('CASE-ASG-TEST-UNASSIGN', 'SYN-CASE-EX-001', 'SYN-ADMIN-001', 'SYN-STAFF-001', NULL, 'unassigned', '2026-11-08T12:00:00.000000Z')"""
        )
        db.commit()
    seed_synthetic_data(path, now=instant("2026-11-08T12:02:00Z"))
    with connect(path) as db:
        assert db.execute(
            "SELECT assigned_staff_account_id FROM synthetic_cases WHERE case_id='SYN-CASE-EX-001'"
        ).fetchone()[0] is None
        event = db.execute("SELECT * FROM product_health_events").fetchone()
        columns = {r["name"] for r in db.execute("PRAGMA table_info(product_health_events)")}
        assert {"event_id", "occurred_at", "event_type", "component", "component_version", "status_code", "error_code", "duration_ms"} == columns
        assert "request_text" not in columns and "prompt" not in columns and "payload" not in columns
        assert event["event_id"] == "SYN-EVENT-SEED-001"
        assert db.execute("SELECT COUNT(*) FROM synthetic_cases").fetchone()[0] == 81
        assert db.execute("SELECT COUNT(*) FROM synthetic_case_catalog").fetchone()[0] == 80


def test_schema_constraints_reject_non_synthetic_case_and_active_without_password(tmp_path):
    path = tmp_path / "constraints.sqlite3"
    seed_synthetic_data(path)
    with connect(path) as db:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO synthetic_cases(case_id, owner_account_id, subject, request_text, status, urgency_band, is_synthetic, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("BAD-1", "SYN-USER-001", "x", "synthetic", "submitted", "unknown", 0, "2026-01-01T00:00:00.000000Z", "2026-01-01T00:00:00.000000Z"),
            )
        with pytest.raises(sqlite3.IntegrityError):
            db.execute(
                "INSERT INTO synthetic_accounts(account_id, username, role, status, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("SYN-X", "x.user", "user", "active", None, "2026-01-01T00:00:00.000000Z", "2026-01-01T00:00:00.000000Z"),
            )


def test_retention_uses_accelerated_clock_and_correct_buckets(tmp_path):
    path = tmp_path / "retention.sqlite3"
    seed_synthetic_data(path, now=instant("2025-01-01T00:00:00Z"))
    with connect(path) as db:
        db.execute(
            "INSERT INTO product_health_events(event_id, occurred_at, event_type, component, component_version, status_code) VALUES (?, ?, ?, ?, ?, ?)",
            ("PH-OLD", "2026-10-08T11:59:59.000000Z", "auth_denied", "auth", "0.1.0", "blocked"),
        )
        db.execute(
            "INSERT INTO product_health_events(event_id, occurred_at, event_type, component, component_version, status_code) VALUES (?, ?, ?, ?, ?, ?)",
            ("PH-KEEP", "2026-10-09T12:00:00.000000Z", "auth_denied", "auth", "0.1.0", "blocked"),
        )
        db.execute(
            "INSERT INTO account_access_events(event_id, actor_account_id, target_account_id, action, occurred_at) VALUES (?, ?, ?, ?, ?)",
            ("AUD-OLD", "SYN-ADMIN-001", "SYN-USER-001", "suspend", "2026-08-10T11:59:59.000000Z"),
        )
        db.execute(
            "INSERT INTO account_access_events(event_id, actor_account_id, target_account_id, action, occurred_at) VALUES (?, ?, ?, ?, ?)",
            ("AUD-KEEP", "SYN-ADMIN-001", "SYN-USER-001", "suspend", "2026-08-10T12:00:00.000000Z"),
        )
        db.execute(
            "INSERT INTO product_health_summaries(summary_id, window_started_at, window_ended_at, component, component_version, event_count, failure_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("SUM-OLD", "2025-11-07T11:59:59.000000Z", "2025-11-07T11:59:59.000000Z", "auth", "0.1.0", 1, 0),
        )
        db.commit()
    counts = purge_expired_metadata(path, now=instant("2026-11-08T12:00:00Z"))
    assert counts == {"product_health_events": 2, "account_access_events": 1, "product_health_summaries": 1}
    with connect(path) as db:
        assert db.execute("SELECT event_id FROM product_health_events WHERE event_id='PH-KEEP'").fetchone()
        assert db.execute("SELECT event_id FROM account_access_events WHERE event_id='AUD-KEEP'").fetchone()
        assert db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 4


def test_reset_deletes_only_allowlisted_synthetic_rows_and_preserves_schema(tmp_path):
    path = tmp_path / "reset.sqlite3"
    seed_synthetic_data(path)
    counts = reset_synthetic_data(path)
    assert counts["synthetic_accounts"] == 3
    assert counts["synthetic_cases"] == 81
    assert counts["synthetic_case_catalog"] == 80
    assert counts["synthetic_case_assignment_events"] == 81
    with connect(path) as db:
        assert db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 4
        assert db.execute("SELECT COUNT(*) FROM synthetic_cases").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM synthetic_case_catalog").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM synthetic_case_assignment_events").fetchone()[0] == 0


def test_known_legacy_case_catalog_checksum_requires_complete_schema_signature(tmp_path):
    path = tmp_path / "legacy-catalog.sqlite3"
    initialize_database(path)
    with connect(path) as db:
        db.execute(
            "UPDATE schema_migrations SET checksum_sha256 = ? WHERE version = 2",
            ("b200a572c5f07a3cf4fbd2108a608582426b8a804fa422c12d2f383da81523d8",),
        )
        db.commit()
    assert initialize_database(path) == 4
    with connect(path) as db:
        db.execute("DROP INDEX synthetic_cases_kind_status_idx")
        db.commit()
    with pytest.raises(MigrationError, match="differs from packaged source"):
        initialize_database(path)
