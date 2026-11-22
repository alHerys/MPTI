"""T4.5: auth, session, demo seed (WBS 4.5, FR-01, FR-16, FR-17)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.models import Business, Product, Sale, User
from app.rate_limit import login_limiter


def test_fr01_unauthenticated_pages_redirect_and_api_401(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == "/login"
    for path in ("/business", "/sales/new", "/sales", "/import"):
        assert client.get(path, follow_redirects=False).status_code == 303
    assert client.get("/api/businesses").status_code == 401
    assert client.get("/healthz").status_code == 200


def test_fr01_wrong_password_rejected(client, user):
    response = client.post("/login", data={"username": "demo", "password": "salah"}, follow_redirects=False)
    assert response.status_code == 401
    assert "salah" in response.text
    assert client.get("/", follow_redirects=False).status_code == 303


def test_fr01_login_and_logout(client, user):
    response = client.post(
        "/login", data={"username": "demo", "password": "demo123"}, follow_redirects=False
    )
    assert response.status_code == 303
    assert client.get("/api/businesses").status_code == 200
    logout = client.post("/logout", follow_redirects=False)
    assert logout.status_code == 303 and logout.headers["location"] == "/login"
    assert client.get("/api/businesses").status_code == 401


def test_login_page_redirects_when_authenticated(auth_client):
    response = auth_client.get("/login", follow_redirects=False)
    assert response.status_code == 303


def test_fr16_seed_creates_demo_user_and_three_stages(tmp_path):
    url = f"sqlite:///{tmp_path / 'seeded.db'}"
    app = create_app(database_url=url, seed=True, startup_check=False)
    with TestClient(app) as c:
        login = c.post("/login", data={"username": "demo", "password": "demo123"}, follow_redirects=False)
        assert login.status_code == 303
        businesses = c.get("/api/businesses").json()
        assert len(businesses) == 3
        stages = []
        for business in businesses:
            products = c.get(f"/api/businesses/{business['id']}/products").json()
            assert len(products) == 5
            items = c.get(f"/api/businesses/{business['id']}/recommendations").json()["items"]
            stages.append({item["stage"] for item in items})
    assert stages == [{"H0"}, {"H3"}, {"H7"}]


def test_seed_is_idempotent(tmp_path):
    url = f"sqlite:///{tmp_path / 'idem.db'}"
    app = create_app(database_url=url, seed=True, startup_check=False)
    with TestClient(app) as c:
        assert len(c.post("/login", data={"username": "demo", "password": "demo123"},
                          follow_redirects=False).content) >= 0
        first = c.get("/api/businesses").json()
    app2 = create_app(database_url=url, seed=True, startup_check=False)
    with TestClient(app2) as c2:
        c2.post("/login", data={"username": "demo", "password": "demo123"})
        second = c2.get("/api/businesses").json()
    assert [b["id"] for b in first] == [b["id"] for b in second]


def test_demo_credentials_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_USER", "pemilik")
    monkeypatch.setenv("DEMO_PASSWORD", "rahasia-sekali")
    url = f"sqlite:///{tmp_path / 'env.db'}"
    app = create_app(database_url=url, seed=True, startup_check=False)
    with TestClient(app) as c:
        assert c.post("/login", data={"username": "demo", "password": "demo123"},
                      follow_redirects=False).status_code == 401
        assert c.post("/login", data={"username": "pemilik", "password": "rahasia-sekali"},
                      follow_redirects=False).status_code == 303


def test_users_are_isolated(auth_client, session, other_user):
    from app.models import Business

    session.add(Business(user_id=other_user.id, name="Usaha Lain", business_type="cafe",
                         location_type="kantor", capacity_factor=1.0))
    session.commit()
    names = [b["name"] for b in auth_client.get("/api/businesses").json()]
    assert names == []


def test_fr17_login_rate_limit_returns_429(client, user):
    login_limiter.reset()
    for _ in range(10):
        assert client.post("/login", data={"username": "demo", "password": "bad"},
                           follow_redirects=False).status_code == 401
    blocked = client.post("/login", data={"username": "demo", "password": "bad"}, follow_redirects=False)
    assert blocked.status_code == 429
    assert "Terlalu banyak" in blocked.text
    # Correct credentials are still blocked from the same IP+username.
    still = client.post("/login", data={"username": "demo", "password": "demo123"}, follow_redirects=False)
    assert still.status_code == 429
    login_limiter.reset()
