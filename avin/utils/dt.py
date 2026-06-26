# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum
from datetime import UTC
from datetime import date as Date
from datetime import datetime as DateTime
from datetime import time as Time
from datetime import timedelta as TimeDelta
from datetime import timezone as TimeZone

__all__ = (
    "DAY_BEGIN",
    "DAY_END",
    "Date",
    "DateTime",
    "FIVE_MINUTE",
    "ONE_DAY",
    "ONE_HOUR",
    "ONE_MINUTE",
    "ONE_MONTH",
    "ONE_SECOND",
    "ONE_WEEK",
    "ONE_YEAR",
    "TEN_MINUTE",
    "Time",
    "TimeDelta",
    "TimeZone",
    "UTC",
    "WeekDays",
    "dt_to_ts",
    "extract_range_dates",
    "next_month",
    "now_utc",
    "prev_month",
    "str_to_utc",
    "ts_to_dt",
    # "now_local",
    # "utc_to_local_str",
)


def dt_to_ts(dt: DateTime) -> int:
    if dt.tzinfo != UTC:
        raise ValueError("dt must be UTC datetime")

    return int(dt.timestamp() * 1_000_000_000)


def ts_to_dt(ts_nanos: int) -> DateTime:
    return DateTime.fromtimestamp(ts_nanos / 1_000_000_000, UTC)


def now_utc() -> DateTime:
    return DateTime.now(UTC)


# def now_local() -> DateTime:
#     return DateTime.now().astimezone(cfg.local_timezone)


def next_month(dt: DateTime) -> DateTime:
    year = dt.year + (dt.month // 12)
    month = (dt.month % 12) + 1

    return dt.replace(
        year=year,
        month=month,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def prev_month(dt: DateTime) -> DateTime:
    year = dt.year - 1 if dt.month == 1 else dt.year
    month = 12 if dt.month == 1 else dt.month - 1

    return dt.replace(
        year=year,
        month=month,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def str_to_utc(s: str) -> DateTime:
    """
    Parse ISO string assumed in UTC+3 (MSK-like) and convert to UTC.
    """
    msk = TimeZone(TimeDelta(hours=3), "MSK")

    dt = DateTime.fromisoformat(s)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=msk)

    return dt.astimezone(UTC)


# def utc_to_local_str(dt: DateTime) -> str:
#     local = dt.astimezone(cfg.local_timezone)
#     return local.strftime(cfg.dt_fmt)


def extract_range_dates(begin: DateTime, end: DateTime) -> list[Date]:
    last_date = (end - TimeDelta(microseconds=1)).date()

    dates = list()
    current = begin.date()
    while current <= last_date:
        dates.append(current)
        current += ONE_DAY

    return dates


class WeekDays(enum.Enum):
    Mon = 0
    Tue = 1
    Wed = 2
    Thu = 3
    Fri = 4
    Sat = 5
    Sun = 6

    @staticmethod
    def isWorkday(day_number: int):
        return day_number < 5

    @staticmethod
    def isHoliday(day_number: int):
        return day_number in (5, 6)


ONE_SECOND = TimeDelta(seconds=1)
ONE_MINUTE = TimeDelta(minutes=1)
FIVE_MINUTE = TimeDelta(minutes=5)
TEN_MINUTE = TimeDelta(minutes=10)
ONE_HOUR = TimeDelta(hours=1)
ONE_DAY = TimeDelta(days=1)
ONE_WEEK = TimeDelta(weeks=1)
ONE_MONTH = TimeDelta(days=30)
ONE_YEAR = TimeDelta(days=365)

DAY_BEGIN = Time(0, 0, tzinfo=UTC)
DAY_END = Time(23, 59, tzinfo=UTC)
