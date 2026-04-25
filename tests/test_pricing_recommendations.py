from commercelens.pricing import (
    CompetitorOffer,
    OwnedProduct,
    RecommendationAction,
    build_margin_leak_report,
    minimum_safe_price,
    recommend_pricing_action,
)


def test_minimum_safe_price_from_margin_floor() -> None:
    assert minimum_safe_price(cost=38.0, min_margin_percent=35.0) == 58.46


def test_do_not_match_when_competitor_breaks_margin_floor() -> None:
    product = OwnedProduct(
        sku="SERUM-50",
        product_name="Hydrating Serum 50ml",
        current_price=59.99,
        cost=38.0,
        min_margin_percent=35,
        weekly_units_sold=24,
    )
    offer = CompetitorOffer(
        sku="SERUM-50",
        competitor_name="Competitor A",
        competitor_price=49.99,
        competitor_availability="in_stock",
    )

    recommendation = recommend_pricing_action(product, offer)

    assert recommendation.recommended_action == RecommendationAction.DO_NOT_MATCH
    assert recommendation.minimum_safe_price == 58.46
    assert recommendation.recommended_price == 59.99
    assert recommendation.risk_level == "high"
    assert "Do not match" in recommendation.explanation


def test_consider_raise_when_competitor_is_much_higher() -> None:
    product = OwnedProduct(
        sku="HOODIE-PRO",
        product_name="Hoodie Pro",
        current_price=64.99,
        cost=34.0,
        min_margin_percent=40,
        weekly_units_sold=18,
    )
    offer = CompetitorOffer(
        sku="HOODIE-PRO",
        competitor_name="Competitor B",
        competitor_price=79.99,
        competitor_availability="in_stock",
    )

    recommendation = recommend_pricing_action(product, offer)

    assert recommendation.recommended_action == RecommendationAction.CONSIDER_RAISE
    assert recommendation.recommended_price is not None
    assert recommendation.recommended_price > product.current_price
    assert recommendation.risk_level == "low"


def test_hold_or_raise_when_competitor_is_out_of_stock() -> None:
    product = OwnedProduct(
        sku="PET-CHEW-30",
        product_name="Daily Pet Chews 30ct",
        current_price=39.99,
        cost=18.5,
        min_margin_percent=45,
        weekly_units_sold=42,
    )
    offer = CompetitorOffer(
        sku="PET-CHEW-30",
        competitor_name="Competitor C",
        competitor_price=35.99,
        competitor_availability="out_of_stock",
    )

    recommendation = recommend_pricing_action(product, offer)

    assert recommendation.recommended_action == RecommendationAction.HOLD_OR_RAISE
    assert "out of stock" in recommendation.explanation


def test_margin_leak_report_counts_actions() -> None:
    products = [
        OwnedProduct(sku="A", product_name="A", current_price=59.99, cost=38, min_margin_percent=35),
        OwnedProduct(sku="B", product_name="B", current_price=64.99, cost=34, min_margin_percent=40),
    ]
    offers = [
        CompetitorOffer(sku="A", competitor_name="Competitor A", competitor_price=49.99),
        CompetitorOffer(sku="B", competitor_name="Competitor B", competitor_price=79.99),
    ]

    report = build_margin_leak_report(products, offers, store_name="Demo Store")

    assert report.store_name == "Demo Store"
    assert report.products_checked == 2
    assert report.competitor_urls_checked == 2
    assert report.unsafe_matches_count == 1
    assert report.safe_raise_count == 1
    assert report.estimated_margin_at_risk > 0
