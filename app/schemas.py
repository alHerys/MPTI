"""Pydantic request/response schemas."""
from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.ml.config import BUSINESS_TYPES, CATEGORIES, LOCATION_TYPES

BusinessType = Literal["warung", "cafe", "gerobak", "bakery", "kantin"]
LocationType = Literal["kampus", "kantor", "permukiman", "pasar"]
Category = Literal["nasi", "mie", "snack", "minuman", "roti"]


class BusinessIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    business_type: BusinessType
    location_type: LocationType
    capacity_factor: float = Field(default=1.0, gt=0, le=100)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Nama usaha wajib diisi.")
        return value


class BusinessUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    business_type: BusinessType | None = None
    location_type: LocationType | None = None
    capacity_factor: float | None = Field(default=None, gt=0, le=100)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Nama usaha wajib diisi.")
        return value


class BusinessOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    business_type: str
    location_type: str
    capacity_factor: float
    created_at: datetime


class ProductIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: Category
    price: int = Field(gt=0)
    unit_cost: int = Field(ge=0)
    salvage_value: int = Field(default=0, ge=0)
    perishable: bool = True

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Nama produk wajib diisi.")
        return value

    @field_validator("salvage_value")
    @classmethod
    def salvage_not_above_cost(cls, value: int, info):
        cost = info.data.get("unit_cost")
        if cost is not None and value > cost:
            raise ValueError("Nilai sisa tidak boleh melebihi biaya per porsi.")
        return value


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: Category | None = None
    price: int | None = Field(default=None, gt=0)
    unit_cost: int | None = Field(default=None, ge=0)
    salvage_value: int | None = Field(default=None, ge=0)
    perishable: bool | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    business_id: int
    name: str
    category: str
    price: int
    unit_cost: int
    salvage_value: int
    perishable: bool
    active: bool


class SaleIn(BaseModel):
    product_id: int
    date: date
    qty_sold: int = Field(ge=0)
    sold_out: bool = False


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    date: date
    qty_sold: int
    sold_out: bool


class DailySalesIn(BaseModel):
    date: date
    rows: list[dict]
