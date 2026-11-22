"""T2.3-UI, T2.4-UI, T4.2, T4.3, T2.6-UI: page-level tests (FR-12, FR-18)."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from app.models import Business, Product, Sale

ROOT = Path(__file__).resolve().parents[1]


def test_fr18_all_pages_render(auth_client, business, product):
    for path, needle in [
        ("/business", "Profil Usaha"),
        ("/sales/new", "Catat Penjualan"),
        ("/sales", "Riwayat Penjualan"),
        ("/import", "Impor Penjualan CSV"),
    ]:
        response = auth_client.get(path)
        assert response.status_code == 200, path
        assert needle in response.text


def test_business_page_lists_products_and_form(auth_client, business, product):
    text = auth_client.get("/business").text
    assert "Nasi Ayam" in text
    assert 'id="product-form"' in text and 'id="profile-form"' in text
    assert 'name="category"' in text
    assert "/static/forms.js" in text
    assert "data-product=" in text


def test_sales_new_page_defaults_to_today_with_active_products(auth_client, business, session):
    session.add(Product(business_id=business.id, name="Aktif", category="nasi", price=10000, unit_cost=4000))
    session.add(Product(business_id=business.id, name="Mati", category="mie", price=9000,
                        unit_cost=3000, active=False))
    session.commit()
    text = auth_client.get("/sales/new").text
    assert f'value="{date.today().isoformat()}"' in text
    assert "Aktif" in text and "Mati" not in text
    assert 'name="sold_out_' in text


def test_sales_history_shows_rows_and_chart(auth_client, business, product, session):
    for offset in range(3):
        session.add(Sale(product_id=product.id, date=date.today() - timedelta(days=offset),
                         qty_sold=5 + offset, sold_out=False))
    session.commit()
    text = auth_client.get("/sales").text
    assert "Nasi Ayam" in text
    assert 'class="bar-chart"' in text
    assert text.count('class="bar"') == 14
    assert "Terjual" in text


def test_fr06_history_date_filter(auth_client, business, product, session):
    old = date.today() - timedelta(days=40)
    session.add(Sale(product_id=product.id, date=old, qty_sold=99))
    session.add(Sale(product_id=product.id, date=date.today(), qty_sold=7))
    session.commit()
    default = auth_client.get("/sales").text
    assert ">99<" not in default and ">7<" in default
    filtered = auth_client.get("/sales", params={"start": old.isoformat(), "end": old.isoformat()})
    assert ">99<" in filtered.text and ">7<" not in filtered.text


def test_import_page_has_file_input_and_sample(auth_client, business):
    text = auth_client.get("/import").text
    assert 'enctype="multipart/form-data"' in text
    assert 'type="file"' in text
    assert "/static/contoh_penjualan.csv" in text


def test_sample_csv_static_file_is_valid(auth_client):
    response = auth_client.get("/static/contoh_penjualan.csv")
    assert response.status_code == 200
    first = response.text.splitlines()[0]
    assert first.startswith("date,product,qty_sold")


def test_fr12_card_template_has_required_parts():
    template = (ROOT / "app" / "templates" / "dashboard.html").read_text(encoding="utf-8")
    assert 'id="rec-card-template"' in template
    for field in ("qty", "p10", "p50", "p90", "confidence", "stage", "reasons"):
        assert f'data-field="{field}"' in template
    assert 'class="range-track"' in template
    js = (ROOT / "app" / "static" / "dashboard.js").read_text(encoding="utf-8")
    assert "confidenceLabel" in js
    assert "Tinggi" in js and "Sedang" in js and "Rendah" in js


def test_forms_js_has_indonesian_validation():
    js = (ROOT / "app" / "static" / "forms.js").read_text(encoding="utf-8")
    for phrase in ("Harga jual harus lebih besar dari 0.", "Nama produk wajib diisi.",
                   "Nilai sisa tidak boleh melebihi biaya per porsi.",
                   "Isi jumlah porsi dengan bilangan bulat 0 atau lebih."):
        assert phrase in js


def test_no_external_resources_in_templates():
    for path in (ROOT / "app" / "templates").glob("*.html"):
        text = path.read_text(encoding="utf-8")
        assert "http://" not in text and "https://" not in text, path
