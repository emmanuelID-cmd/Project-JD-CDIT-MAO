from contextlib import nullcontext

from fastapi.testclient import TestClient

from cdit_support_mao import actionrelay_live
from cdit_support_mao.database import seed_synthetic_data
from cdit_support_mao.main import app
from cdit_support_mao.web import provision_synthetic_password
from test_auditor_decisions import payload_for


def accounts(tmp_path, monkeypatch):
    monkeypatch.setenv("CDIT_DATABASE_PATH", str(tmp_path / "actionrelay.db"))
    seed_synthetic_data()
    clients = {}
    for account in ("user", "staff", "auditor", "admin"):
        password = f"Synthetic-test-{account}-only!"
        provision_synthetic_password(f"SYN-{account.upper()}-001", password)
        client = TestClient(app)
        assert client.post("/auth/login", json={"username": account + ".demo",
                                               "password": password}).status_code == 200
        clients[account] = client
    return clients


def submit(user, text):
    response = user.post("/api/cases", json={"subject": "Synthetic test", "request_text": text})
    assert response.status_code == 201
    return "/api/cases/" + response.json()["case_id"]


def test_billable_run_is_explicit_scoped_and_deduplicated(tmp_path, monkeypatch):
    from cdit_support_mao import actionrelay_outcomes
    monkeypatch.setattr(actionrelay_outcomes, "approved_pdf", lambda: None)
    clients = accounts(tmp_path, monkeypatch)
    user, admin = clients["user"], clients["admin"]
    case = submit(user, "I need the IDNYC application form.")
    route = case + "/agent-runs"
    allow = {"authorize_billable_call": True}
    monkeypatch.delenv("ACTIONRELAY_ENABLE_LIVE_TRIAGE", raising=False)
    assert admin.post(route, json=allow).status_code == 503
    monkeypatch.setenv("ACTIONRELAY_ENABLE_LIVE_TRIAGE", "1")
    unknown_case = submit(user, "The synthetic scheduling portal shows a blank panel after I choose a weekly view.")
    assert user.post(unknown_case + "/agent-runs", json={"authorize_billable_call": False}).status_code == 422
    assert admin.post(unknown_case + "/agent-runs", json={"authorize_billable_call": False}).status_code == 422
    attempts = []
    workflow_roles = []
    monkeypatch.setattr(actionrelay_live, "create_anthropic_client", lambda: nullcontext(object()))

    def invoke(case_id, message, actor, client, record_attempt):
        attempts.append(case_id)
        workflow_roles.append(actor.role)
        record_attempt()
        return {"validated_model_result": True, "triage": "proposal_for_human_review",
                "coordinator": "ready_for_triage", "reason": "proposal_for_human_review",
                "items": [{"index": 1, "category": "Scheduling"}]}

    monkeypatch.setattr(actionrelay_live, "run_triage", invoke)
    run = user.post(unknown_case + "/agent-runs", json=allow)
    assert run.status_code == 201
    assert run.json()["provider_attempts"] == 1
    assert workflow_roles == ["staff"]  # The scoped Coordinator service identity, not a broadened User role.
    admin_view = admin.get(unknown_case + "/agent-runs").json()[0]
    assert admin_view["run_id"] == run.json()["run_id"]
    assert [stage["name"] for stage in admin_view["result"]["stages"]] == ["Coordinator", "Claude Triage"]
    user_view = user.get(unknown_case + "/agent-runs").json()[0]
    assert user_view["provider_attempts"] == 1
    assert [stage["name"] for stage in user_view["result"]["stages"]] == ["Coordinator", "Claude Triage"]
    assert user_view["result"]["items"] == [{"index": 1, "category": "Scheduling"}]
    assert "usage" not in user_view["result"]
    assert user.post(unknown_case + "/agent-runs", json=allow).status_code == 409
    assert len(attempts) == 1
    assert user.get(unknown_case).json()["status"] == "submitted"


def test_auditor_queue_and_version_feedback_scope(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user, staff, auditor, admin = (clients[name] for name in ("user", "staff", "auditor", "admin"))
    case = submit(user, "Synthetic review case")
    case_id = case.rsplit("/", 1)[-1]
    decision_route = case + "/items/auditor-decisions"
    assert staff.get(case).status_code == 404
    assert auditor.get(case).status_code == 200
    category = auditor.get("/api/auditor/taxonomy").json()["categories"][0]
    assert auditor.post(decision_route, json=payload_for(auditor.get(case).json(), category)).status_code == 404
    assert auditor.get("/api/admin/accounts").status_code == 403
    assert auditor.get("/api/auditor/accounts").status_code == 200
    assert admin.patch("/api/admin/cases/" + case_id + "/assignment",
                       json={"staff_account_id": "SYN-AUDITOR-001"}).status_code == 200
    status_update = auditor.patch(case + "/status", json={
        "status": "in_progress", "response": "We have started reviewing this synthetic request."
    })
    assert status_update.status_code == 200, status_update.text
    assert auditor.patch(case + "/status", json={
        "status": "resolved", "response": "This should remain blocked while classification is unknown."
    }).status_code == 409
    requester_view = user.get(case).json()
    assert requester_view["request_text"] == "Synthetic review case"
    assert requester_view["responses"][0]["response_text"] == "We have started reviewing this synthetic request."
    assert auditor.patch(case, json={"request_text": "Auditor rewrite"}).status_code == 403
    assert admin.patch(case, json={"request_text": "Rewrite the requester message"}).status_code == 403
    reviewed = auditor.post(decision_route, json=payload_for(auditor.get(case).json(), category))
    assert reviewed.status_code == 201, reviewed.text
    decision = reviewed.json()["decision_id"]
    feedback = f"/api/admin/auditor-decisions/{decision}/feedback"
    assert auditor.post(feedback, json={"flagged": True}).status_code == 403
    assert admin.post(feedback, json={"note": "Check the evidence", "flagged": True}).status_code == 201
    entries = auditor.get("/api/auditor/feedback").json()
    assert [(row["decision_id"], row["decision_version"], row["flagged"]) for row in entries] == [(decision, 1, 1)]
    assert staff.get("/api/auditor/feedback").status_code == 403
    assert user.get(case).json()["status"] == "in_progress"
