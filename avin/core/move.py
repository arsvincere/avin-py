#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.core.trend import Trend
from avin.core.vawe import Vawe
from avin.utils import logger


class Move:
    def __init__(self, vawes: list[Vawe]):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.__vawes = vawes
        self.__selectTrends()

    # }}}

    def __str__(self):  # {{{
        s = f"Move {self.type.name} [{len(self)}] {self.begin} -> {self.end}"
        return s

    # }}}
    def __len__(self):  # {{{
        # в move всегда нечетное количество трендов.
        # начинается и заканчивается бычий move на бычьи тренды
        # поэтому если трендов 3 то два из них бычьи
        # если 5 // 2 + 1 = 3 тренда бычьих
        return len(self.__trends) // 2 + 1

    # }}}
    def __getitem__(self, index):  # {{{
        assert index < len(self.__trends)
        return self.__trends[index]

    # }}}
    def __iter__(self):  # {{{
        return iter(self.__trends)

    # }}}

    @property  # asset  # {{{
    def asset(self):
        return self.__vawes[0].asset

    # }}}
    @property  # chart  # {{{
    def chart(self):
        return self.__vawes[0].chart

    # }}}
    @property  # timeframe  # {{{
    def timeframe(self):
        return self.__vawes[0].timeframe

    # }}}
    @property  # term  # {{{
    def term(self):
        return self.__vawes[0].term

    # }}}
    @property  # type  # {{{
    def type(self):
        if self.isBull():
            return Trend.Type.BULL

        return Trend.Type.BEAR

    # }}}

    @property  # begin  # {{{
    def begin(self):
        first_trend = self.__trends[0]
        return first_trend.begin

    # }}}
    @property  # end  # {{{
    def end(self):
        last_trend = self.__trends[-1]
        return last_trend.end

    # }}}
    @property  # low  # {{{
    def low(self):
        if self.isBull():
            return self.begin.price

        if self.isBear():
            return self.end.price

    # }}}
    @property  # high  # {{{
    def high(self):
        if self.isBull():
            return self.end.price

        if self.isBear():
            return self.begin.price

    # }}}

    def getVawes(self):  # {{{
        return self.__vawes

    # }}}
    def getTrends(self):  # {{{
        return self.__trends

    # }}}

    def isBull(self):  # {{{
        return self.__vawes[0].isBull()

    # }}}
    def isBear(self):  # {{{
        return self.__vawes[0].isBear()

    # }}}

    def period(self) -> int:  # {{{
        return Extremum.period(self.begin, self.end)

    # }}}
    def deltaPrice(self) -> float:  # {{{
        return Extremum.deltaPrice(self.begin, self.end)

    # }}}
    def deltaPercent(self) -> float:  # {{{
        return Extremum.deltaPercent(self.begin, self.end)

    # }}}
    def speedPrice(self) -> float:  # {{{
        return Extremum.speedPrice(self.begin, self.end)

    # }}}
    def speedPercent(self) -> float:  # {{{
        return Extremum.speedPercent(self.begin, self.end)

    # }}}
    def volume(self) -> int:  # {{{
        return Extremum.volume(self.begin, self.end)

    # }}}

    def bullTrends(self) -> Trend:  # {{{
        bull_trends = list()
        for trend in self.__trends:
            if trend.isBull():
                bull_trends.append(trend)

        return bull_trends

    # }}}
    def bearTrends(self) -> Trend:  # {{{
        bear_trends = list()
        for trend in self.__trends:
            if trend.isBear():
                bear_trends.append(trend)

        return bear_trends

    # }}}
    def isStrong(self) -> bool:  # {{{
        return self.__trends[0].isStrong()

    # }}}
    def isWeak(self) -> bool:  # {{{
        return self.__trends[0].isWeak()

    # }}}

    def __selectTrends(self):  # {{{
        self.__trends = list()
        for vawe in self.__vawes:
            self.__trends.append(vawe.one)  # only one trend in vawe
        self.__trends.append(self.__vawes[-1].two)  # two trend of last vawe

        if self.isBull():
            if self.__trends[0].isBear():
                self.__trends.pop(0)
                self.__trends[0].setStrength(Trend.Strength.STRONG)
            else:
                self.__trends[0].setStrength(Trend.Strength.WEAK)

            if self.__trends[-1].isBear():
                self.__trends.pop(-1)

        elif self.isBear():
            if self.__trends[0].isBull():
                self.__trends.pop(0)
                self.__trends[0].setStrength(Trend.Strength.STRONG)
            else:
                self.__trends[0].setStrength(Trend.Strength.WEAK)

            if self.__trends[-1].isBull():
                self.__trends.pop(-1)


# }}}


if __name__ == "__main__":
    ...
