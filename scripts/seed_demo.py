"""Demo seeding: one demo user plus three businesses at H0, H3, H7."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.config import demo_password, demo_user
from app.models import Business, Product, Sale, User

DEMO_BUSINESSES = [
    {
        "name": "Warung Bu Sari",
        "business_type": "warung",
        "location_type": "permukiman",
        "capacity_factor": 1.0,
        "days": 0,
        "products": [
            ("Nasi Ayam", "nasi", 12000, 6000, 0),
            ("Mie Goreng", "mie", 11000, 5000, 0),
            ("Es Teh", "minuman", 5000, 1500, 0),
            ("Pisang Goreng", "snack", 7000, 2500, 0),
            ("Roti Bakar", "roti", 9000, 3500, 0),
        ],
    },
    {
        "name": "Kafe Kampus",
        "business_type": "cafe",
        "location_type": "kampus",
        "capacity_factor": 1.2,
        "days": 3,
        "products": [
            ("Nasi Goreng Kampus", "nasi", 15000, 7000, 0),
            ("Mie Ayam", "mie", 13000, 6000, 0),
            ("Kopi Susu", "minuman", 12000, 4000, 0),
            ("Pisang Goreng", "snack", 8000, 3000, 0),
            ("Roti Bakar Cokelat", "roti", 10000, 4000, 0),
        ],
    },
    {
        "name": "Gerobak Pak Joko",
        "business_type": "gerobak",
        "location_type": "pasar",
        "capacity_factor": 1.5,
        "days": 7,
        "products": [
            ("Nasi Bungkus", "nasi", 10000, 5000, 0),
            ("Mie Instan", "mie", 9000, 4000, 0),
            ("Es Jeruk", "minuman", 5000, 1500, 0),
            ("Tahu Goreng", "snack", 4000, 1500, 0),
            ("Roti Manis", "roti", 6000, 2500, 0),
        ],
    },
]

# Base daily demand used to fabricate the demo history. Deterministic RNG.
BASE_DEMAND = [24, 20, 30, 14, 12]


def seed_demo(db: Session, username: str | None = None, password: str | None = None) -> bool:
    """Seed only when the database has no users. Returns True when seeding ran."""
    if db.scalar(select(User).limit(1)) is not None:
        return False
    username = username or demo_user()
    password = password or demo_password()
    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.flush()
    rng = np.random.default_rng(42)
    today = date.today()
    for spec in DEMO_BUSINESSES:
        business = Business(
            user_id=user.id,
            name=spec["name"],
            business_type=spec["business_type"],
            location_type=spec["location_type"],
            capacity_factor=spec["capacity_factor"],
        )
        db.add(business)
        db.flush()
        products = []
        for name, category, price, cost, salvage in spec["products"]:
            product = Product(
                business_id=business.id,
                name=name,
                category=category,
                price=price,
                unit_cost=cost,
                salvage_value=salvage,
                active=True,
            )
            db.add(product)
            products.append(product)
        db.flush()
        if spec["days"]:
            start = today - timedelta(days=spec["days"])
            for day_index in range(spec["days"]):
                current = start + timedelta(days=day_index)
                for product, base in zip(products, BASE_DEMAND):
                    weekday_factor = 1.15 if current.weekday() >= 4 else 1.0
                    qty = int(max(0, round(base * weekday_factor * float(rng.uniform(0.85, 1.15)))))
                    sold_out = qty >= base + 4
                    db.add(
                        Sale(
                            product_id=product.id,
                            date=current,
                            qty_sold=qty,
                            sold_out=sold_out,
                        )
                    )
    db.commit()
    return True
