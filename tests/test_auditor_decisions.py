import sqlite3

import pytest
from fastapi.testclient import TestClient

from cdit_support_mao.database import connect, seed_synthetic_data
from cdit_support_mao.main import app
from cdit_support_mao.web import provision_synthetic_password


PASSWORD = "Synthetic-auditor-password-2026!"


def client_for(tmp_path, monkeypatch, role):
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "auditor.sqlite3"
    monkeypatch.setenv("CDIT_DATABASE_PATH", str(path))
    seed_synthetic_data(path)
    account_id = {"user": "SYN-USER-001", "staff": "SYN-AUDITOR-001", "admin": "SYN-ADMIN-001"}[role]
    provision_synthetic_password(account_id, PASSWORD)
    if role == "staff":
        with connect(path) as db:
            db.execute(
                "UPDATE synthetic_cases SET assigned_staff_account_id = ? WHERE case_id = 'SYN-CASE-001'",
                (account_id,),
            )
    client = TestClient(app)
    login_name = "auditor" if role == "staff" else role
    assert client.post("/auth/login", json={"username": login_name + ".demo", "password": PASSWORD}).status_code == 200
    return path, client


def payload_for(case, category, admin_override_reason=None):
    return {
        "item_id": "ITM-SYN-001",
        "item_index": 1,
        "item_count": 1,
        "expected_previous_decision_version": 0,
        "expected_case_version": case["updated_at"],
        "source_id": case["case_id"] + ".request_text",
        "source_version": "case-v1",
        "source_start": 0,
        "source_end": len(case["request_text"]),
        "policy_version": "SYN-SUPPORT-POLICY-0.1",
        "category": category,
        "urgency_band": "medium",
        "destination": "Tier 1 support",
        "rationale": "Synthetic case evidence supports this category and band.",
        "evidence": "Source SYN-CASE-001 request text, characters 0 through end.",
        "admin_override_reason": admin_override_reason,
        "conditions": ["No active safety concern stated"],
        "exceptions": ["Re-review if new impact evidence appears"],
    }


def test_staff_decision_is_item_scoped_versioned_and_does_not_change_ticket(tmp_path, monkeypatch):
    path, staff = client_for(tmp_path, monkeypatch, "staff")
    case = staff.get("/api/cases/SYN-CASE-001").json()
    category = staff.get("/api/auditor/taxonomy").json()["categories"][0]
    decision_url = "/api/cases/SYN-CASE-001/items/auditor-decisions"

    first = staff.post(decision_url, json=payload_for(case, category))
    assert first.status_code == 201, first.text
    assert first.json()["reviewer_account_id"] == "SYN-AUDITOR-001"
    assert first.json()["decision_version"] == 1
    assert first.json()["ticket_changed"] is False

    case_after = staff.get("/api/cases/SYN-CASE-001").json()
    second_payload = payload_for(case_after, category)
    second_payload["expected_previous_decision_version"] = 1
    second_payload["rationale"] = "Revised synthetic rationale after human review."
    second = staff.post(decision_url, json=second_payload)
    assert second.status_code == 201
    assert second.json()["decision_version"] == 2

    history = staff.get("/api/auditor/decisions").json()
    assert [(row["item_id"], row["decision_version"]) for row in history] == [("ITM-SYN-001", 2), ("ITM-SYN-001", 1)]
    assert history[0]["conditions"] == ["No active safety concern stated"]
    assert history[0]["exceptions"] == ["Re-review if new impact evidence appears"]
    assert history[0]["source_digest_sha256"]
    assert history[0]["reviewer_account_id"] == "SYN-AUDITOR-001"
    assert history[0]["case_version"] == case["updated_at"]
    assert staff.get("/api/cases/SYN-CASE-001").json()["status"] == "submitted"

    with connect(path) as db:
        rows = db.execute("SELECT decision_version FROM synthetic_auditor_decisions ORDER BY decision_version").fetchall()
        assert [row["decision_version"] for row in rows] == [1, 2]
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            db.execute("UPDATE synthetic_auditor_decisions SET rationale = 'changed' WHERE decision_id = ?", (first.json()["decision_id"],))


def test_user_cannot_view_taxonomy_or_submit_or_read_auditor_decisions(tmp_path, monkeypatch):
    _path, user = client_for(tmp_path, monkeypatch, "user")
    assert user.get("/api/auditor/taxonomy").status_code == 403
    assert user.get("/api/auditor/decisions").status_code == 403
    assert user.post("/api/cases/SYN-CASE-001/items/auditor-decisions", json={}).status_code == 403


def test_auditor_form_is_rendered_only_in_existing_staff_admin_case_controls():
    client = TestClient(app)
    script = client.get("/assets/app.js")
    assert script.status_code == 200
    assert "function auditorPanel(item, decisions, categories, role)" in script.text
    assert "auditorPanel(item, decisions, categories, role)" in script.text
    assert 'if(role!=="user") [decisions,categories]' in script.text
    assert 'controls = \'<form class="case-edit-form"' in script.text


def test_admin_can_record_but_stale_case_span_and_non_taxonomy_fail_closed(tmp_path, monkeypatch):
    _path, admin = client_for(tmp_path, monkeypatch, "admin")
    case = admin.get("/api/cases/SYN-CASE-001").json()
    categories = admin.get("/api/auditor/taxonomy").json()["categories"]
    url = "/api/cases/SYN-CASE-001/items/auditor-decisions"

    stale = payload_for(case, categories[0], "Synthetic Admin review override")
    stale["expected_case_version"] = "1900-01-01T00:00:00.000000Z"
    assert admin.post(url, json=stale).status_code == 409

    outside_span = payload_for(case, categories[0], "Synthetic Admin review override")
    outside_span["source_end"] = len(case["request_text"]) + 1
    assert admin.post(url, json=outside_span).status_code == 422

    invented_category = payload_for(case, "Unapproved Synthetic Category", "Synthetic Admin review override")
    assert admin.post(url, json=invented_category).status_code == 422
    assert admin.get("/api/auditor/decisions").json() == []

    recorded = admin.post(url, json=payload_for(case, categories[0], "Synthetic Admin review override"))
    assert recorded.status_code == 201
    assert recorded.json()["admin_override_reason"] == "Synthetic Admin review override"
    assert admin.get("/api/auditor/decisions").json()[0]["admin_override_reason"] == "Synthetic Admin review override"


def test_admin_must_supply_override_reason_but_staff_must_not(tmp_path, monkeypatch):
    path, admin = client_for(tmp_path, monkeypatch, "admin")
    case = admin.get("/api/cases/SYN-CASE-001").json()
    category = admin.get("/api/auditor/taxonomy").json()["categories"][0]
    url = "/api/cases/SYN-CASE-001/items/auditor-decisions"
    assert admin.post(url, json=payload_for(case, category)).status_code == 422
    payload = payload_for(case, category, "  Synthetic override reason  ")
    response = admin.post(url, json=payload)
    assert response.status_code == 201
    assert response.json()["admin_override_reason"] == "Synthetic override reason"

    _path, staff = client_for(tmp_path / "staff", monkeypatch, "staff")
    staff_case = staff.get("/api/cases/SYN-CASE-001").json()
    payload = payload_for(staff_case, staff.get("/api/auditor/taxonomy").json()["categories"][0], "not allowed")
    assert staff.post(url, json=payload).status_code == 422


def test_new_decision_requires_current_previous_version_and_forbids_identity_spoofing(tmp_path, monkeypatch):
    _path, staff = client_for(tmp_path, monkeypatch, "staff")
    case = staff.get("/api/cases/SYN-CASE-001").json()
    category = staff.get("/api/auditor/taxonomy").json()["categories"][0]
    url = "/api/cases/SYN-CASE-001/items/auditor-decisions"
    payload = payload_for(case, category)
    first = staff.post(url, json=payload)
    assert first.status_code == 201
    stale_previous = staff.post(url, json=payload)
    assert stale_previous.status_code == 409
    spoofed = payload_for(case, category)
    spoofed["item_id"] = "ITM-SYN-002"
    spoofed["reviewer_account_id"] = "SYN-ADMIN-001"
    assert staff.post(url, json=spoofed).status_code == 422
