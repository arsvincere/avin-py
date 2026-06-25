# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import pytest

from avin.core.direction import Direction
from avin.core.level import Level
from avin.core.tick import Tick


def make_buy_tick(
    price: float = 100.0,
    lots: int = 10,
    value: float = 1000.0,
) -> Tick:
    return Tick(
        ts=0,
        direction=Direction.BUY,
        price=price,
        lots=lots,
        quantity=lots,
        value=value,
    )


def make_sell_tick(
    price: float = 100.0,
    lots: int = 10,
    value: float = 1000.0,
) -> Tick:
    return Tick(
        ts=0,
        direction=Direction.SELL,
        price=price,
        lots=lots,
        quantity=lots,
        value=value,
    )


def test_level_empty():
    level = Level(price=100)

    assert level.price == 100

    assert level.vol_b == 0
    assert level.vol_s == 0

    assert level.val_b == 0
    assert level.val_s == 0

    assert level.trades_b == 0
    assert level.trades_s == 0

    assert level.vol == 0
    assert level.val == 0

    assert level.delta_vol == 0
    assert level.delta_val == 0
    assert level.delta_trades == 0


def test_add_buy_tick():
    level = Level(price=100)

    tick = make_buy_tick(
        price=100,
        lots=5,
        value=500,
    )

    level.add(tick)

    assert level.vol_b == 5
    assert level.vol_s == 0

    assert level.val_b == 500
    assert level.val_s == 0

    assert level.trades_b == 1
    assert level.trades_s == 0

    assert level.vol == 5
    assert level.val == 500

    assert level.delta_vol == 5
    assert level.delta_val == 500
    assert level.delta_trades == 1


def test_add_sell_tick():
    level = Level(price=100)

    tick = make_sell_tick(
        price=100,
        lots=7,
        value=700,
    )

    level.add(tick)

    assert level.vol_b == 0
    assert level.vol_s == 7

    assert level.val_b == 0
    assert level.val_s == 700

    assert level.trades_b == 0
    assert level.trades_s == 1

    assert level.vol == 7
    assert level.val == 700

    assert level.delta_vol == -7
    assert level.delta_val == -700
    assert level.delta_trades == -1


def test_add_buy_and_sell_ticks():
    level = Level(price=100)

    level.add(
        make_buy_tick(
            price=100,
            lots=10,
            value=1000,
        )
    )

    level.add(
        make_sell_tick(
            price=100,
            lots=4,
            value=400,
        )
    )

    assert level.vol_b == 10
    assert level.vol_s == 4

    assert level.val_b == 1000
    assert level.val_s == 400

    assert level.trades_b == 1
    assert level.trades_s == 1

    assert level.vol == 14
    assert level.val == 1400

    assert level.delta_vol == 6
    assert level.delta_val == 600
    assert level.delta_trades == 0


def test_add_multiple_ticks():
    level = Level(price=100)

    level.add(make_buy_tick(price=100, lots=10, value=1000))
    level.add(make_buy_tick(price=100, lots=20, value=2000))
    level.add(make_sell_tick(price=100, lots=5, value=500))

    assert level.vol_b == 30
    assert level.vol_s == 5

    assert level.val_b == 3000
    assert level.val_s == 500

    assert level.trades_b == 2
    assert level.trades_s == 1

    assert level.vol == 35
    assert level.val == 3500

    assert level.delta_vol == 25
    assert level.delta_val == 2500
    assert level.delta_trades == 1


def test_add_tick_with_wrong_price():
    level = Level(price=100)

    tick = make_buy_tick(
        price=101,
        lots=10,
        value=1000,
    )

    with pytest.raises(ValueError):
        level.add(tick)
