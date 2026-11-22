"""Reference dataset loading, feature vectors, and nearest-neighbour search (T3.1)."""
from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from app.ml.config import (
    BUSINESS_TYPES,
    CATEGORIES,
    DEFAULT_CAPACITY_FACTOR,
    LOCATION_TYPES,
    N_NEIGHBORS,
)

FEATURE_DIM = len(BUSINESS_TYPES) + len(LOCATION_TYPES) + len(CATEGORIES) + 1


@dataclass(frozen=True)
class ReferenceSeries:
    series_id: str
    business_type: str
    location_type: str
    category: str
    price: float
    capacity_factor: float
    base_mean: float
    dispersion: float
    mean_daily: float
    weekday_factor: tuple[float, ...]
    feature: np.ndarray = field(repr=False, compare=False)


@dataclass
class ReferenceData:
    series: list[ReferenceSeries]
    price_min: float
    price_max: float

    @property
    def empty(self) -> bool:
        return not self.series

    def without_business(self, business_prefix: str) -> "ReferenceData":
        kept = [s for s in self.series if not s.series_id.startswith(business_prefix)]
        return ReferenceData(kept, self.price_min, self.price_max)

    def only_business(self, business_prefix: str) -> "ReferenceData":
        kept = [s for s in self.series if s.series_id.startswith(business_prefix)]
        return ReferenceData(kept, self.price_min, self.price_max)


def _weekday_factors(dates: list, qtys: list[float]) -> tuple[float, ...]:
    overall = float(np.mean(qtys)) if qtys else 0.0
    factors = []
    for dow in range(7):
        values = [q for d, q in zip(dates, qtys) if d.weekday() == dow]
        if values and overall > 0:
            factors.append(float(np.mean(values) / overall))
        else:
            factors.append(1.0)
    mean = float(np.mean(factors))
    if mean > 0:
        factors = [f / mean for f in factors]
    return tuple(factors)


def build_reference(meta_rows: list[dict], sales_rows: list[dict]) -> ReferenceData:
    """Build a ReferenceData from CSV-shaped dicts (used by tests and load_reference)."""
    from datetime import date

    by_series: dict[str, list[tuple[date, float]]] = {}
    for row in sales_rows:
        day = row["date"] if isinstance(row["date"], date) else date.fromisoformat(str(row["date"]))
        by_series.setdefault(str(row["series_id"]), []).append((day, float(row["qty"])))

    prices = [float(r["price"]) for r in meta_rows if float(r["price"]) > 0]
    price_min = min(prices) if prices else 0.0
    price_max = max(prices) if prices else 0.0

    series: list[ReferenceSeries] = []
    for row in meta_rows:
        sid = str(row["series_id"])
        observations = sorted(by_series.get(sid, []))
        qtys = [q for _, q in observations]
        mean_daily = float(np.mean(qtys)) if qtys else float(row.get("base_mean", 0.0))
        dispersion = float(row.get("dispersion", 0.15))
        feature = _feature_vector(
            row["business_type"],
            row["location_type"],
            row["category"],
            float(row["price"]),
            price_min,
            price_max,
        )
        series.append(
            ReferenceSeries(
                series_id=sid,
                business_type=row["business_type"],
                location_type=row["location_type"],
                category=row["category"],
                price=float(row["price"]),
                capacity_factor=float(row.get("capacity_factor", DEFAULT_CAPACITY_FACTOR)),
                base_mean=float(row.get("base_mean", mean_daily)),
                dispersion=dispersion,
                mean_daily=mean_daily,
                weekday_factor=_weekday_factors([d for d, _ in observations], qtys),
                feature=feature,
            )
        )
    return ReferenceData(series, price_min, price_max)


def _feature_vector(
    business_type: str,
    location_type: str,
    category: str,
    price: float,
    price_min: float,
    price_max: float,
) -> np.ndarray:
    vector = np.zeros(FEATURE_DIM, dtype=float)
    vector[BUSINESS_TYPES.index(business_type)] = 1.0
    offset = len(BUSINESS_TYPES)
    vector[offset + LOCATION_TYPES.index(location_type)] = 1.0
    offset += len(LOCATION_TYPES)
    vector[offset + CATEGORIES.index(category)] = 1.0
    if price_max > price_min:
        scaled = (np.log(max(price, 1e-6)) - np.log(price_min)) / (np.log(price_max) - np.log(price_min))
    else:
        scaled = 0.5
    vector[-1] = float(np.clip(scaled, 0.0, 1.0))
    return vector


def query_feature(
    reference: ReferenceData,
    business_type: str,
    location_type: str,
    category: str,
    price: float,
) -> np.ndarray:
    return _feature_vector(
        business_type, location_type, category, price, reference.price_min, reference.price_max
    )


def nearest_neighbors(
    reference: ReferenceData,
    feature: np.ndarray,
    exclude_ids: set[str] | frozenset[str] = frozenset(),
    k: int = N_NEIGHBORS,
) -> list[tuple[ReferenceSeries, float]]:
    candidates = [s for s in reference.series if s.series_id not in exclude_ids]
    if not candidates:
        return []
    distances = [
        (series, float(np.linalg.norm(series.feature - feature))) for series in candidates
    ]
    distances.sort(key=lambda pair: (pair[1], pair[0].series_id))
    return distances[:k]


def load_reference(data_dir: str | Path = "data") -> ReferenceData:
    """Load reference_sales.csv + reference_meta.csv. Missing files yield an empty reference."""
    directory = Path(data_dir)
    sales_path = directory / "reference_sales.csv"
    meta_path = directory / "reference_meta.csv"
    if not sales_path.exists() or not meta_path.exists():
        return ReferenceData([], 0.0, 0.0)
    with sales_path.open(newline="", encoding="utf-8") as fh:
        sales_rows = list(csv.DictReader(fh))
    with meta_path.open(newline="", encoding="utf-8") as fh:
        meta_rows = list(csv.DictReader(fh))
    return build_reference(meta_rows, sales_rows)
