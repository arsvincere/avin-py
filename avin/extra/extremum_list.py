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
from avin.core.indicator import Indicator
from avin.core.timeframe import TimeFrame
from avin.extra.extremum import Extremum
from avin.extra.term import Term
from avin.extra.trend import Trend
from avin.utils import UTC, Signal, Tree


class ExtremumList(Indicator):
    name = "ExtremumList"

    def __init__(self):  # {{{
        # data
        self.__schema = {
            "dt": pl.datatypes.Datetime("us", UTC),
            "term": str,
            "type": str,
            "price": float,
        }
        # signals
        self.upd_extr = Signal(Extremum)
        self.new_extr = Signal(Extremum)
        self.upd_trend = Signal(Trend)
        self.new_trend = Signal(Trend)

        # cache
        self.cache_trend = Tree()

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

    def setChart(self, chart: Chart) -> None:  # {{{
        self.__chart = chart
        self.__chart.new_bar.connect(self.__updExtr)

        self.__calcExtr()

    # }}}
    def extr(self, term: Term, n: int) -> Extremum | None:  # {{{
        assert n >= 0

        if n == 0:
            match term:
                case Term.T1:
                    data = self.__t1_now
                case Term.T2:
                    data = self.__t2_now
                case Term.T3:
                    data = self.__t3_now
                case Term.T4:
                    data = self.__t4_now
                case Term.T5:
                    data = self.__t5_now
                case _:
                    assert False, "TODO_ME"

            e = Extremum(data, self)
            return e

        # n > 0
        match term:
            case Term.T1:
                df = self.__t1
            case Term.T2:
                df = self.__t2
            case Term.T3:
                df = self.__t3
            case Term.T4:
                df = self.__t4
            case Term.T5:
                df = self.__t5
            case _:
                assert False, "TODO_ME"

        if n > len(df):
            return None

        data = df.row(-n, named=True)
        e = Extremum(data, self)
        return e

    # }}}
    def trend(self, term: Term, n: int) -> Trend | None:  # {{{
        assert n >= 0

        e1 = self.extr(term, n + 1)
        e2 = self.extr(term, n)

        if e1 is not None and e2 is not None:
            t = Trend(e1, e2, self)
            return t

        return None

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
        # try find in cache
        trends = self.cache_trend[term]
        if trends:
            return trends

        all_trends = list()
        n = 1
        trend = self.trend(term, n)
        while trend is not None:
            all_trends.append(trend)
            n += 1
            trend = self.trend(term, n)
        all_trends.reverse()

        self.cache_trend[term] = all_trends

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

    def __calcExtr(self) -> None:  # {{{
        t1, t1_now = self.__calcExtrT1(self.__chart, Term.T1)
        t2, t2_now = self.__calcExtrNext(t1, Term.T2)
        t3, t3_now = self.__calcExtrNext(t2, Term.T3)
        t4, t4_now = self.__calcExtrNext(t3, Term.T4)
        t5, t5_now = self.__calcExtrNext(t4, Term.T5)

        self.__t1 = t1
        self.__t2 = t2
        self.__t3 = t3
        self.__t4 = t4
        self.__t5 = t5
        self.__t1_now = t1_now
        self.__t2_now = t2_now
        self.__t3_now = t3_now
        self.__t4_now = t4_now
        self.__t5_now = t5_now

    # }}}
    def __calcExtrT1(self, chart: Chart, term: Term) -> pl.DataFrame:  # {{{
        out_extr = pl.DataFrame(schema=self.__schema)
        out_now = dict()

        bars = chart.data_frame.with_row_index()
        bars = bars.filter(pl.col("high") != pl.col("low"))  # skip point bars
        if bars.is_empty():
            return out_extr, out_now

        # pop first bar
        prev = bars.row(0, named=True)
        bars = bars[0:-1]

        # set start direction of trend = first bar.type
        if prev["open"] < prev["close"]:
            trend_t = Trend.Type.BULL
            out_now = {
                "dt": prev["dt"],
                "term": term.name,
                "type": Extremum.Type.MAX.name,
                "price": prev["high"],
            }
        else:
            trend_t = Trend.Type.BEAR
            out_now = {
                "dt": prev["dt"],
                "term": term.name,
                "type": Extremum.Type.MAX.name,
                "price": prev["low"],
            }

        # cacl extremums
        for cur in bars.iter_rows(named=True):
            if trend_t == Trend.Type.BULL:
                if cur["high"] > prev["high"]:
                    out_now = {
                        "dt": cur["dt"],
                        "term": term.name,
                        "type": Extremum.Type.MAX.name,
                        "price": cur["high"],
                    }
                else:
                    out_extr.extend(pl.DataFrame(out_now))
                    out_now = {
                        "dt": cur["dt"],
                        "term": term.name,
                        "type": Extremum.Type.MIN.name,
                        "price": cur["low"],
                    }
                    trend_t = Trend.Type.BEAR

            elif trend_t == Trend.Type.BEAR:
                if cur["low"] < prev["low"]:
                    out_now = {
                        "dt": cur["dt"],
                        "term": term.name,
                        "type": Extremum.Type.MIN.name,
                        "price": cur["low"],
                    }
                else:
                    out_extr.extend(pl.DataFrame(out_now))
                    out_now = {
                        "dt": cur["dt"],
                        "term": term.name,
                        "type": Extremum.Type.MAX.name,
                        "price": cur["high"],
                    }
                    trend_t = Trend.Type.BULL

            prev = cur

        return out_extr, out_now

    # }}}
    def __calcExtrNext(self, in_extr, out_term) -> None:  # {{{
        out_extr = pl.DataFrame(schema=self.__schema)
        out_now = dict()
        if in_extr.is_empty():
            return out_extr, out_now

        # pop first extr
        out_now = in_extr.row(0, named=True)
        in_extr = in_extr[1:]

        # cacl extremums high term
        for in_cur in in_extr.iter_rows(named=True):
            if in_cur["type"] != out_now["type"]:
                in_prev = in_cur
                continue

            if out_now["type"] == "MAX":
                if in_cur["price"] > out_now["price"]:
                    out_now = in_cur
                else:
                    out_extr.extend(pl.DataFrame(out_now))
                    out_now = in_prev
                    in_prev = in_cur

            elif out_now["type"] == "MIN":
                if in_cur["price"] < out_now["price"]:
                    out_now = in_cur
                else:
                    out_extr.extend(pl.DataFrame(out_now))
                    out_now = in_prev
                    in_prev = in_cur

        out_extr = out_extr.with_columns(term=pl.lit(out_term.name))
        out_now["term"] = out_term.name
        return out_extr, out_now

    # }}}
    def __updExtr(self, chart: Chart, bar: Bar):  # {{{
        has_new = self.__updExtrT1(chart, bar)
        if not has_new:
            return

        has_new = self.__updExtrNext(
            self.__t1, self.__t2, self.__t2_now, Term.T2
        )
        if not has_new:
            return

        has_new = self.__updExtrNext(
            self.__t2, self.__t3, self.__t3_now, Term.T3
        )
        if not has_new:
            return

        has_new = self.__updExtrNext(
            self.__t3, self.__t4, self.__t4_now, Term.T4
        )
        if not has_new:
            return

        self.__updExtrNext(self.__t4, self.__t5, self.__t5_now, Term.T5)

    # }}}
    def __updExtrT1(self, chart: Chart, bar: Bar):  # {{{
        has_update = False
        has_new_extr = False
        if self.__t1_now["type"] == "MAX":
            if bar.high > self.__t1_now["price"]:
                self.__t1_now = {
                    "dt": bar.dt,
                    "term": Term.T1.name,
                    "type": Extremum.Type.MAX.name,
                    "price": bar.high,
                }
                has_update = True
            else:
                self.__t1.extend(pl.DataFrame(self.__t1_now))
                self.__t1_now = {
                    "dt": bar.dt,
                    "term": Term.T1.name,
                    "type": Extremum.Type.MIN.name,
                    "price": bar.low,
                }
                has_update = True
                has_new_extr = True

        elif self.__t1_now["type"] == "MIN":
            if bar.low < self.__t1_now["price"]:
                self.__t1_now = {
                    "dt": bar.dt,
                    "term": Term.T1.name,
                    "type": Extremum.Type.MIN.name,
                    "price": bar.low,
                }
                has_update = True
            else:
                self.__t1.extend(pl.DataFrame(self.__t1_now))
                self.__t1_now = {
                    "dt": bar.dt,
                    "term": Term.T1.name,
                    "type": Extremum.Type.MAX.name,
                    "price": bar.high,
                }
                has_update = True
                has_new_extr = True

        if has_new_extr:
            e = self.extr(Term.T1, 1)
            t = self.trend(Term.T1, 1)
            self.new_extr.emit(e)
            self.new_trend.emit(t)

            # update cache if exist
            cached_trends = self.cache_trend[Term.T1]
            if cached_trends:
                cached_trends.append(t)

        if has_update:
            self.upd_extr.emit(self.extr(Term.T1, 0))
            self.upd_trend.emit(self.trend(Term.T1, 0))

        return has_new_extr

    # }}}
    def __updExtrNext(  # {{{
        self, in_extr, out_extr, out_now, out_term
    ) -> bool:
        has_update = False
        has_new_extr = False

        in_cur = in_extr.row(-1, named=True)

        # если текущий старший тип != текущий младший тип -> делать ничего
        if in_cur["type"] != out_now["type"]:
            return has_new_extr

        if out_now["type"] == "MAX":
            if in_cur["price"] > out_now["price"]:
                out_now = in_cur
                has_update = True
            else:
                out_extr.extend(pl.DataFrame(out_now))
                out_now = in_extr.row(-2, named=True)
                has_update = True
                has_new_extr = True

        elif out_now["type"] == "MIN":
            if in_cur["price"] < out_now["price"]:
                out_now = in_cur
                has_update = True
            else:
                out_extr.extend(pl.DataFrame(out_now))
                out_now = in_extr.row(-2, named=True)
                has_update = True
                has_new_extr = True

        out_now["term"] = out_term.name
        match out_term:
            case Term.T2:
                self.__t2 = out_extr
                self.__t2_now = out_now
            case Term.T3:
                self.__t3 = out_extr
                self.__t3_now = out_now
            case Term.T4:
                self.__t4 = out_extr
                self.__t4_now = out_now
            case Term.T5:
                self.__t5 = out_extr
                self.__t5_now = out_now

        if has_new_extr:
            e = self.extr(Term.T1, 1)
            t = self.trend(Term.T1, 1)
            self.new_extr.emit(e)
            self.new_trend.emit(t)

            # update cache if exist
            cached_trends = self.cache_trend[Term.T1]
            if cached_trends:
                cached_trends.append(t)

        if has_update:
            self.upd_extr.emit(self.extr(out_term, 0))
            self.upd_trend.emit(self.trend(out_term, 0))

        return has_new_extr

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
