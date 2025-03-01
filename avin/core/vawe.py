#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import asyncio

from avin.core._extremum import Extremum
from avin.core.trend import Trend


class Vawe:  # {{{
    def __init__(self, t1: Trend, t2: Trend):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__({t1}, {t2})")

        self.__t1 = t1
        self.__t2 = t2

    # }}}
    def __str__(self):  # {{{
        return f"Vawe {self.type.name} {self.__t1} || {self.__t2}"

    # }}}

    @property  # asset  # {{{
    def asset(self):
        return self.__t1.asset

    # }}}
    @property  # chart  # {{{
    def chart(self):
        return self.__t1.chart

    # }}}
    @property  # timeframe  # {{{
    def timeframe(self):
        return self.__t1.timeframe

    # }}}
    @property  # term  # {{{
    def term(self):
        return self.__t1.term

    # }}}
    @property  # type  # {{{
    def type(self):
        if self.isBull():
            return Trend.Type.BULL

        return Trend.Type.BEAR

    # }}}
    @property  # one  # {{{
    def one(self):
        return self.__t1

    # }}}
    @property  # two  # {{{
    def two(self):
        return self.__t2

    # }}}
    @property  # begin  # {{{
    def begin(self):
        return self.__t1.begin

    # }}}
    @property  # center  # {{{
    def center(self):
        return self.__t1.end

    # }}}
    @property  # end  # {{{
    def end(self):
        return self.__t2.end

    # }}}

    def isBull(self) -> bool:  # {{{
        """Например:
        то есть есть 3 экстремума: 100 90 110
        дельты:
        d1 = 90 - 100 = -10
        d2 = 110 - 90 = 20
        D = -10 + 20 = 10

        Или по другому через первую и последнюю точку:
        D = 110 - 100 = 10

        Очевидно что в любом случае получится одно и тоже.
        Поэтому проще будет посмотреть дельту по началу и концу
        меньше вычислений.
        """

        return self.__t2.end.price > self.__t1.begin.price

    # }}}
    def isBear(self) -> bool:  # {{{
        return self.__t2.end.price < self.__t1.begin.price

    # }}}
    def isPeak(self) -> bool:  # {{{
        if self.__t1.isBull():
            return True

        return False

    # }}}
    def isCave(self) -> bool:  # {{{
        if self.__t1.isBear():
            return True

        return False

    # }}}
    def isStrong(self) -> bool:  # {{{
        if self.isPeak() and self.isBull() or self.isCave() and self.isBear():
            return True

        return False

    # }}}
    def isBroken(self) -> bool:  # {{{
        if self.isPeak() and self.isBear() or self.isCave() and self.isBull():
            return True

        return False

    # }}}

    def period(self) -> int:  # {{{
        return Extremum.period(self.__t1.begin, self.__t2.end)

    # }}}
    def deltaPrice(self) -> float:  # {{{
        return Extremum.deltaPrice(self.__t1.begin, self.__t2.end)

    # }}}
    def deltaPercent(self) -> float:  # {{{
        return Extremum.deltaPercent(self.__t1.begin, self.__t2.end)

    # }}}
    def speedPrice(self) -> float:  # {{{
        return Extremum.speedPrice(self.__t1.begin, self.__t2.end)

    # }}}
    def speedPercent(self) -> float:  # {{{
        return Extremum.speedPercent(self.__t1.begin, self.__t2.end)

    # }}}
    def volume(self) -> int:  # {{{
        return Extremum.volume(self.__t1.begin, self.__t2.end)

    # }}}

    def bullTrend(self) -> Trend:  # {{{
        if self.__t1.isBull():
            return self.__t1

        if self.__t2.isBull():
            return self.__t2

        assert False, "WTF???"

    # }}}
    def bearTrend(self) -> Trend:  # {{{
        if self.__t1.isBear():
            return self.__t1

        if self.__t2.isBear():
            return self.__t2

        assert False, "WTF???"

    # }}}


# }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(VaweAnalytic.update())
