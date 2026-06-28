# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import polars as pl
from avin.storage.schema import Schema


def test_iid_schema_columns() -> None:
    assert Schema.IID.names() == [
        "exchange",
        "exchange_specific",
        "category",
        "ticker",
        "figi",
        "country",
        "currency",
        "sector",
        "class_code",
        "isin",
        "uid",
        "name",
        "lot",
        "step",
        "long",
        "short",
        "long_qual",
        "short_qual",
        "first_1m",
        "first_d",
    ]


def test_iid_schema_types() -> None:
    assert Schema.IID.dtypes() == [
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
        pl.String,
    ]


def test_bar_schema_columns() -> None:
    assert Schema.BAR.names() == [
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "ts",
    ]


def test_bar_schema_types() -> None:
    assert Schema.BAR.dtypes() == [
        pl.String,
        pl.Float64,
        pl.Float64,
        pl.Float64,
        pl.Float64,
        pl.Int64,
        pl.Int64,
    ]


def test_tick_schema_columns() -> None:
    assert Schema.TICK.names() == [
        "datetime",
        "direction",
        "price",
        "lots",
        "quantity",
        "value",
        "ts",
    ]


def test_tick_schema_types() -> None:
    assert Schema.TICK.dtypes() == [
        pl.String,
        pl.String,
        pl.Float64,
        pl.Int64,
        pl.Int64,
        pl.Float64,
        pl.Int64,
    ]
