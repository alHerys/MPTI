"""T3.2: shrinkage update, stages, stockout uplift, weekday blend (WBS 3.2, FR-10, FR-11)."""
from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.ml.priors import Prior
from app.ml.update import SaleRow, compute_posterior, stage_for

PRIOR = Prior(
    mu0=20.0,
    phi_day=0.1,
    weekday_profile=(1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0),
    neighbor_ids=("A", "B", "C", "D", "E"),
    neighbor_distance_mean=0.2,
    low_reference=False,
)
TARGET = date(2026, 11, 23)  # Monday


def _rows(values, start=date(2026, 11, 1), sold_out_days=()):
    return [
        SaleRow(date=start + timedelta(days=i), qty_sold=q, sold_out=(i in sold_out_days))
        for i, q in enumerate(values)
    ]


def test_n_zero_returns_prior_mean():
    posterior = compute_posterior(PRIOR, [], TARGET)
    assert posterior.n_days == 0
    assert posterior.m == pytest.approx(20.0)
    assert posterior.target_mean == pytest.approx(20.0)
    assert posterior.stage == "H0"


def test_mean_moves_monotonically_toward_ybar():
    values = [40] * 10
    means = []
    for n in range(0, 11):
        posterior = compute_posterior(PRIOR, _rows([40] * n), TARGET)
        means.append(posterior.m)
    assert means[0] == pytest.approx(20.0)
    assert means[-1] > means[0]
    assert means[-1] < 40.0  # shrinkage never fully discards the prior
    assert all(b >= a for a, b in zip(means, means[1:]))
    # Exact shrinkage formula at n=4: w = 0.5.
    assert means[4] == pytest.approx(30.0)


def test_stage_labels():
    assert [stage_for(n) for n in (0, 2, 3, 6, 7)] == ["H0", "H0", "H3", "H3", "H7"]
    for n in (0, 2, 3, 6, 7):
        assert compute_posterior(PRIOR, _rows([10] * n), TARGET).stage == stage_for(n)


def test_sold_out_uplift_applied():
    plain = compute_posterior(PRIOR, _rows([10]), TARGET)
    uplifted = compute_posterior(PRIOR, _rows([10], sold_out_days=(0,)), TARGET)
    assert uplifted.ybar == pytest.approx(11.5)
    assert uplifted.m > plain.m
    assert uplifted.has_stockout is True
    assert plain.has_stockout is False


def test_weekday_blend_only_at_seven_days():
    # Six days Tue..Sun plus one earlier Monday (the target weekday).
    start = TARGET - timedelta(days=6)
    weekday_rows = [
        SaleRow(date=start + timedelta(days=i), qty_sold=10) for i in range(6)
    ]
    monday_row = SaleRow(date=TARGET - timedelta(days=7), qty_sold=60)
    six = compute_posterior(PRIOR, weekday_rows, TARGET)
    seven = compute_posterior(PRIOR, weekday_rows + [monday_row], TARGET)
    assert six.weekday_own_ratio is None
    assert six.f_target == pytest.approx(1.0)
    assert seven.weekday_own_ratio is not None
    assert seven.f_target > 1.0


def test_weekday_profile_used_before_seven_days():
    busy_monday = Prior(
        mu0=20.0,
        phi_day=0.1,
        weekday_profile=(1.3, 1.0, 0.95, 0.95, 0.95, 1.0, 0.85),
        neighbor_ids=(),
        neighbor_distance_mean=0.0,
        low_reference=True,
    )
    posterior = compute_posterior(busy_monday, _rows([10, 12], start=date(2026, 11, 21)), TARGET)
    assert posterior.f_target == pytest.approx(1.3)
    assert posterior.target_mean == pytest.approx(posterior.m * 1.3)


def test_target_mean_floor():
    weak = Prior(0.0, 0.1, (0.01,) * 7, (), 0.0, True)
    posterior = compute_posterior(weak, [], TARGET)
    assert posterior.target_mean == pytest.approx(0.5)
