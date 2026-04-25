from __future__ import annotations

import re

from commercelens.schemas.product import Price

CURRENCY_SYMBOLS = {
    "$": "USD",
    "\u00a3": "GBP",
    "\u20ac": "EUR",
    "\u00a5": "JPY",
    "\u20b9": "INR",
    "\u00c2\u00a3": "GBP",
    "\u00e2\u201a\u00ac": "EUR",
    "\u00c2\u00a5": "JPY",
    "\u00e2\u201a\u00b9": "INR",
}

CURRENCY_CODES = {"USD", "GBP", "EUR", "JPY", "INR", "AUD", "CAD", "NZD", "CHF", "CNY"}

PRICE_RE = re.compile(
    r"(?P<code>USD|GBP|EUR|JPY|INR|AUD|CAD|NZD|CHF|CNY)?\s*"
    r"(?P<symbol>[$\u00a3\u20ac\u00a5\u20b9]|\u00c2\u00a3|\u00e2\u201a\u00ac|\u00c2\u00a5|\u00e2\u201a\u00b9)?\s*"
    r"(?P<amount>[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)",
    flags=re.IGNORECASE,
)


def parse_price(raw: str | None, default_currency: str | None = None) -> Price | None:
    if not raw:
        return None

    text = " ".join(raw.split())
    match = PRICE_RE.search(text)
    if not match:
        return Price(raw=text, currency=default_currency)

    amount_text = match.group("amount").replace(",", "")
    try:
        amount = float(amount_text)
    except ValueError:
        amount = None

    code = match.group("code")
    symbol = match.group("symbol")
    currency = None
    if code and code.upper() in CURRENCY_CODES:
        currency = code.upper()
    elif symbol:
        currency = CURRENCY_SYMBOLS.get(symbol)
    else:
        currency = default_currency

    return Price(amount=amount, currency=currency, raw=text)
