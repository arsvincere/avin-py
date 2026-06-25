# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta

import pytest

from avin.domain.market_data import MarketData


def test_str():
    assert MarketData.BAR_1M.name == "BAR_1M"
    assert str(MarketData.BAR_1M) == "BAR_1M"
    assert str(MarketData.BAR_DAY) == "BAR_DAY"
    assert str(MarketData.TIC) == "TIC"


def test_from_str_by_name():
    assert MarketData.from_str("BAR_1M") is MarketData.BAR_1M
    assert MarketData.from_str("bar_1m") is MarketData.BAR_1M

    assert MarketData.from_str("BAR_DAY") is MarketData.BAR_DAY
    assert MarketData.from_str("bar_day") is MarketData.BAR_DAY

    assert MarketData.from_str("TRADE_STATS") is MarketData.TRADE_STATS


def test_from_str_invalid_type():
    with pytest.raises(TypeError):
        MarketData.from_str(None)

    with pytest.raises(TypeError):
        MarketData.from_str(123)


def test_from_str_invalid_name():
    with pytest.raises(ValueError):
        MarketData.from_str("foo")


def test_timedelta():
    assert MarketData.BAR_1M.timedelta == TimeDelta(minutes=1)
    assert MarketData.BAR_5M.timedelta == TimeDelta(minutes=5)
    assert MarketData.BAR_10M.timedelta == TimeDelta(minutes=10)
    assert MarketData.BAR_1H.timedelta == TimeDelta(hours=1)

    assert MarketData.BAR_DAY.timedelta == TimeDelta(days=1)
    assert MarketData.BAR_WEEK.timedelta == TimeDelta(weeks=1)

    assert MarketData.TRADE_STATS.timedelta == TimeDelta(minutes=5)
    assert MarketData.ORDER_STATS.timedelta == TimeDelta(minutes=5)
    assert MarketData.OB_STATS.timedelta == TimeDelta(minutes=5)


def test_timedelta_month():
    with pytest.raises(NotImplementedError):
        _ = MarketData.BAR_MONTH.timedelta


def test_floor_dt():
    dt = DateTime(2025, 6, 5, 12, 57, 12)

    assert MarketData.BAR_1M.floor_dt(dt) == DateTime(2025, 6, 5, 12, 57, 0)

    assert MarketData.BAR_5M.floor_dt(dt) == DateTime(2025, 6, 5, 12, 55, 0)

    assert MarketData.BAR_10M.floor_dt(dt) == DateTime(2025, 6, 5, 12, 50, 0)

    assert MarketData.BAR_1H.floor_dt(dt) == DateTime(2025, 6, 5, 12, 0, 0)

    assert MarketData.BAR_DAY.floor_dt(dt) == DateTime(2025, 6, 5, 0, 0, 0)

    assert MarketData.BAR_WEEK.floor_dt(dt) == DateTime(2025, 6, 2, 0, 0, 0)

    assert MarketData.BAR_MONTH.floor_dt(dt) == DateTime(2025, 6, 1, 0, 0, 0)


def test_floor_dt_stats():
    dt = DateTime(2025, 6, 5, 12, 57, 12)

    expected = DateTime(2025, 6, 5, 12, 55, 0)

    assert MarketData.TRADE_STATS.floor_dt(dt) == expected
    assert MarketData.ORDER_STATS.floor_dt(dt) == expected
    assert MarketData.OB_STATS.floor_dt(dt) == expected


def test_next_dt():
    dt = DateTime(2025, 6, 5, 12, 57, 12)

    assert MarketData.BAR_1M.next_dt(dt) == DateTime(2025, 6, 5, 12, 58, 0)

    assert MarketData.BAR_5M.next_dt(dt) == DateTime(2025, 6, 5, 13, 0, 0)

    assert MarketData.BAR_10M.next_dt(dt) == DateTime(2025, 6, 5, 13, 0, 0)

    assert MarketData.BAR_1H.next_dt(dt) == DateTime(2025, 6, 5, 13, 0, 0)

    assert MarketData.BAR_DAY.next_dt(dt) == DateTime(2025, 6, 6, 0, 0, 0)

    assert MarketData.BAR_WEEK.next_dt(dt) == DateTime(2025, 6, 9, 0, 0, 0)

    assert MarketData.BAR_MONTH.next_dt(dt) == DateTime(2025, 7, 1, 0, 0, 0)


def test_next_dt_stats():
    dt = DateTime(2025, 6, 5, 12, 57, 12)

    expected = DateTime(2025, 6, 5, 13, 0, 0)

    assert MarketData.TRADE_STATS.next_dt(dt) == expected
    assert MarketData.ORDER_STATS.next_dt(dt) == expected
    assert MarketData.OB_STATS.next_dt(dt) == expected


def test_next_dt_month_year_rollover():
    dt = DateTime(2025, 12, 15, 12, 0, 0)

    assert MarketData.BAR_MONTH.next_dt(dt) == DateTime(2026, 1, 1, 0, 0, 0)


def test_floor_dt_is_idempotent():
    dt = DateTime(2025, 6, 5, 12, 57, 12)

    for md in (
        MarketData.BAR_1M,
        MarketData.BAR_5M,
        MarketData.BAR_10M,
        MarketData.BAR_1H,
        MarketData.BAR_DAY,
        MarketData.BAR_WEEK,
        MarketData.BAR_MONTH,
        MarketData.TRADE_STATS,
        MarketData.ORDER_STATS,
        MarketData.OB_STATS,
    ):
        floor = md.floor_dt(dt)

        assert md.floor_dt(floor) == floor


def test_dt_is_inside_interval():
    dt = DateTime(2025, 6, 5, 12, 57, 12)

    for md in (
        MarketData.BAR_1M,
        MarketData.BAR_5M,
        MarketData.BAR_10M,
        MarketData.BAR_1H,
        MarketData.BAR_DAY,
        MarketData.BAR_WEEK,
        MarketData.BAR_MONTH,
    ):
        floor = md.floor_dt(dt)
        next_ = md.next_dt(dt)

        assert floor <= dt
        assert dt < next_
