"""T2.4: daily sales form endpoint (WBS 2.4, FR-05)."""
from __future__ import annotations

from datetime import date, timedelta

from app.models import Product, Sale


def _add_products(session, business, count=5):
    products = []
    for i in range(count):
        p = Product(
            business_id=business.id,
            name=f"Produk {i + 1}",
            category="nasi",
            price=10000 + i,
            unit_cost=4000,
        )
        session.add(p)
        products.append(p)
    session.commit()
    return products


def test_form_posts_five_products_at_once(auth_client, session, business):
    products = _add_products(session, business)
    payload = {"business_id": str(business.id), "date": date.today().isoformat()}
    for p in products:
        payload[f"qty_{p.id}"] = "7"
    payload[f"sold_out_{products[1].id}"] = "on"

    response = auth_client.post("/sales/new", data=payload)
    assert response.status_code == 200, response.text
    assert "tersimpan" in response.text

    with auth_client.app.state.db.session() as s:
        rows = s.query(Sale).filter(Sale.product_id.in_([p.id for p in products])).all()
    assert len(rows) == 5
    assert all(r.qty_sold == 7 for r in rows)
    assert sum(1 for r in rows if r.sold_out) == 1


def test_repost_same_date_updates_not_duplicates(auth_client, session, business):
    products = _add_products(session, business, count=2)
    day = (date.today() - timedelta(days=1)).isoformat()
    data = {"business_id": str(business.id), "date": day}
    for p in products:
        data[f"qty_{p.id}"] = "5"
    assert auth_client.post("/sales/new", data=data).status_code == 200
    data = {"business_id": str(business.id), "date": day}
    for p in products:
        data[f"qty_{p.id}"] = "9"
    assert auth_client.post("/sales/new", data=data).status_code == 200
    with auth_client.app.state.db.session() as s:
        rows = s.query(Sale).filter(Sale.product_id.in_([p.id for p in products])).all()
    assert len(rows) == 2
    assert all(r.qty_sold == 9 for r in rows)


def test_form_rejects_future_date_and_negative(auth_client, session, business):
    products = _add_products(session, business, count=1)
    future = (date.today() + timedelta(days=2)).isoformat()
    bad = {"business_id": str(business.id), "date": future, f"qty_{products[0].id}": "3"}
    assert auth_client.post("/sales/new", data=bad).status_code == 422

    bad = {
        "business_id": str(business.id),
        "date": date.today().isoformat(),
        f"qty_{products[0].id}": "-3",
    }
    assert auth_client.post("/sales/new", data=bad).status_code == 422
    bad[f"qty_{products[0].id}"] = "abc"
    assert auth_client.post("/sales/new", data=bad).status_code == 422


def test_form_rejects_foreign_business(auth_client, session, other_user):
    from app.models import Business

    foreign = Business(
        user_id=other_user.id, name="X", business_type="warung", location_type="kantor", capacity_factor=1.0
    )
    session.add(foreign)
    session.commit()
    response = auth_client.post(
        "/sales/new", data={"business_id": str(foreign.id), "date": date.today().isoformat()}
    )
    assert response.status_code == 404
