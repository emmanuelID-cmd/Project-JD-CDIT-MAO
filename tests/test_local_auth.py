from datetime import datetime, timezone

import sqlite3
from fastapi.testclient import TestClient

from cdit_support_mao.database import connect, seed_synthetic_data
from cdit_support_mao.main import app
from cdit_support_mao.web import provision_synthetic_password
import cdit_support_mao.web as web


def instant(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def client_with_accounts(tmp_path, monkeypatch):
    path = tmp_path / "auth.sqlite3"
    monkeypatch.setenv("CDIT_DATABASE_PATH", str(path))
    seed_synthetic_data(path, now=instant("2026-11-08T12:00:00Z"))
    for account_id in ("SYN-USER-001", "SYN-STAFF-001", "SYN-ADMIN-001"):
        provision_synthetic_password(account_id, "Synthetic-test-password-2026!")
    client = TestClient(app)
    return path, client


def login(client, username):
    response = client.post("/auth/login", json={"username": username, "password": "Synthetic-test-password-2026!"})
    assert response.status_code == 200
    return response


def test_user_case_scope_and_staff_admin_route_boundaries(tmp_path, monkeypatch):
    path, client = client_with_accounts(tmp_path, monkeypatch)
    assert client.get("/api/cases").status_code == 401
    login(client, "user.demo")
    own = client.post("/api/cases", json={"subject": "Synthetic issue", "request_text": "SYNTHETIC: report export is not visible"})
    assert own.status_code == 201
    case_id = own.json()["case_id"]
    assert client.get("/api/cases/" + case_id).status_code == 200
    assert client.get("/api/admin/accounts").status_code == 403
    assert client.get("/api/product-health").status_code == 403
    with connect(path) as db:
        db.execute(
            "INSERT INTO synthetic_cases(case_id, owner_account_id, subject, request_text, status, urgency_band, is_synthetic, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("SYN-CASE-OTHER", "SYN-STAFF-001", "Private synthetic", "SYNTHETIC: other user data", "submitted", "unknown", 1, "2026-11-08T12:00:00.000000Z", "2026-11-08T12:00:00.000000Z"),
        )
        db.commit()
    assert client.get("/api/cases/SYN-CASE-OTHER").status_code == 404
    client.post("/auth/logout")
    login(client, "staff.demo")
    staff_cases = client.get("/api/cases").json()
    assert len(staff_cases) == 81
    assert "SYN-CASE-OTHER" not in {case["case_id"] for case in staff_cases}
    assert client.get("/api/cases/SYN-CASE-OTHER").status_code == 404
    assert client.patch("/api/cases/SYN-CASE-OTHER/status", json={"status": "in_progress"}).status_code == 404
    assert client.get("/api/admin/accounts").status_code == 403
    client.post("/auth/logout")
    login(client, "admin.demo")
    assert len(client.get("/api/cases").json()) == 83
    assigned = client.patch(
        "/api/admin/cases/SYN-CASE-OTHER/assignment",
        json={"staff_account_id": "SYN-STAFF-001"},
    )
    assert assigned.status_code == 200 and assigned.json()["action"] == "assigned"
    client.post("/auth/logout")
    login(client, "staff.demo")
    staff_cases = client.get("/api/cases").json()
    assert len(staff_cases) == 82
    assert "SYN-CASE-OTHER" in {case["case_id"] for case in staff_cases}


def test_admin_account_change_is_audited_and_revokes_target_session(tmp_path, monkeypatch):
    path, user_client = client_with_accounts(tmp_path, monkeypatch)
    admin_client = TestClient(app)
    login(user_client, "user.demo")
    login(admin_client, "admin.demo")
    changed = admin_client.patch("/api/admin/accounts/SYN-USER-001", json={"status": "suspended"})
    assert changed.status_code == 200
    assert user_client.get("/api/cases").status_code == 401
    with connect(path) as db:
        event = db.execute("SELECT actor_account_id, target_account_id, action, before_status, after_status FROM account_access_events").fetchone()
        assert tuple(event) == ("SYN-ADMIN-001", "SYN-USER-001", "suspend", "active", "suspended")
        assert db.execute("SELECT COUNT(*) FROM sessions WHERE account_id='SYN-USER-001' AND revoked_at IS NOT NULL").fetchone()[0] == 1
    assert admin_client.get("/api/admin/session-extension-alerts").status_code == 200

def test_admin_cannot_activate_account_without_local_password(tmp_path, monkeypatch):
    _path, client = client_with_accounts(tmp_path, monkeypatch)
    login(client, "admin.demo")
    with connect() as db:
        db.execute("UPDATE synthetic_accounts SET status='setup_required', password_hash=NULL WHERE account_id='SYN-STAFF-001'")
        db.commit()
    response = client.patch("/api/admin/accounts/SYN-STAFF-001", json={"status": "active"})
    assert response.status_code == 409


def test_session_warnings_and_extension_alert_do_not_extend_absolute_session(tmp_path, monkeypatch):
    path, client = client_with_accounts(tmp_path, monkeypatch)
    current = [instant("2026-11-08T12:00:00Z")]
    monkeypatch.setattr(web, "now_utc", lambda: current[0])
    login(client, "user.demo")
    current[0] += web.timedelta(minutes=16)
    warning15 = client.get("/auth/session").json()
    assert warning15["warning"] == "15m" and warning15["remaining_seconds"] == 14 * 60
    current[0] += web.timedelta(minutes=11)
    warning5 = client.get("/auth/session").json()
    assert warning5["warning"] == "5m"
    absolute_before = warning5["absolute_expires_at"]
    requested = client.post("/auth/extension-request").json()
    assert requested["session_extended"] is False
    with connect(path) as db:
        alert = db.execute("SELECT alert_id, review_status FROM session_extension_alerts").fetchone()
        assert tuple(alert) == (requested["alert_id"], "new")
    client.post("/auth/logout")
    login(client, "admin.demo")
    reviewed = client.patch("/api/admin/session-extension-alerts/" + requested["alert_id"] + "/review")
    assert reviewed.json()["review_status"] == "reviewed"
    assert reviewed.json()["session_extended"] is False
    assert absolute_before != ""


def test_idle_timeout_expires_without_polling_extending_it(tmp_path, monkeypatch):
    _path, client = client_with_accounts(tmp_path, monkeypatch)
    current = [instant("2026-11-08T12:00:00Z")]
    monkeypatch.setattr(web, "now_utc", lambda: current[0])
    login(client, "user.demo")
    current[0] += web.timedelta(minutes=31)
    assert client.get("/auth/session").json() == {"authenticated": False}
    assert client.get("/api/cases").status_code == 401
