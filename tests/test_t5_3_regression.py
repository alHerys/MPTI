"""T5.3: edge-case regression tests (WBS 5.3) including NFR-01 performance."""
from __future__ import annotations

import time
from datetime import date, timedelta

import pytest

from app.models import Product, Sale


def test_nfr01_recommendations_under_three_seconds(auth_client, session, business):
    for i in range(50):
        session.add(
            Product(
                business_id=business.id,
                name=f"Produk {i:02d}",
                category=["nasi", "mie", "snack", "minuman", "roti"][i % 5],
                price=10000 + i * 100,
                unit_cost=4000,
            )
        )
    session.commit()
    start = time.perf_counter()
    response = auth_client.get(
        f"/api/businesses/{business.id}/recommendations",
        params={"date": (date.today() + timedelta(days=1)).isoformat()},
    )
    elapsed = time.perf_counter() - start
    assert response.status_code == 200
    assert len(response.json()["items"]) == 50
    assert elapsed < 3.0, f"rekomendasi 50 produk butuh {elapsed:.2f}s"


def test_zero_sales_day_is_a_valid_observation(auth_client, product):
    response = auth_client.post(
        "/api/sales",
        json={"product_id": product.id, "date": (date.today() - timedelta(days=1)).isoformat(), "qty_sold": 0},
    )
    assert response.status_code == 200
    rec = auth_client.get(f"/api/products/{product.id}/recommendation").json()
    assert rec["n_days"] == 1
    assert rec["p50"] >= 0


def test_very_large_qty_is_accepted_and_safe(auth_client, product):
    response = auth_client.post(
        "/api/sales",
        json={"product_id": product.id, "date": (date.today() - timedelta(days=1)).isoformat(),
              "qty_sold": 1_000_000},
    )
    assert response.status_code == 200
    rec = auth_client.get(f"/api/products/{product.id}/recommendation").json()
    assert rec["p10"] <= rec["p50"] <= rec["p90"]
    assert rec["recommended_qty"] >= 0


def test_unicode_product_name(auth_client, business):
    name = "Es Krim 🍦 Kacang Ünïcode"
    created = auth_client.post(
        f"/api/businesses/{business.id}/products",
        json={"name": name, "category": "minuman", "price": 8000, "unit_cost": 3000},
    )
    assert created.status_code == 201
    rec = auth_client.get(f"/api/products/{created.json()['id']}/recommendation").json()
    assert rec["name"] == name
    assert name in auth_client.get("/business").text


def test_duplicate_dates_via_form_do_not_duplicate_rows(auth_client, session, business, product):
    day = (date.today() - timedelta(days=2)).isoformat()
    for qty in (3, 4, 5):
        response = auth_client.post(
            "/sales/new", data={"business_id": str(business.id), "date": day, f"qty_{product.id}": str(qty)}
        )
        assert response.status_code == 200
    with auth_client.app.state.db.session() as s:
        rows = s.query(Sale).filter(Sale.product_id == product.id).all()
    assert len(rows) == 1 and rows[0].qty_sold == 5


def test_future_date_rejected_everywhere(auth_client, product, business):
    future = (date.today() + timedelta(days=1)).isoformat()
    assert auth_client.post(
        "/api/sales", json={"product_id": product.id, "date": future, "qty_sold": 1}
    ).status_code == 422
    assert auth_client.post(
        "/sales/new", data={"business_id": str(business.id), "date": future, f"qty_{product.id}": "1"}
    ).status_code == 422


def test_salvage_above_cost_rejected_on_update(auth_client, product):
    response = auth_client.put(f"/api/products/{product.id}", json={"salvage_value": 999999})
    assert response.status_code == 422


def test_price_equals_cost_blocks_recommendation(auth_client, product):
    auth_client.put(f"/api/products/{product.id}", json={"unit_cost": product.price})
    response = auth_client.get(f"/api/products/{product.id}/recommendation")
    assert response.status_code == 422


def test_inactive_product_excluded_after_deactivate(auth_client, business, product):
    auth_client.delete(f"/api/products/{product.id}")
    body = auth_client.get(f"/api/businesses/{business.id}/recommendations").json()
    assert body["items"] == []


def test_healthz_and_login_page_have_no_session_requirement(client):
    assert client.get("/healthz").status_code == 200
    assert client.get("/login").status_code == 200
