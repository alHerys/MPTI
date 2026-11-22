"""Business profile and menu API (T2.3 / WBS 2.3)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import current_user, get_session, owned_business, owned_product
from app.models import Business, Product, User
from app.schemas import BusinessIn, BusinessOut, BusinessUpdate, ProductIn, ProductOut, ProductUpdate

router = APIRouter(prefix="/api", tags=["businesses"])


@router.get("/businesses", response_model=list[BusinessOut])
def list_businesses(user: User = Depends(current_user), db: Session = Depends(get_session)):
    return db.scalars(select(Business).where(Business.user_id == user.id).order_by(Business.id)).all()


@router.post("/businesses", response_model=BusinessOut, status_code=201)
def create_business(
    payload: BusinessIn, user: User = Depends(current_user), db: Session = Depends(get_session)
):
    business = Business(user_id=user.id, **payload.model_dump())
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


@router.get("/businesses/{business_id}", response_model=BusinessOut)
def read_business(
    business_id: int, user: User = Depends(current_user), db: Session = Depends(get_session)
):
    return owned_business(business_id, user, db)


@router.put("/businesses/{business_id}", response_model=BusinessOut)
def update_business(
    business_id: int,
    payload: BusinessUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    business = owned_business(business_id, user, db)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(business, key, value)
    db.commit()
    db.refresh(business)
    return business


@router.get("/businesses/{business_id}/products", response_model=list[ProductOut])
def list_products(
    business_id: int,
    include_inactive: bool = False,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    owned_business(business_id, user, db)
    query = select(Product).where(Product.business_id == business_id).order_by(Product.id)
    if not include_inactive:
        query = query.where(Product.active.is_(True))
    return db.scalars(query).all()


@router.post("/businesses/{business_id}/products", response_model=ProductOut, status_code=201)
def create_product(
    business_id: int,
    payload: ProductIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    owned_business(business_id, user, db)
    product = Product(business_id=business_id, **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_session),
):
    product = owned_product(product_id, user, db)
    data = payload.model_dump(exclude_unset=True)
    cost = data.get("unit_cost", product.unit_cost)
    salvage = data.get("salvage_value", product.salvage_value)
    if salvage > cost:
        raise HTTPException(status_code=422, detail="Nilai sisa tidak boleh melebihi biaya per porsi.")
    for key, value in data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", response_model=ProductOut)
def deactivate_product(
    product_id: int, user: User = Depends(current_user), db: Session = Depends(get_session)
):
    product = owned_product(product_id, user, db)
    product.active = False
    db.commit()
    db.refresh(product)
    return product
