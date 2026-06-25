# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from datetime import UTC, datetime

import pytest

from avin.utils.dt import (
    dt_to_ts,
    next_month,
    # now_local,
    now_utc,
    prev_month,
    str_to_utc,
    ts_to_dt,
    # utc_to_local_str,
)

# =========================
# helpers
# =========================

UTC = UTC


def make_dt(year=2024, month=1, day=1):
    return datetime(year, month, day, tzinfo=UTC)


# =========================
# dt <-> ts
# =========================


def test_dt_to_ts_and_back():
    dt = make_dt(
        2024,
        1,
        1,
    )
    ts = dt_to_ts(dt)
    restored = ts_to_dt(ts)

    assert restored == dt


def test_dt_to_ts_requires_utc():
    dt = datetime.now()  # naive

    with pytest.raises(ValueError):
        dt_to_ts(dt)


# =========================
# now
# =========================


def test_now_utc_is_utc():
    dt = now_utc()
    assert dt.tzinfo == UTC


# def test_now_local_has_tz():
#     dt = now_local()
#     assert dt.tzinfo is not None


# =========================
# month navigation
# =========================


@pytest.mark.parametrize(
    "y,m,expected_y,expected_m",
    [
        (2024, 1, 2024, 2),
        (2024, 11, 2024, 12),
        (2024, 12, 2025, 1),
    ],
)
def test_next_month(y, m, expected_y, expected_m):
    dt = make_dt(y, m)
    res = next_month(dt)

    assert res.year == expected_y
    assert res.month == expected_m
    assert res.day == 1


@pytest.mark.parametrize(
    "y,m,expected_y,expected_m",
    [
        (2024, 2, 2024, 1),
        (2024, 1, 2023, 12),
    ],
)
def test_prev_month(y, m, expected_y, expected_m):
    dt = make_dt(y, m)
    res = prev_month(dt)

    assert res.year == expected_y
    assert res.month == expected_m
    assert res.day == 1


# =========================
# parsing
# =========================


def test_str_to_utc_with_naive_input():
    # interpreted as MSK (+3) then converted to UTC
    s = "2024-01-01T03:00:00"

    dt = str_to_utc(s)

    assert dt.tzinfo == UTC
    assert dt.hour == 0  # 03 MSK -> 00 UTC


# =========================
# formatting
# =========================


# def test_utc_to_local_str_contains_string():
#     dt = datetime(2024, 1, 1, tzinfo=UTC)
#     s = utc_to_local_str(dt)
#
#     assert isinstance(s, str)
#     assert len(s) > 0
