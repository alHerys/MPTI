"""T2.6: CSV import validation tests (WBS 2.6, FR-07, FR-08)."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.models import Product, Sale

TODAY = date.today()


def _products(session, business):
    names = ["Nasi Ayam", "Es Teh", "Roti Bakar"]
    for i, name in enumerate(names):
        session.add(
            Product(
                business_id=business.id,
                name=name,
                category=["nasi", "minuman", "roti"][i],
                price=10000,
                unit_cost=4000,
            )
        )
    session.commit()
    return names


def _upload(client, business_id, content: bytes, filename="data.csv"):
    return client.post(
        f"/api/businesses/{business_id}/sales/import",
        files={"file": (filename, content, "text/csv")},
    )


def _csv(rows: str, header: str = "date,product,qty_sold") -> bytes:
    return (header + "\n" + rows).encode("utf-8")


def test_fr07_valid_file_accepted(auth_client, session, business):
    _products(session, business)
    content = _csv(
        f"{TODAY.isoformat()},Nasi Ayam,10\n"
        f"{TODAY.isoformat()},Es Teh,20,ya\n"
        f"{(TODAY - timedelta(days=1)).isoformat()},Roti Bakar,4\n"
    ).replace(b",20,ya", b",20")
    # Header includes sold_out for the second test instead; keep simple here:
    content = (
        "date,product,qty_sold,sold_out\n"
        f"{TODAY.isoformat()},Nasi Ayam,10,false\n"
        f"{TODAY.isoformat()},Es Teh,20,true\n"
        f"{(TODAY - timedelta(days=1)).isoformat()},Roti Bakar,4,\n"
    ).encode()
    response = _upload(auth_client, business.id, content)
    assert response.status_code == 200, response.text
    assert response.json()["accepted"] == 3
    with auth_client.app.state.db.session() as s:
        rows = s.query(Sale).all()
    assert len(rows) == 3
    assert sum(1 for r in rows if r.sold_out) == 1


def test_import_upserts_existing_rows(auth_client, session, business, product):
    first = _csv(f"{TODAY.isoformat()},Nasi Ayam,5\n")
    assert _upload(auth_client, business.id, first).status_code == 200
    second = _csv(f"{TODAY.isoformat()},Nasi Ayam,9\n")
    assert _upload(auth_client, business.id, second).status_code == 200
    with auth_client.app.state.db.session() as s:
        rows = s.query(Sale).all()
    assert len(rows) == 1 and rows[0].qty_sold == 9


@pytest.mark.parametrize(
    "content,needle",
    [
        (_csv(f"{TODAY.isoformat()},Nasi Ayam,5\n", header="tanggal,produk,jumlah"), "Header tidak valid"),
        (_csv("2026-13-01,Nasi Ayam,5\n"), "Tanggal tidak valid"),
        (_csv(f"{(TODAY + timedelta(days=3)).isoformat()},Nasi Ayam,5\n"), "masa depan"),
        (_csv(f"{TODAY.isoformat()},Nasi Ayam,-2\n"), "negatif"),
        (_csv(f"{TODAY.isoformat()},Nasi Ayam,dua\n"), "bukan bilangan bulat"),
        (_csv(f"{TODAY.isoformat()},Sate Kambing,2\n"), "Produk tidak dikenal"),
        (
            _csv(f"{TODAY.isoformat()},Nasi Ayam,2\n{TODAY.isoformat()},Nasi Ayam,3\n"),
            "Duplikat",
        ),
    ],
)
def test_fr08_invalid_files_rejected_with_nothing_stored(auth_client, session, business, content, needle):
    _products(session, business)
    response = _upload(auth_client, business.id, content)
    assert response.status_code == 422, response.text
    body = response.json()
    assert body["errors"] and "line" in body["errors"][0] and "message" in body["errors"][0]
    assert needle.lower() in body["errors"][0]["message"].lower()
    with auth_client.app.state.db.session() as s:
        assert s.query(Sale).count() == 0


def test_reject_too_many_rows(auth_client, session, business, product):
    lines = "\n".join(
        f"{(TODAY - timedelta(days=i % 300)).isoformat()},Nasi Ayam,1" for i in range(5001)
    )
    content = _csv(lines + "\n")
    response = _upload(auth_client, business.id, content)
    assert response.status_code == 422
    assert "5.000" in response.json()["detail"]
    with auth_client.app.state.db.session() as s:
        assert s.query(Sale).count() == 0


def test_reject_oversized_file(auth_client, session, business, product):
    big = (b"date,product,qty_sold\n" + b"2026-01-01,Nasi Ayam,1\n" * 60000)
    assert len(big) > 1024 * 1024
    response = _upload(auth_client, business.id, big)
    assert response.status_code == 422
    assert "1 MB" in response.json()["detail"]


def test_reject_non_utf8(auth_client, session, business, product):
    content = b"date,product,qty_sold\n2026-01-01,Nasi Ayam,1\n\xff\xfe garbage"
    response = _upload(auth_client, business.id, content)
    assert response.status_code == 422
    assert "UTF-8" in response.json()["detail"]


def test_accepts_crlf_and_bom(auth_client, session, business, product):
    content = (
        b"\xef\xbb\xbfdate,product,qty_sold\r\n"
        + f"{TODAY.isoformat()},Nasi Ayam,6\r\n".encode()
    )
    response = _upload(auth_client, business.id, content)
    assert response.status_code == 200, response.text
    assert response.json()["accepted"] == 1


def test_rejects_unknown_business(auth_client, session, other_user):
    from app.models import Business

    foreign = Business(
        user_id=other_user.id, name="F", business_type="cafe", location_type="pasar", capacity_factor=1.0
    )
    session.add(foreign)
    session.commit()
    response = _upload(auth_client, foreign.id, _csv(f"{TODAY.isoformat()},X,1\n"))
    assert response.status_code == 404
