"""Confidence labels and Indonesian explanations (T3.5, PLAN.md 5.6)."""
from __future__ import annotations

from app.ml.config import (
    CONFIDENCE_LEVELS, CONFIDENCE_RATIO_LIMIT, STOCKOUT_UPLIFT,
    WEEKDAY_NAMES, WEEKDAY_REASON_THRESHOLD,
)
from app.ml.update import Posterior


def confidence_label(n_days: int, p10: int, p50: int, p90: int, low_reference: bool) -> str:
    index = 0 if n_days < 3 else (1 if n_days < 7 else 2)
    if (p90 - p10) / max(p50, 1) > CONFIDENCE_RATIO_LIMIT:
        index = max(index - 1, 0)
    return CONFIDENCE_LEVELS[0 if low_reference else index]


def _rupiah(value: float) -> str:
    return f"Rp{int(round(value)):,}".replace(",", ".")


def build_reasons(
    posterior: Posterior,
    *,
    alpha: float,
    cu: float,
    co: float,
    confidence: str,
    neighbor_count: int,
    low_reference: bool,
) -> list[str]:
    n = posterior.n_days
    if n == 0:
        reasons = [f"Belum ada data penjualan; estimasi dari {neighbor_count} usaha serupa."]
    elif n < 7:
        reasons = [f"Berdasarkan {n} hari data Anda dan usaha serupa."]
    else:
        reasons = [f"Berdasarkan {n} hari data penjualan Anda."]

    deviation = posterior.f_target - 1.0
    if abs(deviation) > WEEKDAY_REASON_THRESHOLD:
        direction = "lebih ramai" if deviation > 0 else "lebih sepi"
        reasons.append(
            f"Hari {WEEKDAY_NAMES[posterior.target_dow]} biasanya {direction} (±{abs(deviation) * 100:.0f}%)."
        )
    if posterior.has_stockout:
        reasons.append(
            f"Ada hari kehabisan stok; permintaan disesuaikan naik {round((STOCKOUT_UPLIFT - 1) * 100)}%."
        )
    reasons.append(
        f"Margin {_rupiah(cu)} per porsi vs kerugian sisa {_rupiah(co)}; "
        f"target peluang cukup stok {round(alpha * 100)}%."
    )
    if confidence == "rendah" or low_reference:
        reasons.append("Keyakinan rendah; catat penjualan harian agar rekomendasi membaik.")
    return reasons
