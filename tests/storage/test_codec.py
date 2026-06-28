# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import polars as pl
from avin.domain.chart.bar import Bar
from avin.domain.common.direction import Direction
from avin.domain.raw.tick import Tick
from avin.storage.codec import StorageCodec
from avin.storage.schema import Schema


def test_bars_to_df_uses_bar_schema() -> None:
    bars = [
        Bar(ts=1, open=10.0, high=12.0, low=9.0, close=11.0, vol=100),
        Bar(ts=2, open=11.0, high=13.0, low=8.0, close=10.5, vol=200),
    ]

    df = StorageCodec.bars_to_df(bars)

    assert df.columns == Schema.BAR.names()
    assert df.to_dicts() == [
        {
            "datetime": str(bars[0].dt),
            "open": 10.0,
            "high": 12.0,
            "low": 9.0,
            "close": 11.0,
            "volume": 100,
            "ts": 1,
        },
        {
            "datetime": str(bars[1].dt),
            "open": 11.0,
            "high": 13.0,
            "low": 8.0,
            "close": 10.5,
            "volume": 200,
            "ts": 2,
        },
    ]


def test_bars_from_df_restores_bars() -> None:
    df = pl.DataFrame(
        {
            "datetime": ["ignored-1", "ignored-2"],
            "open": [10.0, 11.0],
            "high": [12.0, 13.0],
            "low": [9.0, 8.0],
            "close": [11.0, 10.5],
            "volume": [100, 200],
            "ts": [1, 2],
        }
    )

    bars = StorageCodec.bars_from_df(df)

    assert bars == [
        Bar(ts=1, open=10.0, high=12.0, low=9.0, close=11.0, vol=100),
        Bar(ts=2, open=11.0, high=13.0, low=8.0, close=10.5, vol=200),
    ]


def test_bars_from_df_selects_schema_columns() -> None:
    df = pl.DataFrame(
        {
            "extra": ["ignored"],
            "ts": [1],
            "volume": [100],
            "close": [11.0],
            "low": [9.0],
            "high": [12.0],
            "open": [10.0],
            "datetime": ["ignored"],
        }
    )

    bars = StorageCodec.bars_from_df(df)

    assert bars == [
        Bar(ts=1, open=10.0, high=12.0, low=9.0, close=11.0, vol=100)
    ]


def test_ticks_to_df_uses_tick_schema() -> None:
    ticks = [
        Tick(
            ts=1,
            direction=Direction.BUY,
            price=10.0,
            lots=2,
            quantity=20,
            value=200.0,
        ),
        Tick(
            ts=2,
            direction=Direction.SELL,
            price=11.0,
            lots=3,
            quantity=30,
            value=330.0,
        ),
    ]

    df = StorageCodec.ticks_to_df(ticks)

    assert df.columns == Schema.TICK.names()
    assert df.to_dicts() == [
        {
            "datetime": str(ticks[0].dt),
            "direction": "B",
            "price": 10.0,
            "lots": 2,
            "quantity": 20,
            "value": 200.0,
            "ts": 1,
        },
        {
            "datetime": str(ticks[1].dt),
            "direction": "S",
            "price": 11.0,
            "lots": 3,
            "quantity": 30,
            "value": 330.0,
            "ts": 2,
        },
    ]


def test_ticks_from_df_restores_ticks() -> None:
    df = pl.DataFrame(
        {
            "datetime": ["ignored-1", "ignored-2"],
            "direction": ["B", "S"],
            "price": [10.0, 11.0],
            "lots": [2, 3],
            "quantity": [20, 30],
            "value": [200.0, 330.0],
            "ts": [1, 2],
        }
    )

    ticks = StorageCodec.ticks_from_df(df)

    assert ticks == [
        Tick(
            ts=1,
            direction=Direction.BUY,
            price=10.0,
            lots=2,
            quantity=20,
            value=200.0,
        ),
        Tick(
            ts=2,
            direction=Direction.SELL,
            price=11.0,
            lots=3,
            quantity=30,
            value=330.0,
        ),
    ]


def test_ticks_from_df_selects_schema_columns() -> None:
    df = pl.DataFrame(
        {
            "extra": ["ignored"],
            "ts": [1],
            "value": [200.0],
            "quantity": [20],
            "lots": [2],
            "price": [10.0],
            "direction": ["BUY"],
            "datetime": ["ignored"],
        }
    )

    ticks = StorageCodec.ticks_from_df(df)

    assert ticks == [
        Tick(
            ts=1,
            direction=Direction.BUY,
            price=10.0,
            lots=2,
            quantity=20,
            value=200.0,
        )
    ]
