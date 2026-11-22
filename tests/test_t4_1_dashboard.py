"""T4.1/T4.2/T4.4: dashboard layout and JS rendering (WBS 4.1, 4.2, 4.4, FR-12, FR-15)."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from app.models import Business, Product, Sale

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_renders_for_authenticated_user(auth_client, business, product):
    response = auth_client.get("/")
    assert response.status_code == 200
    assert "Rekomendasi Produksi" in response.text
    assert 'id="recommendation-grid"' in response.text
    assert 'data-business-id="' in response.text
    assert 'src="/static/dashboard.js"' in response.text
    assert 'name="viewport"' in response.text


def test_fr15_css_has_mobile_first_media_query():
    css = (ROOT / "app" / "static" / "app.css").read_text(encoding="utf-8")
    assert "@media (min-width: 640px)" in css
    assert ".card-grid { display: grid; gap: 16px; grid-template-columns: 1fr; }" in css


def test_dashboard_template_has_no_hardcoded_recommendations():
    template = (ROOT / "app" / "templates" / "dashboard.html").read_text(encoding="utf-8")
    js = (ROOT / "app" / "static" / "dashboard.js").read_text(encoding="utf-8")
    for needle in ("Produksi ±", "P10 ", "P90 ", "recommended_qty", "sedang", "tinggi"):
        assert needle not in template
    assert template.count("data-field=") >= 8
    # JS builds text from API fields, not literal numbers.
    assert "/recommendations?date=" in js
    assert "Produksi ± " in js
    assert "P10 " in js and "P90 " in js


def test_dashboard_js_fetches_expected_api(auth_client, session, user):
    business = Business(user_id=user.id, name="JS Bus", business_type="warung",
                        location_type="kampus", capacity_factor=1.0)
    session.add(business)
    session.flush()
    for i in range(2):
        session.add(Product(business_id=business.id, name=f"P{i}", category="nasi",
                            price=10000, unit_cost=4000))
    session.commit()
    target = (date.today() + timedelta(days=1)).isoformat()
    response = auth_client.get("/", params={"business_id": business.id, "date_str": target})
    assert f'data-business-id="{business.id}"' in response.text
    assert f'data-date="{target}"' in response.text
    payload = auth_client.get(
        f"/api/businesses/{business.id}/recommendations", params={"date": target}
    ).json()
    assert len(payload["items"]) == 2
    for item in payload["items"]:
        assert item["stage"] == "H0"
        assert item["p10"] <= item["p50"] <= item["p90"]
        assert item["recommended_qty"] >= 0
        assert item["confidence"] in {"rendah", "sedang", "tinggi"}
        assert item["reasons"]


def test_business_selector_lists_all_businesses(auth_client, session, user):
    for name in ("A", "B"):
        session.add(Business(user_id=user.id, name=name, business_type="warung",
                             location_type="pasar", capacity_factor=1.0))
    session.commit()
    text = auth_client.get("/").text
    assert ">A<" in text and ">B<" in text


def test_dashboard_defaults_date_to_tomorrow(auth_client, business):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert f'value="{tomorrow}"' in auth_client.get("/").text
