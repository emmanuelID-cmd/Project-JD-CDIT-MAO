from fastapi.testclient import TestClient

from cdit_support_mao.database import seed_synthetic_data
from cdit_support_mao.main import app
from cdit_support_mao.web import provision_synthetic_password


def setup(tmp_path, monkeypatch, role):
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "ui.sqlite3"
    monkeypatch.setenv("CDIT_DATABASE_PATH", str(path))
    seed_synthetic_data(path)
    account_id = {"user": "SYN-USER-001", "staff": "SYN-STAFF-001", "admin": "SYN-ADMIN-001"}[role]
    provision_synthetic_password(account_id, "Synthetic-test-password-2026!")
    client = TestClient(app)
    login = client.post("/auth/login", json={"username": role + ".demo", "password": "Synthetic-test-password-2026!"})
    assert login.status_code == 200
    return client


def test_login_and_static_preview_routes_are_available_without_auth():
    client = TestClient(app)
    assert client.get("/login").status_code == 200
    for role in ("user", "staff", "admin"):
        response = client.get("/preview/" + role)
        assert response.status_code == 200
        assert "STATIC ROLE SHOWCASE" in response.text
        assert "<script" not in response.text.lower()
        assert "/api/" not in response.text
        assert "connect-src" not in response.text.lower()
        assert "default-src 'none'" in response.headers["content-security-policy"]


def test_preview_css_has_no_external_resource_import():
    client = TestClient(app)
    css = client.get("/assets/app.css")
    assert css.status_code == 200
    assert "@import" not in css.text.lower()
    assert "https://" not in css.text.lower()


def test_authenticated_role_pages_require_matching_server_authorization(tmp_path, monkeypatch):
    for role in ("user", "staff", "admin"):
        client = setup(tmp_path / role, monkeypatch, role)
        expected = client.get("/app/" + role)
        assert expected.status_code == 200
        assert 'data-role="' + role + '"' in expected.text
        for other in {"user", "staff", "admin"} - {role}:
            denied = client.get("/app/" + other)
            assert denied.status_code == 403




def test_protected_pages_redirect_and_role_denials_are_safe(tmp_path, monkeypatch):
    client = TestClient(app)
    response = client.get("/app/user", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/login?next=")

    client = setup(tmp_path / "role-denial", monkeypatch, "user")
    denied = client.get("/app/admin")
    assert denied.status_code == 403
    assert "No protected data was returned" in denied.text
    assert "account-list" not in denied.text


def test_user_request_content_is_parameterized_and_remains_plain_synthetic_text(tmp_path, monkeypatch):
    client = setup(tmp_path / "sql-input", monkeypatch, "user")
    marker = "SYNTHETIC '; DROP TABLE synthetic_cases; --"
    response = client.post("/api/cases", json={"subject": marker, "request_text": marker})
    assert response.status_code == 201
    listing = client.get("/api/cases")
    assert listing.status_code == 200
    assert any(case["subject"] == marker and case["request_text"] == marker for case in listing.json())
    assert client.get("/health").json()["database"] == "ok"
