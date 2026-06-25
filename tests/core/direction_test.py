# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import pytest

from avin.core.direction import Direction


def test_buy_value():
    assert Direction.BUY.value == 1


def test_sell_value():
    assert Direction.SELL.value == -1


def test_str():
    assert str(Direction.BUY) == "BUY"


def test_invalid():
    with pytest.raises(ValueError):
        Direction.from_str("hold")


def test_direction_buy():
    value = 123456.99
    direction = Direction.BUY

    assert direction.name == "BUY"
    assert value * direction.value == value


def test_direction_sell():
    value = 123456.99
    direction = Direction.SELL

    assert direction.name == "SELL"
    assert value * direction.value == value * -1


def test_direction_from_str():
    assert Direction.from_str("BUY") == Direction.BUY
    assert Direction.from_str("buy") == Direction.BUY
    assert Direction.from_str("B") == Direction.BUY

    assert Direction.from_str("SELL") == Direction.SELL
    assert Direction.from_str("sell") == Direction.SELL
    assert Direction.from_str("S") == Direction.SELL


def test_direction_short_name():
    assert Direction.BUY.short_name == "B"
    assert Direction.SELL.short_name == "S"
