"""Recommendation engine entry point (T3.6, PLAN.md 5.7). Pure: no DB access."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.ml.distribution import predict
from app.ml.explain import build_reasons, confidence_label
from app.ml.optimize import optimize
from app.ml.priors import build_prior
from app.ml.reference import ReferenceData
from app.ml.update import SaleRow, compute_posterior


@dataclass(frozen=True)
class ProductInput:
    id: int
    name: str
    category: str
    price: float
    unit_cost: float
    salvage_value: float = 0.0


@dataclass(frozen=True)
class BusinessInput:
    business_type: str
    location_type: str
    capacity_factor: float = 1.0


@dataclass
class Recommendation:
    product_id: int
    name: str
    date: date
    stage: str
    n_days: int
    mean: float
    p10: int
    p50: int
    p90: int
    alpha: float
    recommended_qty: int
    nearest_band: str
    confidence: str
    reasons: list[str] = field(default_factory=list)
    neighbor_count: int = 0
    low_reference: bool = False
    weekday_factor: float = 1.0

    def as_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "date": self.date.isoformat(),
            "stage": self.stage,
            "n_days": self.n_days,
            "mean": round(self.mean, 2),
            "p10": self.p10,
            "p50": self.p50,
            "p90": self.p90,
            "alpha": round(self.alpha, 3),
            "recommended_qty": self.recommended_qty,
            "nearest_band": self.nearest_band,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "neighbor_count": self.neighbor_count,
        }


def recommend(
    product: ProductInput,
    business: BusinessInput,
    sales_rows: list[SaleRow],
    target_date: date,
    reference: ReferenceData,
) -> Recommendation:
    prior = build_prior(
        reference,
        business_type=business.business_type,
        location_type=business.location_type,
        category=product.category,
        price=product.price,
        capacity_factor=business.capacity_factor,
    )
    posterior = compute_posterior(prior, sales_rows, target_date)
    prediction = predict(posterior.target_mean, prior.phi_day, posterior.n_days)
    optimization = optimize(
        posterior.target_mean,
        prior.phi_day,
        posterior.n_days,
        product.price,
        product.unit_cost,
        product.salvage_value,
    )
    confidence = confidence_label(
        posterior.n_days, prediction.p10, prediction.p50, prediction.p90, prior.low_reference
    )
    reasons = build_reasons(
        posterior,
        alpha=optimization.alpha,
        cu=optimization.cu,
        co=optimization.co,
        confidence=confidence,
        neighbor_count=len(prior.neighbor_ids),
        low_reference=prior.low_reference,
    )
    return Recommendation(
        product_id=product.id,
        name=product.name,
        date=target_date,
        stage=posterior.stage,
        n_days=posterior.n_days,
        mean=posterior.target_mean,
        p10=prediction.p10,
        p50=prediction.p50,
        p90=prediction.p90,
        alpha=optimization.alpha,
        recommended_qty=optimization.recommended_qty,
        nearest_band=optimization.nearest_band,
        confidence=confidence,
        reasons=reasons,
        neighbor_count=len(prior.neighbor_ids),
        low_reference=prior.low_reference,
        weekday_factor=posterior.f_target,
    )
