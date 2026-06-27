# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import polars as pl

IID_SCHEMA = pl.Schema(
    {
        "exchange": pl.String,
        "exchange_specific": pl.String,
        "category": pl.String,
        "ticker": pl.String,
        "figi": pl.String,
        "country": pl.String,
        "currency": pl.String,
        "sector": pl.String,
        "class_code": pl.String,
        "isin": pl.String,
        "uid": pl.String,
        "name": pl.String,
        "lot": pl.String,
        "step": pl.String,
        "long": pl.String,
        "short": pl.String,
        "long_qual": pl.String,
        "short_qual": pl.String,
        "first_1m": pl.String,
        "first_d": pl.String,
    }
)

TINKOFF_BAR_CSV_SCHEMA = pl.Schema(
    {
        "uid": pl.String,
        "datetime": pl.String,
        "open": pl.Float64,
        "close": pl.Float64,
        "high": pl.Float64,
        "low": pl.Float64,
        "volume": pl.Int64,
        "x": pl.String,
    }
)

TINKOFF_TIC_CSV_SCHEMA = pl.Schema(
    {
        "datetime": pl.String,
        "ticker": pl.String,
        "direction": pl.String,
        "price": pl.Float64,
        "lots": pl.Int64,
        "source": pl.String,
        "uid": pl.String,
        "x": pl.String,
    }
)
