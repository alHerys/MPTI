"""Predictive negative-binomial distribution and quantiles (T3.3, PLAN.md 5.4)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import nbinom

from app.ml.config import CV0, SHRINKAGE_K


@dataclass(frozen=True)
class Prediction:
    mean: float
    phi_eff: float
    r: float
    p: float
    p10: int
    p50: int
    p90: int


def effective_dispersion(phi_day: float, n_days: int) -> float:
    return float(phi_day + CV0**2 * SHRINKAGE_K / (n_days + SHRINKAGE_K))


def nbinom_params(mean: float, phi_eff: float) -> tuple[float, float]:
    mean, phi_eff = max(float(mean), 1e-6), max(float(phi_eff), 1e-6)
    r = 1.0 / phi_eff
    return r, r / (r + mean)


def _quantile(r: float, p: float, level: float) -> int:
    value = nbinom.ppf(level, r, p)
    if not np.isfinite(value):
        return int(round(r * (1 - p) / p))
    return int(max(0, np.floor(value)))


def predict(mean: float, phi_day: float, n_days: int) -> Prediction:
    phi_eff = effective_dispersion(phi_day, n_days)
    r, p = nbinom_params(mean, phi_eff)
    quantiles = np.maximum.accumulate(
        np.array([_quantile(r, p, 0.10), _quantile(r, p, 0.50), _quantile(r, p, 0.90)], dtype=int)
    )
    return Prediction(float(mean), phi_eff, r, p, int(quantiles[0]), int(quantiles[1]), int(quantiles[2]))


def quantile_at(mean: float, phi_day: float, n_days: int, level: float) -> int:
    """Exact integer quantile for an arbitrary level (newsvendor step)."""
    phi_eff = effective_dispersion(phi_day, n_days)
    return _quantile(*nbinom_params(mean, phi_eff), level)
