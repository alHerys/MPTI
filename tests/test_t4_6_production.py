"""T4.6: production readiness tests (WBS 4.6, FR-17)."""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import validate_production_settings
from app.main import create_app
from app.rate_limit import login_limiter

ROOT = Path(__file__).resolve().parents[1]


def test_missing_secret_key_refused(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.setenv("DEMO_PASSWORD", "kuat-sekali")
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        validate_production_settings()


def test_default_demo_password_refused(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "x" * 32)
    monkeypatch.setenv("DEMO_PASSWORD", "demo123")
    with pytest.raises(RuntimeError, match="DEMO_PASSWORD"):
        validate_production_settings()


def test_short_secret_key_refused(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "pendek")
    monkeypatch.setenv("DEMO_PASSWORD", "kuat-sekali")
    with pytest.raises(RuntimeError, match="terlalu pendek"):
        validate_production_settings()


def test_startup_refuses_in_production_without_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(database_url="sqlite://", seed=False)


def test_production_settings_accepted_and_cookie_flags(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "y" * 40)
    monkeypatch.setenv("DEMO_PASSWORD", "kuat-sekali")
    validate_production_settings()
    app = create_app(database_url="sqlite://", seed=False, startup_check=False)
    cookie = None
    with TestClient(app) as client:
        login_limiter.reset()
        response = client.post("/login", data={"username": "nobody", "password": "x"},
                               follow_redirects=False)
        assert response.status_code == 401
    # Middleware configured with https_only in production; assert through app stack.
    middleware = [m for m in app.user_middleware if "SessionMiddleware" in str(m)]
    assert middleware and middleware[0].kwargs.get("https_only") is True
    assert middleware[0].kwargs.get("same_site") == "lax"


def test_healthz_shape(client):
    response = client.get("/healthz")
    assert response.json() == {"status": "ok", "db": "ok"}


def test_healthz_reports_db_failure(app):
    with TestClient(app) as client:
        app.state.db.engine.dispose()

        class Broken:
            def healthcheck(self):
                raise RuntimeError("down")

        original = app.state.db
        app.state.db = Broken()
        try:
            response = client.get("/healthz")
            assert response.json() == {"status": "error", "db": "error"}
        finally:
            app.state.db = original


def test_run_prod_script_excludes_defaults():
    script = (ROOT / "scripts" / "run_prod.sh").read_text(encoding="utf-8")
    assert "set -euo pipefail" in script
    assert ".env.prod" in script
    assert "SECRET_KEY" in script and "DEMO_PASSWORD" in script
    assert "--proxy-headers" in script
    assert "127.0.0.1" in script
    assert "sqlite:///./var/" in script


def test_deployment_artifacts_exist():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "python:3.11-slim" in dockerfile
    assert "USER app" in dockerfile
    assert "--proxy-headers" in dockerfile
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")
    assert "generateValue: true" in render and "DATABASE_URL" in render and "DEMO_PASSWORD" in render
    plist = (ROOT / "deploy" / "com.coldstart.app.plist").read_text(encoding="utf-8")
    assert "<key>KeepAlive</key>" in plist and "run_prod.sh" in plist
    assert (ROOT / "docs" / "deploy.md").exists()


def test_requirements_only_allowed_dependencies():
    allowed = {
        "fastapi", "uvicorn", "jinja2", "sqlalchemy", "python-multipart", "itsdangerous",
        "numpy", "scipy", "pytest", "httpx", "psycopg2-binary",
    }
    lines = [
        line.strip() for line in (ROOT / "requirements.txt").read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    names = {line.split("[")[0].split("==")[0].split(">=")[0].strip() for line in lines}
    assert names <= allowed, names - allowed
