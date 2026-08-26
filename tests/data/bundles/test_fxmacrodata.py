import pandas as pd

from zipline.data.bundles.fxmacrodata import (
    format_fxmacrodata_url,
    parse_symbols,
    split_pair,
)


def test_parse_symbols_from_environment():
    symbols = parse_symbols({"FXMACRODATA_SYMBOLS": "eur/usd, gbp-usd, AUDUSD"})

    assert symbols == ["EURUSD", "GBPUSD", "AUDUSD"]


def test_split_pair_accepts_compact_and_delimited_symbols():
    assert split_pair("EURUSD") == ("EUR", "USD")
    assert split_pair("EUR/USD") == ("EUR", "USD")


def test_format_fxmacrodata_url():
    url = format_fxmacrodata_url(
        "EURUSD",
        pd.Timestamp("2026-01-01"),
        pd.Timestamp("2026-01-31"),
        api_key="test key",
    )

    assert url == (
        "https://api.fxmacrodata.com/v1/forex/eur/usd?"
        "start_date=2026-01-01&end_date=2026-01-31&api_key=test+key"
    )
