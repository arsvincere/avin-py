#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
from typing import Optional, TypeVar

import polars as pl

from avin.config import Usr
from avin.core.range import Range
from avin.utils import DateTime

Chart = TypeVar("Chart")


class Bar:
    class Type(enum.Flag):  # {{{
        UNDEFINE = 0
        # BEAR = 1
        # BULL = 2
        INSIDE = 4
        OVERFLOW = 8
        OUTSIDE = 16
        EXTREMUM = 32

    # }}}

    def __init__(self, data: dict, chart=None):  # {{{
        self.__data = data
        self.__chart = chart

    # }}}
    def __str__(self):  # {{{
        usr_dt = self.dt + Usr.TIME_DIF
        str_dt = usr_dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"Bar {str_dt} O={self.open} H={self.high} "
            f"L={self.low} C={self.close} V={self.volume} "
        )
        return string

    # }}}
    def __contains__(self, price: float) -> bool:  # {{{
        return self.low <= price <= self.high

    # }}}

    @property  # dt  # {{{
    def dt(self) -> DateTime:
        return self.__data["dt"]

    # }}}
    @property  # open  # {{{
    def open(self) -> float:
        return self.__data["open"]

    # }}}
    @property  # high  # {{{
    def high(self) -> float:
        return self.__data["high"]

    # }}}
    @property  # low  # {{{
    def low(self) -> float:
        return self.__data["low"]

    # }}}
    @property  # close  # {{{
    def close(self) -> float:
        return self.__data["close"]

    # }}}
    @property  # volume  # {{{
    def volume(self) -> int:
        return self.__data["volume"]

    # }}}
    @property  # data  # {{{
    def data(self) -> dict:
        return self.__data

    # }}}

    @property  # full  # {{{
    def full(self) -> Range:
        return Range(self.low, self.high, Range.Type.FULL, self)

    # }}}
    @property  # body  # {{{
    def body(self) -> Range:
        if self.open < self.close:
            return Range(self.open, self.close, Range.Type.BODY, self)
        else:
            return Range(self.close, self.open, Range.Type.BODY, self)

    # }}}
    @property  # lower  # {{{
    def lower(self) -> Range:
        if self.isBull():
            return Range(self.low, self.open, Range.Type.LOWER, self)
        else:
            return Range(self.low, self.close, Range.Type.LOWER, self)

    # }}}
    @property  # upper  # {{{
    def upper(self) -> Range:
        if self.isBull():
            return Range(self.close, self.high, Range.Type.UPPER, self)
        else:
            return Range(self.open, self.high, Range.Type.UPPER, self)

    # }}}
    @property  # chart  # {{{
    def chart(self):
        return self.__chart

    # }}}

    def setChart(self, chart) -> None:  # {{{
        self.__chart = chart

    # }}}
    def addFlag(self, flag: Bar.Type) -> None:  # {{{
        assert isinstance(flag, Bar.Type)
        self.__flags |= flag

    # }}}
    def delFlag(self, flag: Bar.Type) -> None:  # {{{
        assert isinstance(flag, Bar.Type)
        self.__flags &= ~flag

    # }}}
    def isBull(self) -> bool:  # {{{
        return self.open < self.close

    # }}}
    def isBear(self) -> bool:  # {{{
        return self.open > self.close

    # }}}
    def isInside(self) -> bool:  # {{{
        return self.__flags & Bar.Type.INSIDE == Bar.Type.INSIDE

    # }}}
    def isOverflow(self) -> bool:  # {{{
        return self.__flags & Bar.Type.OVERFLOW == Bar.Type.OVERFLOW

    # }}}
    def isOutside(self) -> bool:  # {{{
        return self.__flags & Bar.Type.OUTSIDE == Bar.Type.OUTSIDE

    # }}}
    def isExtremum(self) -> bool:  # {{{
        return self.__flags & Bar.Type.EXTREMUM == Bar.Type.EXTREMUM

    # }}}

    def to_df(self):  # {{{
        return pl.DataFrame(self.__data)

    # }}}

    @classmethod  # new  # {{{
    def new(
        cls,
        dt: DateTime,
        open: float,
        high: float,
        low: float,
        close: float,
        vol: int,
        chart: Optional[Chart] = None,
    ):
        dct = {
            "dt": dt,
            "open": open,
            "high": high,
            "low": low,
            "close": close,
            "volume": vol,
        }
        bar = cls(dct, chart)
        return bar

    # }}}
    @classmethod  # fromRecord  # {{{
    def fromRecord(cls, record: asyncpg.Record, chart=None):
        bar = cls(dict(record), chart)
        return bar

    # }}}


if __name__ == "__main__":
    ...
