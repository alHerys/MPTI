"""Shared pytest fixtures: isolated DB, test client, seeded users."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.auth import hash_password  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models import Business, Product, User  # noqa: E402
from app.rate_limit import login_limiter  # noqa: E402


@pytest.fixture()
def app(tmp_path):
    url = f"sqlite:///{tmp_path / 'test.db'}"
    application = create_app(database_url=url, seed=False, startup_check=False)
    return application


@pytest.fixture()
def client(app):
    login_limiter.reset()
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def session(app):
    with app.state.db.session() as s:
        yield s


@pytest.fixture()
def user(session):
    u = User(username="demo", password_hash=hash_password("demo123"))
    session.add(u)
    session.commit()
    return u


@pytest.fixture()
def other_user(session):
    u = User(username="lain", password_hash=hash_password("rahasia"))
    session.add(u)
    session.commit()
    return u


@pytest.fixture()
def auth_client(client, user):
    response = client.post("/login", data={"username": "demo", "password": "demo123"}, follow_redirects=False)
    assert response.status_code == 303
    return client


@pytest.fixture()
def business(session, user):
    b = Business(
        user_id=user.id,
        name="Warung Uji",
        business_type="warung",
        location_type="kampus",
        capacity_factor=1.0,
    )
    session.add(b)
    session.commit()
    return b


@pytest.fixture()
def product(session, business):
    p = Product(
        business_id=business.id,
        name="Nasi Ayam",
        category="nasi",
        price=12000,
        unit_cost=6000,
        salvage_value=0,
    )
    session.add(p)
    session.commit()
    return p
