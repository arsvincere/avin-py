# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import pytest

from avin.core.direction import Direction
from avin.core.tick import Tick
from avin.utils.dt import ts_to_dt


def test_tick_init():
    tick = Tick(
        ts=1710000000,
        direction=Direction.BUY,
        price=100.5,
        lots=2,
        quantity=20,
        value=2010.0,
    )

    assert tick.ts == 1710000000
    assert tick.direction == Direction.BUY
    assert tick.price == 100.5
    assert tick.lots == 2
    assert tick.quantity == 20
    assert tick.value == 2010.0


def test_tick():
    buy = Tick(
        1710000000,
        Direction.BUY,
        100.0,
        1,
        10,
        1000.0,
    )

    sell = Tick(
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


def test_tick_dt():
    tick = Tick(
        1710000000,
        Direction.BUY,
        100.0,
        1,
        10,
        1000.0,
    )

    assert tick.dt == ts_to_dt(1710000000)


def test_tick_str():
    tick = Tick(
        1710000000,
        Direction.BUY,
        100.0,
        2,
        10,
        1000.0,
    )

    s = str(tick)

    assert "Tick:" in s
    assert "BUY" in s
    assert "2x10x100.0" in s


def test_tick_immutable():
    tick = Tick(
        1710000000,
        Direction.BUY,
        100.0,
        1,
        10,
        1000.0,
    )

    with pytest.raises(Exception):
        tick.price = 999.0
