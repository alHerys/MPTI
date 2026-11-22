"""T3.5: confidence labels and Indonesian reasons (WBS 3.5, FR-13, FR-14)."""
from __future__ import annotations

from datetime import date

from app.ml.explain import build_reasons, confidence_label
from app.ml.update import Posterior

BASE = dict(
    n_days=0,
    ybar=0.0,
    weight=0.0,
    m=20.0,
    f_target=1.0,
    target_mean=20.0,
    stage="H0",
    has_stockout=False,
    weekday_own_ratio=None,
    weekday_count=0,
    target_dow=0,
)


def _posterior(**overrides):
    return Posterior(**{**BASE, **overrides})


def test_confidence_base_levels():
    assert confidence_label(0, 10, 20, 30, False) == "rendah"
    assert confidence_label(2, 10, 20, 30, False) == "rendah"
    assert confidence_label(3, 10, 20, 30, False) == "sedang"
    assert confidence_label(6, 10, 20, 30, False) == "sedang"
    assert confidence_label(7, 10, 20, 30, False) == "tinggi"


def test_confidence_downgrade_on_wide_ratio():
    # ratio = (90-10)/20 = 4.0 > 1.2 -> tinggi becomes sedang, sedang becomes rendah
    assert confidence_label(7, 10, 20, 90, False) == "sedang"
    assert confidence_label(3, 10, 20, 90, False) == "rendah"
    assert confidence_label(0, 10, 20, 90, False) == "rendah"


def test_confidence_force_low_when_low_reference():
    assert confidence_label(7, 10, 20, 30, True) == "rendah"


def test_reason_stage_variants():
    zero = build_reasons(_posterior(n_days=0), alpha=0.5, cu=6000, co=6000,
                         confidence="rendah", neighbor_count=5, low_reference=False)
    assert zero[0] == "Belum ada data penjualan; estimasi dari 5 usaha serupa."
    three = build_reasons(_posterior(n_days=3, stage="H3"), alpha=0.5, cu=6000, co=6000,
                          confidence="sedang", neighbor_count=5, low_reference=False)
    assert three[0] == "Berdasarkan 3 hari data Anda dan usaha serupa."
    seven = build_reasons(_posterior(n_days=7, stage="H7"), alpha=0.5, cu=6000, co=6000,
                          confidence="tinggi", neighbor_count=5, low_reference=False)
    assert seven[0] == "Berdasarkan 7 hari data penjualan Anda."


def test_reason_weekday_busy_and_quiet():
    busy = build_reasons(_posterior(f_target=1.25, target_dow=4), alpha=0.5, cu=6000, co=6000,
                         confidence="sedang", neighbor_count=5, low_reference=False)
    assert any("Jumat biasanya lebih ramai" in r and "25%" in r for r in busy)
    quiet = build_reasons(_posterior(f_target=0.8, target_dow=6), alpha=0.5, cu=6000, co=6000,
                          confidence="sedang", neighbor_count=5, low_reference=False)
    assert any("Minggu biasanya lebih sepi" in r and "20%" in r for r in quiet)
    neutral = build_reasons(_posterior(f_target=1.05), alpha=0.5, cu=6000, co=6000,
                            confidence="sedang", neighbor_count=5, low_reference=False)
    assert not any("biasanya" in r for r in neutral)


def test_reason_stockout_and_cost_and_low_confidence():
    reasons = build_reasons(
        _posterior(n_days=2, has_stockout=True), alpha=0.667, cu=7000, co=3000,
        confidence="rendah", neighbor_count=5, low_reference=False,
    )
    assert any("kehabisan stok" in r and "15%" in r for r in reasons)
    assert "Margin Rp7.000 per porsi vs kerugian sisa Rp3.000; target peluang cukup stok 67%." in reasons
    assert reasons[-1] == "Keyakinan rendah; catat penjualan harian agar rekomendasi membaik."


def test_reason_order_is_fixed():
    reasons = build_reasons(
        _posterior(n_days=2, has_stockout=True, f_target=1.3, target_dow=5),
        alpha=0.7, cu=7000, co=3000, confidence="rendah", neighbor_count=5, low_reference=False,
    )
    assert reasons[0].startswith("Berdasarkan 2 hari")
    assert reasons[1].startswith("Hari Sabtu biasanya lebih ramai")
    assert reasons[2].startswith("Ada hari kehabisan stok")
    assert reasons[3].startswith("Margin Rp7.000")
    assert reasons[4].startswith("Keyakinan rendah")
