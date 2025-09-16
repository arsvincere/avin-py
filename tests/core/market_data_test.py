# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from datetime import datetime as DateTime

from avin import *


def test_name():
    md = MarketData.BAR_1M
    assert md.name == "BAR_1M"
    assert str(md) == "BAR_1M"


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


def test_from_timeframe():
    assert MarketData.from_timeframe(TimeFrame.M1) == MarketData.BAR_1M
    assert MarketData.from_timeframe(TimeFrame.M1) == MarketData.BAR_1M
    assert MarketData.from_timeframe(TimeFrame.M10) == MarketData.BAR_10M
    assert MarketData.from_timeframe(TimeFrame.H1) == MarketData.BAR_1H
    assert MarketData.from_timeframe(TimeFrame.DAY) == MarketData.BAR_D
    assert MarketData.from_timeframe(TimeFrame.WEEK) == MarketData.BAR_W
    assert MarketData.from_timeframe(TimeFrame.MONTH) == MarketData.BAR_M


def test_next_prev():
    dt = DateTime(2025, 6, 5, 12, 57, 12)
    assert MarketData.BAR_1M.prev_dt(dt) == DateTime(2025, 6, 5, 12, 57, 0)
    assert MarketData.BAR_1M.next_dt(dt) == DateTime(2025, 6, 5, 12, 58, 0)

    # assert MarketData.BAR_5M.prev_dt(dt) == DateTime(2025, 6, 5, 12, 55, 0)
    # assert MarketData.BAR_5M.next_dt(dt) == DateTime(2025, 6, 5, 13, 0, 0)

    assert MarketData.BAR_10M.prev_dt(dt) == DateTime(2025, 6, 5, 12, 50, 0)
    assert MarketData.BAR_10M.next_dt(dt) == DateTime(2025, 6, 5, 13, 0, 0)

    assert MarketData.BAR_1H.prev_dt(dt) == DateTime(2025, 6, 5, 12, 0, 0)
    assert MarketData.BAR_1H.next_dt(dt) == DateTime(2025, 6, 5, 13, 0, 0)

    assert MarketData.BAR_D.prev_dt(dt) == DateTime(2025, 6, 5, 0, 0, 0)
    assert MarketData.BAR_D.next_dt(dt) == DateTime(2025, 6, 6, 0, 0, 0)

    assert MarketData.BAR_W.prev_dt(dt) == DateTime(2025, 6, 2, 0, 0, 0)
    assert MarketData.BAR_W.next_dt(dt) == DateTime(2025, 6, 9, 0, 0, 0)

    assert MarketData.BAR_M.prev_dt(dt) == DateTime(2025, 6, 1, 0, 0, 0)
    assert MarketData.BAR_M.next_dt(dt) == DateTime(2025, 7, 1, 0, 0, 0)
