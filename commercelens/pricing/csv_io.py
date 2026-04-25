from __future__ import annotations

import csv
from pathlib import Path

from commercelens.pricing.recommendations import CompetitorOffer, OwnedProduct


def load_owned_products_csv(path: str | Path) -> list[OwnedProduct]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return [_owned_product_from_row(row) for row in csv.DictReader(handle)]


def load_competitor_offers_csv(path: str | Path) -> list[CompetitorOffer]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return [_competitor_offer_from_row(row) for row in csv.DictReader(handle)]


def _optional_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def _owned_product_from_row(row: dict[str, str | None]) -> OwnedProduct:
    return OwnedProduct(
        sku=row.get("sku") or "",
        product_name=row.get("product_name") or row.get("name") or "",
        brand=row.get("brand") or None,
        category=row.get("category") or None,
        current_price=float(row.get("current_price") or row.get("price") or 0),
        cost=float(row.get("cost") or 0),
        min_margin_percent=float(row.get("min_margin_percent") or 35),
        product_url=row.get("product_url") or row.get("url") or None,
        inventory_status=row.get("inventory_status") or None,
        weekly_units_sold=_optional_int(row.get("weekly_units_sold")),
    )


def _competitor_offer_from_row(row: dict[str, str | None]) -> CompetitorOffer:
    return CompetitorOffer(
        sku=row.get("sku") or "",
        competitor_name=row.get("competitor_name") or "",
        competitor_url=row.get("competitor_url") or row.get("url") or None,
        competitor_price=_optional_float(row.get("competitor_price") or row.get("price")),
        competitor_currency=row.get("competitor_currency") or row.get("currency") or None,
        competitor_availability=row.get("competitor_availability") or row.get("availability") or None,
        extraction_confidence=float(row.get("extraction_confidence") or 1.0),
        last_checked_at=row.get("last_checked_at") or None,
    )
