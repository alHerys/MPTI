"""T3.4: newsvendor alpha and clamping (WBS 3.4, FR-12)."""
from __future__ import annotations

import pytest

from app.ml.distribution import predict
from app.ml.optimize import PricingError, critical_ratio, nearest_band, optimize


def test_worked_example_price_10000_cost_3000():
    alpha, cu, co = critical_ratio(10000, 3000)
    assert cu == 7000 and co == 3000
    assert alpha == pytest.approx(0.70)
    p = predict(30, 0.2, 3)
    result = optimize(30, 0.2, 3, 10000, 3000)
    assert result.alpha == pytest.approx(0.70)
    assert p.p50 <= result.recommended_qty <= p.p90


def test_worked_example_price_10000_cost_6000():
    alpha, _, _ = critical_ratio(10000, 6000)
    assert alpha == pytest.approx(0.40)
    p = predict(30, 0.2, 3)
    result = optimize(30, 0.2, 3, 10000, 6000)
    assert p.p10 <= result.recommended_qty <= p.p50


def test_worked_example_price_10000_cost_9000():
    alpha, _, _ = critical_ratio(10000, 9000)
    assert alpha == pytest.approx(0.10)
    p = predict(30, 0.2, 3)
    result = optimize(30, 0.2, 3, 10000, 9000)
    assert result.recommended_qty == pytest.approx(p.p10, abs=1)


def test_price_at_or_below_cost_raises():
    with pytest.raises(PricingError):
        critical_ratio(5000, 5000)
    with pytest.raises(PricingError):
        optimize(20, 0.2, 3, 5000, 6000)


def test_alpha_clamped_to_bounds():
    # Huge leftover loss (co >> cu) clamps to the floor.
    alpha, _, co = critical_ratio(10000, 9900)
    assert alpha == pytest.approx(0.05) and co == 9900
    # Margin tiny vs leftover cost -> raw 0.03, clamped to floor.
    alpha, _, _ = critical_ratio(10000, 9700)
    assert alpha == pytest.approx(0.05)
    # Co = 0 -> ceiling.
    alpha, _, _ = critical_ratio(10000, 3000, salvage_value=3000)
    assert alpha == pytest.approx(0.95)


def test_salvage_value_reduces_leftover_cost():
    _, cu, co = critical_ratio(10000, 6000, salvage_value=4000)
    assert cu == 4000 and co == 2000
    assert critical_ratio(10000, 6000, 4000)[0] == pytest.approx(2 / 3)


def test_nearest_band_levels():
    assert nearest_band(0.10) == "P10"
    assert nearest_band(0.40) == "P50"
    assert nearest_band(0.50) == "P50"
    assert nearest_band(0.70) == "P50"
    assert nearest_band(0.80) == "P90"
    assert nearest_band(0.95) == "P90"


def test_zero_leftover_costs_alpha_at_ceiling():
    alpha, _, _ = critical_ratio(10000, 3000, salvage_value=3000)
    assert alpha == pytest.approx(0.95)
