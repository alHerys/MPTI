"""T3.6: engine wiring and recommendation API (WBS 3.6, FR-09..FR-14)."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.models import Product, Sale

TODAY = date.today()
TARGET = (TODAY + timedelta(days=1)).isoformat()

FIELD_SET = {
    "product_id", "name", "date", "stage", "n_days", "mean", "p10", "p50", "p90",
    "alpha", "recommended_qty", "nearest_band", "confidence", "reasons", "neighbor_count",
}


def _add_days(auth_client, product_id, days, qty=12):
    start = TODAY - timedelta(days=days)
    for i in range(days):
        response = auth_client.post(
            "/api/sales",
            json={"product_id": product_id, "date": (start + timedelta(days=i)).isoformat(), "qty_sold": qty},
        )
        assert response.status_code == 200, response.text


@pytest.mark.parametrize("days,stage", [(0, "H0"), (3, "H3"), (7, "H7")])
def test_fr09_fr10_fr11_stage_by_history(auth_client, product, days, stage):
    _add_days(auth_client, product.id, days)
    response = auth_client.get(f"/api/products/{product.id}/recommendation", params={"date": TARGET})
    assert response.status_code == 200, response.text
    body = response.json()
    assert FIELD_SET <= set(body)
    assert body["stage"] == stage and body["n_days"] == days
    assert body["p10"] <= body["p50"] <= body["p90"]
    assert isinstance(body["recommended_qty"], int) and body["recommended_qty"] >= 0
    assert body["confidence"] in {"rendah", "sedang", "tinggi"}
    assert body["reasons"]
    assert body["nearest_band"] in {"P10", "P50", "P90"}
    assert body["neighbor_count"] >= 1


def test_fr09_recommendation_with_zero_sales_positive(auth_client, product):
    body = auth_client.get(f"/api/products/{product.id}/recommendation").json()
    assert body["n_days"] == 0 and body["stage"] == "H0"
    assert body["p50"] > 0 and body["mean"] > 0


def test_fr11_results_change_with_new_sales(auth_client, product):
    first = auth_client.get(f"/api/products/{product.id}/recommendation", params={"date": TARGET}).json()
    _add_days(auth_client, product.id, 4, qty=40)
    second = auth_client.get(f"/api/products/{product.id}/recommendation", params={"date": TARGET}).json()
    assert second["n_days"] == 4
    assert second["stage"] == "H3"
    assert (second["p50"], second["recommended_qty"]) != (first["p50"], first["recommended_qty"])


def test_business_recommendations_excludes_inactive(auth_client, session, business):
    for name in ("Aktif 1", "Aktif 2"):
        session.add(Product(business_id=business.id, name=name, category="nasi", price=10000, unit_cost=4000))
    session.commit()
    inactive = Product(business_id=business.id, name="Nonaktif", category="mie", price=9000, unit_cost=3000, active=False)
    session.add(inactive)
    session.commit()
    body = auth_client.get(
        f"/api/businesses/{business.id}/recommendations", params={"date": TARGET}
    ).json()
    names = [i["name"] for i in body["items"]]
    assert names == ["Aktif 1", "Aktif 2"]
    assert body["date"] == TARGET


def test_recommendation_ownership_and_inactive_404(auth_client, session, other_user):
    from app.models import Business

    foreign = Business(
        user_id=other_user.id, name="F", business_type="cafe", location_type="pasar", capacity_factor=1.0
    )
    session.add(foreign)
    session.flush()
    foreign_product = Product(
        business_id=foreign.id, name="Milik Orang", category="nasi", price=9000, unit_cost=3000
    )
    session.add(foreign_product)
    session.commit()

    assert auth_client.get(f"/api/products/{foreign_product.id}/recommendation").status_code == 404
    assert auth_client.get(f"/api/businesses/{foreign.id}/recommendations").status_code == 404


def test_price_below_cost_returns_422(auth_client, product):
    auth_client.put(f"/api/products/{product.id}", json={"unit_cost": 12000})
    response = auth_client.get(f"/api/products/{product.id}/recommendation")
    assert response.status_code == 422
    assert "biaya" in response.json()["detail"].lower()


def test_bad_date_returns_422(auth_client, product):
    response = auth_client.get(f"/api/products/{product.id}/recommendation", params={"date": "23-11-2026"})
    assert response.status_code == 422


def test_engine_is_pure_no_db_reference():
    import inspect

    import app.ml.engine as engine

    source = inspect.getsource(engine)
    assert "sqlalchemy" not in source
    assert "app.models" not in source
