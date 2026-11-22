"""T3.3: P10/P50/P90 properties (WBS 3.3, FR-12)."""
from __future__ import annotations

import itertools

from app.ml.distribution import effective_dispersion, predict, quantile_at


def test_quantile_order_over_200_combinations():
    combos = list(itertools.product(
        [0.5, 1.0, 5.0, 10.0, 20.0, 35.0, 60.0, 90.0],
        [0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0],
        [0, 1, 2, 3, 5, 7, 14, 30, 60],
    ))
    assert len(combos) >= 200
    for mean, phi, n in combos:
        p = predict(mean, phi, n)
        assert isinstance(p.p10, int) and p.p10 >= 0
        assert p.p10 <= p.p50 <= p.p90, (mean, phi, n)


def test_width_shrinks_as_n_grows():
    widths = []
    for n in [0, 1, 2, 3, 4, 5, 7, 10, 20, 40, 80]:
        p = predict(12.0, 0.3, n)
        widths.append(p.p90 - p.p10)
    assert all(b <= a for a, b in zip(widths, widths[1:])), widths


def test_effective_dispersion_formula():
    import pytest

    assert effective_dispersion(0.1, 0) == pytest.approx(0.1 + 0.16)
    assert effective_dispersion(0.1, 4) == pytest.approx(0.1 + 0.16 * 4 / 8)


def test_means_near_zero_are_safe():
    p = predict(0.5, 0.9, 0)
    assert p.p10 == 0 and p.p50 >= 0 and p.p90 >= 0
    assert quantile_at(0.5, 0.9, 0, 0.5) >= 0
