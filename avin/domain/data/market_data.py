# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import enum

from avin.utils.dt import DateTime, TimeDelta


class MarketData(enum.StrEnum):
    """Enum for selecting market data type."""

    BAR_1M = "BAR_1M"
    BAR_5M = "BAR_5M"
    BAR_10M = "BAR_10M"
    BAR_15M = "BAR_15M"
    BAR_1H = "BAR_1H"
    BAR_4H = "BAR_4H"
    BAR_DAY = "BAR_DAY"
    BAR_WEEK = "BAR_WEEK"
    BAR_MONTH = "BAR_MONTH"
    TICK = "TICK"
    BOOK = "BOOK"
    TRADE_STATS = "TRADE_STATS"
    ORDER_STATS = "ORDER_STATS"
    OB_STATS = "OB_STATS"

    @property
    def timedelta(self) -> TimeDelta:
        match self:
            case MarketData.BAR_1M:
                return TimeDelta(minutes=1)
            case (
                MarketData.BAR_5M
                | MarketData.TRADE_STATS
                | MarketData.ORDER_STATS
                | MarketData.OB_STATS
            ):
                return TimeDelta(minutes=5)
            case MarketData.BAR_10M:
                return TimeDelta(minutes=10)
            case MarketData.BAR_15M:
                return TimeDelta(minutes=15)
            case MarketData.BAR_1H:
                return TimeDelta(hours=1)
            case MarketData.BAR_4H:
                return TimeDelta(hours=4)
            case MarketData.BAR_DAY:
                return TimeDelta(days=1)
            case MarketData.BAR_WEEK:
                return TimeDelta(weeks=1)
            case MarketData.BAR_MONTH:
                raise NotImplementedError(
                    "Month period has no fixed timedelta"
                )
            case _:
                raise NotImplementedError(self)

    def floor_dt(self, dt: DateTime) -> DateTime:
        match self:
            case MarketData.BAR_1M:
                prev = dt.replace(second=0, microsecond=0)

            case (
                MarketData.BAR_5M
                | MarketData.TRADE_STATS
                | MarketData.ORDER_STATS
                | MarketData.OB_STATS
            ):
                prev = dt.replace(second=0, microsecond=0)
                past = dt.minute % 5
                prev -= TimeDelta(minutes=past)
            case MarketData.BAR_10M:
                prev = dt.replace(second=0, microsecond=0)
                past = dt.minute % 10
                prev -= TimeDelta(minutes=past)
            case MarketData.BAR_15M:
                prev = dt.replace(second=0, microsecond=0)
                past = dt.minute % 15
                prev -= TimeDelta(minutes=past)

            case MarketData.BAR_1H:
                prev = dt.replace(minute=0, second=0, microsecond=0)
            case MarketData.BAR_4H:
                prev = dt.replace(minute=0, second=0, microsecond=0)
                past = dt.hour % 4
                prev -= TimeDelta(hours=past)

            case MarketData.BAR_DAY:
                prev = dt.replace(hour=0, minute=0, second=0, microsecond=0)

            case MarketData.BAR_WEEK:
                prev = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                past = dt.weekday()
                prev -= TimeDelta(days=past)

            case MarketData.BAR_MONTH:
                prev = dt.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )

            case _:
                raise NotImplementedError(self)

        return prev

    def next_dt(self, dt: DateTime) -> DateTime:
        match self:
            case MarketData.BAR_1M:
                next = dt.replace(second=0, microsecond=0)
                next += TimeDelta(minutes=1)

            case (
                MarketData.BAR_5M
                | MarketData.TRADE_STATS
                | MarketData.ORDER_STATS
                | MarketData.OB_STATS
            ):
                next = dt.replace(second=0, microsecond=0)
                need_minutes = 5 - (dt.minute % 5)
                next += TimeDelta(minutes=need_minutes)
            case MarketData.BAR_10M:
                next = dt.replace(second=0, microsecond=0)
                need_minutes = 10 - (dt.minute % 10)
                next += TimeDelta(minutes=need_minutes)
            case MarketData.BAR_15M:
                next = dt.replace(second=0, microsecond=0)
                need_minutes = 15 - (dt.minute % 15)
                next += TimeDelta(minutes=need_minutes)

            case MarketData.BAR_1H:
                next = dt.replace(minute=0, second=0, microsecond=0)
                next += TimeDelta(hours=1)
            case MarketData.BAR_4H:
                next = dt.replace(minute=0, second=0, microsecond=0)
                need_hours = 4 - (dt.hour % 4)
                next += TimeDelta(hours=need_hours)

            case MarketData.BAR_DAY:
                next = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                next += TimeDelta(days=1)

            case MarketData.BAR_WEEK:
                next = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                need_days = 7 - dt.weekday()
                next += TimeDelta(days=need_days)

            case MarketData.BAR_MONTH:
                if dt.month == 12:
                    next = dt.replace(
                        year=dt.year + 1,
                        month=1,
                        day=1,
                        hour=0,
                        minute=0,
                        second=0,
                        microsecond=0,
                    )
                else:
                    next = dt.replace(
                        month=dt.month + 1,
                        day=1,
                        hour=0,
                        minute=0,
                        second=0,
                        microsecond=0,
                    )

            case _:
                raise NotImplementedError(self)

        return next

    @classmethod
    def from_str(cls, value: str) -> MarketData:
        if not isinstance(value, str):
            raise TypeError(value)

        s = value.upper()
        if s in cls.__members__:
            return cls[s]

        for item in cls:
            if item.value == s:
                return item

        raise ValueError(
            f"Invalid market data name: '{value}'. "
            f"Choice from {[m.value for m in cls]}"
        )

    @classmethod
    def all_bar_kind(cls) -> list[MarketData]:
        return [
            cls.BAR_1M,
            cls.BAR_5M,
            cls.BAR_10M,
            cls.BAR_15M,
            cls.BAR_1H,
            cls.BAR_4H,
            cls.BAR_DAY,
            cls.BAR_WEEK,
            cls.BAR_MONTH,
        ]
