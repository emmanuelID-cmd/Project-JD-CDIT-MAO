from fastapi.testclient import TestClient

from cdit_support_mao import actionrelay_outcomes
from cdit_support_mao.database import connect
from cdit_support_mao.main import app
from test_actionrelay_live import accounts, submit
from test_auditor_decisions import payload_for


def test_public_file_delivery_is_atomic_scoped_and_human_closed(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user, admin = clients["user"], clients["admin"]
    sample_pdf = b"%PDF-1.7\n% synthetic test document\n%%EOF\n"
    monkeypatch.setattr(actionrelay_outcomes, "approved_pdf", lambda: sample_pdf)
    case = submit(user, "Can I get the IDNYC application form?")
    item = user.get(case).json()
    assert item["status"] == "resolved" and item["urgency_band"] == "low"
    assert item["review_flag"] is True
    assert user.get(case + "/form.pdf").content == sample_pdf
    assert TestClient(app).get(case + "/form.pdf").status_code == 401
    assert clients["staff"].get(case + "/form.pdf").status_code == 404
    assert clients["auditor"].patch(case + "/status", json={"status": "closed", "response": "Closing this request."}).status_code == 404
    with connect() as db:
        outcome = db.execute("SELECT * FROM actionrelay_ticket_outcomes").fetchone()
        actor = actionrelay_outcomes.Actor("SYN-USER-001", "user.demo", "user")
        actionrelay_outcomes.apply_intake_outcome(outcome["case_id"], outcome["case_version"],
                                                 item["request_text"], actor)
        assert db.execute("SELECT count(*) FROM actionrelay_ticket_outcomes").fetchone()[0] == 1
    assert admin.patch(case + "/status", json={"status": "closed", "response": "The request is complete."}).status_code == 200
    assert user.get(case).json()["review_flag"] is False
    assert user.get(case + "/form.pdf").content == sample_pdf
    events = admin.get("/api/queue/activity").json()["events"]
    assert [event["kind"] for event in events if event["case_id"] == item["case_id"]] == [
        "user_submitted", "automatic_fulfillment", "admin_status_updated",
    ]


def test_unavailable_form_mixed_request_and_personal_record_stay_open(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    calls = []
    monkeypatch.setattr(actionrelay_outcomes, "approved_pdf", lambda: calls.append("fetch"))
    user, admin = clients["user"], clients["admin"]
    for text, reason in (
        ("I need the IDNYC application form.", "approved_pdf_unavailable"),
        ("I need a copy of my personal W-2.", "personal_record"),
        ("I need the IDNYC application form and my W-2.", None),
    ):
        case = submit(user, text)
        assert user.get(case).json()["status"] == "submitted"
        assert user.get(case + "/form.pdf").status_code == 404
        reply = user.get(case + "/reply").json()
        assert (reply["reason"] if reply else None) == reason
        assert admin.patch(case + "/status", json={"status": "closed", "response": "Classification is required before closeout."}).status_code == 409
    assert calls == ["fetch"]


def test_failed_resolution_update_rolls_back_file_and_reply(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    with connect() as db:
        db.execute("""CREATE TRIGGER fail_resolution BEFORE UPDATE OF status ON synthetic_cases
                   WHEN NEW.status = 'resolved' BEGIN SELECT RAISE(ABORT, 'simulated failure'); END""")
    monkeypatch.setattr(actionrelay_outcomes, "approved_pdf", lambda: b"%PDF-1.7\n%%EOF\n")
    user = clients["user"]
    case = submit(user, "I need the IDNYC application form.")
    assert user.get(case).json()["status"] == "submitted"
    assert user.get(case + "/reply").json() is None
    assert user.get(case + "/form.pdf").status_code == 404


def test_employee_sample_forms_are_fillable_and_resolve_only_exact_requests(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user, admin = clients["user"], clients["admin"]
    root = __import__("pathlib").Path(actionrelay_outcomes.__file__).with_name("static")
    cases = (
        ("I need a blank weekly timesheet.", "ActionRelay-Sample-Weekly-Timesheet.pdf"),
        ("I need the shift options and change request form.", "ActionRelay-Sample-Shift-Options-and-Change-Request.pdf"),
    )
    for phrase, filename in cases:
        route = submit(user, phrase)
        item = next(row for row in user.get("/api/cases").json()
                    if row["case_id"] == route.rsplit("/", 1)[-1])
        assert item["status"] == "resolved" and item["urgency_band"] == "low"
        assert item["category"] == "Forms & Documents"
        delivered = user.get(route + "/form.pdf")
        assert delivered.status_code == 200
        assert delivered.content == (root / filename).read_bytes()
        assert filename in delivered.headers["content-disposition"]
        assert clients["staff"].get(route + "/form.pdf").status_code == 404
        assert admin.patch(route + "/status", json={"status": "closed", "response": "The request is complete."}).status_code == 200


def test_official_benefits_links_resolve_resource_delivery_not_enrollment(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user = clients["user"]
    expected = (
        ("I need a SNAP application form.", "https://www.otda.ny.gov/PROGRAMS/APPLICATIONS/4826-DD.pdf"),
        ("Where can I apply for SNAP in New York City?", "https://www.nyc.gov/site/hra/help/snap-application-documents.page"),
        ("Where can I compare health insurance plans in New York?", "https://nystateofhealth.ny.gov/"),
    )
    for phrase, source_url in expected:
        route = submit(user, phrase)
        item = next(row for row in user.get("/api/cases").json()
                    if row["case_id"] == route.rsplit("/", 1)[-1])
        assert item["status"] == "resolved" and item["urgency_band"] == "low"
        assert item["reply_route"] == "resource_link"
        assert item["reply_url"] == source_url
        assert user.get(route + "/form.pdf").status_code == 404
    health_case = submit(user, expected[2][0])
    assert "does not enroll" in user.get(health_case + "/reply").json()["reply"]


def test_personal_and_employer_action_requests_remain_for_human_review(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user = clients["user"]
    for phrase, reason in (
        ("I need a copy of my personal W-2.", "personal_record"),
        ("I want to change my shift.", "schedule_change"),
        ("My withholding or deduction changed unexpectedly before this payroll closes.", "payroll_change"),
    ):
        route = submit(user, phrase)
        item = next(row for row in user.get("/api/cases").json()
                    if row["case_id"] == route.rsplit("/", 1)[-1])
        assert item["status"] == "submitted"
        assert item["reply_route"] == "human_review"
        assert user.get(route + "/reply").json()["reason"] == reason


def test_current_auditor_decision_runs_real_knowledge_and_rejects_stale(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user, admin, auditor = (clients[key] for key in ("user", "admin", "auditor"))
    case = submit(user, "My withholding or deduction changed unexpectedly before this payroll closes.")
    case_id = case.rsplit("/",1)[-1]
    assert admin.patch("/api/admin/cases/" + case_id + "/assignment",
                       json={"staff_account_id": "SYN-AUDITOR-001"}).status_code == 200
    item = auditor.get(case).json()
    categories = auditor.get("/api/auditor/taxonomy").json()["categories"]
    payload = payload_for(item, categories[0])
    decisions = case + "/items/auditor-decisions"
    decision = auditor.post(decisions, json=payload).json()
    body = {"decision_id": decision["decision_id"]}
    resume = case + "/resume-review"
    result = auditor.post(resume, json=body)
    assert result.status_code == 200, result.text
    assert result.json()["status"] == "human_review", result.text
    assert result.json()["result"]["stages"][0]["name"] == "Knowledge"
    assert auditor.post(resume, json=body).json() == result.json()
    assert user.get(case).json()["status"] == "submitted"
    payload["expected_case_version"] = auditor.get(case).json()["updated_at"]
    payload["expected_previous_decision_version"] = 1
    payload["rationale"] = "Revised classification after reviewing the source."
    assert auditor.post(decisions, json=payload).status_code == 201
    assert auditor.post(resume, json=body).status_code == 409

    supported = submit(user, "Site user cannot find where to export the site enrollment report.")
    supported_id = supported.rsplit("/", 1)[-1]
    assert admin.patch("/api/admin/cases/" + supported_id + "/assignment",
                       json={"staff_account_id": "SYN-AUDITOR-001"}).status_code == 200
    known = payload_for(auditor.get(supported).json(), "Product how-to / documentation request")
    recorded = auditor.post(supported + "/items/auditor-decisions", json=known)
    assert recorded.status_code == 201, recorded.text
    complete = auditor.post(supported + "/resume-review", json={"decision_id": recorded.json()["decision_id"]})
    assert complete.status_code == 200, complete.text
    assert [(stage["name"], stage["status"]) for stage in complete.json()["result"]["stages"]] == [
        ("Knowledge", "completed"), ("Troubleshooting", "completed"),
        ("Escalation", "completed"), ("Documentation", "completed"),
    ]
    assert user.get(supported).json()["status"] == "submitted"


def test_ticket_replies_deliver_catalogued_synthetic_forms(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user = clients["user"]
    expected = (
        ("I need the company directory.", "synthetic-company-directory.pdf"),
        ("Please send the workplace policy guide.", "synthetic-workplace-guide.pdf"),
        ("Can I get the company policy book?", "synthetic-workplace-guide.pdf"),
        ("I need a vacation request form.", "synthetic-vacation-request.pdf"),
        ("Can I get the workplace complaint form?", "synthetic-workplace-complaint.pdf"),
    )
    root = __import__("pathlib").Path(actionrelay_outcomes.__file__).resolve().parents[2] / "docs" / "resources"
    for phrase, filename in expected:
        route = submit(user, phrase)
        item = user.get(route).json()
        assert item["status"] == "resolved"
        delivered = user.get(route + "/form.pdf")
        assert delivered.status_code == 200
        assert delivered.content == (root / filename).read_bytes()
        assert filename in delivered.headers["content-disposition"]


def test_official_forms_are_delivered_as_ticket_links_with_conditions(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user = clients["user"]
    expected = (
        ("Please send me the blank 2026 W-4 form.", {"https://www.irs.gov/pub/irs-pdf/fw4.pdf"}),
        ("I need the FMLA form.", {
            "https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-e.pdf",
            "https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-f.pdf",
        }),
        ("Please send the NYS paid family leave forms.", {
            "https://www.wcb.ny.gov/content/main/forms/PFLDocs/PFL3.pdf",
            "https://www.wcb.ny.gov/content/main/forms/PFLDocs/PFL2.pdf",
            "https://paidfamilyleave.ny.gov/forms",
        }),
    )
    for phrase, expected_urls in expected:
        route = submit(user, phrase)
        item = user.get(route).json()
        assert item["status"] == "resolved"
        reply = user.get(route + "/reply").json()
        assert {link["url"] for link in reply["delivery_links"]} == expected_urls
        assert all(link["label"] for link in reply["delivery_links"])
        assert user.get(route + "/form.pdf").status_code == 404
        if "fmla" in phrase.casefold() or "family leave" in phrase.casefold():
            assert "speak with your employer" in reply["reply"].casefold()
            assert "does not accept or retain personal documents" in reply["reply"].casefold()


def test_closed_prior_resource_resolution_is_used_as_private_precedent(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user, admin = clients["user"], clients["admin"]
    first = submit(user, "I need a vacation request form.")
    first_id = first.rsplit("/", 1)[-1]
    assert admin.patch(first + "/status", json={"status": "closed", "response": "The request is complete."}).status_code == 200
    second = submit(user, "Could you send me the vacation request application?")
    second_id = second.rsplit("/", 1)[-1]
    assert user.get(second).json()["status"] == "resolved"
    with connect() as db:
        row = db.execute("SELECT resolution_basis_case_id FROM actionrelay_ticket_outcomes WHERE case_id = ?",
                         (second_id,)).fetchone()
    assert row["resolution_basis_case_id"] == first_id
    assert first_id not in user.get(second + "/reply").text


def test_personal_or_health_details_block_repeat_resource_automation(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user = clients["user"]
    route = submit(user, "I need the FMLA form for my diagnosis of asthma.")
    item = user.get(route).json()
    assert item["status"] == "submitted"
    reply = user.get(route + "/reply").json()
    assert reply["route"] == "human_review"
    assert reply["reason"] == "sensitive_details_require_human"
    assert reply["delivery_links"] == []


def test_multiple_resource_requests_are_not_partially_resolved(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user = clients["user"]
    route = submit(user, "Please send the company directory and vacation request form.")
    assert user.get(route).json()["status"] == "submitted"
    assert user.get(route + "/reply").json() is None


def test_high_band_receives_safe_resource_reply_without_auto_resolution(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user = clients["user"]
    original = actionrelay_outcomes.apply_intake_outcome
    monkeypatch.setattr(actionrelay_outcomes, "apply_intake_outcome", lambda *args: {"status": "submitted", "urgency_band": "unknown"})
    phrase = "I need the company directory."
    route = submit(user, phrase)
    case_id = route.rsplit("/", 1)[-1]
    with connect() as db:
        db.execute("UPDATE synthetic_cases SET urgency_band = 'high', category = 'Benefits & Resources' WHERE case_id = ?",
                   (case_id,))
        version = db.execute("SELECT updated_at FROM synthetic_cases WHERE case_id = ?", (case_id,)).fetchone()[0]
    monkeypatch.setattr(actionrelay_outcomes, "apply_intake_outcome", original)
    actor = actionrelay_outcomes.Actor("SYN-USER-001", "user.demo", "user")
    result = original(case_id, version, phrase, actor)
    item = user.get(route).json()
    assert result["resource_delivered"] is True
    assert item["status"] == "submitted" and item["urgency_band"] == "high"
    assert user.get(route + "/form.pdf").status_code == 200


def test_mixed_known_and_unmatched_request_is_not_partially_fulfilled(tmp_path, monkeypatch):
    clients = accounts(tmp_path, monkeypatch)
    user = clients["user"]
    route = submit(user, "I need a vacation form and I also need payroll help.")
    assert user.get(route).json()["status"] == "submitted"
    assert user.get(route + "/reply").json() is None
