#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
from typing import TypeVar

import polars as pl

from avin.config import Usr
from avin.extra.term import Term

ExtremumList = TypeVar("ExtremumList")


class Extremum:  # {{{
    class Type(enum.Enum):  # {{{
        MIN = 0
        MAX = 1

        def __str__(self):  # {{{
            return self.name

        # }}}

        @classmethod  # fromStr  # {{{
        def fromStr(cls, typ: str):
            types = {
                "MIN": Extremum.Type.MIN,
                "MAX": Extremum.Type.MAX,
            }
            return types[typ]

        # }}}

    # }}}

    def __init__(self, data: dict, elist: ExtremumList):  # {{{
        self.__data = data
        self.__elist = elist

    # }}}
    def __str__(self):  # {{{
        dt = Usr.localTime(self.dt)
        s = f"{dt} {self.term} {self.type} {self.price}"
        return s

    # }}}
    def __lt__(self, other):  # operator <  # {{{
        assert isinstance(other, Extremum)

        return self.price < other.price

    # }}}
    def __le__(self, other):  # operator <=  # {{{
        assert isinstance(other, Extremum)
        return self.price <= other.price

    # }}}
    def __gt__(self, other):  # operator >  # {{{
        assert isinstance(other, Extremum)
        return self.price > other.price

    # }}}
    def __ge__(self, other):  # operator >=  # {{{
        assert isinstance(other, Extremum)
        return self.price >= other.price

    # }}}
    def __eq__(self, other):  # operator ==  # {{{
        assert isinstance(other, Extremum)
        return self.price == other.price

    # }}}
    def __sub__(self, other):  # operator -  # {{{
        assert isinstance(other, Extremum)
        return self.price - other.price

    # }}}

    @property  # dt  # {{{
    def dt(self):
        return self.__data["dt"]

    # }}}
    @property  # term  # {{{
    def term(self):
        return Term.fromStr(self.__data["term"])

    # }}}
    @property  # type  # {{{
    def type(self):
        return Extremum.Type.fromStr(self.__data["type"])

    # }}}
    @property  # price  # {{{
    def price(self):
        return self.__data["price"]

    # }}}
    @property  # elist  # {{{
    def elist(self):
        return self.__elist

    # }}}
    @property  # asset  # {{{
    def asset(self):
        return self.__elist.asset

    # }}}
    @property  # chart  # {{{
    def chart(self):
        return self.__elist.chart

    # }}}
    @property  # timeframe  # {{{
    def timeframe(self):
        return self.__elist.timeframe

    # }}}

    def isMin(self) -> bool:  # {{{
        return self.type == Extremum.Type.MIN

    # }}}
    def isMax(self) -> bool:  # {{{
        return self.type == Extremum.Type.MAX

    # }}}
    def isT1(self) -> bool:  # {{{
        return self.term == Term.T1

    # }}}
    def isT2(self) -> bool:  # {{{
        return self.term == Term.T2

    # }}}
    def isT3(self) -> bool:  # {{{
        return self.term == Term.T3

    # }}}

    @classmethod  # period  # {{{
    def period(cls, e1: Extremum, e2: Extremum) -> int:
        assert e1.dt < e2.dt

        chart = e1.chart
        bars = chart.select(e1.dt, e2.dt)
        return len(bars)

    # }}}
    @classmethod  # deltaPrice  # {{{
    def deltaPrice(cls, e1: Extremum, e2: Extremum) -> float:
        assert e1.dt < e2.dt

        delta = abs(e2.price - e1.price)
        return delta

    # }}}
    @classmethod  # deltaPercent  # {{{
    def deltaPercent(cls, e1: Extremum, e2: Extremum) -> float:
        assert e1.dt < e2.dt

        delta = abs(e2.price - e1.price)
        percent = delta / e1.price * 100

        return round(percent, 2)

    # }}}
    @classmethod  # speedPrice  # {{{
    def speedPrice(cls, e1: Extremum, e2: Extremum) -> float:
        assert e1.dt < e2.dt

        delta = abs(e2.price - e1.price)
        period = cls.period(e1, e2)
        speed = delta / period

        return round(speed, 2)

    # }}}
    @classmethod  # speedPercent  # {{{
    def speedPercent(cls, e1: Extremum, e2: Extremum) -> float:
        assert e1.dt < e2.dt

        delta = abs(e2.price - e1.price)
        percent = delta / e1.price * 100
        period = cls.period(e1, e2)
        speed = percent / period

        return round(speed, 2)

    # }}}
    @classmethod  # volumeBear  # {{{
    def volumeBear(cls, e1: Extremum, e2: Extremum) -> int:
        assert e1.dt < e2.dt

        chart = e1.chart
        bars = chart.select(e1.dt, e2.dt)
        bear = bars.filter(pl.col("open") > pl.col("close"))
        vol = bear["volume"].sum()

        return vol

    # }}}
    @classmethod  # volumeBull  # {{{
    def volumeBull(cls, e1: Extremum, e2: Extremum) -> int:
        assert e1.dt < e2.dt

        chart = e1.chart
        bars = chart.select(e1.dt, e2.dt)
        bull = bars.filter(pl.col("open") < pl.col("close"))
        vol = bull["volume"].sum()

        return vol

    # }}}
    @classmethod  # volumeTotal  # {{{
    def volumeTotal(cls, e1: Extremum, e2: Extremum) -> int:
        assert e1.dt < e2.dt

        chart = e1.chart
        bars = chart.select(e1.dt, e2.dt)
        vol = bars["volume"].sum()

        return vol

    # }}}


# }}}

if __name__ == "__main__":
    ...
