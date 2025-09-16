# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from datetime import UTC
from datetime import datetime as DateTime

import polars as pl

from avin import *


def test_dt_ts():
    dt = DateTime(2025, 9, 14, 12, 0, 0, tzinfo=UTC)

    ts = dt_to_ts(dt)
    from_ts = ts_to_dt(ts)

    assert dt == from_ts


def test_next_month():
    # at middle of year
    dt = DateTime(2025, 9, 14, 12, 0, 0, tzinfo=UTC)
    next = next_month(dt)
    expected = DateTime(2025, 10, 1, 0, 0, 0, tzinfo=UTC)
    assert expected == next

    # at the end of year
    dt = DateTime(2025, 12, 14, 12, 0, 0, tzinfo=UTC)
    next = next_month(dt)
    expected = DateTime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
    assert expected == next


def test_prev_month():
    # at middle of year
    dt = DateTime(2025, 9, 14, 12, 0, 0, tzinfo=UTC)
    next = prev_month(dt)
    expected = DateTime(2025, 8, 1, 0, 0, 0, tzinfo=UTC)
    assert expected == next

    # at the begin of year
    dt = DateTime(2025, 1, 14, 12, 0, 0, tzinfo=UTC)
    next = prev_month(dt)
    expected = DateTime(2024, 12, 1, 0, 0, 0, tzinfo=UTC)
    assert expected == next


def test_str_to_utc():
    s = "2025-09-14 12:30"

    dt = str_to_utc(s)
    expected = DateTime(2025, 9, 14, 9, 30, 0, tzinfo=UTC)
    assert expected == dt


def test_utc_to_local():
    dt = DateTime(2025, 9, 14, 12, 39, 22, tzinfo=UTC)

    local = utc_to_local(dt)
    expected = "2025-09-14 15:39:22"
    assert local == expected


def test_filter_dt():
    dt1 = DateTime(2025, 1, 16, 17, 43, 00, tzinfo=UTC)
    dt2 = DateTime(2025, 1, 16, 17, 44, 00, tzinfo=UTC)  # begin
    dt3 = DateTime(2025, 1, 16, 17, 45, 00, tzinfo=UTC)
    dt4 = DateTime(2025, 1, 16, 17, 46, 00, tzinfo=UTC)  # end
    dt5 = DateTime(2025, 1, 16, 17, 47, 00, tzinfo=UTC)

    ts1 = dt_to_ts(dt1)
    ts2 = dt_to_ts(dt2)
    ts3 = dt_to_ts(dt3)
    ts4 = dt_to_ts(dt4)
    ts5 = dt_to_ts(dt5)

    df = pl.DataFrame({"ts_nanos": [ts1, ts2, ts3, ts4, ts5]})

    df = filter_dt(dt2, dt4, df)
    assert len(df) == 2
