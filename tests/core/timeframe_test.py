# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from datetime import timedelta as TimeDelta

from avin import *


def test_name():
    assert TimeFrame.M1.name == "1M"
    assert TimeFrame.M10.name == "10M"
    assert TimeFrame.H1.name == "1H"
    assert TimeFrame.DAY.name == "D"
    assert TimeFrame.WEEK.name == "W"
    assert TimeFrame.MONTH.name == "M"


def test_timedelta():
    assert TimeDelta(minutes=1) == TimeFrame.M1.timedelta()
    assert TimeDelta(minutes=10) == TimeFrame.M10.timedelta()
    assert TimeDelta(minutes=60) == TimeFrame.H1.timedelta()
    assert TimeDelta(days=1) == TimeFrame.DAY.timedelta()
    assert TimeDelta(days=7) == TimeFrame.WEEK.timedelta()
    assert TimeDelta(days=30) == TimeFrame.MONTH.timedelta()


def test_nanos():
    assert TimeFrame.M1.nanos() == 1 * 60 * 1_000_000_000
    assert TimeFrame.M10.nanos() == 10 * 60 * 1_000_000_000
    assert TimeFrame.H1.nanos() == 60 * 60 * 1_000_000_000
    assert TimeFrame.DAY.nanos() == 24 * 60 * 60 * 1_000_000_000
    assert TimeFrame.WEEK.nanos() == 7 * 24 * 60 * 60 * 1_000_000_000
    assert TimeFrame.MONTH.nanos() == 30 * 24 * 60 * 60 * 1_000_000_000


def test_market_data():
    assert TimeFrame.M1.market_data() == MarketData.BAR_1M
    assert TimeFrame.M10.market_data() == MarketData.BAR_10M
    assert TimeFrame.H1.market_data() == MarketData.BAR_1H
    assert TimeFrame.DAY.market_data() == MarketData.BAR_D
    assert TimeFrame.WEEK.market_data() == MarketData.BAR_W
    assert TimeFrame.MONTH.market_data() == MarketData.BAR_M


def test_next_ts():
    dt = str_to_utc("2025-09-15 16:02")
    ts = dt_to_ts(dt)
    next_ts = TimeFrame.M1.next_ts(ts)
    next_dt = ts_to_dt(next_ts)
    assert next_dt == str_to_utc("2025-09-15 16:03")

    dt = str_to_utc("2025-09-15 16:02")
    ts = dt_to_ts(dt)
    next_ts = TimeFrame.M10.next_ts(ts)
    next_dt = ts_to_dt(next_ts)
    assert next_dt == str_to_utc("2025-09-15 16:10")

    dt = str_to_utc("2025-09-15 16:02")
    ts = dt_to_ts(dt)
    next_ts = TimeFrame.H1.next_ts(ts)
    next_dt = ts_to_dt(next_ts)
    assert next_dt == str_to_utc("2025-09-15 17:00")

    dt = str_to_utc("2025-09-15 16:02")
    ts = dt_to_ts(dt)
    next_ts = TimeFrame.DAY.next_ts(ts)
    next_dt = ts_to_dt(next_ts)
    assert next_dt == str_to_utc("2025-09-16 03:00")

    dt = str_to_utc("2025-09-15 16:02")
    ts = dt_to_ts(dt)
    next_ts = TimeFrame.WEEK.next_ts(ts)
    next_dt = ts_to_dt(next_ts)
    assert next_dt == str_to_utc("2025-09-21 03:00")

    dt = str_to_utc("2025-09-15 16:02")
    ts = dt_to_ts(dt)
    next_ts = TimeFrame.MONTH.next_ts(ts)
    next_dt = ts_to_dt(next_ts)
    assert next_dt == str_to_utc("2025-10-01 03:00")
