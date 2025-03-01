#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from avin.core._extremum import Extremum
from avin.core.bar import Bar
from avin.core.chart import Chart
from avin.core.move import Move
from avin.core.term import Term
from avin.core.trend import Trend
from avin.core.vawe import Vawe


class ExtremumList:
    def __init__(self, chart: Chart):  # {{{
        self.__chart = chart
        self.__shortterm = list()
        self.__midterm = list()
        self.__longterm = list()
        self.update()

    # }}}

    @property  # sterm  # {{{
    def sterm(self):
        return self.__shortterm

    # }}}
    @property  # mterm  # {{{
    def mterm(self):
        return self.__midterm

    # }}}
    @property  # lterm  # {{{
    def lterm(self):
        return self.__longterm

    # }}}
    @property  # chart  # {{{
    def chart(self) -> Chart:
        return self.__chart

    # }}}

    def update(self) -> None:  # {{{
        self.__markInsideDays()
        self.__markOutsideDays()
        self.__markOverflowDays()
        self.__updateShorttem()
        self.__updateMidterm()
        self.__updateLongterm()

    # }}}

    # def sMax(self):  # {{{
    #     max_of_sterm = -1
    #     for extr in self.__shortterm:
    #         if extr.isMax():
    #             max_of_sterm = max(extr.price, max_of_sterm)
    #
    #     if max_of_sterm == -1:
    #         return None
    #
    #     return max_of_sterm
    #
    # # }}}

    def extr(self, term: Term, n: int) -> Extremum | None:  # {{{
        """
        self.__shortterm self.__midterm self.__longterm
        хранят экстремумы по порядку, то есть 0 это самый старый,
        мне же нужно по n=1 выдать последний экстремум, n=2
        предпоследний и тп. То есть получается:
        n = 1  ->  self.__shortterm[-1]
        n = 2  ->  self.__shortterm[-2]
        ...
        При этом n=0 - не имеет смысла - текущий экстремум не
        известен еще. Или... см ТODO. А пока на 0 поставлю
        временно ассерт.
        """
        # TODO:
        # а вообще-то текущий экстремум - это отдельная задача
        # которую надо будет порешать. Текущий экстремум это
        # highestHigh / lowestLow среди баров которые пришли
        # после последнего зафиксированного экстремума.
        # Это для шорт терм. А для m-l там сложнее
        # Там уже нужно смотреть не просто на бары - а на
        # экстремумы. Хотя можно и на бары но это будет
        # очень долго... надо на экстремумы смотреть.
        assert n != 0

        match term:
            case Term.STERM:
                if n > len(self.__shortterm):
                    return None
                return self.__shortterm[-n]

            case Term.MTERM:
                if n > len(self.__midterm):
                    return None
                return self.__midterm[-n]

            case Term.LTERM:
                if n > len(self.__longterm):
                    return None
                return self.__longterm[-n]

    # }}}
    def trend(self, term: Term, n: int) -> Trend | None:  # {{{
        match term:
            case Term.STERM:
                return self.__sTrend(n)
            case Term.MTERM:
                return self.__mTrend(n)
            case Term.LTERM:
                return self.__lTrend(n)

    # }}}
    def vawe(self, term: Term, n: int) -> Vawe | None:  # {{{
        match term:
            case Term.STERM:
                return self.__sVawe(n)
            case Term.MTERM:
                return self.__mVawe(n)
            case Term.LTERM:
                return self.__lVawe(n)

    # }}}
    def move(self, term: Term, n: int) -> Move | None:  # {{{
        match term:
            case Term.STERM:
                return self.__sMove(n)
            case Term.MTERM:
                return self.__mMove(n)
            case Term.LTERM:
                return self.__lMove(n)

    # }}}
    def getAllTrends(self, term: Term) -> list[Trend]:  # {{{
        match term:
            case Term.STERM:
                return self.__getAllSTrends()
            case Term.MTERM:
                return self.__getAllMTrends()
            case Term.LTERM:
                return self.__getAllLTrends()

    # }}}
    def getAllVawes(self, term: Term) -> list[Vawe]:  # {{{
        match term:
            case Term.STERM:
                return self.__getAllSVawes()
            case Term.MTERM:
                return self.__getAllMVawes()
            case Term.LTERM:
                return self.__getAllLVawes()

    # }}}
    def getAllMoves(self, term: Term) -> list[Move]:  # {{{
        match term:
            case Term.STERM:
                return self.__getAllSMoves()
            case Term.MTERM:
                return self.__getAllMMoves()
            case Term.LTERM:
                return self.__getAllLMoves()

    # }}}

    def __isOverflowOf(self, this, of) -> bool:  # {{{
        return this.high > of or this.low < of.low

    # }}}
    def __isInsideOf(self, this, of) -> bool:  # {{{
        return this.high <= of.high and this.low >= of.low

    # }}}
    def __isOutsideOf(self, this, of) -> bool:  # {{{
        return this.high >= of.high and this.low <= of.low

    # }}}
    def __markInsideDays(self):  # {{{
        bars = self.__chart.getBars()
        if len(bars) < 2:
            return

        i = 0
        previous = bars[i]
        previous.delFlag(Bar.Type.INSIDE)
        i += 1

        while i < len(bars):
            current_bar = bars[i]
            if self.__isInsideOf(current_bar, previous):
                current_bar.addFlag(Bar.Type.INSIDE)
            else:
                current_bar.delFlag(Bar.Type.INSIDE)
                previous = current_bar
            i += 1

    # }}}
    def __markOutsideDays(self):  # {{{
        bars = self.__chart.getBars()
        if len(bars) < 2:
            return

        i = 0
        previous = bars[i]
        previous.delFlag(Bar.Type.OUTSIDE)
        i += 1

        while i < len(bars):
            current_bar = bars[i]
            if self.__isOutsideOf(current_bar, previous):
                current_bar.addFlag(Bar.Type.OUTSIDE)
            else:
                current_bar.delFlag(Bar.Type.OUTSIDE)
                previous = current_bar
            i += 1

    # }}}
    def __markOverflowDays(self):  # {{{
        bars = self.__chart.getBars()
        for bar in bars:
            if not bar.isInside() and not bar.isOutside():
                bar.addFlag(Bar.Type.OVERFLOW)

    # }}}
    def __skipInsideOutside(self):  # {{{
        # NOTE:
        # если их скипать получается гораздо больше неадеквата
        # чем если их оставить.
        # Самая жесть после СВО, там инсайд потом пол года идет.
        # Лучше пусть шорт-терм чаще колеблется, и больше смотреть
        # на m-term, l-term. Чисто визуально мне кажется это лучше
        # сейчас будет работать.
        # Отключаю эту функцию временно, но не удаляю пока.
        return self.__chart.getBars()

        bars = self.__chart.getBars()
        without_inside_outside = list()
        for bar in bars:
            if bar.isInside() or bar.isOutside():
                continue
            else:
                without_inside_outside.append(bar)

        return without_inside_outside

    # }}}
    def __updateShorttem(self):  # {{{
        self.__shortterm.clear()
        bars = self.__skipInsideOutside()
        if len(bars) < 3:
            return

        i = 1
        count = len(bars) - 1
        while i < count:
            left = bars[i - 1]
            bar = bars[i]
            right = bars[i + 1]
            if left.high < bar.high > right.high:
                e = Extremum(Extremum.Type.MAX | Extremum.Type.SHORTTERM, bar)
                self.__shortterm.append(e)
            if left.low > bar.low < right.low:
                e = Extremum(Extremum.Type.MIN | Extremum.Type.SHORTTERM, bar)
                self.__shortterm.append(e)
            i += 1

        self.__popRepeatedExtr(self.__shortterm)

    # }}}
    def __updateMidterm(self):  # {{{
        self.__midterm.clear()

        short_extr = self.__shortterm
        if len(short_extr) < 5:
            return

        i = 2
        count = len(short_extr) - 2
        while i < count:
            left = short_extr[i - 2]
            e = short_extr[i]
            right = short_extr[i + 2]
            if (
                e.isMax()
                and left < e > right
                or e.isMin()
                and left > e < right
            ):
                e.addFlag(Extremum.Type.MIDTERM)
                self.__midterm.append(e)
            i += 1

        self.__popRepeatedExtr(self.__midterm)

    # }}}
    def __updateLongterm(self):  # {{{
        self.__longterm.clear()

        mid_extr = self.__midterm
        if len(mid_extr) < 5:
            return

        i = 2
        count = len(mid_extr) - 2
        while i < count:
            left = mid_extr[i - 2]
            e = mid_extr[i]
            right = mid_extr[i + 2]
            if (
                e.isMax()
                and (left < e > right)
                or e.isMin()
                and (left > e < right)
            ):
                e.addFlag(Extremum.Type.LONGTERM)
                self.__longterm.append(e)
            i += 1

        self.__popRepeatedExtr(self.__longterm)

    # }}}
    def __popRepeatedExtr(self, elist):  # {{{
        if len(elist) < 2:
            return

        i = 0
        previous = elist[i]
        i += 1
        while i < len(elist):
            current = elist[i]
            if current.isMax() and previous.isMax():  # double max
                if current > previous:
                    elist.pop(i - 1)
                    previous = current
                    continue
                else:
                    elist.pop(i)
                    continue
            elif current.isMin() and previous.isMin():  # double min
                if current < previous:
                    elist.pop(i - 1)
                    previous = current
                    continue
                else:
                    elist.pop(i)
                    continue
            elif (
                (  # перегиб бычьего, next min > prev max
                    current.isMin()
                    and previous.isMax()
                    and current > previous
                )
                or (  # перегиб медвежьего, next max < prev min
                    current.isMax()
                    and previous.isMin()
                    and current < previous
                )
                or current.dt == previous.dt  # double extr in one bar
            ):
                elist.pop(i)
                continue

            previous = current
            i += 1

    # }}}

    def __sTrend(self, n) -> Trend | None:  # {{{
        """
        Тренд 0 - это текущий незавершенный тренд
        Тренд 1 - это прошлый тренд
        Тренд 2 - это позапрошлый тренд и тд
        """
        assert n >= 0

        if n > (len(self.__shortterm) - 1):
            return None

        t = Extremum.Type
        if n == 0:
            e1 = self.__shortterm[-1]

            # TODO: тут нужно не просто last_bar брать как сейчас
            # а смотреть на самое экстримальное значение среди баров
            # от прошлого экстремума до последнего исторического бара
            # self.__chart.getBars(e1.bar, self.__chart.last)
            last_bar = self.__chart.last

            if e1.isMax():
                e2 = Extremum(t.MIN | t.SHORTTERM, last_bar)
            else:
                e2 = Extremum(t.MAX | t.SHORTTERM, last_bar)

            trend = Trend(e1, e2, Term.STERM)
            return trend

        # n >= 1
        e1 = self.__shortterm[-n - 1]
        e2 = self.__shortterm[-n]
        trend = Trend(e1, e2, Term.STERM)
        return trend

    # }}}
    def __mTrend(self, n) -> Trend | None:  # {{{
        assert n >= 0

        if n > (len(self.__midterm) - 1):
            return None

        t = Extremum.Type
        if n == 0:
            e1 = self.__midterm[-1]

            last_bar = self.__chart.last
            if e1.isMax():
                e2 = Extremum(t.MIN | t.SHORTTERM, last_bar)
            else:
                e2 = Extremum(t.MAX | t.SHORTTERM, last_bar)

            trend = Trend(e1, e2, Term.MTERM)
            return trend

        # n >= 1
        e1 = self.__midterm[-n - 1]
        e2 = self.__midterm[-n]
        trend = Trend(e1, e2, Term.MTERM)
        return trend

    # }}}
    def __lTrend(self, n) -> Trend | None:  # {{{
        assert n >= 0

        if n > (len(self.__longterm) - 1):
            return None

        t = Extremum.Type
        if n == 0:
            e1 = self.__longterm[-1]

            last_bar = self.__chart.last
            if e1.isMax():
                e2 = Extremum(t.MIN | t.SHORTTERM, last_bar)
            else:
                e2 = Extremum(t.MAX | t.SHORTTERM, last_bar)

            trend = Trend(e1, e2, Term.LTERM)
            return trend

        # n >= 1
        e1 = self.__longterm[-n - 1]
        e2 = self.__longterm[-n]
        trend = Trend(e1, e2, Term.LTERM)
        return trend

    # }}}
    def __sVawe(self, n) -> Vawe | None:  # {{{
        """
        Волна 0 состоит из тренда 1 и тренда 0
        Волна 1 состоит из тренда 2 и тренда 1
        Волна 2 состоит из тренда 3 и тренда 2
        """
        assert n >= 0

        t1 = self.__sTrend(n + 1)
        t2 = self.__sTrend(n)
        if t1 is None:
            return None

        return Vawe(t1, t2)

    # }}}
    def __mVawe(self, n) -> Vawe | None:  # {{{
        """
        Волна 0 состоит из тренда 1 и тренда 0
        Волна 1 состоит из тренда 2 и тренда 1
        Волна 2 состоит из тренда 3 и тренда 2
        """
        assert n >= 0

        t1 = self.__mTrend(n + 1)
        t2 = self.__mTrend(n)
        if t1 is None:
            return None

        return Vawe(t1, t2)

    # }}}
    def __lVawe(self, n) -> Vawe | None:  # {{{
        """
        Волна 0 состоит из тренда 1 и тренда 0
        Волна 1 состоит из тренда 2 и тренда 1
        Волна 2 состоит из тренда 3 и тренда 2
        """
        assert n >= 0

        t1 = self.__lTrend(n + 1)
        t2 = self.__lTrend(n)
        if t1 is None:
            return None

        return Vawe(t1, t2)

    # }}}
    def __sMove(self, n) -> Move | None:  # {{{
        assert n >= 0
        moves = self.__getAllSMoves()
        if not moves:
            return None

        if len(moves) < n:
            return None

        return moves[n]

    # }}}
    def __mMove(self, n) -> Move | None:  # {{{
        assert n >= 0
        moves = self.__getAllMMoves()
        if not moves:
            return None

        if len(moves) < n:
            return None

        return moves[n]

    # }}}
    def __lMove(self, n) -> Move | None:  # {{{
        assert n >= 0
        moves = self.__getAllLMoves()
        if not moves:
            return None

        if len(moves) < n:
            return None

        return moves[n]

    # }}}

    def __getAllSTrends(self) -> list[Trend]:  # {{{
        all_trends = list()

        n = 0
        trend = self.__sTrend(n)
        while trend is not None:
            all_trends.append(trend)
            n += 1
            trend = self.__sTrend(n)

        all_trends.reverse()
        return all_trends

    # }}}
    def __getAllMTrends(self) -> list[Trend]:  # {{{
        all_trends = list()

        n = 0
        trend = self.__mTrend(n)
        while trend is not None:
            all_trends.append(trend)
            n += 1
            trend = self.__mTrend(n)

        all_trends.reverse()
        return all_trends

    # }}}
    def __getAllLTrends(self) -> list[Trend]:  # {{{
        all_trends = list()

        n = 0
        trend = self.__lTrend(n)
        while trend is not None:
            all_trends.append(trend)
            n += 1
            trend = self.__lTrend(n)

        all_trends.reverse()
        return all_trends

    # }}}
    def __getAllSVawes(self) -> list[Vawe]:  # {{{
        all_vawes = list()

        n = 0
        vawe = self.__sVawe(n)
        while vawe is not None:
            all_vawes.append(vawe)
            n += 1
            vawe = self.__sVawe(n)

        all_vawes.reverse()
        return all_vawes

    # }}}
    def __getAllMVawes(self) -> list[Vawe]:  # {{{
        all_vawes = list()

        n = 0
        vawe = self.__mVawe(n)
        while vawe is not None:
            all_vawes.append(vawe)
            n += 1
            vawe = self.__mVawe(n)

        all_vawes.reverse()
        return all_vawes

    # }}}
    def __getAllLVawes(self) -> list[Vawe]:  # {{{
        all_vawes = list()

        n = 0
        vawe = self.__lVawe(n)
        while vawe is not None:
            all_vawes.append(vawe)
            n += 1
            vawe = self.__lVawe(n)

        all_vawes.reverse()
        return all_vawes

    # }}}

    def __getAllSMoves(self) -> list[Move]:  # {{{
        vawes = self.__getAllSVawes()

        all_moves = list()
        i = 0
        while i < len(vawes):
            first = i
            last = i
            while last < len(vawes):
                if vawes[first].type == vawes[last].type:
                    last += 1
                else:
                    break

            unidirectional = vawes[first:last]
            move = Move(unidirectional)
            all_moves.append(move)

            i = last

        return all_moves

    # }}}
    def __getAllMMoves(self) -> list[Move]:  # {{{
        vawes = self.__getAllMVawes()

        all_moves = list()
        i = 0
        while i < len(vawes):
            first = i
            last = i
            while last < len(vawes):
                if vawes[first].type == vawes[last].type:
                    last += 1
                else:
                    break

            unidirectional = vawes[first:last]
            move = Move(unidirectional)
            all_moves.append(move)

            i = last

        return all_moves

    # }}}
    def __getAllLMoves(self) -> list[Move]:  # {{{
        vawes = self.__getAllLVawes()

        all_moves = list()
        i = 0
        while i < len(vawes):
            first = i
            last = i
            while last < len(vawes):
                if vawes[first].type == vawes[last].type:
                    last += 1
                else:
                    break

            unidirectional = vawes[first:last]
            move = Move(unidirectional)
            all_moves.append(move)

            i = last

        return all_moves

    # }}}

    # def __sPeaks(self, start: int):  # {{{
    #     all_peaks = list()
    #     vawe = self.__sVawe(start)
    #     while vawe is not None:
    #         if vawe.isBull() and vawe.isPeak():
    #             peak = Peak(vawe.one, vawe.two)
    #             all_peaks.append(peak)
    #         else:
    #             break
    #
    #         start += 2
    #         vawe = self.__sVawe(start)
    #
    #     return all_peaks
    #
    # # }}}
    # def __sCaves(self, start: int):  # {{{
    #     all_caves = list()
    #     vawe = self.__sVawe(start)
    #     while vawe is not None:
    #         if vawe.isBear() and vawe.isCave():
    #             cave = Cave(vawe.one, vawe.two)
    #             all_caves.append(cave)
    #         else:
    #             break
    #
    #         start += 2
    #         vawe = self.__sVawe(start)
    #
    #     return all_caves
    #
    # # }}}
    #
    # def __sMove(self, n) -> Move | None:  # {{{
    #     assert n >= 0
    #
    #     # временный асерт, пока отдача только последнее движение сделано
    #     assert n == 0
    #
    #     # Начинаем смотреть с прошлой волны
    #     v1 = self.__sVawe(1)
    #
    #     # это получается бычье движение
    #     if v1.isBull() and v1.isPeak():
    #         peaks = self.__sPeaks(start=1)
    #         # и сейчас peak0 только начинается, идет bull фаза
    #         # берем один текущий тренд и None вместо второго
    #         t1 = self.trend(Term.STERM, n=0)
    #         t2 = None
    #         peak_0 = Peak(t1, t2)
    #         return [peak_0] + peaks
    #
    #     # это получается медвежье движение
    #     elif v1.isBear() and v1.isCave():
    #         caves = self.__sCaves(start=1)
    #         # и сейчас cave0 только начинается, идет bear фаза
    #         # берем один текущий тренд и None вместо второго
    #         t1 = self.trend(Term.STERM, n=0)
    #         t2 = None
    #         cave_0 = Cave(t1, t2)
    #         return [cave_0] + caves
    #
    #     # Значит прошлая волна либо bull cave, либо bear peak
    #     # тогда смотрим на предыдущую волну
    #     v2 = self.__sVawe(2)
    #
    #     # это получается бычье движение
    #     if v2.isBull() and v2.isPeak():
    #         peaks = self.__sPeaks(start=2)
    #         # и сейчас peak0 уже идет, идет 2 фаза - bear
    #         # берем прошлый и текущий тренд = текущей незавершенный peak
    #         t1 = self.trend(Term.STERM, n=1)
    #         t2 = self.trend(Term.STERM, n=0)
    #         peak_0 = Peak(t1, t2)
    #         return [peak_0] + peaks
    #
    #     # это получается медвежье движение
    #     elif v2.isBear() and v2.isCave():
    #         caves = self.__sCaves(start=2)
    #         # и сейчас peak0 уже идет, идет 2 фаза - bull
    #         # берем прошлый и текущий тренд = текущей незавершенный cave
    #
    #         t1 = self.trend(Term.STERM, n=1)
    #         t2 = self.trend(Term.STERM, n=0)
    #         cave_0 = Cave(t1, t2)
    #         return [cave_0] + caves
    #
    #     else:
    #         assert False, "WTF???"
    #
    # # }}}
    # def __mMove(self, n) -> Move | None:  # {{{
    #     pass
    #
    # # }}}
    # def __lMove(self, n) -> Move | None:  # {{{
    #     pass
    #
    # # }}}


if __name__ == "__main__":
    ...
