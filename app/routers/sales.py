"""Sales storage/read API (T2.5 / WBS 2.5) and daily form endpoint (T2.4)."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import current_user, get_session, owned_business, owned_product
from app.models import Product, Sale, User
from app.schemas import SaleIn, SaleOut

router = APIRouter(prefix="/api", tags=["sales"])


def _ensure_not_future(day: date) -> None:
    if day > date.today():
        raise HTTPException(status_code=422, detail="Tanggal penjualan tidak boleh di masa depan.")


def upsert_sale(db: Session, product_id: int, day: date, qty_sold: int, sold_out: bool) -> Sale:
    sale = db.scalar(select(Sale).where(Sale.product_id == product_id, Sale.date == day))
    if sale is None:
        sale = Sale(product_id=product_id, date=day, qty_sold=qty_sold, sold_out=sold_out)
        db.add(sale)
    else:
        sale.qty_sold = qty_sold
        sale.sold_out = sold_out
    return sale


@router.post("/sales", response_model=SaleOut)
def create_or_update_sale(
    payload: SaleIn, user: User = Depends(current_user), db: Session = Depends(get_session)
):
    product = owned_product(payload.product_id, user, db)
    if not product.active:
        raise HTTPException(status_code=422, detail="Produk sudah tidak aktif.")
    _ensure_not_future(payload.date)
    sale = upsert_sale(db, product.id, payload.date, payload.qty_sold, payload.sold_out)
    db.commit()
    db.refresh(sale)
    return sale


@router.get("/products/{product_id}/sales", response_model=list[SaleOut])
def list_product_sales(
    product_id: int,
    from_: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    product = owned_product(product_id, user, db)
    query = select(Sale).where(Sale.product_id == product.id).order_by(Sale.date)
    if from_:
        query = query.where(Sale.date >= from_)
    if to:
        query = query.where(Sale.date <= to)
    return db.scalars(query).all()


@router.get("/businesses/{business_id}/sales")
def list_business_sales(
    business_id: int,
    start: str | None = None,
    end: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    owned_business(business_id, user, db)
    query = (
        select(Sale, Product.name)
        .join(Product, Product.id == Sale.product_id)
        .where(Product.business_id == business_id)
        .order_by(Sale.date.desc(), Product.name)
    )
    if start:
        query = query.where(Sale.date >= date.fromisoformat(start))
    if end:
        query = query.where(Sale.date <= date.fromisoformat(end))
    return [
        {
            "id": sale.id,
            "product_id": sale.product_id,
            "product": name,
            "date": sale.date.isoformat(),
            "qty_sold": sale.qty_sold,
            "sold_out": sale.sold_out,
        }
        for sale, name in db.execute(query).all()
    ]


def recent_sales_count(db: Session, business_id: int, days: int = 7) -> int:
    since = date.today() - timedelta(days=days)
    return len(
        db.scalars(
            select(Sale.id)
            .join(Product, Product.id == Sale.product_id)
            .where(Product.business_id == business_id, Sale.date >= since)
        ).all()
    )


@router.post("/businesses/{business_id}/sales/import")
async def import_sales_csv(
    business_id: int,
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    from fastapi.responses import JSONResponse

    from app.csv_import import ImportError_, parse_sales_csv

    business = owned_business(business_id, user, db)
    form = await request.form()
    upload = form.get("file")
    if upload is None or not hasattr(upload, "read"):
        return JSONResponse(
            status_code=422, content={"detail": "Berkas CSV wajib diunggah.", "errors": []}
        )
    raw = await upload.read()
    products = db.scalars(
        select(Product).where(Product.business_id == business.id, Product.active.is_(True))
    ).all()
    products_by_name = {p.name: p.id for p in products}
    try:
        rows = parse_sales_csv(raw, products_by_name)
    except ImportError_ as exc:
        return JSONResponse(status_code=422, content={"detail": exc.message, "errors": exc.errors})

    try:
        for row in rows:
            upsert_sale(db, row["product_id"], row["date"], row["qty_sold"], row["sold_out"])
        db.commit()
    except Exception:
        db.rollback()
        return JSONResponse(
            status_code=422,
            content={"detail": "Impor gagal disimpan.", "errors": [{"line": 0, "message": str(exc)}]},
        )
    return {"accepted": len(rows), "business_id": business.id}
