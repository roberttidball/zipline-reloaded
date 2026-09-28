from unittest import mock

import pandas as pd

from zipline.data.bundles.fxmacrodata import (
    fetch_fx_pair,
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
    )

    assert url == (
        "https://api.fxmacrodata.com/v1/forex/eur/usd?"
        "start_date=2026-01-01&end_date=2026-01-31&limit=100&offset=0"
    )


def test_fetch_fx_pair_sends_api_key_header():
    response = mock.Mock()
    response.json.return_value = {"data": [{"date": "2026-01-02", "val": 1.1}]}

    with mock.patch(
        "zipline.data.bundles.fxmacrodata.requests.get", return_value=response
    ) as get:
        fetch_fx_pair(
            "EURUSD",
            pd.Timestamp("2026-01-01"),
            pd.Timestamp("2026-01-31"),
            api_key="test-key",
        )
        fetch_fx_pair("EURUSD", pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-31"))

    assert "api_key" not in get.call_args_list[0].args[0]
    assert get.call_args_list[0].kwargs["headers"] == {"X-API-Key": "test-key"}
    assert get.call_args_list[1].kwargs["headers"] == {}


def test_fetch_fx_pair_follows_pagination():
    first = mock.Mock()
    first.json.return_value = {
        "data": [
            {"date": "2026-01-03", "val": 1.3},
            {"date": "2026-01-02", "val": 1.2},
        ],
        "pagination": {"has_more": True, "next_offset": 2},
    }
    second = mock.Mock()
    second.json.return_value = {
        "data": [{"date": "2026-01-01", "val": 1.1}],
        "pagination": {"has_more": False, "next_offset": None},
    }

    with mock.patch(
        "zipline.data.bundles.fxmacrodata.requests.get", side_effect=[first, second]
    ) as get:
        data = fetch_fx_pair(
            "EURUSD", pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-31")
        )

    assert get.call_args_list[0].args[0].endswith("limit=100&offset=0")
    assert get.call_args_list[1].args[0].endswith("limit=100&offset=2")
    assert data["close"].tolist() == [1.1, 1.2, 1.3]
