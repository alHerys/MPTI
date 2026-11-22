"""Page routes: authenticated HTML screens (dashboard and forms)."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import current_user, get_session
from app.models import Business, Product, User

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


def _default_business(db: Session, user: User) -> Business | None:
    return db.scalars(
        select(Business).where(Business.user_id == user.id).order_by(Business.id)
    ).first()


def _business_or_redirect(db: Session, user: User, business_id: int | None):
    businesses = db.scalars(select(Business).where(Business.user_id == user.id).order_by(Business.id)).all()
    selected = None
    if business_id:
        selected = next((b for b in businesses if b.id == business_id), None)
    if selected is None and businesses:
        selected = businesses[0]
    return businesses, selected


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    business_id: int | None = None,
    date_str: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    businesses, selected = _business_or_redirect(db, user, business_id)
    target = date.today() + timedelta(days=1)
    if date_str:
        try:
            target = date.fromisoformat(date_str)
        except ValueError:
            pass
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "user": user,
            "nav": "dashboard",
            "businesses": businesses,
            "selected": selected,
            "target_date": target.isoformat(),
        },
    )


@router.get("/business", response_class=HTMLResponse)
def business_page(
    request: Request,
    business_id: int | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    businesses, selected = _business_or_redirect(db, user, business_id)
    products = []
    if selected:
        products = db.scalars(
            select(Product)
            .where(Product.business_id == selected.id, Product.active.is_(True))
            .order_by(Product.id)
        ).all()
    return templates.TemplateResponse(
        request,
        "business.html",
        {"user": user, "nav": "business", "businesses": businesses, "selected": selected, "products": products},
    )


@router.get("/sales/new", response_class=HTMLResponse)
def sales_new_page(
    request: Request,
    business_id: int | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    businesses, selected = _business_or_redirect(db, user, business_id)
    products = []
    if selected:
        products = db.scalars(
            select(Product)
            .where(Product.business_id == selected.id, Product.active.is_(True))
            .order_by(Product.id)
        ).all()
    return templates.TemplateResponse(
        request,
        "sales_new.html",
        {
            "user": user,
            "nav": "sales_new",
            "businesses": businesses,
            "selected": selected,
            "products": products,
            "today": date.today().isoformat(),
        },
    )


@router.get("/sales", response_class=HTMLResponse)
def sales_history_page(
    request: Request,
    business_id: int | None = None,
    start: str | None = None,
    end: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    from datetime import timedelta as _td

    businesses, selected = _business_or_redirect(db, user, business_id)
    end_date = date.today()
    start_date = end_date - _td(days=13)
    if start:
        try:
            start_date = date.fromisoformat(start)
        except ValueError:
            pass
    if end:
        try:
            end_date = date.fromisoformat(end)
        except ValueError:
            pass
    rows = []
    chart = []
    if selected:
        from app.models import Sale

        rows = db.execute(
            select(Sale, Product.name)
            .join(Product, Product.id == Sale.product_id)
            .where(Product.business_id == selected.id, Sale.date >= start_date, Sale.date <= end_date)
            .order_by(Sale.date.desc(), Product.name)
        ).all()
        chart_start = end_date - _td(days=13)
        totals = db.execute(
            select(Sale.date, __import__("sqlalchemy").func.sum(Sale.qty_sold))
            .join(Product, Product.id == Sale.product_id)
            .where(Product.business_id == selected.id, Sale.date >= chart_start, Sale.date <= end_date)
            .group_by(Sale.date)
            .order_by(Sale.date)
        ).all()
        by_date = {d: int(q or 0) for d, q in totals}
        for offset in range(14):
            d = chart_start + _td(days=offset)
            chart.append({"date": d.isoformat(), "qty": by_date.get(d, 0)})
    return templates.TemplateResponse(
        request,
        "sales_history.html",
        {
            "user": user,
            "nav": "sales",
            "businesses": businesses,
            "selected": selected,
            "rows": rows,
            "chart": chart,
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
    )


@router.get("/import", response_class=HTMLResponse)
def import_page(
    request: Request,
    business_id: int | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    businesses, selected = _business_or_redirect(db, user, business_id)
    return templates.TemplateResponse(
        request,
        "import.html",
        {"user": user, "nav": "import", "businesses": businesses, "selected": selected},
    )


@router.post("/sales/new")
async def sales_new_submit(
    request: Request,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    """T2.4: one date, one qty per active product, all-or-nothing."""
    form = await request.form()
    business_id_raw = form.get("business_id")
    day_raw = (form.get("date") or "").strip()
    try:
        business_id = int(business_id_raw)
        day = date.fromisoformat(day_raw)
    except (TypeError, ValueError):
        return templates.TemplateResponse(
            request,
            "sales_new.html",
            {
                "user": user,
                "nav": "sales_new",
                "businesses": db.scalars(select(Business).where(Business.user_id == user.id)).all(),
                "selected": None,
                "products": [],
                "today": date.today().isoformat(),
                "error": "Tanggal atau usaha tidak valid.",
            },
            status_code=422,
        )
    if day > date.today():
        return _sales_form_error(request, db, user, business_id, day, "Tanggal tidak boleh di masa depan.", 422)
    business = db.get(Business, business_id)
    if business is None or business.user_id != user.id:
        return _sales_form_error(request, db, user, business_id, day, "Usaha tidak ditemukan.", 404)

    products = db.scalars(
        select(Product)
        .where(Product.business_id == business.id, Product.active.is_(True))
        .order_by(Product.id)
    ).all()
    values: list[tuple[Product, int, bool]] = []
    for product in products:
        raw_qty = form.get(f"qty_{product.id}")
        if raw_qty is None or str(raw_qty).strip() == "":
            continue
        try:
            qty = int(str(raw_qty).strip())
        except ValueError:
            return _sales_form_error(
                request, db, user, business_id, day, f"Jumlah untuk {product.name} harus bilangan bulat.", 422
            )
        if qty < 0:
            return _sales_form_error(
                request, db, user, business_id, day, f"Jumlah untuk {product.name} tidak boleh negatif.", 422
            )
        sold_out = str(form.get(f"sold_out_{product.id}", "")).lower() in {"on", "true", "1", "yes"}
        values.append((product, qty, sold_out))

    from app.routers.sales import upsert_sale

    try:
        for product, qty, sold_out in values:
            upsert_sale(db, product.id, day, qty, sold_out)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return templates.TemplateResponse(
        request,
        "sales_new.html",
        {
            "user": user,
            "nav": "sales_new",
            "businesses": db.scalars(select(Business).where(Business.user_id == user.id)).all(),
            "selected": business,
            "products": products,
            "today": day.isoformat(),
            "success": f"Penjualan tanggal {day.isoformat()} tersimpan untuk {len(values)} produk.",
        },
    )


def _sales_form_error(request, db, user, business_id, day, message, status_code):
    businesses = db.scalars(select(Business).where(Business.user_id == user.id).order_by(Business.id)).all()
    selected = next((b for b in businesses if b.id == business_id), None)
    products = []
    if selected:
        products = db.scalars(
            select(Product)
            .where(Product.business_id == selected.id, Product.active.is_(True))
            .order_by(Product.id)
        ).all()
    return templates.TemplateResponse(
        request,
        "sales_new.html",
        {
            "user": user,
            "nav": "sales_new",
            "businesses": businesses,
            "selected": selected,
            "products": products,
            "today": day.isoformat() if day else date.today().isoformat(),
            "error": message,
        },
        status_code=status_code,
    )
