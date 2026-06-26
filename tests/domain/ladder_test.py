# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import pytest

from avin.domain.common.direction import Direction
from avin.domain.footprint.ladder import Ladder
from avin.domain.raw.tick import Tick


def buy_tick(
    *,
    price: float,
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


def sell_tick(
    *,
    price: float,
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


def test_empty_ladder():
    ladder = Ladder()

    assert ladder.is_empty
    assert len(ladder) == 0

    assert ladder.sorted_prices == []
    assert ladder.sorted_levels == []


def test_empty_ladder_high():
    ladder = Ladder()

    with pytest.raises(ValueError, match="ladder is empty"):
        _ = ladder.high


def test_empty_ladder_low():
    ladder = Ladder()

    with pytest.raises(ValueError, match="ladder is empty"):
        _ = ladder.low


def test_add_first_tick_creates_level():
    ladder = Ladder()

    ladder.add(
        buy_tick(
            price=100.0,
            lots=5,
            value=500.0,
        )
    )

    assert not ladder.is_empty
    assert len(ladder) == 1

    assert 100.0 in ladder

    level = ladder.get(100.0)

    assert level is not None
    assert level.price == 100.0
    assert level.vol_b == 5


def test_add_ticks_same_price():
    ladder = Ladder()

    ladder.add(
        buy_tick(
            price=100.0,
            lots=10,
            value=1000.0,
        )
    )

    ladder.add(
        sell_tick(
            price=100.0,
            lots=4,
            value=400.0,
        )
    )

    assert len(ladder) == 1

    level = ladder.get(100.0)

    assert level is not None

    assert level.vol_b == 10
    assert level.vol_s == 4

    assert level.trades_b == 1
    assert level.trades_s == 1


def test_add_ticks_different_prices():
    ladder = Ladder()

    ladder.add(buy_tick(price=102.0))
    ladder.add(buy_tick(price=100.0))
    ladder.add(buy_tick(price=101.0))

    assert len(ladder) == 3

    assert 100.0 in ladder
    assert 101.0 in ladder
    assert 102.0 in ladder


def test_get_unknown_price_returns_none():
    ladder = Ladder()

    ladder.add(buy_tick(price=100.0))

    assert ladder.get(999.0) is None


def test_high_low():
    ladder = Ladder()

    ladder.add(buy_tick(price=102.0))
    ladder.add(buy_tick(price=100.0))
    ladder.add(buy_tick(price=101.0))

    assert ladder.high == 102.0
    assert ladder.low == 100.0


def test_prices_are_sorted():
    ladder = Ladder()

    ladder.add(buy_tick(price=102.0))
    ladder.add(buy_tick(price=100.0))
    ladder.add(buy_tick(price=101.0))

    assert ladder.sorted_prices == [
        100.0,
        101.0,
        102.0,
    ]


def test_sorted_levels_are_sorted_by_price():
    ladder = Ladder()

    ladder.add(buy_tick(price=102.0))
    ladder.add(buy_tick(price=100.0))
    ladder.add(buy_tick(price=101.0))

    prices = [level.price for level in ladder.sorted_levels]

    assert prices == [
        100.0,
        101.0,
        102.0,
    ]


def test_iter_returns_levels_sorted_by_price():
    ladder = Ladder()

    ladder.add(buy_tick(price=102.0))
    ladder.add(buy_tick(price=100.0))
    ladder.add(buy_tick(price=101.0))

    prices = [level.price for level in ladder]

    assert prices == [
        100.0,
        101.0,
        102.0,
    ]
