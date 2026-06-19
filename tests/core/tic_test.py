# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_tic_is_buy():
    ts = 100500
    direction = Direction.Buy
    lots = 10
    price = 320.5
    value = lots * price

    tic = Tic(ts, direction, lots, price, value)
    assert tic.isBuy()


def test_tic_is_sell():
    ts = 100500
    direction = Direction.Sell
    lots = 10
    price = 320.5
    value = lots * price

    tic = Tic(ts, direction, lots, price, value)
    assert tic.isSell()
