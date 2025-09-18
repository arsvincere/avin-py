# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_new():
    ts = 100500
    direction = Direction.BUY
    lots = 1
    price = 325.15
    value = 3251.5

    tic = Tic.new(ts, direction, lots, price, value)

    assert tic.ts == ts
    assert tic.direction == direction
    assert tic.lots == lots
    assert tic.price == price
    assert tic.value == value

    assert tic.is_buy()
    assert not tic.is_sell()
