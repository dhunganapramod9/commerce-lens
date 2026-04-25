from commercelens.pricing import (
    CompetitorOffer,
    OwnedProduct,
    build_margin_leak_report,
    render_margin_leak_report_html,
)


def test_render_margin_leak_report_html_contains_customer_facing_sections() -> None:
    report = build_margin_leak_report(
        [OwnedProduct(sku="SERUM-50", product_name="Hydrating Serum", current_price=59.99, cost=38, min_margin_percent=35)],
        [CompetitorOffer(sku="SERUM-50", competitor_name="Competitor A", competitor_price=49.99)],
        store_name="Demo Store",
    )

    html = render_margin_leak_report_html(report)

    assert "Demo Store Margin Leak Report" in html
    assert "This Week's Actions" in html
    assert "Do not match" in html
    assert "Margin at risk" in html
    assert "Hydrating Serum" in html
