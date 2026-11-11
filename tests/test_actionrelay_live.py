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
    built = []

    def no_provider():
        # Never build a real client here, even on a machine whose .env holds a key.
        built.append(True)
        raise AssertionError("a rejected request must not reach client construction")

    monkeypatch.setattr(actionrelay_live, "create_anthropic_client", no_provider)
    monkeypatch.delenv("ACTIONRELAY_ENABLE_LIVE_TRIAGE", raising=False)
    assert admin.post(route, json=allow).status_code == 503
    monkeypatch.setenv("ACTIONRELAY_ENABLE_LIVE_TRIAGE", "1")
    assert user.post(route, json=allow).status_code == 403
    assert admin.post(route, json={"authorize_billable_call": False}).status_code == 422
    # Bounded synthetic free text is eligible; over-length and likely-sensitive text are not.
    assert admin.post(submit(user, "x" * 2001) + "/agent-runs", json=allow).status_code == 422
    assert admin.post(submit(user, "Please check my SSN 123-45-6789 on file.") + "/agent-runs",
                      json=allow).status_code == 422
    assert built == []
    attempts = []
    monkeypatch.setattr(actionrelay_live, "create_anthropic_client", lambda: nullcontext(object()))

    def invoke(case_id, message, actor, client, record_attempt):
        attempts.append(case_id)
        record_attempt()
        return {"validated_model_result": True, "triage": "proposal_for_human_review"}

    monkeypatch.setattr(actionrelay_live, "run_triage", invoke)
    run = admin.post(route, json=allow)
    assert run.status_code == 201
    assert run.json()["provider_attempts"] == 1
    # The activity view joins this run with any outcome for the same case version.
    timeline = admin.get(route).json()[0]
    assert (timeline["run_id"], timeline["case_version"], timeline["provider_attempts"]) == (
        run.json()["run_id"], run.json()["case_version"], 1)
    assert timeline["result"]["stages"][0] == {"name": "Claude Triage",
                                               "status": "proposal_for_human_review"}
    assert admin.post(route, json=allow).status_code == 409
    assert len(attempts) == 1
    assert user.get(case).json()["status"] == "submitted"
    assert "result" not in user.get(route).json()[0]


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
    assert auditor.patch(case + "/status", json={"status": "in_progress"}).status_code == 403
    assert admin.patch("/api/admin/cases/" + case_id + "/assignment",
                       json={"staff_account_id": "SYN-AUDITOR-001"}).status_code == 200
    reviewed = auditor.post(decision_route, json=payload_for(auditor.get(case).json(), category))
    assert reviewed.status_code == 201, reviewed.text
    decision = reviewed.json()["decision_id"]
    feedback = f"/api/admin/auditor-decisions/{decision}/feedback"
    assert auditor.post(feedback, json={"flagged": True}).status_code == 403
    assert admin.post(feedback, json={"note": "Check the evidence", "flagged": True}).status_code == 201
    entries = auditor.get("/api/auditor/feedback").json()
    assert [(row["decision_id"], row["decision_version"], row["flagged"]) for row in entries] == [(decision, 1, 1)]
    assert staff.get("/api/auditor/feedback").status_code == 403
    assert user.get(case).json()["status"] == "submitted"


def test_live_triage_summary_reports_proposed_category_not_its_label():
    # Fake client only: no provider call. The summary must show the proposed
    # category; "inference"/"unknown" is its evidence label, kept separately.
    from test_manny_triage_runtime_harness import FakeClient, FakeMessages
    from cdit_support_mao.web import Actor

    messages = FakeMessages(category="Work access blocked", quote="cannot access")
    attempts = []
    result = actionrelay_live.run_triage(
        "SYN-CASE-summary", "I cannot access the portal",
        Actor("SYN-ADMIN-001", "admin.demo", "admin"), FakeClient(messages),
        lambda: attempts.append(1),
    )
    assert result["validated_model_result"] is True
    assert result["items"] == [{
        "index": 1, "category": "Work access blocked", "category_label": "inference",
        "urgency": "unknown", "urgency_label": "unknown",
    }]
    assert len(messages.calls) == 1 and attempts == [1]
