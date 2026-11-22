"""Bayesian-style shrinkage update from the vendor's own sales (T3.2, PLAN.md 5.3)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np

from app.ml.config import MIN_TARGET_MEAN, OWN_WEEKDAY_K, SHRINKAGE_K, STOCKOUT_UPLIFT
from app.ml.priors import Prior


@dataclass(frozen=True)
class SaleRow:
    date: date
    qty_sold: int
    sold_out: bool = False

    @property
    def adjusted_qty(self) -> float:
        return float(self.qty_sold) * (STOCKOUT_UPLIFT if self.sold_out else 1.0)


@dataclass(frozen=True)
class Posterior:
    n_days: int
    ybar: float
    weight: float
    m: float
    f_target: float
    target_mean: float
    stage: str
    has_stockout: bool
    weekday_own_ratio: float | None
    weekday_count: int
    target_dow: int


def stage_for(n_days: int) -> str:
    return "H0" if n_days < 3 else ("H3" if n_days < 7 else "H7")


def compute_posterior(prior: Prior, sales_rows: list[SaleRow], target_date: date) -> Posterior:
    rows = sorted(sales_rows, key=lambda r: r.date)
    n = len(rows)
    values = [row.adjusted_qty for row in rows]
    ybar = float(np.mean(values)) if values else 0.0
    weight = n / (n + SHRINKAGE_K) if n > 0 else 0.0
    m = weight * ybar + (1.0 - weight) * prior.mu0

    dow = target_date.weekday()
    f_ref = prior.weekday_profile[dow]
    f_target = f_ref
    own_ratio: float | None = None
    weekday_count = 0
    if n >= 7 and ybar > 0:
        same_weekday = [row.adjusted_qty for row in rows if row.date.weekday() == dow]
        weekday_count = len(same_weekday)
        if weekday_count >= 1:
            own_ratio = float(np.mean(same_weekday) / ybar)
            f_target = f_ref + (weekday_count / (weekday_count + OWN_WEEKDAY_K)) * (own_ratio - f_ref)

    return Posterior(
        n_days=n,
        ybar=ybar,
        weight=weight,
        m=m,
        f_target=f_target,
        target_mean=max(m * f_target, MIN_TARGET_MEAN),
        stage=stage_for(n),
        has_stockout=any(row.sold_out for row in rows),
        weekday_own_ratio=own_ratio,
        weekday_count=weekday_count,
        target_dow=dow,
    )
