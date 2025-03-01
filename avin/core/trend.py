#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import asyncio
import enum

from avin.core._extremum import Extremum
from avin.utils import logger


class Trend:
    class Type(enum.Enum):  # {{{
        BEAR = 1
        BULL = 2

        def __str__(self):  # {{{
            return self.name

        # }}}

    # }}}
    class Strength(enum.Enum):  # {{{
        UNDEFINE = 0
        WEAK = 1
        STRONG = 2

        def __str__(self):  # {{{
            return self.name

        # }}}

    # }}}

    def __init__(self, e1: Extremum, e2: Extremum, term: Term):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__({e1}, {e2})")
        # assert e1.dt < e2.dt

        self.__e1 = e1
        self.__e2 = e2
        self.__term = term
        self.__strength = Trend.Strength.UNDEFINE

    # }}}
    def __str__(self):  # {{{
        return f"Trend {self.type.name} {self.__e1} -> {self.__e2}"

    # }}}

    @property  # begin  # {{{
    def begin(self):
        return self.__e1

    # }}}
    @property  # end  # {{{
    def end(self):
        return self.__e2

    # }}}
    @property  # asset  # {{{
    def asset(self):
        return self.__e1.bar.chart.instrument

    # }}}
    @property  # chart  # {{{
    def chart(self):
        return self.__e1.bar.chart

    # }}}
    @property  # timeframe  # {{{
    def timeframe(self):
        return self.__e1.bar.chart.timeframe

    # }}}
    @property  # term  # {{{
    def term(self):
        return self.__term

    # }}}
    @property  # type  # {{{
    def type(self):
        if self.isBull():
            return Trend.Type.BULL

        return Trend.Type.BEAR

    # }}}
    @property  # strength  # {{{
    def strength(self):
        return self.__strength

    # }}}

    def isBull(self) -> bool:  # {{{
        return self.__e2.price > self.__e1.price

    # }}}
    def isBear(self) -> bool:  # {{{
        return self.__e2.price < self.__e1.price

    # }}}
    def period(self) -> int:  # {{{
        return Extremum.period(self.__e1, self.__e2)

    # }}}
    def deltaPrice(self) -> float:  # {{{
        return Extremum.deltaPrice(self.__e1, self.__e2)

    # }}}
    def deltaPercent(self) -> float:  # {{{
        return Extremum.deltaPercent(self.__e1, self.__e2)

    # }}}
    def speedPrice(self) -> float:  # {{{
        return Extremum.speedPrice(self.__e1, self.__e2)

    # }}}
    def speedPercent(self) -> float:  # {{{
        return Extremum.speedPercent(self.__e1, self.__e2)

    # }}}
    def volume(self) -> int:  # {{{
        return Extremum.volume(self.__e1, self.__e2)

    # }}}

    def setStrength(self, strength: Trend.Strength):  # {{{
        self.__strength = strength

    # }}}
    def isStrong(self):  # {{{
        return self.__strength == Trend.Strength.STRONG

    # }}}
    def isWeak(self):  # {{{
        return self.__strength == Trend.Strength.WEAK

    # }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(TrendAnalytic.update())
