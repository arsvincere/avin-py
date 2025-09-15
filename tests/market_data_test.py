# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_from_str():
    assert MarketData.from_str("BAR_1M") == MarketData.BAR_1M
    assert MarketData.from_str("BAR_10M") == MarketData.BAR_10M
    assert MarketData.from_str("BAR_1H") == MarketData.BAR_1H
    assert MarketData.from_str("BAR_D") == MarketData.BAR_D
    assert MarketData.from_str("BAR_W") == MarketData.BAR_W
    assert MarketData.from_str("BAR_M") == MarketData.BAR_M
    assert MarketData.from_str("TIC") == MarketData.TIC
    assert MarketData.from_str("TRADE_STATS") == MarketData.TRADE_STATS
    assert MarketData.from_str("ORDER_STATS") == MarketData.ORDER_STATS
    assert MarketData.from_str("OB_STATS") == MarketData.OB_STATS
