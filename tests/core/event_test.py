# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_bar_event():
    figi = "BBG004730N88"
    tf = TimeFrame.M1
    bar = Bar.from_ohlcv(100500, 10, 20, 5, 15, 100)
    e = BarEvent(figi, tf, bar)

    assert e.figi == figi
    assert e.tf == tf
    assert e.bar == bar


def test_tic_event():
    ts = 100500
    direction = Direction.BUY
    lots = 10
    price = 320.5
    value = 3205.0
    figi = "BBG004730N88"

    tic = Tic.new(ts, direction, lots, price, value)

    e = TicEvent(figi, tic)

    assert e.figi == figi
    assert e.tic == tic
