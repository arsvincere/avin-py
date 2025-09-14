#!/usr/bin/env python3
# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from datetime import UTC
from datetime import datetime as DateTime

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
