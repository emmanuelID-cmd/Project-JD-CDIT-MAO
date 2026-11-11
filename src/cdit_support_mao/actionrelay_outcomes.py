"""Application-owned public-form fulfillment and case-scoped replies."""
from __future__ import annotations

from contextlib import closing
from datetime import UTC, datetime
from hashlib import sha256
import os
import re
import json
from pathlib import Path
import sqlite3
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, build_opener

from fastapi import APIRouter, Depends, HTTPException, Response

from cdit_support_mao.database import connect
from cdit_support_mao.web import Actor, get_case, list_cases, require_roles, stamp

router = APIRouter()
IDNYC_PDF = (
    "https://www.nyc.gov/assets/idnyc/downloads/pdf/application-materials/"
    "IDNYC-1b-IDNYC-14-and-Older-Application-English.pdf"
)
IDNYC_REQUESTS = frozenset({
    "i need the idnyc application form",
    "where can i get an idnyc application form",
    "can i get the idnyc application form",
})
PERSONAL_W2 = "i need a copy of my personal w-2"
FORM_DIR = Path(__file__).with_name("static")
PROJECT_RESOURCES = Path(__file__).resolve().parents[2] / "docs" / "resources"
RESOURCES = {
    "idnyc": {
        "kind": "pdf", "reason": "approved_idnyc_english_14_plus",
        "title": "Official blank English IDNYC application, ages 14 and older",
        "reply": "Here is the official blank English IDNYC application for ages 14 and older.",
        "filename": "IDNYC-application-English.pdf",
        "source_url": IDNYC_PDF,
    },
    "weekly_timesheet": {
        "kind": "pdf", "reason": "synthetic_weekly_timesheet",
        "title": "Download the fillable weekly timesheet sample",
        "reply": "Here is a fillable weekly timesheet sample. It is labeled as a development template and is not a CDIT or employer-approved payroll form.",
        "filename": "ActionRelay-Sample-Weekly-Timesheet.pdf",
        "source_url": "/assets/ActionRelay-Sample-Weekly-Timesheet.pdf",
        "sha256": "5a2477c787f3f1d9093da3617feb9da1523f7770ced8fd455a84a3914df9320c",
    },
    "shift_options": {
        "kind": "pdf", "reason": "synthetic_shift_options",
        "title": "Download the fillable shift options and request sample",
        "reply": "Here is a fillable shift-options and change-request sample. A–D and Morning, Evening, and Night are placeholders; the employer must provide actual days and hours. This form does not change a schedule.",
        "filename": "ActionRelay-Sample-Shift-Options-and-Change-Request.pdf",
        "source_url": "/assets/ActionRelay-Sample-Shift-Options-and-Change-Request.pdf",
        "sha256": "3e98414e0fdcb5ba62551b5598b1d13fb9e8e8a355793c68e8b6ab3959ae5ec1",
    },
    "company_directory": {
        "kind": "pdf", "reason": "synthetic_company_directory",
        "title": "Synthetic company directory",
        "reply": "Here is the synthetic company directory for this demonstration. All names and contact details are fictional.",
        "filename": "synthetic-company-directory.pdf",
        "source_path": "synthetic-company-directory.pdf",
        "source_url": "/project-docs/resources/synthetic-company-directory.pdf",
        "sha256": "5ed3e5f2c1204873dfdbc6b14da552bd1c50543eff0be1bbae0c46022e294f2f",
    },
    "workplace_guide": {
        "kind": "pdf", "reason": "synthetic_workplace_guide",
        "title": "Synthetic workplace guide",
        "reply": "Here is the synthetic workplace guide. It is an illustrative sample, not official company policy.",
        "filename": "synthetic-workplace-guide.pdf",
        "source_path": "synthetic-workplace-guide.pdf",
        "source_url": "/project-docs/resources/synthetic-workplace-guide.pdf",
        "sha256": "36833cc0169c746970c6d10dd2c7f85097d477dc718ad6975e02e00ac0f6b35c",
    },
    "vacation_request": {
        "kind": "pdf", "reason": "synthetic_vacation_request",
        "title": "Blank synthetic vacation request form",
        "reply": "Here is a blank synthetic vacation request form. Submitting it does not approve leave or change a schedule; send completed forms through the approved HR channel.",
        "filename": "synthetic-vacation-request.pdf",
        "source_path": "synthetic-vacation-request.pdf",
        "source_url": "/project-docs/resources/synthetic-vacation-request.pdf",
        "sha256": "df616123576c0ff0a70b4f6db709c7abfc58d057aa1cedf6599ab29c3ee20ff5",
    },
    "workplace_complaint": {
        "kind": "pdf", "reason": "synthetic_workplace_complaint",
        "title": "Blank synthetic workplace complaint form",
        "reply": "Here is a blank synthetic workplace complaint form. It is a prototype template, not an official company form.",
        "filename": "synthetic-workplace-complaint.pdf",
        "source_path": "synthetic-workplace-complaint.pdf",
        "source_url": "/project-docs/resources/synthetic-workplace-complaint.pdf",
        "sha256": "3ad9cdc99a0ad739beba4c8e5facc5d866486c5e78717968d4c20be86f06d800",
    },
    "w4": {
        "kind": "link", "reason": "official_irs_w4_2026",
        "title": "Official blank IRS Form W-4 (2026)",
        "reply": "Here is the official blank 2026 IRS Form W-4. This provides the form only; it does not change payroll withholding. Do not submit a completed tax form through this synthetic prototype.",
        "source_url": "https://www.irs.gov/pub/irs-pdf/fw4.pdf",
        "delivery_links": [{"label": "Download IRS Form W-4 (2026)", "url": "https://www.irs.gov/pub/irs-pdf/fw4.pdf"}],
    },
    "fmla": {
        "kind": "link", "reason": "official_dol_fmla_forms",
        "title": "Official DOL FMLA certification forms",
        "reply": "These are blank U.S. Department of Labor FMLA certification forms. Speak with your employer or HR before completing them. Eligibility and supporting documentation depend on the situation and are determined by the employer/plan administrator. Potential supporting records may include an employee identifier, provider or hospital certification, relationship or qualifying-event records, and insurer information when relevant; exact requirements vary. Submit only documents HR specifically requests through its approved department channel. This prototype does not accept or retain personal documents.",
        "source_url": "https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-e.pdf",
        "delivery_links": [
            {"label": "WH-380-E — employee's own serious health condition", "url": "https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-e.pdf"},
            {"label": "WH-380-F — family member's serious health condition", "url": "https://www.dol.gov/sites/dolgov/files/WHD/legacy/files/wh-380-f.pdf"},
        ],
    },
    "pfl": {
        "kind": "link", "reason": "official_nys_pfl_forms",
        "title": "Official New York Paid Family Leave form packages",
        "reply": "These are official New York Paid Family Leave blank form packages. PFL applies only to qualifying circumstances; speak with your employer/HR and insurer before completing them. Eligibility and required documentation depend on your situation. Potential records may include an employee identifier, provider or hospital certification, relationship or qualifying-event records, and insurer information when relevant; exact requirements vary. Submit only documents HR specifically requests through its approved department channel. This prototype does not accept or retain personal documents.",
        "source_url": "https://www.wcb.ny.gov/content/main/forms/PFLDocs/PFL3.pdf",
        "delivery_links": [
            {"label": "Family-care package — PFL-1, PFL-3 and PFL-4", "url": "https://www.wcb.ny.gov/content/main/forms/PFLDocs/PFL3.pdf"},
            {"label": "Bonding package — PFL-1 and PFL-2", "url": "https://www.wcb.ny.gov/content/main/forms/PFLDocs/PFL2.pdf"},
            {"label": "NYS Paid Family Leave forms and instructions", "url": "https://paidfamilyleave.ny.gov/forms"},
        ],
    },
    "snap": {
        "kind": "link", "reason": "official_snap_application_resources",
        "title": "Open the official fillable New York State SNAP application PDF",
        "reply": "This opens the official fillable New York State SNAP application/recertification form (LDSS-4826 DD, Rev. 12/23). Complete it privately and submit it to the appropriate social-services district. Do not upload a completed form or personal details to ActionRelay; this ticket only supplies the blank form and does not apply for benefits or determine eligibility.",
        "source_url": "https://www.otda.ny.gov/PROGRAMS/APPLICATIONS/4826-DD.pdf",
    },
    "snap_nyc_resources": {
        "kind": "link", "reason": "official_nyc_snap_application_resources",
        "title": "Open official NYC HRA SNAP forms and instructions",
        "reply": "This official NYC HRA page lists SNAP applications, recertification forms, and instructions. The portal or paper application must be completed and submitted separately; ActionRelay has not applied for benefits or determined eligibility.",
        "source_url": "https://www.nyc.gov/site/hra/help/snap-application-documents.page",
    },
    "health_marketplace": {
        "kind": "link", "reason": "official_nys_health_marketplace",
        "title": "Open the official NY State of Health marketplace",
        "reply": "Open NY State of Health to review individual or family coverage options. If you mean an insurance plan offered by your employer, contact HR for that plan’s enrollment instructions; this link does not enroll you in an employer plan.",
        "source_url": "https://nystateofhealth.ny.gov/",
    },
}
RESOURCE_REQUESTS = {
    **{text: "idnyc" for text in IDNYC_REQUESTS},
    "i need a blank weekly timesheet": "weekly_timesheet",
    "can i get the weekly timesheet form": "weekly_timesheet",
    "i need the weekly time sheet form": "weekly_timesheet",
    "show me the shift schedules a b c and d for morning evening and night": "shift_options",
    "i need the shift options and change request form": "shift_options",
    "can i see the shift schedule options": "shift_options",
    "i need a snap application form": "snap",
    "where can i get a snap application": "snap",
    "i need the snap application form": "snap",
    "where can i apply for snap in new york city": "snap_nyc_resources",
    "where can i get nyc snap application forms": "snap_nyc_resources",
    "where can i compare health insurance plans in new york": "health_marketplace",
    "where do i find the new york state of health": "health_marketplace",
    "i want to compare health insurance plans in new york state": "health_marketplace",
    "send me the company directory": "company_directory",
    "i need the company directory": "company_directory",
    "send me the workplace guide": "workplace_guide",
    "i need the workplace guide": "workplace_guide",
    "i need the vacation request form": "vacation_request",
    "send me a vacation request form": "vacation_request",
    "i need a blank vacation form": "vacation_request",
    "i need a workplace complaint form": "workplace_complaint",
    "send me the complaint form": "workplace_complaint",
    "i need a blank complaint form": "workplace_complaint",
    "i need a blank w-4 form": "w4",
    "i need a w4 form": "w4",
    "send me a blank w-4": "w4",
    "i need an fmla form": "fmla",
    "send me the fmla forms": "fmla",
    "i need fmla paperwork": "fmla",
    "i need a pfl form": "pfl",
    "send me the paid family leave forms": "pfl",
    "i need the new york paid family leave forms": "pfl",
}
RESOURCE_PATTERNS = (
    (re.compile(r"\b(?:company )?(?:contact )?directory\b"), "company_directory"),
    (re.compile(r"\b(?:workplace|company|hr) (?:policy )?(?:guide|handbook|book)\b"), "workplace_guide"),
    (re.compile(r"\bvacation (?:request )?(?:form|application)\b"), "vacation_request"),
    (re.compile(r"\b(?:workplace )?complaint form\b"), "workplace_complaint"),
    (re.compile(r"\b(?:blank )?w[- ]?4 form\b|\bform w[- ]?4\b"), "w4"),
    (re.compile(r"\b(?:fmla|family and medical leave)\b.*\b(?:forms?|paperwork|blank|download|send|get)\b|\b(?:forms?|paperwork|blank)\b.*\b(?:fmla|family and medical leave)\b"), "fmla"),
    (re.compile(r"\b(?:pfl|paid family leave)\b.*\b(?:forms?|paperwork|blank|download|send|get)\b|\b(?:forms?|paperwork|blank)\b.*\b(?:pfl|paid family leave)\b"), "pfl"),
    (re.compile(r"\b(?:weekly )?time ?sheet\b"), "weekly_timesheet"),
    (re.compile(r"\bshift (?:schedule|options|patterns)\b"), "shift_options"),
    (re.compile(r"\bsnap (?:application|form|paperwork)\b"), "snap"),
)
SENSITIVE_INPUT = re.compile(
    r"(?:\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|"
    r"\b\d{3}[ .-]\d{3}[ .-]\d{4}\b|\b(?:date of birth|dob|social security|ssn|"
    r"passport number|employee id|member id|medical record|diagnosis|health condition|doctor|"
    r"my (?:medical|health) (?:leave|condition|record)|medical leave for|health information|"
    r"my w-?2|my pay ?stub|bank account|routing number)\b)"
)
def matching_resources(normalized: str) -> list[str]:
    direct = RESOURCE_REQUESTS.get(normalized)
    if direct:
        return [direct]
    if SENSITIVE_INPUT.search(normalized):
        return []
    return list(dict.fromkeys(key for pattern, key in RESOURCE_PATTERNS if pattern.search(normalized)))

def match_resource(normalized: str) -> str | None:
    matches = matching_resources(normalized)
    return matches[0] if len(matches) == 1 else None

HUMAN_REQUESTS = {
    PERSONAL_W2: ("personal_record", "A personal W-2 contains private payroll information and needs human review. Contact your employer’s payroll or HR team."),
    "i need to change my shift": ("schedule_change", "A schedule change needs HR or manager review. The sample shift form does not change an employee’s schedule."),
    "i want to change my shift": ("schedule_change", "A schedule change needs HR or manager review. The sample shift form does not change an employee’s schedule."),
    "my withholding or deduction changed unexpectedly before this payroll closes": ("payroll_change", "An unexpected payroll withholding change needs prompt payroll or HR review. No change was made to your payroll record."),
}
PDF_LIMIT = 3_000_000


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def approved_pdf() -> bytes | None:
    """Fetch a fixed public source, or use an operator-verified copy with a pinned digest."""
    configured = os.environ.get("ACTIONRELAY_IDNYC_PDF")
    try:
        if configured:
            with Path(configured).open("rb") as stream:
                data = stream.read(PDF_LIMIT + 1)
            if sha256(data).hexdigest() != os.environ.get("ACTIONRELAY_IDNYC_SHA256"):
                return None
        else:
            with build_opener(NoRedirect()).open(IDNYC_PDF, timeout=4) as response:
                if response.headers.get_content_type() != "application/pdf":
                    return None
                data = response.read(PDF_LIMIT + 1)
    except (OSError, URLError):
        return None
    if len(data) > PDF_LIMIT or not data.startswith(b"%PDF-") or b"%%EOF" not in data[-1024:]:
        return None
    return data


def resource_pdf(resource: dict) -> bytes | None:
    if resource["reason"] == "approved_idnyc_english_14_plus":
        return approved_pdf()
    try:
        base = PROJECT_RESOURCES if resource.get("source_path") else FORM_DIR
        relative = resource.get("source_path", resource["filename"])
        path = (base / relative).resolve()
        if base.resolve() not in path.parents:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if (len(data) > PDF_LIMIT or not data.startswith(b"%PDF-")
            or b"%%EOF" not in data[-1024:]
            or sha256(data).hexdigest() != resource["sha256"]):
        return None
    return data


def apply_intake_outcome(case_id: str, version: str, request: str, actor: Actor) -> dict:
    """Use a fixed, whole-request rule. The model cannot select a resource or authorize a write."""
    normalized = " ".join(request.casefold().rstrip("?.!").split())
    sensitive = bool(SENSITIVE_INPUT.search(normalized))
    matches = matching_resources(normalized)
    exact_single_request = normalized in RESOURCE_REQUESTS
    if len(matches) > 1 or (matches and not exact_single_request and re.search(r"\b(?:and|also|plus)\b", normalized)):
        return {"status": "submitted", "urgency_band": "unknown"}
    resource_key = None if sensitive else (matches[0] if matches else None)
    human = HUMAN_REQUESTS.get(normalized)
    if sensitive:
        # A mixed request remains untouched as a parent case; no partial automatic reply.
        if re.search(r"\b(?:and|also|plus)\b", normalized):
            return {"status": "submitted", "urgency_band": "unknown"}
        human = ("sensitive_details_require_human", "This request includes personal or health-related details. It remains open for authorized department review; do not enter additional personal documents in this synthetic prototype.")
    if resource_key is None and human is None:
        return {"status": "submitted", "urgency_band": "unknown"}

    resource = RESOURCES.get(resource_key) if resource_key else None
    pdf = resource_pdf(resource) if resource and resource["kind"] == "pdf" else None
    if resource and resource["kind"] == "link":
        route, reason, reply = "resource_link", resource["reason"], resource["reply"]
        source_url = resource["source_url"]
    elif resource and pdf:
        route, reason, reply = "routine_form", resource["reason"], resource["reply"]
        source_url = resource["source_url"]
    else:
        route, reason, reply = "human_review", human[0] if human else "approved_pdf_unavailable", (
            human[1] if human else "The approved document is unavailable. Your request remains open for human review.")
        source_url = None

    delivery_links = (resource.get("delivery_links") or [{"label": resource["title"], "url": resource["source_url"]}]) if resource and resource["kind"] == "link" else []
    basis_case_id = None
    if resource:
        with closing(connect()) as history_db:
            prior = history_db.execute(
                """SELECT o.case_id FROM actionrelay_ticket_outcomes o
                   JOIN synthetic_cases c ON c.case_id = o.case_id
                   WHERE o.reason = ? AND o.case_id != ? AND c.status IN ('resolved','closed')
                     AND o.route IN ('routine_form','resource_link')
                   ORDER BY c.updated_at DESC LIMIT 1""",
                (resource["reason"], case_id),
            ).fetchone()
            basis_case_id = prior["case_id"] if prior else None

    try:
        with closing(connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            case = db.execute(
                """SELECT c.updated_at, c.status, c.urgency_band, c.request_text, c.withdrawal_requested_at,
                          c.assigned_staff_account_id, a.status AS account_status
                   FROM synthetic_cases c JOIN synthetic_accounts a ON a.account_id = c.owner_account_id
                   WHERE c.case_id = ? AND c.owner_account_id = ? AND c.is_synthetic = 1
                     AND c.record_kind = 'user_request' AND a.role = 'user'""",
                (case_id, actor.account_id),
            ).fetchone()
            if (case is None or case["updated_at"] != version or case["status"] != "submitted"
                    or case["request_text"] != request or case["account_status"] != "active"
                    or case["withdrawal_requested_at"] or case["assigned_staff_account_id"]):
                return {"status": case["status"] if case else "submitted",
                        "urgency_band": case["urgency_band"] if case else "unknown"}
            at = stamp(datetime.now(UTC))
            inserted = db.execute(
                """INSERT OR IGNORE INTO actionrelay_ticket_outcomes
                   (case_id, case_version, route, reason, recorded_at, actor_account_id,
                    reply, source_url, pdf_digest, pdf, delivery_links_json, resolution_basis_case_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (case_id, version, route, reason, at, actor.account_id, reply,
                 source_url, sha256(pdf).hexdigest() if pdf else None, pdf,
                 json.dumps(delivery_links, ensure_ascii=False), basis_case_id),
            ).rowcount
            if inserted and route in {"routine_form", "resource_link"}:
                if case["urgency_band"] in {"medium", "high"}:
                    return {"status": case["status"], "urgency_band": case["urgency_band"], "resource_delivered": True}
                updated = db.execute(
                    """UPDATE synthetic_cases SET status = 'resolved', urgency_band = 'low',
                       category = ?, updated_at = ? WHERE case_id = ? AND updated_at = ?""",
                    ("Benefits & Resources" if resource and resource["kind"] == "link" else "Forms & Documents",
                     at, case_id, version),
                ).rowcount
                if updated != 1:
                    raise RuntimeError("outcome_case_version_changed")
                return {"status": "resolved", "urgency_band": "low"}
    except (OSError, RuntimeError, sqlite3.Error):
        # The context manager rolls back both changes on failure.
        return {"status": "submitted", "urgency_band": "unknown"}
    return {"status": "submitted", "urgency_band": "unknown"}


@router.get("/api/cases/{case_id}/reply")
def read_reply(case_id: str, actor: Actor = Depends(require_roles("user", "staff", "admin"))):
    get_case(case_id, actor)
    with closing(connect()) as db:
        row = db.execute(
            """SELECT route, reason, reply, recorded_at, source_url, delivery_links_json, resolution_basis_case_id
               FROM actionrelay_ticket_outcomes WHERE case_id = ?""", (case_id,),
        ).fetchone()
    if not row:
        return None
    result = dict(row)
    result["delivery_links"] = json.loads(result.pop("delivery_links_json") or "[]")
    if actor.role == "user":
        result.pop("resolution_basis_case_id", None)
    return result


@router.get("/api/cases/{case_id}/form.pdf")
def download_form(case_id: str, actor: Actor = Depends(require_roles("user", "staff", "admin"))):
    get_case(case_id, actor)
    with closing(connect()) as db:
        row = db.execute(
            "SELECT pdf, pdf_digest, source_url FROM actionrelay_ticket_outcomes WHERE case_id = ? AND route = 'routine_form'",
            (case_id,),
        ).fetchone()
    if row is None or row["pdf"] is None or sha256(row["pdf"]).hexdigest() != row["pdf_digest"]:
        raise HTTPException(404, "An approved form is not available for this ticket.")
    filename = next((item["filename"] for item in RESOURCES.values()
                     if item["source_url"] == row["source_url"]), "approved-form.pdf")
    return Response(row["pdf"], media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@router.get("/api/queue/activity")
def queue_activity(actor: Actor = Depends(require_roles("staff", "admin"))):
    """Return lifecycle events for the same case scope as the queue."""
    cases = list_cases(actor)
    allowed = {case["case_id"] for case in cases}
    with closing(connect()) as db:
        events = [dict(row) for row in db.execute(
            """SELECT case_id, after_status AS status, occurred_at AS at, action AS kind
               FROM synthetic_case_change_events
               UNION ALL
               SELECT o.case_id, 'resolved', o.recorded_at, 'automatic_fulfillment'
               FROM actionrelay_ticket_outcomes o JOIN synthetic_cases c ON c.case_id = o.case_id
               WHERE o.route IN ('routine_form', 'resource_link') AND c.status IN ('resolved', 'closed')
               ORDER BY at"""
        ) if row["case_id"] in allowed]
        handoffs = [dict(row) for row in db.execute(
            """SELECT case_id, recorded_at AS at FROM actionrelay_ticket_outcomes WHERE route = 'human_review'
               UNION SELECT case_id, completed_at FROM actionrelay_review_runs
               WHERE status = 'human_review' AND completed_at IS NOT NULL
               UNION SELECT case_id, completed_at FROM actionrelay_runs
               WHERE status IN ('human_review', 'blocked') AND completed_at IS NOT NULL"""
        ) if row["case_id"] in allowed]
    return {
        "cases": [{key: case[key] for key in ("case_id", "status", "created_at", "category", "urgency_band",
                   "record_kind")} for case in cases],
        "events": events,
        "handoffs": handoffs,
    }
