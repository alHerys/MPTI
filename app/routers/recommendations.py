"""Production recommendation API (T3.6 / WBS 3.6)."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import current_user, get_session, owned_business, owned_product
from app.models import Business, Product, Sale, User
from app.ml.engine import BusinessInput, ProductInput, recommend
from app.ml.optimize import PricingError
from app.ml.reference import ReferenceData, load_reference
from app.ml.update import SaleRow

router = APIRouter(prefix="/api", tags=["recommendations"])

_reference_cache: dict[str, tuple[float, ReferenceData]] = {}


def get_reference() -> ReferenceData:
    """Load the synthetic reference dataset once per process (mtime-aware)."""
    path = Path("data") / "reference_sales.csv"
    key = str(path.resolve())
    mtime = path.stat().st_mtime if path.exists() else 0.0
    cached = _reference_cache.get(key)
    if cached and cached[0] == mtime:
        return cached[1]
    reference = load_reference("data")
    _reference_cache[key] = (mtime, reference)
    return reference


def _sales_for(db: Session, product_id: int) -> list[SaleRow]:
    rows = db.scalars(
        select(Sale).where(Sale.product_id == product_id).order_by(Sale.date)
    ).all()
    return [SaleRow(date=r.date, qty_sold=r.qty_sold, sold_out=r.sold_out) for r in rows]


def _target(value: str | None) -> date:
    default = date.today() + timedelta(days=1)
    if not value:
        return default
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=422, detail="Format tanggal harus YYYY-MM-DD.")


def _recommend_product(
    db: Session, product: Product, business: Business, target: date, reference: ReferenceData
) -> dict:
    try:
        result = recommend(
            ProductInput(
                id=product.id,
                name=product.name,
                category=product.category,
                price=product.price,
                unit_cost=product.unit_cost,
                salvage_value=product.salvage_value,
            ),
            BusinessInput(
                business_type=business.business_type,
                location_type=business.location_type,
                capacity_factor=business.capacity_factor,
            ),
            _sales_for(db, product.id),
            target,
            reference,
        )
    except PricingError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Harga jual produk '{product.name}' harus lebih besar dari biaya per porsi.",
        ) from exc
    return result.as_dict()


@router.get("/products/{product_id}/recommendation")
def product_recommendation(
    product_id: int,
    date_str: str | None = Query(default=None, alias="date"),
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    product = owned_product(product_id, user, db)
    if not product.active:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan atau sudah tidak aktif.")
    target = _target(date_str)
    return _recommend_product(db, product, product.business, target, get_reference())


@router.get("/businesses/{business_id}/recommendations")
def business_recommendations(
    business_id: int,
    date_str: str | None = Query(default=None, alias="date"),
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    business = owned_business(business_id, user, db)
    target = _target(date_str)
    reference = get_reference()
    products = db.scalars(
        select(Product)
        .where(Product.business_id == business.id, Product.active.is_(True))
        .order_by(Product.id)
    ).all()
    items = [_recommend_product(db, p, business, target, reference) for p in products]
    return {"business_id": business.id, "date": target.isoformat(), "items": items}
