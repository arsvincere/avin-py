# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import polars as pl
import pytest

from avin.core.direction import Direction
from avin.core.tic import Tic
from avin.utils.dt import ts_to_dt


def test_tic_init():
    tic = Tic(
        ts=1710000000,
        direction=Direction.BUY,
        price=100.5,
        lots=2,
        quantity=20,
        value=2010.0,
    )

    assert tic.ts == 1710000000
    assert tic.direction == Direction.BUY
    assert tic.price == 100.5
    assert tic.lots == 2
    assert tic.quantity == 20
    assert tic.value == 2010.0


def test_tic_is_buy_sell():
    buy = Tic(
        1710000000,
        Direction.BUY,
        100.0,
        1,
        10,
        1000.0,
    )

    sell = Tic(
        1710000000,
        Direction.SELL,
        100.0,
        1,
        10,
        1000.0,
    )

    assert buy.is_buy()
    assert not buy.is_sell()

    assert sell.is_sell()
    assert not sell.is_buy()


def test_tic_dt():
    tic = Tic(
        1710000000,
        Direction.BUY,
        100.0,
        1,
        10,
        1000.0,
    )

    assert tic.dt == ts_to_dt(1710000000)


def test_tic_str():
    tic = Tic(
        1710000000,
        Direction.BUY,
        100.0,
        2,
        10,
        1000.0,
    )

    s = str(tic)

    assert "Tic:" in s
    assert "BUY" in s
    assert "2x10x100.0" in s


def test_tic_to_df():
    tic = Tic(
        1710000000,
        Direction.BUY,
        100.5,
        2,
        20,
        2010.0,
    )

    df = tic.to_df()

    assert df.height == 1

    row = df.row(0, named=True)

    assert row["direction"] == "B"
    assert row["price"] == 100.5
    assert row["lots"] == 2
    assert row["quantity"] == 20
    assert row["value"] == 2010.0
    assert row["ts"] == 1710000000


def test_tic_from_df():
    df = pl.DataFrame(
        {
            "datetime": ["dummy"],
            "direction": ["S"],
            "price": [99.9],
            "lots": [3],
            "quantity": [30],
            "value": [2997.0],
            "ts": [1710000001],
        }
    )

    tics = Tic.from_df(df)

    assert len(tics) == 1

    tic = tics[0]

    assert tic.direction == Direction.SELL
    assert tic.price == 99.9
    assert tic.lots == 3
    assert tic.quantity == 30
    assert tic.value == 2997.0
    assert tic.ts == 1710000001


def test_tic_roundtrip_df():
    tic = Tic(
        1710000000,
        Direction.BUY,
        123.45,
        7,
        70,
        8641.5,
    )

    restored = Tic.from_df(tic.to_df())

    assert restored == [tic]


def test_tic_schema():
    schema = Tic.schema()

    assert schema["datetime"] == pl.String
    assert schema["direction"] == pl.String
    assert schema["price"] == pl.Float64
    assert schema["lots"] == pl.Int64
    assert schema["quantity"] == pl.Int64
    assert schema["value"] == pl.Float64
    assert schema["ts"] == pl.Int64


def test_tic_immutable():
    tic = Tic(
        1710000000,
        Direction.BUY,
        100.0,
        1,
        10,
        1000.0,
    )

    with pytest.raises(Exception):
        tic.price = 999.0
