"""T3.1: reference features, nearest neighbours and Day-0 prior (WBS 3.1, FR-09)."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from app.ml.priors import build_prior, weighted_median
from app.ml.reference import ReferenceData, build_reference, load_reference


def _fixture_series(sid, business_type, location_type, category, price, capacity, base, dispersion, days=30):
    start = date(2026, 1, 1)
    meta = {
        "series_id": sid,
        "business_type": business_type,
        "location_type": location_type,
        "category": category,
        "price": price,
        "capacity_factor": capacity,
        "base_mean": base,
        "dispersion": dispersion,
    }
    rows = [
        {"series_id": sid, "date": (start + timedelta(days=i)).isoformat(), "qty": base}
        for i in range(days)
    ]
    return meta, rows


@pytest.fixture(scope="module")
def small_reference():
    meta, rows = [], []
    specs = [
        ("S1", "kantin", "kampus", "nasi", 12000, 1.0, 40, 0.10),
        ("S2", "kantin", "kampus", "nasi", 13000, 1.0, 38, 0.12),
        ("S3", "kantin", "kampus", "nasi", 11000, 1.0, 42, 0.08),
        ("S4", "kantin", "kampus", "minuman", 5000, 1.0, 12, 0.20),
        ("S5", "warung", "pasar", "snack", 6000, 1.0, 15, 0.25),
        ("S6", "cafe", "kantor", "roti", 9000, 1.0, 10, 0.18),
        ("S7", "bakery", "permukiman", "roti", 8000, 1.0, 9, 0.22),
    ]
    for spec in specs:
        m, r = _fixture_series(*spec)
        meta.append(m)
        rows.extend(r)
    return build_reference(meta, rows)


def test_day0_prior_positive_without_sales(small_reference):
    prior = build_prior(
        small_reference,
        business_type="kantin",
        location_type="kampus",
        category="nasi",
        price=12500,
    )
    assert prior.mu0 > 0
    assert 0.02 <= prior.phi_day <= 1.0
    assert len(prior.weekday_profile) == 7
    assert abs(float(np.mean(prior.weekday_profile)) - 1.0) < 1e-6
    assert len(prior.neighbor_ids) == 5
    assert prior.low_reference is False


def test_nasi_kantin_prior_exceeds_minuman(small_reference):
    nasi = build_prior(
        small_reference, business_type="kantin", location_type="kampus", category="nasi", price=12500
    )
    minuman = build_prior(
        small_reference, business_type="kantin", location_type="kampus", category="minuman", price=12500
    )
    assert nasi.mu0 > minuman.mu0


def test_capacity_factor_scales_prior(small_reference):
    base = build_prior(
        small_reference, business_type="kantin", location_type="kampus", category="nasi", price=12000,
        capacity_factor=1.0,
    )
    doubled = build_prior(
        small_reference, business_type="kantin", location_type="kampus", category="nasi", price=12000,
        capacity_factor=2.0,
    )
    assert doubled.mu0 == pytest.approx(base.mu0 * 2.0, rel=0.02)


def test_empty_reference_fallback():
    prior = build_prior(
        ReferenceData([], 0.0, 0.0),
        business_type="warung",
        location_type="kampus",
        category="nasi",
        price=10000,
    )
    assert prior.mu0 == 10.0
    assert prior.phi_day == 0.15
    assert prior.weekday_profile == (1.0,) * 7
    assert prior.low_reference is True
    assert prior.neighbor_ids == ()


def test_fewer_than_five_series_is_low_reference(small_reference):
    tiny = ReferenceData(small_reference.series[:3], small_reference.price_min, small_reference.price_max)
    prior = build_prior(
        tiny, business_type="kantin", location_type="kampus", category="nasi", price=12000
    )
    assert len(prior.neighbor_ids) == 3
    assert prior.low_reference is True
    assert prior.mu0 > 0


def test_committed_reference_dataset_loads():
    ref = load_reference("data")
    assert len(ref.series) == 168
    prior = build_prior(
        ref, business_type="warung", location_type="permukiman", category="nasi", price=12000
    )
    assert prior.mu0 > 0 and not prior.low_reference


def test_weighted_median_prefers_heavy_weight():
    assert weighted_median([1.0, 10.0], [9.0, 1.0]) == 1.0
    assert weighted_median([1.0, 10.0], [1.0, 9.0]) == 10.0
