"""Allowlisted presentation and project documents for signed-in accounts."""
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from cdit_support_mao.web import Actor, require_roles

router = APIRouter()
DOCS = Path(__file__).resolve().parents[2] / "docs"
DOCUMENTS = frozenset({
    "requirements/PRD-v4.md",
    "requirements/CASE-SCENARIOS.md",
    "requirements/PRD-USER-NEEDS-AND-USE-CASE-PRIORITIES.md",
    "architecture/actionrelay-field-guide.html",
    "architecture/actionrelay-architecture.html",
    "architecture/actionrelay-architecture.svg",
    "architecture/ActionRelay-Architecture.md",
    "planning/AGENT-IMPLEMENTATION-PHASE-PLAN.md",
    "planning/DEFERRED-DECISIONS.md",
    "planning/phase/undecided/unassigned/LOCAL-APP-DATA-AUTH-PLAN.md",
    "artifacts/cdit-support-mao-architecture-prd-v2.jpg",
    "artifacts/cdit-support-mao-field-guide.html",
    "presentations/ActionRelay-review/actionrelay-demo.html",
    "presentations/ActionRelay-review/actionrelay-demo-beats.html",
    "presentations/ACTIONRELAY-REVIEW.md",
    "presentations/ActionRelay-v2/actionrelay-final.html",
    "presentations/ActionRelay/actionrelay-demo.html",
    "presentations/ActionRelay/actionrelay-demo-beats.html",
    "presentations/ActionRelay/actionrelay-final.html",
    "resources/synthetic-workplace-guide.pdf",
    "resources/synthetic-company-directory.pdf",
    "resources/synthetic-vacation-request.pdf",
    "resources/synthetic-workplace-complaint.pdf",
    "presentations/ActionRelay/ActionRelay-Sample-Weekly-Timesheet.pdf",
    "presentations/ActionRelay/ActionRelay-Sample-Shift-Options-and-Change-Request.pdf",
})


@router.get("/project-docs/{name:path}", include_in_schema=False)
def project_resource(name: str, _actor: Actor = Depends(require_roles("user", "staff", "admin"))):
    if name not in DOCUMENTS or not (DOCS / name).is_file():
        raise HTTPException(404, "Project resource not found.")
    return FileResponse(
        DOCS / name,
        media_type="text/plain; charset=utf-8" if name.endswith(".md") else None,
        headers={
            "X-Frame-Options": "SAMEORIGIN",
            "Cache-Control": "no-store",
            "Content-Security-Policy": (
                "sandbox allow-scripts allow-downloads allow-popups allow-popups-to-escape-sandbox; "
                "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; "
                "img-src 'self' data:; media-src data: blob:; connect-src 'none'; frame-ancestors 'self'"
            ),
        },
    )
