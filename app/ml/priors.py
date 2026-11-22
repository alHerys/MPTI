"""Cold-start prior from similar businesses (T3.1, PLAN.md 5.2)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.ml.config import (
    DEFAULT_CAPACITY_FACTOR, FALLBACK_MU0, FALLBACK_PHI_DAY, N_NEIGHBORS,
    NEIGHBOR_DISTANCE_EPS, PHI_DAY_MAX, PHI_DAY_MIN,
)
from app.ml.reference import ReferenceData, nearest_neighbors, query_feature


@dataclass(frozen=True)
class Prior:
    mu0: float
    phi_day: float
    weekday_profile: tuple[float, ...]
    neighbor_ids: tuple[str, ...]
    neighbor_distance_mean: float
    low_reference: bool


def weighted_median(values: list[float], weights: list[float]) -> float:
    if not values:
        raise ValueError("weighted_median requires at least one value")
    order = sorted(range(len(values)), key=lambda i: values[i])
    total = float(sum(weights[i] for i in order))
    if total <= 0:
        return float(np.median(values))
    cumulative = 0.0
    for index in order:
        cumulative += weights[index]
        if cumulative >= total / 2.0:
            return float(values[index])
    return float(values[order[-1]])


def _fallback() -> Prior:
    return Prior(FALLBACK_MU0, FALLBACK_PHI_DAY, (1.0,) * 7, (), 0.0, True)


def build_prior(
    reference: ReferenceData,
    *,
    business_type: str,
    location_type: str,
    category: str,
    price: float,
    capacity_factor: float | None = None,
    exclude_ids: set[str] | frozenset[str] = frozenset(),
) -> Prior:
    """PLAN.md 5.2 steps 1-6."""
    if reference.empty:
        return _fallback()
    vendor_capacity = DEFAULT_CAPACITY_FACTOR if capacity_factor is None else float(capacity_factor)
    feature = query_feature(reference, business_type, location_type, category, price)
    neighbors = nearest_neighbors(reference, feature, exclude_ids=exclude_ids, k=N_NEIGHBORS)
    if not neighbors:
        return _fallback()

    base = weighted_median(
        [series.mean_daily for series, _ in neighbors],
        [1.0 / (distance + NEIGHBOR_DISTANCE_EPS) for _, distance in neighbors],
    )
    neighbor_capacity = float(np.median([s.capacity_factor for s, _ in neighbors])) or DEFAULT_CAPACITY_FACTOR
    mu0 = max(base * (vendor_capacity / neighbor_capacity), 0.01)

    phi = float(np.median([s.dispersion for s, _ in neighbors]))
    phi = FALLBACK_PHI_DAY if not np.isfinite(phi) else float(np.clip(phi, PHI_DAY_MIN, PHI_DAY_MAX))

    profile = np.mean([s.weekday_factor for s, _ in neighbors], axis=0)
    profile_mean = float(np.mean(profile))
    profile = np.ones(7) if profile_mean <= 0 else profile / profile_mean

    return Prior(
        mu0=float(mu0),
        phi_day=phi,
        weekday_profile=tuple(float(x) for x in profile),
        neighbor_ids=tuple(s.series_id for s, _ in neighbors),
        neighbor_distance_mean=float(np.mean([d for _, d in neighbors])),
        low_reference=len(reference.series) < N_NEIGHBORS,
    )
