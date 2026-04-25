from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from enum import Enum
from typing import Iterable
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class RecommendationAction(str, Enum):
    DO_NOT_MATCH = "do_not_match"
    MATCH_OR_NEAR_MATCH = "match_or_near_match"
    HOLD_OR_RAISE = "hold_or_raise"
    CONSIDER_RAISE = "consider_raise"
    NEEDS_REVIEW = "needs_review"


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class OwnedProduct(BaseModel):
    sku: str
    product_name: str
    current_price: float = Field(gt=0)
    cost: float = Field(ge=0)
    min_margin_percent: float = Field(default=35.0, ge=0, lt=100)
    brand: str | None = None
    category: str | None = None
    product_url: str | None = None
    inventory_status: str | None = None
    weekly_units_sold: int | None = Field(default=None, ge=0)

    @field_validator("sku", "product_name")
    @classmethod
    def require_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be blank.")
        return value


class CompetitorOffer(BaseModel):
    sku: str
    competitor_name: str
    competitor_url: str | None = None
    competitor_price: float | None = Field(default=None, gt=0)
    competitor_currency: str | None = None
    competitor_availability: str | None = None
    extraction_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    last_checked_at: str | None = None

    @field_validator("sku", "competitor_name")
    @classmethod
    def require_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be blank.")
        return value

    @property
    def is_out_of_stock(self) -> bool:
        if not self.competitor_availability:
            return False
        normalized = self.competitor_availability.strip().lower().replace("-", "_").replace(" ", "_")
        return normalized in {"out_of_stock", "sold_out", "unavailable"}


class PricingRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid4().hex[:16]}")
    sku: str
    product_name: str
    current_price: float
    cost: float
    current_margin_percent: float
    min_margin_percent: float
    minimum_safe_price: float
    competitor_name: str | None = None
    competitor_price: float | None = None
    competitor_availability: str | None = None
    recommended_action: RecommendationAction
    recommended_price: float | None = None
    expected_margin_percent: float | None = None
    estimated_impact: float | None = None
    risk_level: str
    explanation: str
    status: RecommendationStatus = RecommendationStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).replace(microsecond=0).isoformat())


class MarginLeakReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"mlr_{uuid4().hex[:16]}")
    store_name: str | None = None
    week_start: str | None = None
    week_end: str | None = None
    products_checked: int = 0
    competitor_urls_checked: int = 0
    unsafe_matches_count: int = 0
    safe_raise_count: int = 0
    match_opportunities_count: int = 0
    out_of_stock_competitors_count: int = 0
    needs_review_count: int = 0
    estimated_margin_at_risk: float = 0.0
    recommendations: list[PricingRecommendation] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).replace(microsecond=0).isoformat())


def gross_margin_percent(price: float, cost: float) -> float:
    if price <= 0:
        return 0.0
    return round(((price - cost) / price) * 100, 2)


def minimum_safe_price(cost: float, min_margin_percent: float) -> float:
    if min_margin_percent >= 100:
        raise ValueError("min_margin_percent must be below 100.")
    return round(cost / (1 - min_margin_percent / 100), 2)


def recommend_pricing_action(
    product: OwnedProduct,
    offer: CompetitorOffer | None = None,
) -> PricingRecommendation:
    safe_price = minimum_safe_price(product.cost, product.min_margin_percent)
    current_margin = gross_margin_percent(product.current_price, product.cost)

    if offer is None or offer.competitor_price is None or offer.extraction_confidence < 0.5:
        return PricingRecommendation(
            sku=product.sku,
            product_name=product.product_name,
            current_price=product.current_price,
            cost=product.cost,
            current_margin_percent=current_margin,
            min_margin_percent=product.min_margin_percent,
            minimum_safe_price=safe_price,
            competitor_name=offer.competitor_name if offer else None,
            competitor_price=offer.competitor_price if offer else None,
            competitor_availability=offer.competitor_availability if offer else None,
            recommended_action=RecommendationAction.NEEDS_REVIEW,
            risk_level="medium",
            status=RecommendationStatus.NEEDS_REVIEW,
            explanation="Needs review. CommerceLens could not get reliable competitor price data for this product.",
        )

    competitor_price = offer.competitor_price
    estimated_units = product.weekly_units_sold or 1

    if offer.is_out_of_stock:
        recommended_price = product.current_price
        if competitor_price > product.current_price * 1.05:
            recommended_price = round(min(competitor_price * 0.98, product.current_price * 1.08), 2)
        return PricingRecommendation(
            sku=product.sku,
            product_name=product.product_name,
            current_price=product.current_price,
            cost=product.cost,
            current_margin_percent=current_margin,
            min_margin_percent=product.min_margin_percent,
            minimum_safe_price=safe_price,
            competitor_name=offer.competitor_name,
            competitor_price=competitor_price,
            competitor_availability=offer.competitor_availability,
            recommended_action=RecommendationAction.HOLD_OR_RAISE,
            recommended_price=recommended_price,
            expected_margin_percent=gross_margin_percent(recommended_price, product.cost),
            estimated_impact=round((recommended_price - product.current_price) * estimated_units, 2),
            risk_level="low",
            explanation=(
                f"{offer.competitor_name} is out of stock at {competitor_price:.2f}. "
                "Do not match an unavailable competitor. Hold price or consider a small raise."
            ),
        )

    if competitor_price < safe_price:
        return PricingRecommendation(
            sku=product.sku,
            product_name=product.product_name,
            current_price=product.current_price,
            cost=product.cost,
            current_margin_percent=current_margin,
            min_margin_percent=product.min_margin_percent,
            minimum_safe_price=safe_price,
            competitor_name=offer.competitor_name,
            competitor_price=competitor_price,
            competitor_availability=offer.competitor_availability,
            recommended_action=RecommendationAction.DO_NOT_MATCH,
            recommended_price=product.current_price,
            expected_margin_percent=current_margin,
            estimated_impact=round((safe_price - competitor_price) * estimated_units, 2),
            risk_level="high",
            explanation=(
                f"Do not match {offer.competitor_name}. Their price ({competitor_price:.2f}) "
                f"is below your minimum safe price ({safe_price:.2f}) and would push margin "
                f"below your {product.min_margin_percent:.0f}% floor."
            ),
        )

    if competitor_price < product.current_price:
        recommended_price = round(max(competitor_price, safe_price), 2)
        return PricingRecommendation(
            sku=product.sku,
            product_name=product.product_name,
            current_price=product.current_price,
            cost=product.cost,
            current_margin_percent=current_margin,
            min_margin_percent=product.min_margin_percent,
            minimum_safe_price=safe_price,
            competitor_name=offer.competitor_name,
            competitor_price=competitor_price,
            competitor_availability=offer.competitor_availability,
            recommended_action=RecommendationAction.MATCH_OR_NEAR_MATCH,
            recommended_price=recommended_price,
            expected_margin_percent=gross_margin_percent(recommended_price, product.cost),
            estimated_impact=round((product.current_price - recommended_price) * estimated_units, 2),
            risk_level="medium",
            explanation=(
                f"{offer.competitor_name} is cheaper at {competitor_price:.2f}, and matching "
                "stays above your margin floor. Review a match or near-match this week."
            ),
        )

    if competitor_price >= product.current_price * 1.1:
        recommended_price = round(min(competitor_price * 0.98, product.current_price * 1.08), 2)
        return PricingRecommendation(
            sku=product.sku,
            product_name=product.product_name,
            current_price=product.current_price,
            cost=product.cost,
            current_margin_percent=current_margin,
            min_margin_percent=product.min_margin_percent,
            minimum_safe_price=safe_price,
            competitor_name=offer.competitor_name,
            competitor_price=competitor_price,
            competitor_availability=offer.competitor_availability,
            recommended_action=RecommendationAction.CONSIDER_RAISE,
            recommended_price=recommended_price,
            expected_margin_percent=gross_margin_percent(recommended_price, product.cost),
            estimated_impact=round((recommended_price - product.current_price) * estimated_units, 2),
            risk_level="low",
            explanation=(
                f"{offer.competitor_name} is priced meaningfully higher at {competitor_price:.2f}. "
                f"Consider raising to {recommended_price:.2f} while staying competitive."
            ),
        )

    return PricingRecommendation(
        sku=product.sku,
        product_name=product.product_name,
        current_price=product.current_price,
        cost=product.cost,
        current_margin_percent=current_margin,
        min_margin_percent=product.min_margin_percent,
        minimum_safe_price=safe_price,
        competitor_name=offer.competitor_name,
        competitor_price=competitor_price,
        competitor_availability=offer.competitor_availability,
        recommended_action=RecommendationAction.NEEDS_REVIEW,
        recommended_price=product.current_price,
        expected_margin_percent=current_margin,
        risk_level="low",
        status=RecommendationStatus.NEEDS_REVIEW,
        explanation="No clear pricing leak found. Keep this product on the weekly review list.",
    )


def build_margin_leak_report(
    products: Iterable[OwnedProduct],
    offers: Iterable[CompetitorOffer],
    store_name: str | None = None,
    week_start: str | None = None,
    week_end: str | None = None,
) -> MarginLeakReport:
    product_list = list(products)
    offer_list = list(offers)
    offers_by_sku: dict[str, list[CompetitorOffer]] = {}
    for offer in offer_list:
        offers_by_sku.setdefault(offer.sku, []).append(offer)

    recommendations: list[PricingRecommendation] = []
    for product in product_list:
        sku_offers = offers_by_sku.get(product.sku) or []
        if not sku_offers:
            recommendations.append(recommend_pricing_action(product, None))
            continue
        for offer in sku_offers:
            recommendations.append(recommend_pricing_action(product, offer))

    counts = Counter(item.recommended_action for item in recommendations)
    estimated_margin_at_risk = sum(
        item.estimated_impact or 0
        for item in recommendations
        if item.recommended_action == RecommendationAction.DO_NOT_MATCH
    )

    return MarginLeakReport(
        store_name=store_name,
        week_start=week_start,
        week_end=week_end,
        products_checked=len(product_list),
        competitor_urls_checked=len(offer_list),
        unsafe_matches_count=counts[RecommendationAction.DO_NOT_MATCH],
        safe_raise_count=counts[RecommendationAction.CONSIDER_RAISE],
        match_opportunities_count=counts[RecommendationAction.MATCH_OR_NEAR_MATCH],
        out_of_stock_competitors_count=counts[RecommendationAction.HOLD_OR_RAISE],
        needs_review_count=counts[RecommendationAction.NEEDS_REVIEW],
        estimated_margin_at_risk=round(estimated_margin_at_risk, 2),
        recommendations=recommendations,
    )
