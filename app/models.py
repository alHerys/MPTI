"""SQLAlchemy 2.x ORM models and database helpers."""
from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    businesses: Mapped[list["Business"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    business_type: Mapped[str] = mapped_column(String(20), nullable=False)
    location_type: Mapped[str] = mapped_column(String(20), nullable=False)
    capacity_factor: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="businesses")
    products: Mapped[list["Product"]] = relationship(
        back_populates="business", cascade="all, delete-orphan", order_by="Product.id"
    )

    __table_args__ = (CheckConstraint("capacity_factor > 0", name="ck_business_capacity_positive"),)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[int] = mapped_column(Integer, nullable=False)
    salvage_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    perishable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    business: Mapped[Business] = relationship(back_populates="products")
    sales: Mapped[list["Sale"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", order_by="Sale.date"
    )


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    qty_sold: Mapped[int] = mapped_column(Integer, nullable=False)
    sold_out: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    product: Mapped[Product] = relationship(back_populates="sales")

    __table_args__ = (
        UniqueConstraint("product_id", "date", name="uq_sale_product_date"),
        CheckConstraint("qty_sold >= 0", name="ck_sale_qty_non_negative"),
    )


def make_engine(url: str | None = None):
    from app.config import database_url

    url = url or database_url()
    kwargs: dict = {"future": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        if ":memory:" in url or url == "sqlite://":
            kwargs["poolclass"] = StaticPool
    return create_engine(url, **kwargs)


def make_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


_engine = None
_session_factory = None


def init_db(engine=None):
    """Create all tables. Safe to call repeatedly."""
    global _engine, _session_factory
    if engine is not None:
        Base.metadata.create_all(engine)
        return engine
    if _engine is None:
        _engine = make_engine()
        _session_factory = make_session_factory(_engine)
    Base.metadata.create_all(_engine)
    return _engine


def get_session_factory():
    if _session_factory is None:
        init_db()
    return _session_factory


def get_db():
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
