"""T2.3: business profile and menu API tests (WBS 2.3, FR-02, FR-03, FR-04)."""
from __future__ import annotations

from app.models import Business


def _create_business(client, **overrides):
    payload = {
        "name": "Warung Baru",
        "business_type": "warung",
        "location_type": "kampus",
        "capacity_factor": 1.2,
    }
    payload.update(overrides)
    return client.post("/api/businesses", json=payload)


def test_fr02_create_read_update_business(auth_client):
    created = _create_business(auth_client)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["business_type"] == "warung"
    business_id = body["id"]

    read = auth_client.get(f"/api/businesses/{business_id}")
    assert read.status_code == 200 and read.json()["name"] == "Warung Baru"

    updated = auth_client.put(f"/api/businesses/{business_id}", json={"name": "Warung Lama"})
    assert updated.status_code == 200 and updated.json()["name"] == "Warung Lama"

    listed = auth_client.get("/api/businesses")
    assert [b["id"] for b in listed.json()] == [business_id]


def test_fr02_validation_rejects_bad_vocabulary_and_name(auth_client):
    assert _create_business(auth_client, business_type="restoran").status_code == 422
    assert _create_business(auth_client, location_type="bulan").status_code == 422
    assert _create_business(auth_client, name="   ").status_code == 422
    assert _create_business(auth_client, capacity_factor=0).status_code == 422


def test_fr03_product_crud_and_soft_delete(auth_client, business):
    created = auth_client.post(
        f"/api/businesses/{business.id}/products",
        json={"name": "Es Teh", "category": "minuman", "price": 5000, "unit_cost": 1500},
    )
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]
    assert created.json()["active"] is True

    updated = auth_client.put(f"/api/products/{product_id}", json={"price": 6000, "unit_cost": 2000})
    assert updated.status_code == 200 and updated.json()["price"] == 6000

    deleted = auth_client.delete(f"/api/products/{product_id}")
    assert deleted.status_code == 200 and deleted.json()["active"] is False

    listed = auth_client.get(f"/api/businesses/{business.id}/products").json()
    assert listed == []
    all_products = auth_client.get(
        f"/api/businesses/{business.id}/products", params={"include_inactive": "true"}
    ).json()
    assert [p["id"] for p in all_products] == [product_id]


def test_fr03_product_validation(auth_client, business):
    base = {"name": "X", "category": "nasi", "price": 10000, "unit_cost": 4000}
    assert auth_client.post(f"/api/businesses/{business.id}/products", json={**base, "price": 0}).status_code == 422
    assert auth_client.post(f"/api/businesses/{business.id}/products", json={**base, "unit_cost": -1}).status_code == 422
    assert auth_client.post(f"/api/businesses/{business.id}/products", json={**base, "category": "pizza"}).status_code == 422


def test_fr04_cross_user_access_is_404(auth_client, session, other_user):
    foreign = Business(
        user_id=other_user.id,
        name="Milik Orang",
        business_type="cafe",
        location_type="kantor",
        capacity_factor=1.0,
    )
    session.add(foreign)
    session.commit()
    foreign_id = foreign.id

    assert auth_client.get(f"/api/businesses/{foreign_id}").status_code == 404
    assert auth_client.put(f"/api/businesses/{foreign_id}", json={"name": "Hack"}).status_code == 404
    assert auth_client.get(f"/api/businesses/{foreign_id}/products").status_code == 404
    assert auth_client.post(
        f"/api/businesses/{foreign_id}/products",
        json={"name": "X", "category": "nasi", "price": 9000, "unit_cost": 3000},
    ).status_code == 404


def test_fr04_cross_user_product_update_is_404(auth_client, session, other_user):
    foreign_business = Business(
        user_id=other_user.id, name="B2", business_type="bakery", location_type="pasar", capacity_factor=1.0
    )
    session.add(foreign_business)
    session.flush()
    from app.models import Product

    foreign_product = Product(
        business_id=foreign_business.id, name="Roti", category="roti", price=8000, unit_cost=3000
    )
    session.add(foreign_product)
    session.commit()
    product_id = foreign_product.id

    assert auth_client.put(f"/api/products/{product_id}", json={"price": 9000}).status_code == 404
    assert auth_client.delete(f"/api/products/{product_id}").status_code == 404


def test_api_requires_login(client):
    assert client.get("/api/businesses").status_code == 401
    assert client.post("/api/businesses", json={}).status_code == 401
