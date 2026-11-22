"""T2.5: sales API tests (WBS 2.5, FR-05, FR-06, FR-04)."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

TODAY = date.today()


def test_fr05_upsert_is_idempotent(auth_client, product):
    first = auth_client.post(
        "/api/sales",
        json={"product_id": product.id, "date": "2026-01-05", "qty_sold": 10, "sold_out": False},
    )
    assert first.status_code == 200, first.text
    second = auth_client.post(
        "/api/sales",
        json={"product_id": product.id, "date": "2026-01-05", "qty_sold": 14, "sold_out": True},
    )
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]

    rows = auth_client.get(f"/api/products/{product.id}/sales").json()
    assert len(rows) == 1
    assert rows[0]["qty_sold"] == 14 and rows[0]["sold_out"] is True


def test_fr06_range_filter_is_inclusive(auth_client, product):
    base = TODAY - timedelta(days=10)
    for offset, qty in ((0, 1), (1, 2), (2, 3), (3, 4)):
        day = base + timedelta(days=offset)
        auth_client.post(
            "/api/sales", json={"product_id": product.id, "date": day.isoformat(), "qty_sold": qty}
        )
    start = (base + timedelta(days=1)).isoformat()
    end = (base + timedelta(days=2)).isoformat()
    rows = auth_client.get(f"/api/products/{product.id}/sales", params={"from": start, "to": end}).json()
    assert [r["qty_sold"] for r in rows] == [2, 3]


def test_fr05_validation_rejects_negative_and_future(auth_client, product):
    future = (TODAY + timedelta(days=1)).isoformat()
    assert auth_client.post(
        "/api/sales", json={"product_id": product.id, "date": future, "qty_sold": 3}
    ).status_code == 422
    assert auth_client.post(
        "/api/sales", json={"product_id": product.id, "date": "2026-01-01", "qty_sold": -2}
    ).status_code == 422
    assert auth_client.post(
        "/api/sales", json={"product_id": product.id, "date": "2026-01-01", "qty_sold": 1.5}
    ).status_code == 422
    assert auth_client.post(
        "/api/sales", json={"product_id": 99999, "date": "2026-01-01", "qty_sold": 1}
    ).status_code == 404


def test_fr04_sales_ownership(auth_client, session, other_user):
    from app.models import Business, Product

    foreign = Business(
        user_id=other_user.id, name="B", business_type="warung", location_type="pasar", capacity_factor=1.0
    )
    session.add(foreign)
    session.flush()
    foreign_product = Product(
        business_id=foreign.id, name="S", category="snack", price=5000, unit_cost=2000
    )
    session.add(foreign_product)
    session.commit()
    pid = foreign_product.id
    bid = foreign.id

    assert auth_client.get(f"/api/products/{pid}/sales").status_code == 404
    assert auth_client.get(f"/api/businesses/{bid}/sales").status_code == 404
    assert auth_client.post(
        "/api/sales", json={"product_id": pid, "date": "2026-01-01", "qty_sold": 1}
    ).status_code == 404


def test_business_sales_listing_includes_names(auth_client, product):
    auth_client.post(
        "/api/sales", json={"product_id": product.id, "date": "2026-01-02", "qty_sold": 7}
    )
    rows = auth_client.get(f"/api/businesses/{product.business_id}/sales").json()
    assert len(rows) == 1
    assert rows[0]["product"] == "Nasi Ayam"
    assert rows[0]["qty_sold"] == 7
    filtered = auth_client.get(
        f"/api/businesses/{product.business_id}/sales", params={"start": "2026-01-03"}
    ).json()
    assert filtered == []


def test_inactive_product_cannot_receive_sales(auth_client, product):
    auth_client.delete(f"/api/products/{product.id}")
    response = auth_client.post(
        "/api/sales", json={"product_id": product.id, "date": "2026-01-01", "qty_sold": 2}
    )
    assert response.status_code == 422
