from fastapi.testclient import TestClient

from cdit_support_mao.database import connect, seed_synthetic_data
from cdit_support_mao.main import app
from cdit_support_mao.web import provision_synthetic_password


PASSWORD = "Synthetic-assignment-password-2026!"


def login(path, role, account_id=None, username=None):
    account_id = account_id or {"user": "SYN-USER-001", "staff": "SYN-STAFF-001", "admin": "SYN-ADMIN-001"}[role]
    username = username or role + ".demo"
    provision_synthetic_password(account_id, PASSWORD)
    client = TestClient(app)
    response = client.post("/auth/login", json={"username": username, "password": PASSWORD})
    assert response.status_code == 200
    return client


def test_admin_assignment_scopes_staff_and_records_history(tmp_path, monkeypatch):
    path = tmp_path / "assignments.sqlite3"
    monkeypatch.setenv("CDIT_DATABASE_PATH", str(path))
    seed_synthetic_data(path)
    staff = login(path, "staff")
    admin = login(path, "admin")
    user = login(path, "user")
    with connect(path) as db:
        db.execute(
            """INSERT INTO synthetic_accounts
               (account_id, username, role, status, password_hash, created_at, updated_at)
               VALUES ('SYN-STAFF-002', 'staff.second', 'staff', 'setup_required', NULL, '2026-11-08T12:00:00Z', '2026-11-08T12:00:00Z')"""
        )
        db.commit()
    second_staff = login(path, "staff", "SYN-STAFF-002", "staff.second")

    initial_case = staff.get("/api/cases/SYN-CASE-001").json()
    category = staff.get("/api/auditor/taxonomy").json()["categories"][0]
    decision_payload = {
        "item_id": "ITM-ASSIGNMENT-001", "item_index": 1, "item_count": 1,
        "expected_previous_decision_version": 0,
        "expected_case_version": initial_case["updated_at"],
        "source_id": "SYN-CASE-001.request_text", "source_version": "case-v1",
        "source_start": 0, "source_end": len(initial_case["request_text"]),
        "policy_version": "SYN-POLICY-0.1", "category": category,
        "urgency_band": "medium", "destination": "Tier 1",
        "rationale": "Synthetic assignment authorization test.",
        "evidence": "Synthetic case text.",
    }
    decision_url = "/api/cases/SYN-CASE-001/items/auditor-decisions"
    assert staff.post(decision_url, json=decision_payload).status_code == 201

    assigned = admin.patch(
        "/api/admin/cases/SYN-CASE-001/assignment",
        json={"staff_account_id": "SYN-STAFF-002"},
    )
    assert assigned.status_code == 200 and assigned.json()["action"] == "reassigned"
    assert "SYN-CASE-001" not in {case["case_id"] for case in staff.get("/api/cases").json()}
    assert staff.get("/api/cases/SYN-CASE-001").status_code == 404
    assert staff.patch("/api/cases/SYN-CASE-001/status", json={"status": "in_progress"}).status_code == 404
    decision_payload["expected_previous_decision_version"] = 1
    assert staff.post(decision_url, json=decision_payload).status_code == 404
    assert "SYN-CASE-001" in {case["case_id"] for case in second_staff.get("/api/cases").json()}
    assert second_staff.get("/api/cases/SYN-CASE-001").json()["assigned_staff_account_id"] == "SYN-STAFF-002"
    assert len(admin.get("/api/cases").json()) == 81
    assert staff.get("/api/auditor/decisions").json() == []
    assert len(second_staff.get("/api/auditor/decisions").json()) == 1
    assert len(admin.get("/api/auditor/decisions").json()) == 1

    requester_view = user.get("/api/cases/SYN-CASE-001").json()
    assert requester_view["owner_account_id"] == "SYN-USER-001"
    assert "assigned_staff_account_id" not in requester_view

    events = admin.get("/api/admin/case-assignment-events")
    assert events.status_code == 200
    reassignment = next(event for event in events.json() if event["event_id"] == assigned.json()["event_id"])
    assert reassignment["case_id"] == "SYN-CASE-001"
    assert reassignment["actor_account_id"] == "SYN-ADMIN-001"
    assert reassignment["previous_staff_account_id"] == "SYN-STAFF-001"
    assert reassignment["assigned_staff_account_id"] == "SYN-STAFF-002"
    assert staff.get("/api/admin/case-assignment-events").status_code == 403

    unassigned = admin.patch("/api/admin/cases/SYN-CASE-001/assignment", json={"staff_account_id": None})
    assert unassigned.status_code == 200 and unassigned.json()["action"] == "unassigned"
    assert second_staff.get("/api/cases/SYN-CASE-001").status_code == 404
    assert admin.get("/api/cases/SYN-CASE-001").status_code == 200


def test_only_admin_can_assign_and_targets_must_be_active_staff(tmp_path, monkeypatch):
    path = tmp_path / "assignment-validation.sqlite3"
    monkeypatch.setenv("CDIT_DATABASE_PATH", str(path))
    seed_synthetic_data(path)
    admin = login(path, "admin")
    staff = login(path, "staff")
    route = "/api/admin/cases/SYN-CASE-001/assignment"
    assert staff.patch(route, json={"staff_account_id": "SYN-STAFF-001"}).status_code == 403
    assert admin.patch(route, json={"staff_account_id": "SYN-USER-001"}).status_code == 422
    assert admin.patch(route, json={"staff_account_id": "SYN-STAFF-999"}).status_code == 422
    assert admin.patch(route, json={"staff_account_id": "SYN-STAFF-001"}).json()["changed"] is False
