from pathlib import Path

from commercelens.pricing import build_margin_leak_report, load_competitor_offers_csv, load_owned_products_csv


def test_load_templates_and_generate_margin_report() -> None:
    root = Path(__file__).resolve().parents[1]
    products = load_owned_products_csv(root / "examples" / "owned_products_template.csv")
    offers = load_competitor_offers_csv(root / "examples" / "competitor_urls_template.csv")

    report = build_margin_leak_report(products, offers, store_name="Template Store")

    assert report.store_name == "Template Store"
    assert report.products_checked == 3
    assert report.competitor_urls_checked == 3
    assert report.unsafe_matches_count == 1
    assert report.safe_raise_count == 1
    assert report.out_of_stock_competitors_count == 1
