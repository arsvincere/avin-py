# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_from_str():
    assert Direction.from_str("B") == Direction.BUY
    assert Direction.from_str("BUY") == Direction.BUY
    assert Direction.from_str("S") == Direction.SELL
    assert Direction.from_str("SELL") == Direction.SELL


def test_short_name():
    assert Direction.BUY.short_name() == "B"
    assert Direction.SELL.short_name() == "S"
