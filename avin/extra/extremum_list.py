#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import polars as pl

from avin.core.bar import Bar
from avin.core.chart import Chart
from avin.core.timeframe import TimeFrame
from avin.extra.extremum import Extremum
from avin.extra.term import Term
from avin.extra.trend import Trend
from avin.utils import UTC, Signal


class ExtremumList:
    def __init__(self, chart: Chart):  # {{{
        self.__chart = chart

        # data
        self.__schema = {
            "dt": pl.datatypes.Datetime("us", UTC),
            "term": str,
            "type": str,
            "price": float,
        }
        self.__t1 = pl.DataFrame(schema=self.__schema)
        self.__t2 = pl.DataFrame(schema=self.__schema)
        self.__t3 = pl.DataFrame(schema=self.__schema)
        self.__t4 = pl.DataFrame(schema=self.__schema)
        self.__t5 = pl.DataFrame(schema=self.__schema)
        self.__now = pl.DataFrame(schema=self.__schema)

        # signals
        self.upd_extr = Signal(ExtremumList, Extremum)
        self.new_extr = Signal(ExtremumList, Extremum)

        # connect
        self.__chart.new_bar.connect(self.__onNewBar)
        self.__chart.upd_bar.connect(self.__onUpdBar)

        # calc extremums
        self.__calcExtrT1()
        self.__calcExtrT2()
        self.__calcExtrT3()

    # }}}

    @property  # asset   # {{{
    def asset(self) -> Asset:
        return self.__chart.asset

    # }}}
    @property  # chart  # {{{
    def chart(self) -> Chart:
        return self.__chart

    # }}}
    @property  # timeframe # {{{
    def timeframe(self) -> TimeFrame:
        return self.__chart.timeframe

    # }}}
    @property  # t1  # {{{
    def t1(self):
        return self.__t1

    # }}}
    @property  # t2  # {{{
    def t2(self):
        return self.__t2

    # }}}
    @property  # t3  # {{{
    def t3(self):
        return self.__t3

    # }}}
    @property  # t4  # {{{
    def t4(self):
        return self.__t4

    # }}}
    @property  # t5  # {{{
    def t5(self):
        return self.__t5

    # }}}

    def extr(self, term: Term, n: int) -> Extremum | None:  # {{{
        assert n > 0

        match term:
            case Term.T1:
                df = self.__t1
            case Term.T2:
                df = self.__t2
            case Term.T3:
                df = self.__t3

        if n > len(df):
            return None

        dct = df.row(-n, named=True)
        e = Extremum(dct, self)
        return e

    # }}}
    def trend(self, term: Term, n: int) -> Trend | None:  # {{{
        assert n > 0
        match term:
            case Term.T1:
                df = self.__t1
            case Term.T2:
                df = self.__t2
            case Term.T3:
                df = self.__t3
            case _:
                assert False, "TODO_ME"

        if n > len(df) - 1:
            return None

        # if n == 0:
        #     e1_data = self.__t1[-1]
        #     e2_data = self.__now
        e1_data = df[-n - 1]
        e2_data = df[-n]
        e1 = Extremum(e1_data.row(0, named=True), self)
        e2 = Extremum(e2_data.row(0, named=True), self)

        t = Trend(e1, e2, self)
        return t

    # }}}
    # def vawe(self, term: Term, n: int) -> Vawe | None:  # {{{
    #     assert False, "TODO_ME_UPDATE"
    #     match term:
    #         case Term.STERM:
    #             return self.__sVawe(n)
    #         case Term.MTERM:
    #             return self.__mVawe(n)
    #         case Term.LTERM:
    #             return self.__lVawe(n)
    #
    # # }}}
    # def move(self, term: Term, n: int) -> Move | None:  # {{{
    #     assert False, "TODO_ME_UPDATE"
    #     match term:
    #         case Term.STERM:
    #             return self.__sMove(n)
    #         case Term.MTERM:
    #             return self.__mMove(n)
    #         case Term.LTERM:
    #             return self.__lMove(n)
    #
    # # }}}
    def getAllTrends(self, term: Term) -> list[Trend]:  # {{{
        all_trends = list()

        n = 1
        trend = self.trend(term, n)
        while trend is not None:
            all_trends.append(trend)
            n += 1
            trend = self.trend(term, n)

        all_trends.reverse()
        return all_trends

    # }}}
    # def getAllVawes(self, term: Term) -> list[Vawe]:  # {{{
    #     assert False, "TODO_ME_UPDATE"
    #     match term:
    #         case Term.STERM:
    #             return self.__getAllSVawes()
    #         case Term.MTERM:
    #             return self.__getAllMVawes()
    #         case Term.LTERM:
    #             return self.__getAllLVawes()
    #
    # # }}}
    # def getAllMoves(self, term: Term) -> list[Move]:  # {{{
    #     assert False, "TODO_ME_UPDATE"
    #     match term:
    #         case Term.STERM:
    #             return self.__getAllSMoves()
    #         case Term.MTERM:
    #             return self.__getAllMMoves()
    #         case Term.LTERM:
    #             return self.__getAllLMoves()
    #
    # # }}}

    def __calcExtrT1(self) -> None:  # {{{
        term = Term.T1
        df = self.__chart.data_frame.with_row_index()
        df = df.filter(pl.col("high") != pl.col("low"))  # skip point bars
        if df.is_empty():
            return

        # pop first bar
        prev = df.row(0, named=True)
        df = df.filter(pl.col("index") != 0)

        # set start direction of trend = first bar.type
        if prev["open"] < prev["close"]:
            trend_t = Trend.Type.BULL
        elif prev["open"] > prev["close"]:
            trend_t = Trend.Type.BEAR
        else:
            assert False, "TODO: skip point bars???"

        # cacl extremums
        for cur in df.iter_rows(named=True):
            if trend_t == Trend.Type.BULL:
                if cur["high"] > prev["high"]:
                    self.__now = pl.DataFrame(
                        {
                            "dt": cur["dt"],
                            "term": term.name,
                            "type": Extremum.Type.MAX.name,
                            "price": cur["high"],
                        }
                    )
                else:
                    self.__t1.extend(self.__now)
                    self.__now = pl.DataFrame(
                        {
                            "dt": cur["dt"],
                            "term": term.name,
                            "type": Extremum.Type.MIN.name,
                            "price": cur["low"],
                        }
                    )
                    trend_t = Trend.Type.BEAR

            elif trend_t == Trend.Type.BEAR:
                if cur["low"] < prev["low"]:
                    self.__now = pl.DataFrame(
                        {
                            "dt": cur["dt"],
                            "term": term.name,
                            "type": Extremum.Type.MIN.name,
                            "price": cur["low"],
                        }
                    )
                else:
                    self.__t1.extend(self.__now)
                    self.__now = pl.DataFrame(
                        {
                            "dt": cur["dt"],
                            "term": term.name,
                            "type": Extremum.Type.MAX.name,
                            "price": cur["high"],
                        }
                    )
                    trend_t = Trend.Type.BULL

            prev = cur

    # }}}
    def __calcExtrT2(self) -> None:  # {{{
        df = self.__t1

        # pop first extr
        prev = df.row(0, named=True)
        now_t2 = pl.DataFrame(prev)
        df = df.filter(pl.col("dt") != prev["dt"])

        # set start direction of trend
        if prev["type"] == "MAX":
            trend_t = Trend.Type.BULL
            prev_max = prev
            prev_min = None
        else:
            trend_t = Trend.Type.BEAR
            prev_max = None
            prev_min = prev

        # cacl extremums T2
        for cur in df.iter_rows(named=True):
            if trend_t == Trend.Type.BULL:
                if cur["type"] == "MIN":
                    prev_min = cur
                elif cur["price"] > prev_max["price"]:
                    now_t2 = pl.DataFrame(cur)
                    prev_max = cur
                else:
                    self.__t2.extend(now_t2)
                    now_t2 = pl.DataFrame(prev_min)
                    trend_t = Trend.Type.BEAR
                    prev_max = cur

            elif trend_t == Trend.Type.BEAR:
                if cur["type"] == "MAX":
                    prev_max = cur
                elif cur["price"] < prev_min["price"]:
                    now_t2 = pl.DataFrame(cur)
                    prev_min = cur
                else:
                    self.__t2.extend(now_t2)
                    now_t2 = pl.DataFrame(prev_max)
                    trend_t = Trend.Type.BULL
                    prev_min = cur

        # replace values of column "term" from "T1" to "T2"
        self.__t2 = self.__t2.with_columns(term=pl.lit("T2"))

    # }}}
    def __calcExtrT3(self) -> None:  # {{{
        df = self.__t2

        # pop first extr
        prev = df.row(0, named=True)
        now_t3 = pl.DataFrame(prev)
        df = df.filter(pl.col("dt") != prev["dt"])

        # set start direction of trend
        if prev["type"] == "MAX":
            trend_t = Trend.Type.BULL
            prev_max = prev
            prev_min = None
        else:
            trend_t = Trend.Type.BEAR
            prev_max = None
            prev_min = prev

        # cacl extremums T2
        for cur in df.iter_rows(named=True):
            if trend_t == Trend.Type.BULL:
                if cur["type"] == "MIN":
                    prev_min = cur
                elif cur["price"] > prev_max["price"]:
                    now_t3 = pl.DataFrame(cur)
                    prev_max = cur
                else:
                    self.__t3.extend(now_t3)
                    now_t3 = pl.DataFrame(prev_min)
                    trend_t = Trend.Type.BEAR
                    prev_max = cur

            elif trend_t == Trend.Type.BEAR:
                if cur["type"] == "MAX":
                    prev_max = cur
                elif cur["price"] < prev_min["price"]:
                    now_t3 = pl.DataFrame(cur)
                    prev_min = cur
                else:
                    self.__t3.extend(now_t3)
                    now_t3 = pl.DataFrame(prev_max)
                    trend_t = Trend.Type.BULL
                    prev_min = cur

        # replace values of column "term" from "T2" to "T3"
        self.__t3 = self.__t3.with_columns(term=pl.lit("T3"))

    # }}}
    def __onNewBar(self, chart: Chart, bar: Bar):  # {{{
        pass

    # }}}
    def __onUpdBar(self, chart: Chart, bar: Bar):  # {{{
        pass

    # }}}


########## old code

# def __updateShorttem(self):  # {{{
#     self.__shortterm.clear()
#     bars = self.__skipInsideOutside()
#     if len(bars) < 3:
#         return
#
#     i = 1
#     count = len(bars) - 1
#     while i < count:
#         left = bars[i - 1]
#         bar = bars[i]
#         right = bars[i + 1]
#         if left.high < bar.high > right.high:
#             e = Extremum(Extremum.Type.MAX | Extremum.Type.SHORTTERM, bar)
#             self.__shortterm.append(e)
#         if left.low > bar.low < right.low:
#             e = Extremum(Extremum.Type.MIN | Extremum.Type.SHORTTERM, bar)
#             self.__shortterm.append(e)
#         i += 1
#
#     self.__popRepeatedExtr(self.__shortterm)
#
# # }}}
# def __updateMidterm(self):  # {{{
#     self.__midterm.clear()
#
#     short_extr = self.__shortterm
#     if len(short_extr) < 5:
#         return
#
#     i = 2
#     count = len(short_extr) - 2
#     while i < count:
#         left = short_extr[i - 2]
#         e = short_extr[i]
#         right = short_extr[i + 2]
#         if (
#             e.isMax()
#             and left < e > right
#             or e.isMin()
#             and left > e < right
#         ):
#             e.addFlag(Extremum.Type.MIDTERM)
#             self.__midterm.append(e)
#         i += 1
#
#     self.__popRepeatedExtr(self.__midterm)
#
# # }}}
# def __updateLongterm(self):  # {{{
#     self.__longterm.clear()
#
#     mid_extr = self.__midterm
#     if len(mid_extr) < 5:
#         return
#
#     i = 2
#     count = len(mid_extr) - 2
#     while i < count:
#         left = mid_extr[i - 2]
#         e = mid_extr[i]
#         right = mid_extr[i + 2]
#         if (
#             e.isMax()
#             and (left < e > right)
#             or e.isMin()
#             and (left > e < right)
#         ):
#             e.addFlag(Extremum.Type.LONGTERM)
#             self.__longterm.append(e)
#         i += 1
#
#     self.__popRepeatedExtr(self.__longterm)
#
# # }}}
# def __popRepeatedExtr(self, elist):  # {{{
#     if len(elist) < 2:
#         return
#
#     i = 0
#     previous = elist[i]
#     i += 1
#     while i < len(elist):
#         current = elist[i]
#         if current.isMax() and previous.isMax():  # double max
#             if current > previous:
#                 elist.pop(i - 1)
#                 previous = current
#                 continue
#             else:
#                 elist.pop(i)
#                 continue
#         elif current.isMin() and previous.isMin():  # double min
#             if current < previous:
#                 elist.pop(i - 1)
#                 previous = current
#                 continue
#             else:
#                 elist.pop(i)
#                 continue
#         elif (
#             (  # перегиб бычьего, next min > prev max
#                 current.isMin()
#                 and previous.isMax()
#                 and current > previous
#             )
#             or (  # перегиб медвежьего, next max < prev min
#                 current.isMax()
#                 and previous.isMin()
#                 and current < previous
#             )
#             or current.dt == previous.dt  # double extr in one bar
#         ):
#             elist.pop(i)
#             continue
#
#         previous = current
#         i += 1
#
# # }}}

# def __sTrend(self, n) -> Trend | None:  # {{{
#     """
#     Тренд 0 - это текущий незавершенный тренд
#     Тренд 1 - это прошлый тренд
#     Тренд 2 - это позапрошлый тренд и тд
#     """
#     assert n >= 0
#
#     if n > (len(self.__shortterm) - 1):
#         return None
#
#     t = Extremum.Type
#     if n == 0:
#         e1 = self.__shortterm[-1]
#
#         # TODO: тут нужно не просто last_bar брать как сейчас
#         # а смотреть на самое экстримальное значение среди баров
#         # от прошлого экстремума до последнего исторического бара
#         # self.__chart.getBars(e1.bar, self.__chart.last)
#         last_bar = self.__chart.last
#
#         if e1.isMax():
#             e2 = Extremum(t.MIN | t.SHORTTERM, last_bar)
#         else:
#             e2 = Extremum(t.MAX | t.SHORTTERM, last_bar)
#
#         trend = Trend(e1, e2, Term.STERM)
#         return trend
#
#     # n >= 1
#     e1 = self.__shortterm[-n - 1]
#     e2 = self.__shortterm[-n]
#     trend = Trend(e1, e2, Term.STERM)
#     return trend
#
# # }}}
# def __mTrend(self, n) -> Trend | None:  # {{{
#     assert n >= 0
#
#     if n > (len(self.__midterm) - 1):
#         return None
#
#     t = Extremum.Type
#     if n == 0:
#         e1 = self.__midterm[-1]
#
#         last_bar = self.__chart.last
#         if e1.isMax():
#             e2 = Extremum(t.MIN | t.SHORTTERM, last_bar)
#         else:
#             e2 = Extremum(t.MAX | t.SHORTTERM, last_bar)
#
#         trend = Trend(e1, e2, Term.MTERM)
#         return trend
#
#     # n >= 1
#     e1 = self.__midterm[-n - 1]
#     e2 = self.__midterm[-n]
#     trend = Trend(e1, e2, Term.MTERM)
#     return trend
#
# # }}}
# def __lTrend(self, n) -> Trend | None:  # {{{
#     assert n >= 0
#
#     if n > (len(self.__longterm) - 1):
#         return None
#
#     t = Extremum.Type
#     if n == 0:
#         e1 = self.__longterm[-1]
#
#         last_bar = self.__chart.last
#         if e1.isMax():
#             e2 = Extremum(t.MIN | t.SHORTTERM, last_bar)
#         else:
#             e2 = Extremum(t.MAX | t.SHORTTERM, last_bar)
#
#         trend = Trend(e1, e2, Term.LTERM)
#         return trend
#
#     # n >= 1
#     e1 = self.__longterm[-n - 1]
#     e2 = self.__longterm[-n]
#     trend = Trend(e1, e2, Term.LTERM)
#     return trend
#
# # }}}
# def __sVawe(self, n) -> Vawe | None:  # {{{
#     """
#     Волна 0 состоит из тренда 1 и тренда 0
#     Волна 1 состоит из тренда 2 и тренда 1
#     Волна 2 состоит из тренда 3 и тренда 2
#     """
#     assert n >= 0
#
#     t1 = self.__sTrend(n + 1)
#     t2 = self.__sTrend(n)
#     if t1 is None:
#         return None
#
#     return Vawe(t1, t2)
#
# # }}}
# def __mVawe(self, n) -> Vawe | None:  # {{{
#     """
#     Волна 0 состоит из тренда 1 и тренда 0
#     Волна 1 состоит из тренда 2 и тренда 1
#     Волна 2 состоит из тренда 3 и тренда 2
#     """
#     assert n >= 0
#
#     t1 = self.__mTrend(n + 1)
#     t2 = self.__mTrend(n)
#     if t1 is None:
#         return None
#
#     return Vawe(t1, t2)
#
# # }}}
# def __lVawe(self, n) -> Vawe | None:  # {{{
#     """
#     Волна 0 состоит из тренда 1 и тренда 0
#     Волна 1 состоит из тренда 2 и тренда 1
#     Волна 2 состоит из тренда 3 и тренда 2
#     """
#     assert n >= 0
#
#     t1 = self.__lTrend(n + 1)
#     t2 = self.__lTrend(n)
#     if t1 is None:
#         return None
#
#     return Vawe(t1, t2)
#
# # }}}
# def __sMove(self, n) -> Move | None:  # {{{
#     assert n >= 0
#     moves = self.__getAllSMoves()
#     if not moves:
#         return None
#
#     if len(moves) < n:
#         return None
#
#     return moves[n]
#
# # }}}
# def __mMove(self, n) -> Move | None:  # {{{
#     assert n >= 0
#     moves = self.__getAllMMoves()
#     if not moves:
#         return None
#
#     if len(moves) < n:
#         return None
#
#     return moves[n]
#
# # }}}
# def __lMove(self, n) -> Move | None:  # {{{
#     assert n >= 0
#     moves = self.__getAllLMoves()
#     if not moves:
#         return None
#
#     if len(moves) < n:
#         return None
#
#     return moves[n]
#
# # }}}

# def __getAllSTrends(self) -> list[Trend]:  # {{{
#     all_trends = list()
#
#     n = 0
#     trend = self.__sTrend(n)
#     while trend is not None:
#         all_trends.append(trend)
#         n += 1
#         trend = self.__sTrend(n)
#
#     all_trends.reverse()
#     return all_trends
#
# # }}}
# def __getAllMTrends(self) -> list[Trend]:  # {{{
#     all_trends = list()
#
#     n = 0
#     trend = self.__mTrend(n)
#     while trend is not None:
#         all_trends.append(trend)
#         n += 1
#         trend = self.__mTrend(n)
#
#     all_trends.reverse()
#     return all_trends
#
# # }}}
# def __getAllLTrends(self) -> list[Trend]:  # {{{
#     all_trends = list()
#
#     n = 0
#     trend = self.__lTrend(n)
#     while trend is not None:
#         all_trends.append(trend)
#         n += 1
#         trend = self.__lTrend(n)
#
#     all_trends.reverse()
#     return all_trends
#
# # }}}
# def __getAllSVawes(self) -> list[Vawe]:  # {{{
#     all_vawes = list()
#
#     n = 0
#     vawe = self.__sVawe(n)
#     while vawe is not None:
#         all_vawes.append(vawe)
#         n += 1
#         vawe = self.__sVawe(n)
#
#     all_vawes.reverse()
#     return all_vawes
#
# # }}}
# def __getAllMVawes(self) -> list[Vawe]:  # {{{
#     all_vawes = list()
#
#     n = 0
#     vawe = self.__mVawe(n)
#     while vawe is not None:
#         all_vawes.append(vawe)
#         n += 1
#         vawe = self.__mVawe(n)
#
#     all_vawes.reverse()
#     return all_vawes
#
# # }}}
# def __getAllLVawes(self) -> list[Vawe]:  # {{{
#     all_vawes = list()
#
#     n = 0
#     vawe = self.__lVawe(n)
#     while vawe is not None:
#         all_vawes.append(vawe)
#         n += 1
#         vawe = self.__lVawe(n)
#
#     all_vawes.reverse()
#     return all_vawes
#
# # }}}

# def __getAllSMoves(self) -> list[Move]:  # {{{
#     vawes = self.__getAllSVawes()
#
#     all_moves = list()
#     i = 0
#     while i < len(vawes):
#         first = i
#         last = i
#         while last < len(vawes):
#             if vawes[first].type == vawes[last].type:
#                 last += 1
#             else:
#                 break
#
#         unidirectional = vawes[first:last]
#         move = Move(unidirectional)
#         all_moves.append(move)
#
#         i = last
#
#     return all_moves
#
# # }}}
# def __getAllMMoves(self) -> list[Move]:  # {{{
#     vawes = self.__getAllMVawes()
#
#     all_moves = list()
#     i = 0
#     while i < len(vawes):
#         first = i
#         last = i
#         while last < len(vawes):
#             if vawes[first].type == vawes[last].type:
#                 last += 1
#             else:
#                 break
#
#         unidirectional = vawes[first:last]
#         move = Move(unidirectional)
#         all_moves.append(move)
#
#         i = last
#
#     return all_moves
#
# # }}}
# def __getAllLMoves(self) -> list[Move]:  # {{{
#     vawes = self.__getAllLVawes()
#
#     all_moves = list()
#     i = 0
#     while i < len(vawes):
#         first = i
#         last = i
#         while last < len(vawes):
#             if vawes[first].type == vawes[last].type:
#                 last += 1
#             else:
#                 break
#
#         unidirectional = vawes[first:last]
#         move = Move(unidirectional)
#         all_moves.append(move)
#
#         i = last
#
#     return all_moves
#
# # }}}

# old unused code
# def __update(self) -> None:  # {{{
#     self.__markInsideDays()
#     self.__markOutsideDays()
#     self.__markOverflowDays()
#     self.__updateShorttem()
#     self.__updateMidterm()
#     self.__updateLongterm()
#
# # }}}
# def __isOverflowOf(self, this, of) -> bool:  # {{{
#     return this.high > of or this.low < of.low
#
# # }}}
# def __isInsideOf(self, this, of) -> bool:  # {{{
#     return this.high <= of.high and this.low >= of.low
#
# # }}}
# def __isOutsideOf(self, this, of) -> bool:  # {{{
#     return this.high >= of.high and this.low <= of.low
#
# # }}}
# def __markInsideDays(self):  # {{{
#     bars = self.__chart.getBars()
#     if len(bars) < 2:
#         return
#
#     i = 0
#     previous = bars[i]
#     previous.delFlag(Bar.Type.INSIDE)
#     i += 1
#
#     while i < len(bars):
#         current_bar = bars[i]
#         if self.__isInsideOf(current_bar, previous):
#             current_bar.addFlag(Bar.Type.INSIDE)
#         else:
#             current_bar.delFlag(Bar.Type.INSIDE)
#             previous = current_bar
#         i += 1
#
# # }}}
# def __markOutsideDays(self):  # {{{
#     bars = self.__chart.getBars()
#     if len(bars) < 2:
#         return
#
#     i = 0
#     previous = bars[i]
#     previous.delFlag(Bar.Type.OUTSIDE)
#     i += 1
#
#     while i < len(bars):
#         current_bar = bars[i]
#         if self.__isOutsideOf(current_bar, previous):
#             current_bar.addFlag(Bar.Type.OUTSIDE)
#         else:
#             current_bar.delFlag(Bar.Type.OUTSIDE)
#             previous = current_bar
#         i += 1
#
# # }}}
# def __markOverflowDays(self):  # {{{
#     bars = self.__chart.getBars()
#     for bar in bars:
#         if not bar.isInside() and not bar.isOutside():
#             bar.addFlag(Bar.Type.OVERFLOW)
#
# # }}}
# def __skipInsideOutside(self):  # {{{
#     # NOTE:
#     # если их скипать получается гораздо больше неадеквата
#     # чем если их оставить.
#     # Самая жесть после СВО, там инсайд потом пол года идет.
#     # Лучше пусть шорт-терм чаще колеблется, и больше смотреть
#     # на m-term, l-term. Чисто визуально мне кажется это лучше
#     # сейчас будет работать.
#     # Отключаю эту функцию временно, но не удаляю пока.
#     return self.__chart.getBars()
#
#     bars = self.__chart.getBars()
#     without_inside_outside = list()
#     for bar in bars:
#         if bar.isInside() or bar.isOutside():
#             continue
#         else:
#             without_inside_outside.append(bar)
#
#     return without_inside_outside
#
# # }}}


if __name__ == "__main__":
    ...
