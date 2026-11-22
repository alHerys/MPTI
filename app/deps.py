"""Shared FastAPI dependencies: database session, current user, ownership."""
from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.models import Business, Product, User


class LoginRequired(Exception):
    """Raised by page routes so the handler can redirect to /login."""


def get_session(request: Request) -> Session:
    db: Session = request.app.state.db.session()
    try:
        yield db
    finally:
        db.close()


def current_user_id(request: Request) -> int:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Silakan masuk terlebih dahulu.")
    return int(user_id)


def current_user(request: Request, db: Session = Depends(get_session)) -> User:
    user_id = current_user_id(request)
    user = db.get(User, user_id)
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Sesi tidak valid. Silakan masuk lagi.")
    return user


def page_user(request: Request, db: Session = Depends(get_session)) -> User:
    user_id = request.session.get("user_id")
    user = db.get(User, int(user_id)) if user_id else None
    if user is None:
        raise LoginRequired()
    return user


def owned_business(business_id: int, user: User, db: Session) -> Business:
    business = db.get(Business, business_id)
    if business is None or business.user_id != user.id:
        raise HTTPException(status_code=404, detail="Usaha tidak ditemukan.")
    return business


def owned_product(product_id: int, user: User, db: Session) -> Product:
    product = db.get(Product, product_id)
    if product is None or product.business.user_id != user.id:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan.")
    return product
