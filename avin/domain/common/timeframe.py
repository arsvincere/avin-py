# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from enum import StrEnum

from avin.utils.dt import (
    ONE_DAY,
    ONE_HOUR,
    ONE_MINUTE,
    ONE_SECOND,
    TimeDelta,
    dt_to_ts,
    next_month,
    ts_to_dt,
)


class TimeFrame(StrEnum):
    S1 = "1S"
    S5 = "5S"
    S10 = "10S"
    S30 = "30S"

    M1 = "1M"
    M5 = "5M"
    M15 = "15M"

    H1 = "1H"
    H4 = "4H"

    DAY = "D"
    WEEK = "W"
    MONTH = "M"

    @property
    def nanos(self) -> int:
        match self:
            case TimeFrame.MONTH:
                raise ValueError("MONTH has no fixed nanos")
            case _:
                return self.seconds * 1_000_000_000

    @property
    def seconds(self) -> int:
        match self:
            case TimeFrame.S1:
                return 1
            case TimeFrame.S5:
                return 5
            case TimeFrame.S10:
                return 10
            case TimeFrame.S30:
                return 30
            case TimeFrame.M1:
                return 60
            case TimeFrame.M5:
                return 300
            case TimeFrame.M15:
                return 900
            case TimeFrame.H1:
                return 3600
            case TimeFrame.H4:
                return 14400
            case TimeFrame.DAY:
                return 86400
            case TimeFrame.WEEK:
                return 604800
            case TimeFrame.MONTH:
                raise ValueError("MONTH has no fixed seconds")
            case _:
                raise ValueError("...")

    @property
    def timedelta(self) -> TimeDelta:
        match self:
            case TimeFrame.MONTH:
                raise ValueError("MONTH has no fixed timedelta")
            case _:
                return TimeDelta(seconds=self.seconds)

    def begin_frame_ts(self, ts: int) -> int:
        """Previous"""

        dt = ts_to_dt(ts)

        match self:
            case TimeFrame.S1:
                dt = dt.replace(microsecond=0)
            case TimeFrame.S5:
                dt = dt.replace(microsecond=0)
                past_seconds = dt.second % 5
                dt -= past_seconds * ONE_SECOND
            case TimeFrame.S10:
                dt = dt.replace(microsecond=0)
                past_seconds = dt.second % 10
                dt -= past_seconds * ONE_SECOND
            case TimeFrame.S30:
                dt = dt.replace(microsecond=0)
                past_seconds = dt.second % 30
                dt -= past_seconds * ONE_SECOND

            case TimeFrame.M1:
                dt = dt.replace(microsecond=0, second=0)
            case TimeFrame.M5:
                dt = dt.replace(microsecond=0, second=0)
                past_minutes = dt.minute % 5
                dt -= past_minutes * ONE_MINUTE
            case TimeFrame.M15:
                dt = dt.replace(microsecond=0, second=0)
                past_minutes = dt.minute % 15
                dt -= past_minutes * ONE_MINUTE

            case TimeFrame.H1:
                dt = dt.replace(microsecond=0, second=0, minute=0)
            case TimeFrame.H4:
                dt = dt.replace(microsecond=0, second=0, minute=0)
                past_hours = dt.hour % 4
                dt -= past_hours * ONE_HOUR

            case TimeFrame.DAY:
                dt = dt.replace(microsecond=0, second=0, minute=0, hour=0)
            case TimeFrame.WEEK:
                past_days = dt.weekday()
                dt -= past_days * ONE_DAY
                dt = dt.replace(microsecond=0, second=0, minute=0, hour=0)
            case TimeFrame.MONTH:
                dt = dt.replace(
                    microsecond=0, second=0, minute=0, hour=0, day=1
                )
            case _:
                raise NotImplementedError()

        return dt_to_ts(dt)

    def end_frame_ts(self, ts: int) -> int:
        """Next"""

        floor = self.begin_frame_ts(ts)

        match self:
            case TimeFrame.MONTH:
                dt = ts_to_dt(floor)
                dt = next_month(dt)
                return dt_to_ts(dt)
            case _:
                return floor + self.nanos

    @classmethod
    def from_str(cls, value: str) -> TimeFrame:
        if not isinstance(value, str):
            raise TypeError(value)

        s = value.upper()
        if s in cls.__members__:
            return cls[s]

        for item in cls:
            if item.value == s:
                return item

        raise ValueError(
            f"Invalid timeframe name: '{value}'. "
            f"Choice from {[m.value for m in cls]}"
        )
