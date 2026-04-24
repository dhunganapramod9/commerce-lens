from commercelens.extractors.price import parse_price


def test_parse_usd_symbol_price() -> None:
    price = parse_price("$1,299.99")
    assert price is not None
    assert price.amount == 1299.99
    assert price.currency == "USD"


def test_parse_gbp_symbol_price() -> None:
    price = parse_price("£51.77")
    assert price is not None
    assert price.amount == 51.77
    assert price.currency == "GBP"


def test_parse_currency_code() -> None:
    price = parse_price("USD 20.00")
    assert price is not None
    assert price.amount == 20.0
    assert price.currency == "USD"
