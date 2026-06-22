# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from datetime import UTC
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta
from datetime import timezone as TimeZone

from avin.utils.conf import cfg

# =========================
# Time conversion
# =========================


def dt_to_ts(dt: DateTime) -> int:
    if dt.tzinfo != UTC:
        raise ValueError("dt must be UTC datetime")

    return int(dt.timestamp() * 1_000_000_000)


def ts_to_dt(ts_nanos: int) -> DateTime:
    return DateTime.fromtimestamp(ts_nanos / 1_000_000_000, UTC)


# =========================
# Current time
# =========================


def now_utc() -> DateTime:
    return DateTime.now(UTC)


def now_local() -> DateTime:
    return DateTime.now().astimezone(cfg.local_timezone)


# =========================
# Month navigation
# =========================


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


# =========================
# Parsing
# =========================


def str_to_utc(s: str) -> DateTime:
    """
    Parse ISO string assumed in UTC+3 (MSK-like) and convert to UTC.
    """
    msk = TimeZone(TimeDelta(hours=3), "MSK")

    dt = DateTime.fromisoformat(s)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=msk)

    return dt.astimezone(UTC)


# =========================
# Formatting
# =========================


def utc_to_local_str(dt: DateTime) -> str:
    local = dt.astimezone(cfg.local_timezone)
    return local.strftime(cfg.dt_fmt)
