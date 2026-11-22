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
    cu = price - unit_cost
    co = unit_cost - salvage_value
    if co < 0:
        co = 0.0
    raw = cu / (cu + co) if (cu + co) > 0 else 1.0
    alpha = min(max(raw, ALPHA_MIN), ALPHA_MAX)
    return float(alpha), float(cu), float(co)


def nearest_band(alpha: float) -> str:
    distances = [(abs(alpha - level), level, name) for level, name in zip(QUANTILE_LEVELS, NEAREST_BANDS)]
    distances.sort(key=lambda item: (item[0], item[1]))
    return distances[0][2]


def optimize(
    mean: float,
    phi_day: float,
    n_days: int,
    price: float,
    unit_cost: float,
    salvage_value: float = 0.0,
) -> Optimization:
    alpha, cu, co = critical_ratio(price, unit_cost, salvage_value)
    qty = quantile_at(mean, phi_day, n_days, alpha)
    return Optimization(
        alpha=alpha,
        recommended_qty=int(max(qty, 0)),
        nearest_band=nearest_band(alpha),
        cu=cu,
        co=co,
    )
