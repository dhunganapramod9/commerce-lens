from __future__ import annotations

from bs4 import BeautifulSoup


def get_meta(soup: BeautifulSoup, *names: str) -> str | None:
    for name in names:
        tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return str(tag["content"]).strip()
    return None


def extract_opengraph(soup: BeautifulSoup) -> dict[str, str]:
    fields = {
        "title": get_meta(soup, "og:title", "twitter:title"),
        "description": get_meta(soup, "og:description", "twitter:description", "description"),
        "image": get_meta(soup, "og:image", "twitter:image"),
        "url": get_meta(soup, "og:url"),
        "price_amount": get_meta(soup, "product:price:amount", "og:price:amount"),
        "price_currency": get_meta(soup, "product:price:currency", "og:price:currency"),
        "availability": get_meta(soup, "product:availability", "og:availability"),
        "brand": get_meta(soup, "product:brand", "og:brand"),
    }
    return {key: value for key, value in fields.items() if value}
