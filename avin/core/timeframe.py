# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum
from datetime import timedelta as TimeDelta

from avin.utils import dt_to_ts, next_month, ts_to_dt


class TimeFrame(enum.Enum):
    M1 = enum.auto()
    M10 = enum.auto()
    H1 = enum.auto()
    DAY = enum.auto()
    WEEK = enum.auto()
    MONTH = enum.auto()

    def __str__(self):
        return self.name

    @property
    def name(self):
        match self:
            case TimeFrame.M1:
                return "1M"
            case TimeFrame.M10:
                return "10M"
            case TimeFrame.H1:
                return "1H"
            case TimeFrame.DAY:
                return "D"
            case TimeFrame.WEEK:
                return "W"
            case TimeFrame.MONTH:
                return "M"

    def timedelta(self) -> TimeDelta:
        match self:
            case TimeFrame.M1:
                return TimeDelta(minutes=1)
            case TimeFrame.M10:
                return TimeDelta(minutes=10)
            case TimeFrame.H1:
                return TimeDelta(hours=1)
            case TimeFrame.DAY:
                return TimeDelta(days=1)
            case TimeFrame.WEEK:
                return TimeDelta(weeks=1)
            case TimeFrame.MONTH:
                return TimeDelta(days=30)

    def nanos(self) -> int:
        match self:
            case TimeFrame.M1:
                return 1 * 60 * 1_000_000_000
            case TimeFrame.M10:
                return 10 * 60 * 1_000_000_000
            case TimeFrame.H1:
                return 60 * 60 * 1_000_000_000
            case TimeFrame.DAY:
                return 24 * 60 * 60 * 1_000_000_000
            case TimeFrame.WEEK:
                return 7 * 24 * 60 * 60 * 1_000_000_000
            case TimeFrame.MONTH:
                return 30 * 24 * 60 * 60 * 1_000_000_000

    def next_ts(self, ts: int) -> int:
        dt = ts_to_dt(ts)
        dt = dt.replace(microsecond=0, second=0)

        match self:
            case TimeFrame.M1:
                dt += TimeDelta(minutes=1)
            case TimeFrame.M10:
                need_minutes = 10 - dt.minute % 10
                dt += TimeDelta(minutes=need_minutes)
            case TimeFrame.H1:
                dt = dt.replace(minute=0) + TimeDelta(hours=1)
            case TimeFrame.DAY:
                dt = dt.replace(minute=0, hour=0) + TimeDelta(days=1)
            case TimeFrame.WEEK:
                need_days = 6 - dt.weekday()
                dt = dt.replace(hour=0, minute=0) + TimeDelta(days=need_days)
            case TimeFrame.MONTH:
                dt = next_month(dt)

        return dt_to_ts(dt)

    def prev_ts(self, ts: int) -> int:
        raise NotImplementedError()


if __name__ == "__main__":
    ...
