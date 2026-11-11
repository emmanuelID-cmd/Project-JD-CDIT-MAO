from fastapi.testclient import TestClient

from cdit_support_mao.database import connect, seed_synthetic_data
from cdit_support_mao.main import app
from cdit_support_mao.web import provision_synthetic_password


PASSWORD = "Synthetic-lifecycle-password-2026!"


def make_client(tmp_path, monkeypatch, role):
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "cases.sqlite3"
    monkeypatch.setenv("CDIT_DATABASE_PATH", str(path))
    seed_synthetic_data(path)
    account_id = {"user": "SYN-USER-001", "staff": "SYN-STAFF-001", "admin": "SYN-ADMIN-001"}[role]
    provision_synthetic_password(account_id, PASSWORD)
    client = TestClient(app)
    response = client.post("/auth/login", json={"username": role + ".demo", "password": PASSWORD})
    assert response.status_code == 200
    return path, client


def test_eighty_examples_visible_to_staff_admin_but_not_client(tmp_path, monkeypatch):
    _path, client = make_client(tmp_path / "user", monkeypatch, "user")
    user_cases = client.get("/api/cases").json()
    assert len(user_cases) == 1
    assert user_cases[0]["record_kind"] == "user_request"
    assert all(case["record_kind"] != "development_example" for case in user_cases)

    _path, staff = make_client(tmp_path / "staff", monkeypatch, "staff")
    staff_cases = staff.get("/api/cases").json()
    examples = [case for case in staff_cases if case["record_kind"] == "development_example"]
    assert len(examples) == 80
    assert examples[0]["catalog_id"] == "SYN-CAT-001"
    assert examples[-1]["catalog_id"] == "SYN-CAT-080"

    _path, admin = make_client(tmp_path / "admin", monkeypatch, "admin")
    assert len([case for case in admin.get("/api/cases").json() if case["record_kind"] == "development_example"]) == 80


def test_user_can_edit_only_before_review_then_cancel_unresolved(tmp_path, monkeypatch):
    path, user = make_client(tmp_path, monkeypatch, "user")
    staff_path, staff = make_client(tmp_path, monkeypatch, "staff")
    assert path == staff_path
    edited = user.patch("/api/cases/SYN-CASE-001", json={"subject": "Corrected synthetic title"})
    assert edited.status_code == 200

    started = staff.patch("/api/cases/SYN-CASE-001/status", json={"status": "in_progress"})
    assert started.status_code == 200
    visible = user.get("/api/cases/SYN-CASE-001").json()
    assert visible["status"] == "in_progress"
    assert visible["display_status"] == "in_review"
    assert visible["can_edit"] is False and visible["can_cancel"] is True

    denied_edit = user.patch("/api/cases/SYN-CASE-001", json={"request_text": "Late edit"})
    assert denied_edit.status_code == 409
    cancelled = user.post("/api/cases/SYN-CASE-001/cancel")
    assert cancelled.status_code == 200
    assert cancelled.json()["withdrawal_requested"] is True
    final = user.get("/api/cases/SYN-CASE-001").json()
    assert final["status"] == "in_progress" and final["can_cancel"] is False
    assert final["withdrawal_requested_at"]

    with connect(path) as db:
        events = db.execute(
            "SELECT action, before_status, after_status FROM synthetic_case_change_events WHERE case_id = 'SYN-CASE-001' ORDER BY occurred_at, event_id"
        ).fetchall()
        actions = [event["action"] for event in events]
        assert "user_edited" in actions
        assert "staff_status_updated" in actions
        assert "requester_cancelled" in actions


def test_staff_can_change_example_status_and_edit_is_audited(tmp_path, monkeypatch):
    path, staff = make_client(tmp_path, monkeypatch, "staff")
    case_id = "SYN-CASE-EX-001"
    changed = staff.patch("/api/cases/" + case_id + "/status", json={"status": "in_progress"})
    assert changed.status_code == 200
    edited = staff.patch("/api/cases/" + case_id, json={"subject": "Revised synthetic example"})
    assert edited.status_code == 200
    with connect(path) as db:
        row = db.execute("SELECT status, subject, record_kind FROM synthetic_cases WHERE case_id = ?", (case_id,)).fetchone()
        assert tuple(row) == ("in_progress", "Revised synthetic example", "development_example")
        events = db.execute(
            "SELECT action, subject_changed FROM synthetic_case_change_events WHERE case_id = ? ORDER BY occurred_at",
            (case_id,),
        ).fetchall()
        assert any(row["action"] == "staff_status_updated" for row in events)
        assert any(row["action"] == "staff_edited" and row["subject_changed"] == 1 for row in events)


def test_case_status_transitions_fail_closed_and_admin_can_reopen_resolved_case(tmp_path, monkeypatch):
    path, admin = make_client(tmp_path, monkeypatch, "admin")
    impossible = admin.patch("/api/cases/SYN-CASE-001/status", json={"status": "resolved"})
    assert impossible.status_code == 409
    started = admin.patch("/api/cases/SYN-CASE-001/status", json={"status": "in_progress"})
    assert started.status_code == 200
    assert admin.patch("/api/cases/SYN-CASE-001/status", json={"status": "resolved"}).status_code == 409
    with connect(path) as db:
        db.execute("UPDATE synthetic_cases SET category = 'Forms', urgency_band = 'low' WHERE case_id = 'SYN-CASE-001'")
    resolved = admin.patch("/api/cases/SYN-CASE-001/status", json={"status": "resolved"})
    assert resolved.status_code == 200
    reopened = admin.patch("/api/cases/SYN-CASE-001/status", json={"status": "in_progress"})
    assert reopened.status_code == 200
    closed = admin.patch("/api/cases/SYN-CASE-001/status", json={"status": "closed"})
    assert closed.status_code == 200
    cannot_reopen_closed = admin.patch("/api/cases/SYN-CASE-001/status", json={"status": "in_progress"})
    assert cannot_reopen_closed.status_code == 409
