"""Generate the synthetic reference dataset (PLAN.md 5.1).

Usage:
    python scripts/gen_reference.py --seed 42 [--out data]

Writes reference_sales.csv (series_id,date,qty) and
reference_meta.csv (series_id,business_type,location_type,category,price,
capacity_factor,base_mean,dispersion). Output is byte-for-byte reproducible
for a given seed.
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ml.config import BUSINESS_TYPES, CATEGORIES, LOCATION_TYPES, WEEKDAY_FACTORS  # noqa: E402

START_DATE = date(2026, 6, 1)
DAYS = 90
BUSINESS_COUNT = 24
# 24 businesses, 6..8 products each, average 7 -> 168 series x 90 days = 15,120 rows.
PRODUCT_COUNTS = [6, 7, 8] * 8
PRICE_RANGES = {
    "nasi": (10000, 18000),
    "mie": (9000, 14000),
    "snack": (4000, 9000),
    "minuman": (4000, 12000),
    "roti": (6000, 15000),
}
BASE_MEANS = {"nasi": 20.0, "mie": 18.0, "snack": 15.0, "minuman": 24.0, "roti": 12.0}
LOCATION_MULTIPLIER = {"kampus": 1.15, "kantor": 0.95, "permukiman": 0.80, "pasar": 1.30}
TYPE_MULTIPLIER = {"warung": 1.00, "cafe": 0.85, "gerobak": 1.25, "bakery": 0.70, "kantin": 1.10}
CAPACITY_FACTORS = (0.8, 1.0, 1.2, 1.5, 2.0)


def negative_binomial_qty(rng: np.random.Generator, mean: float, dispersion: float) -> int:
    """Draw from NegBin with the given mean and dispersion (var = mean + phi*mean^2)."""
    mean = max(mean, 0.1)
    r = 1.0 / dispersion
    p = r / (r + mean)
    return int(rng.negative_binomial(r, p))


def build_businesses(rng: np.random.Generator) -> list[dict]:
    businesses = []
    total_series = 0
    for idx in range(BUSINESS_COUNT):
        business_type = BUSINESS_TYPES[idx % len(BUSINESS_TYPES)]
        location_type = LOCATION_TYPES[(idx // len(BUSINESS_TYPES)) % len(LOCATION_TYPES)]
        product_count = PRODUCT_COUNTS[idx]
        total_series += product_count
        categories = [CATEGORIES[(idx + j) % len(CATEGORIES)] for j in range(product_count)]
        # Guarantee at least one nasi and one minuman series per business so the
        # category vocabulary is exercised across every vendor.
        categories[0] = "nasi" if idx % 2 == 0 else "mie"
        categories[-1] = "minuman"
        capacity_factor = float(CAPACITY_FACTORS[idx % len(CAPACITY_FACTORS)])
        products = []
        for j, category in enumerate(categories):
            low, high = PRICE_RANGES[category]
            price = float(rng.integers(low, high + 1, endpoint=True))
            base_mean = (
                BASE_MEANS[category]
                * capacity_factor
                * TYPE_MULTIPLIER[business_type]
                * LOCATION_MULTIPLIER[location_type]
                * float(rng.uniform(0.85, 1.15))
            )
            dispersion = float(rng.uniform(0.05, 0.30))
            products.append(
                {
                    "series_id": f"B{idx + 1:02d}-P{j + 1:02d}",
                    "business_type": business_type,
                    "location_type": location_type,
                    "category": category,
                    "price": price,
                    "capacity_factor": capacity_factor,
                    "base_mean": base_mean,
                    "dispersion": dispersion,
                }
            )
        businesses.append({"id": f"B{idx + 1:02d}", "products": products})
    assert total_series == 168, total_series
    return businesses


def generate(seed: int) -> tuple[list[dict], list[dict]]:
    rng = np.random.default_rng(seed)
    meta_rows: list[dict] = []
    sales_rows: list[dict] = []
    for business in build_businesses(rng):
        for product in business["products"]:
            meta_rows.append(product)
            weekday = WEEKDAY_FACTORS[product["category"]]
            for day_offset in range(DAYS):
                current = START_DATE + timedelta(days=day_offset)
                noise = float(rng.lognormal(mean=-(0.08**2) / 2, sigma=0.08))
                mean = product["base_mean"] * weekday[current.weekday()] * noise
                qty = negative_binomial_qty(rng, mean, product["dispersion"])
                sales_rows.append(
                    {"series_id": product["series_id"], "date": current.isoformat(), "qty": qty}
                )
    return meta_rows, sales_rows


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic reference data.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=Path("data"))
    args = parser.parse_args(argv)
    meta_rows, sales_rows = generate(args.seed)
    write_csv(
        args.out / "reference_sales.csv", ["series_id", "date", "qty"], sales_rows
    )
    write_csv(
        args.out / "reference_meta.csv",
        [
            "series_id",
            "business_type",
            "location_type",
            "category",
            "price",
            "capacity_factor",
            "base_mean",
            "dispersion",
        ],
        meta_rows,
    )
    print(f"series={len(meta_rows)} rows={len(sales_rows)} seed={args.seed} out={args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
