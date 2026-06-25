# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from datetime import UTC, datetime

import pytest

from avin.domain.timeframe import TimeFrame
from avin.utils.dt import dt_to_ts

# ============================================================================
# Helpers
# ============================================================================


def ts(
    year: int,
    month: int,
    day: int,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> int:
    dt = datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
        tzinfo=UTC,
    )
    return dt_to_ts(dt)


# ============================================================================
# from_str
# ============================================================================


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("S1", TimeFrame.S1),
        ("1S", TimeFrame.S1),
        ("s1", TimeFrame.S1),
        ("1s", TimeFrame.S1),
        ("M5", TimeFrame.M5),
        ("5M", TimeFrame.M5),
        ("m15", TimeFrame.M15),
        ("15m", TimeFrame.M15),
        ("H4", TimeFrame.H4),
        ("4h", TimeFrame.H4),
        ("D", TimeFrame.DAY),
        ("d", TimeFrame.DAY),
        ("W", TimeFrame.WEEK),
        ("w", TimeFrame.WEEK),
        ("M", TimeFrame.MONTH),
    ],
)
def test_from_str(value, expected):
    assert TimeFrame.from_str(value) is expected


def test_from_str_invalid():
    with pytest.raises(ValueError):
        TimeFrame.from_str("LOL")


def test_from_str_type_error():
    with pytest.raises(TypeError):
        TimeFrame.from_str(123)  # type: ignore


# ============================================================================
# seconds
# ============================================================================


@pytest.mark.parametrize(
    ("tf", "seconds"),
    [
        (TimeFrame.S1, 1),
        (TimeFrame.S5, 5),
        (TimeFrame.S10, 10),
        (TimeFrame.S30, 30),
        (TimeFrame.M1, 60),
        (TimeFrame.M5, 300),
        (TimeFrame.M15, 900),
        (TimeFrame.H1, 3600),
        (TimeFrame.H4, 14400),
        (TimeFrame.DAY, 86400),
        (TimeFrame.WEEK, 604800),
    ],
)
def test_seconds(tf, seconds):
    assert tf.seconds == seconds


def test_month_seconds_error():
    with pytest.raises(ValueError):
        _ = TimeFrame.MONTH.seconds


# ============================================================================
# nanos
# ============================================================================


def test_nanos():
    assert TimeFrame.M1.nanos == 60 * 1_000_000_000


def test_month_nanos_error():
    with pytest.raises(ValueError):
        _ = TimeFrame.MONTH.nanos


# ============================================================================
# begin_frame_ts
# ============================================================================


def test_begin_frame_ts_s1():
    value = ts(2026, 6, 25, 12, 34, 56)

    assert TimeFrame.S1.begin_frame_ts(value) == ts(2026, 6, 25, 12, 34, 56)


def test_begin_frame_ts_s5():
    value = ts(2026, 6, 25, 12, 34, 58)

    assert TimeFrame.S5.begin_frame_ts(value) == ts(2026, 6, 25, 12, 34, 55)


def test_begin_frame_ts_s10():
    value = ts(2026, 6, 25, 12, 34, 58)

    assert TimeFrame.S10.begin_frame_ts(value) == ts(2026, 6, 25, 12, 34, 50)


def test_begin_frame_ts_s30():
    value = ts(2026, 6, 25, 12, 34, 58)

    assert TimeFrame.S30.begin_frame_ts(value) == ts(2026, 6, 25, 12, 34, 30)


def test_begin_frame_ts_m1():
    value = ts(2026, 6, 25, 12, 34, 58)

    assert TimeFrame.M1.begin_frame_ts(value) == ts(2026, 6, 25, 12, 34, 0)


def test_begin_frame_ts_m5():
    value = ts(2026, 6, 25, 12, 34, 58)

    assert TimeFrame.M5.begin_frame_ts(value) == ts(2026, 6, 25, 12, 30, 0)


def test_begin_frame_ts_m15():
    value = ts(2026, 6, 25, 12, 34, 58)

    assert TimeFrame.M15.begin_frame_ts(value) == ts(2026, 6, 25, 12, 30, 0)


def test_begin_frame_ts_h1():
    value = ts(2026, 6, 25, 12, 34, 58)

    assert TimeFrame.H1.begin_frame_ts(value) == ts(2026, 6, 25, 12, 0, 0)


def test_begin_frame_ts_h4():
    value = ts(2026, 6, 25, 13, 34, 58)

    assert TimeFrame.H4.begin_frame_ts(value) == ts(2026, 6, 25, 12, 0, 0)


def test_begin_frame_ts_day():
    value = ts(2026, 6, 25, 13, 34, 58)

    assert TimeFrame.DAY.begin_frame_ts(value) == ts(2026, 6, 25, 0, 0, 0)


def test_begin_frame_ts_week():
    # Thursday 2026-06-25
    value = ts(2026, 6, 25, 13, 34, 58)

    assert TimeFrame.WEEK.begin_frame_ts(value) == ts(2026, 6, 22, 0, 0, 0)


def test_begin_frame_ts_month():
    value = ts(2026, 6, 25, 13, 34, 58)

    assert TimeFrame.MONTH.begin_frame_ts(value) == ts(2026, 6, 1, 0, 0, 0)


# ============================================================================
# end_frame_ts
# ============================================================================


def test_end_frame_ts_m1():
    value = ts(2026, 6, 25, 12, 34, 58)

    assert TimeFrame.M1.end_frame_ts(value) == ts(2026, 6, 25, 12, 35, 0)


def test_end_frame_ts_m5():
    value = ts(2026, 6, 25, 12, 34, 58)

    assert TimeFrame.M5.end_frame_ts(value) == ts(2026, 6, 25, 12, 35, 0)


def test_end_frame_ts_h4():
    value = ts(2026, 6, 25, 13, 34, 58)

    assert TimeFrame.H4.end_frame_ts(value) == ts(2026, 6, 25, 16, 0, 0)


def test_end_frame_ts_day():
    value = ts(2026, 6, 25, 13, 34, 58)

    assert TimeFrame.DAY.end_frame_ts(value) == ts(2026, 6, 26, 0, 0, 0)


def test_end_frame_ts_week():
    value = ts(2026, 6, 25, 13, 34, 58)

    assert TimeFrame.WEEK.end_frame_ts(value) == ts(2026, 6, 29, 0, 0, 0)


def test_end_frame_ts_month():
    value = ts(2026, 6, 25, 13, 34, 58)

    assert TimeFrame.MONTH.end_frame_ts(value) == ts(2026, 7, 1, 0, 0, 0)


def test_frame_border():
    value = ts(2026, 6, 25, 12, 35, 0)

    assert TimeFrame.M5.begin_frame_ts(value) == value

    assert TimeFrame.M5.end_frame_ts(value) == ts(2026, 6, 25, 12, 40, 0)
