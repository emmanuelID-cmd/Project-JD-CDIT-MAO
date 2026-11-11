"""FastAPI entry point for the local synthetic prototype."""
from __future__ import annotations

from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.exception_handlers import http_exception_handler
from urllib.parse import quote
from fastapi.staticfiles import StaticFiles

from cdit_support_mao.actionrelay_live import router as actionrelay_router
from cdit_support_mao.actionrelay_outcomes import router as outcomes_router
from cdit_support_mao.actionrelay_resources import router as resources_router
from cdit_support_mao.actionrelay_review import router as review_router
from cdit_support_mao.database import check_database
from cdit_support_mao.web import Actor, current_actor, require_roles, router as web_router


STATIC_DIR = Path(__file__).parent / "static"
app = FastAPI(
    title="CDIT Support Desk MAO",
    description="Local synthetic ActionRelay prototype with supervised live Triage.",
    version="0.1.0",
)
app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")
app.include_router(web_router)
app.include_router(actionrelay_router)
app.include_router(outcomes_router)
app.include_router(resources_router)
app.include_router(review_router)


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
    if request.url.path.startswith("/app/") or request.url.path.startswith("/api/"):
        response.headers.setdefault("Cache-Control", "no-store")
    return response


@app.exception_handler(HTTPException)
async def page_access_error(request, exc: HTTPException):
    if request.url.path.startswith("/app/") and exc.status_code == 401:
        return RedirectResponse("/login?next=" + quote(request.url.path), status_code=303)
    if request.url.path.startswith("/app/") and exc.status_code == 403:
        return FileResponse(STATIC_DIR / "denied.html", status_code=403, headers={"Cache-Control": "no-store"})
    return await http_exception_handler(request, exc)


@app.get("/", include_in_schema=False)
def home() -> RedirectResponse:
    return RedirectResponse("/login", status_code=303)


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "login.html", headers={"Cache-Control": "no-store"})


@app.get("/preview/{role}", response_class=HTMLResponse, include_in_schema=False)
def role_preview(role: str) -> FileResponse:
    if role not in {"user", "staff", "admin"}:
        raise HTTPException(status_code=404, detail="Preview not found")
    page = STATIC_DIR / ("preview-" + role + ".html")
    return FileResponse(
        page,
        headers={
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'; style-src 'self'; font-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
        },
    )


def _app_page(role: str, actor: Actor) -> HTMLResponse:
    template = (STATIC_DIR / "app.html").read_text(encoding="utf-8-sig")
    page = template.replace("<body>", '<body data-role="' + role + '">')
    return HTMLResponse(
        page,
        headers={
            "Cache-Control": "no-store",
            "X-Authenticated-Role": actor.role,
        },
    )


@app.get("/app/resources", response_class=HTMLResponse, include_in_schema=False)
def resources_app(actor: Actor = Depends(current_actor)) -> HTMLResponse:
    return _app_page(actor.role, actor)


@app.get("/app/user", response_class=HTMLResponse, include_in_schema=False)
def user_app(actor: Actor = Depends(require_roles("user"))) -> HTMLResponse:
    return _app_page("user", actor)


@app.get("/app/staff", response_class=HTMLResponse, include_in_schema=False)
def staff_app(actor: Actor = Depends(require_roles("staff"))) -> HTMLResponse:
    return _app_page("staff", actor)


@app.get("/app/admin", response_class=HTMLResponse, include_in_schema=False)
def admin_app(actor: Actor = Depends(require_roles("admin"))) -> HTMLResponse:
    return _app_page("admin", actor)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Report API availability and local SQLite connectivity."""
    check_database()
    return {"status": "ok", "database": "ok"}
