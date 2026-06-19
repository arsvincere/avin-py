# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_market_data_name():
    md = MarketData.BAR_1M
    assert md.name == "BAR_1M"
    assert str(md) == "1M"


def test_market_data_from_str():
    from_str = MarketData.from_str("BAR_10M")
    assert from_str == MarketData.BAR_10M

    from_str = MarketData.from_str("10M")
    assert from_str == MarketData.BAR_10M


def test_market_data_next_prev():
    dt = DateTime(2025, 6, 5, 12, 57, 12)
    assert MarketData.BAR_1M.prev_dt(dt) == DateTime(2025, 6, 5, 12, 57, 0)
    assert MarketData.BAR_1M.next_dt(dt) == DateTime(2025, 6, 5, 12, 58, 0)

    assert MarketData.BAR_5M.prev_dt(dt) == DateTime(2025, 6, 5, 12, 55, 0)
    assert MarketData.BAR_5M.next_dt(dt) == DateTime(2025, 6, 5, 13, 0, 0)

    assert MarketData.BAR_10M.prev_dt(dt) == DateTime(2025, 6, 5, 12, 50, 0)
    assert MarketData.BAR_10M.next_dt(dt) == DateTime(2025, 6, 5, 13, 0, 0)

    assert MarketData.BAR_1H.prev_dt(dt) == DateTime(2025, 6, 5, 12, 0, 0)
    assert MarketData.BAR_1H.next_dt(dt) == DateTime(2025, 6, 5, 13, 0, 0)

    assert MarketData.BAR_DAY.prev_dt(dt) == DateTime(2025, 6, 5, 0, 0, 0)
    assert MarketData.BAR_DAY.next_dt(dt) == DateTime(2025, 6, 6, 0, 0, 0)

    assert MarketData.BAR_WEEK.prev_dt(dt) == DateTime(2025, 6, 2, 0, 0, 0)
    assert MarketData.BAR_WEEK.next_dt(dt) == DateTime(2025, 6, 9, 0, 0, 0)

    assert MarketData.BAR_MONTH.prev_dt(dt) == DateTime(2025, 6, 1, 0, 0, 0)
    assert MarketData.BAR_MONTH.next_dt(dt) == DateTime(2025, 7, 1, 0, 0, 0)
