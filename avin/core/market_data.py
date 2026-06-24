# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta


class MarketData(enum.StrEnum):
    """Enum for selet what data type to download."""

    BAR_1M = "BAR_1M"
    BAR_5M = "BAR_5M"
    BAR_10M = "BAR_10M"
    BAR_1H = "BAR_1H"
    BAR_DAY = "BAR_DAY"
    BAR_WEEK = "BAR_WEEK"
    BAR_MONTH = "BAR_MONTH"
    TIC = "TIC"
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
            case MarketData.BAR_1H:
                return TimeDelta(hours=1)
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

            case MarketData.BAR_1H:
                prev = dt.replace(minute=0, second=0, microsecond=0)

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

            case MarketData.BAR_1H:
                next = dt.replace(minute=0, second=0, microsecond=0)
                next += TimeDelta(hours=1)

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
    def from_str(cls, string: str) -> MarketData:
        if not isinstance(string, str):
            raise TypeError(string)

        s = string.upper()
        if s in cls.__members__:
            return cls[s]

        for item in cls:
            if item.value == s:
                return item

        raise ValueError(
            f"Invalid market data name: '{string}'. "
            f"Choice from {MarketData._member_names_}"
        )

    @classmethod
    def all_bar_kind(
        self,
    ) -> list[MarketData]:
        return [
            self.BAR_1M,
            self.BAR_5M,
            self.BAR_10M,
            self.BAR_1H,
            self.BAR_DAY,
            self.BAR_WEEK,
            self.BAR_MONTH,
        ]


if __name__ == "__main__":
    ...
