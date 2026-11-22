"""Cost-based newsvendor production quantity (T3.4, PLAN.md 5.5)."""
from __future__ import annotations

from dataclasses import dataclass

from app.ml.config import ALPHA_MAX, ALPHA_MIN, NEAREST_BANDS, QUANTILE_LEVELS
from app.ml.distribution import quantile_at


class PricingError(ValueError):
    """Raised when price <= unit_cost makes the newsvendor rule meaningless."""


@dataclass(frozen=True)
class Optimization:
    alpha: float
    recommended_qty: int
    nearest_band: str
    cu: float
    co: float


def critical_ratio(price: float, unit_cost: float, salvage_value: float = 0.0) -> tuple[float, float, float]:
    if price <= unit_cost:
        raise PricingError("Harga jual harus lebih besar dari biaya per porsi.")
    cu = float(price - unit_cost)
    co = max(float(unit_cost - salvage_value), 0.0)
    raw = cu / (cu + co) if (cu + co) > 0 else 1.0
    return float(min(max(raw, ALPHA_MIN), ALPHA_MAX)), cu, co


def nearest_band(alpha: float) -> str:
    distances = [(abs(alpha - level), level, name) for level, name in zip(QUANTILE_LEVELS, NEAREST_BANDS)]
    return sorted(distances, key=lambda item: (item[0], item[1]))[0][2]


def optimize(
    mean: float, phi_day: float, n_days: int, price: float, unit_cost: float, salvage_value: float = 0.0
) -> Optimization:
    alpha, cu, co = critical_ratio(price, unit_cost, salvage_value)
    return Optimization(
        alpha=alpha,
        recommended_qty=int(max(quantile_at(mean, phi_day, n_days, alpha), 0)),
        nearest_band=nearest_band(alpha),
        cu=cu,
        co=co,
    )
