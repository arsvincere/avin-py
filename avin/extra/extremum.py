#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from avin.config import Usr
from avin.core.bar import Bar
from avin.extra.term import Term


class Extremum:
    class Type(enum.Enum):  # {{{
        MIN = 0
        MAX = 1

    # }}}
    def __init__(self, typ: Extremum.Type, term: Term, bar: Bar):  # {{{
        self.__bar = bar  # сохраняем исходный бар
        self.__bar.addFlag(Bar.Type.EXTREMUM)  # вешаем бару флаг экстремум
        self.__term = term
        self.__type = typ

        # определяем и сохраняем цену в зависимости от типа (MIN/MAX)
        if typ == Extremum.Type.MAX:
            self.__price = bar.high
        elif typ == Extremum.Type.MIN:
            self.__price = bar.low

    # }}}
    def __str__(self):  # {{{
        dt = Usr.localTime(self.__bar.dt)
        ticker = self.__bar.chart.asset.ticker
        s = f"{ticker} {dt} {self.price}"
        s += " MAX" if self.isMax() else " MIN"
        s += f"{self.__term}"
        return s

    # }}}
    def __lt__(self, other):  # operator <  # {{{
        assert isinstance(other, Extremum)

        # TODO: а с float ведь тоже можно делать сравнения...
        return self.__price < other.__price

    # }}}
    def __le__(self, other):  # operator <=  # {{{
        assert isinstance(other, Extremum)
        return self.__price <= other.__price

    # }}}
    def __gt__(self, other):  # operator >  # {{{
        assert isinstance(other, Extremum)
        return self.__price > other.__price

    # }}}
    def __ge__(self, other):  # operator >=  # {{{
        assert isinstance(other, Extremum)
        return self.__price >= other.__price

    # }}}
    def __eq__(self, other):  # operator ==  # {{{
        assert isinstance(other, Extremum)
        return self.__price == other.__price

    # }}}
    def __sub__(self, other):  # operator -  # {{{
        assert isinstance(other, Extremum)
        return self.__price - other.__price

    # }}}

    @property  # dt  # {{{
    def dt(self):
        return self.__bar.dt

    # }}}
    @property  # price  # {{{
    def price(self):
        return self.__price

    # }}}
    @property  # bar   # {{{
    def bar(self) -> Bar:
        return self.__bar

    # }}}
    @property  # type  # {{{
    def type(self):
        self.__type

    # }}}
    @property  # term  # {{{
    def type(self):
        self.__term

    # }}}
    @property  # asset   # {{{
    def asset(self) -> Asset:
        return self.__bar.chart.asset

    # }}}

    def isMin(self) -> bool:  # {{{
        return self.__type == Extremum.Type.MIN

    # }}}
    def isMax(self) -> bool:  # {{{
        return self.__type == Extremum.Type.MAX

    # }}}
    def isT1(self) -> bool:  # {{{
        return self.__term == Term.T1

    # }}}
    def isT2(self) -> bool:  # {{{
        return self.__term == Term.T2

    # }}}
    def isT3(self) -> bool:  # {{{
        return self.__term == Term.T3

    # }}}

    @classmethod  # period  # {{{
    def period(cls, e1: Extremum, e2: Extremum) -> int:
        assert False, "TODO_ME"
        ### old code

        assert e1.dt < e2.dt

        chart = e1.bar.chart
        index1 = chart.getIndex(e1.bar)
        index2 = chart.getIndex(e2.bar)
        period = index2 - index1

        return period

    # }}}
    @classmethod  # deltaPrice  # {{{
    def deltaPrice(cls, e1: Extremum, e2: Extremum) -> float:
        assert False, "TODO_ME"
        ### old code
        assert e1.dt < e2.dt

        delta = abs(e2.price - e1.price)

        return delta

    # }}}
    @classmethod  # deltaPercent  # {{{
    def deltaPercent(cls, e1: Extremum, e2: Extremum) -> float:
        assert False, "TODO_ME"
        ### old code
        assert e1.dt < e2.dt

        delta = abs(e2.price - e1.price)
        percent = delta / e1.price * 100

        return round(percent, 2)

    # }}}
    @classmethod  # speedPrice  # {{{
    def speedPrice(cls, e1: Extremum, e2: Extremum) -> float:
        assert False, "TODO_ME"
        ### old code
        assert e1.dt < e2.dt

        delta = abs(e2.price - e1.price)
        period = cls.period(e1, e2)
        speed = delta / period

        return round(speed, 2)

    # }}}
    @classmethod  # speedPercent  # {{{
    def speedPercent(cls, e1: Extremum, e2: Extremum) -> float:
        assert False, "TODO_ME"
        ### old code
        assert e1.dt < e2.dt

        delta = abs(e2.price - e1.price)
        percent = delta / e1.price * 100
        period = cls.period(e1, e2)
        speed = percent / period

        return round(speed, 2)

    # }}}
    @classmethod  # volume  # {{{
    def volume(cls, e1: Extremum, e2: Extremum) -> int:
        assert False, "TODO_ME"
        ### old code
        assert e1.dt < e2.dt

        chart = e1.bar.chart
        bars = chart.getBars(begin=e1.bar, end=e2.bar)

        # не учитываем объем первого экстремума, только объем баров движения
        # от первого экстремума до второго
        trend_bars = bars[1:]

        # считаем сумму объемов
        all_volume = 0
        for bar in trend_bars:
            all_volume += bar.vol

        return all_volume

    # }}}


if __name__ == "__main__":
    ...
