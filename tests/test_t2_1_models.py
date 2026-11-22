"""T2.1: database schema tests (WBS 2.1)."""
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.auth import hash_password, verify_password
from app.models import Business, Product, Sale, User, init_db, make_engine, make_session_factory


@pytest.fixture()
def session():
    engine = make_engine("sqlite://")
    init_db(engine)
    Session = make_session_factory(engine)
    with Session() as s:
        yield s


def _seed(session):
    user = User(username="u1", password_hash=hash_password("pw"))
    session.add(user)
    session.flush()
    business = Business(user_id=user.id, name="Warung A", business_type="warung", location_type="kampus")
    session.add(business)
    session.flush()
    product = Product(
        business_id=business.id, name="Nasi Ayam", category="nasi", price=12000, unit_cost=6000
    )
    session.add(product)
    session.flush()
    sale = Sale(product_id=product.id, date=date(2026, 1, 1), qty_sold=12, sold_out=True)
    session.add(sale)
    session.commit()
    return user, business, product, sale


def test_tables_created_and_rows_roundtrip(session):
    user, business, product, sale = _seed(session)
    session.expire_all()
    assert session.get(User, user.id).username == "u1"
    assert session.get(Business, business.id).name == "Warung A"
    assert session.get(Product, product.id).price == 12000
    stored = session.get(Sale, sale.id)
    assert stored.qty_sold == 12 and stored.sold_out is True


def test_unique_product_date_constraint(session):
    _, _, product, _ = _seed(session)
    session.add(Sale(product_id=product.id, date=date(2026, 1, 1), qty_sold=3))
    with pytest.raises(IntegrityError):
        session.commit()


def test_negative_qty_rejected(session):
    _, _, product, _ = _seed(session)
    session.add(Sale(product_id=product.id, date=date(2026, 1, 2), qty_sold=-1))
    with pytest.raises(IntegrityError):
        session.commit()


def test_password_hash_roundtrip():
    stored = hash_password("demo123")
    assert verify_password("demo123", stored)
    assert not verify_password("wrong", stored)
    assert not verify_password("demo123", "garbage")
