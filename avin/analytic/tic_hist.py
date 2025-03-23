#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import polars as pl

from avin.analytic._analytic import Analytic
from avin.analytic.volume import VolumeAnalytic
from avin.core.bar import Bar
from avin.core.chart import Chart
from avin.core.indicator import Indicator
from avin.core.timeframe import TimeFrame
from avin.utils import UTC, DateTime, Signal, TimeDelta


class Hist(Indicator):
    name = "Hist"
    delay = TimeDelta(seconds=5)  # seconds

    def __init__(self):  # {{{
        super().__init__()
        # data
        self.__schema = {
            "dt": pl.datatypes.Datetime("us", UTC),
            "b_amount": float,
            "s_amount": float,
            "b_lots": int,
            "s_lots": int,
        }
        self.__last_update = DateTime(1, 1, 1, tzinfo=UTC)

        # signals
        self.upd_hist = Signal(Bar, dict)
        self.new_hist = Signal(Bar, dict)

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

    def setChart(self, chart: Chart) -> None:  # {{{
        self.__chart = chart
        self.__asset = chart.asset
        self.__tics = chart.asset.tics
        self.__hist = pl.DataFrame(schema=self.__schema)
        self.__hist_now = dict()

        self.__calcSizes()
        self.__calcHist()
        self.__calcHistNow()
        self.__calcHistSizes()

        # connect
        self.__chart.upd_bar.connect(self.__onRealTimeBar)
        self.__chart.new_bar.connect(self.__onHistoricalBar)

    # }}}
    def historicalHist(self) -> pl.DataFrame:  # {{{
        return self.__hist

    # }}}
    def nowHist(self) -> dict:  # {{{
        return self.__hist_now

    # }}}

    def __calcSizes(self):  # {{{
        sizes = VolumeAnalytic.getSimpleSizes(self.asset, self.timeframe)

        # INFO: например объем XL бара идет
        # Range(1000, 10_000)
        # Но это суммарный, тут же гистограмма отдельно бычий медвежий
        # так как не возможности пока посчитать по тикам... условно
        # считаю что объем в среднем одинаковый бычий и медвежий,
        # тогда надо его поделить на 2 - это будут размеры диапазонов
        # для bear & bull
        self.__sizes = sizes.with_columns(
            begin=pl.col("begin") // 2,
            end=pl.col("end") // 2,
        )

    # }}}
    def __calcHist(self) -> None:  # {{{
        #### dbg begin
        dt = DateTime(2025, 3, 19, tzinfo=UTC)
        df = self.__chart.selectBarsOfDay(dt)
        #### dbg end

        # df = self.__chart.selectTodayBars()
        for row in df.iter_rows(named=True):
            bar = Bar(row, self.__chart)
            hist_of_bar = self.__tics.getHist(bar)
            self.__hist.extend(pl.DataFrame(hist_of_bar))

        self.__hist = self.__hist.rechunk()

    # }}}
    def __calcHistNow(self) -> None:  # {{{
        now_bar = self.__chart.now
        if now_bar is None:
            self.__hist_now = None
            return

        self.__hist_now = self.__tics.getHist(self.__chart.now)

    # }}}
    def __calcHistSizes(self) -> None:  # {{{
        self.__hist = self.__hist.with_columns(
            self.__hist["b_lots"]
            .map_elements(
                lambda x: str(Analytic._identifySimpleSize(x, self.__sizes)),
                return_dtype=pl.Object,  # type = avin.Size
            )
            .alias("b_lots_ssize"),
        )
        self.__hist = self.__hist.with_columns(
            self.__hist["s_lots"]
            .map_elements(
                lambda x: str(Analytic._identifySimpleSize(x, self.__sizes)),
                return_dtype=pl.Object,  # type = avin.Size
            )
            .alias("s_lots_ssize"),
        )

    # }}}
    def __onRealTimeBar(self, bar: Bar):  # {{{
        time = now()
        if time - self.__last_update < self.delay:
            return

        hist = self.__tics.getHist(bar)
        self.__hist_now = hist
        self.__last_update = time

        self.upd_hist.emit(bar, hist)

    # }}}
    def __onHistoricalBar(self, bar: Bar):  # {{{
        new_hist = self.__tics.getHist(bar)
        self.__hist.extend(pl.DataFrame(new_hist))

        self.new_hist.emit(bar, new_hist)

    # }}}


if __name__ == "__main__":
    ...
