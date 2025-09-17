#!/usr/bin/env  python3
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

from avin.core.timeframe import TimeFrame
from avin.utils import InvalidMarketData, log


class MarketData(enum.Enum):
    """List for selecting the market data type.

    # ru
    Перечисление для выбора типа данных.
    """

    BAR_1M = enum.auto()
    BAR_10M = enum.auto()
    BAR_1H = enum.auto()
    BAR_D = enum.auto()
    BAR_W = enum.auto()
    BAR_M = enum.auto()
    TIC = enum.auto()
    TRADE_STATS = enum.auto()
    ORDER_STATS = enum.auto()
    OB_STATS = enum.auto()

    def __str__(self) -> str:
        return self.name

    def __hash__(self):
        return hash(self.name)

    def timedelta(self) -> TimeDelta:
        periods = {
            "BAR_1M": TimeDelta(minutes=1),
            "BAR_5M": TimeDelta(minutes=5),
            "BAR_10M": TimeDelta(minutes=10),
            "BAR_1H": TimeDelta(hours=1),
            "BAR_D": TimeDelta(days=1),
            "BAR_W": TimeDelta(weeks=1),
            # "M": TimeDelta(days=30),  # don't use it! it dangerous
            "TRADE_STATS": TimeDelta(minutes=5),
            "ORDER_STATS": TimeDelta(minutes=5),
            "OB_STATS": TimeDelta(minutes=5),
        }
        return periods[self.name]

    def prev_dt(self, dt: DateTime) -> DateTime:
        match self:
            case MarketData.BAR_1M:
                prev = dt.replace(second=0, microsecond=0)

            # case MarketData.BAR_5M:
            #     prev = dt.replace(second=0, microsecond=0)
            #     past = dt.minute % 5
            #     prev -= TimeDelta(minutes=past)
            case MarketData.TRADE_STATS:
                prev = dt.replace(second=0, microsecond=0)
                past = dt.minute % 5
                prev -= TimeDelta(minutes=past)
            case MarketData.ORDER_STATS:
                prev = dt.replace(second=0, microsecond=0)
                past = dt.minute % 5
                prev -= TimeDelta(minutes=past)
            case MarketData.OB_STATS:
                prev = dt.replace(second=0, microsecond=0)
                past = dt.minute % 5
                prev -= TimeDelta(minutes=past)

            case MarketData.BAR_10M:
                prev = dt.replace(second=0, microsecond=0)
                past = dt.minute % 10
                prev -= TimeDelta(minutes=past)

            case MarketData.BAR_1H:
                prev = dt.replace(minute=0, second=0, microsecond=0)

            case MarketData.BAR_D:
                prev = dt.replace(hour=0, minute=0, second=0, microsecond=0)

            case MarketData.BAR_W:
                prev = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                past = dt.weekday()
                prev -= TimeDelta(days=past)

            case MarketData.BAR_M:
                prev = dt.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )

            case _:
                log.error(f"Not implemented prev_dt: {self}")
                exit(1)

        return prev

    def next_dt(self, dt: DateTime) -> DateTime:
        match self:
            case MarketData.BAR_1M:
                next = dt.replace(second=0, microsecond=0)
                next += TimeDelta(minutes=1)

            # case MarketData.BAR_5M:
            #     next = dt.replace(second=0, microsecond=0)
            #     need_minutes = 5 - (dt.minute % 5)
            #     next += TimeDelta(minutes=need_minutes)
            case MarketData.TRADE_STATS:
                next = dt.replace(second=0, microsecond=0)
                need_minutes = 5 - (dt.minute % 5)
                next += TimeDelta(minutes=need_minutes)
            case MarketData.ORDER_STATS:
                next = dt.replace(second=0, microsecond=0)
                need_minutes = 5 - (dt.minute % 5)
                next += TimeDelta(minutes=need_minutes)
            case MarketData.OB_STATS:
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

            case MarketData.BAR_D:
                next = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                next += TimeDelta(days=1)

            case MarketData.BAR_W:
                next = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                need_days = 7 - dt.weekday()
                next += TimeDelta(days=need_days)

            case MarketData.BAR_M:
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
                log.error(f"Not implemented next_dt: {self}")
                exit(1)

        return next

    @classmethod
    def from_str(cls, string: str) -> MarketData:
        """Get enum from str.

        Args:
            string: market data name.

        Returns:
            MarketData Enum.

        Raises:
            InvalidMarketData if market data not exists.
        """
        if attr := getattr(cls, string.upper(), None):
            return attr

        raise InvalidMarketData(
            f"Invalid name. Choice from {MarketData._member_names_}"
        )

    @classmethod
    def from_timeframe(cls, tf: TimeFrame) -> MarketData:
        match tf:
            case TimeFrame.M1:
                return MarketData.BAR_1M
            case TimeFrame.M10:
                return MarketData.BAR_10M
            case TimeFrame.H1:
                return MarketData.BAR_1H
            case TimeFrame.DAY:
                return MarketData.BAR_D
            case TimeFrame.WEEK:
                return MarketData.BAR_W
            case TimeFrame.MONTH:
                return MarketData.BAR_M


if __name__ == "__main__":
    ...
