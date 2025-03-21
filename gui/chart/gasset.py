#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import polars as pl
import tinkoff.invest as ti

from avin import (
    Asset,
    Chart,
    Event,
    TimeFrame,
    Tinkoff,
    Tree,
    logger,
    now,
)
from gui.chart.gchart import GChart
from gui.chart.thread import Thread


class GAsset:
    def __init__(self, asset: Asset):
        self.__asset = asset
        self.__gcharts_cache = Tree()
        self.__client = None
        self.__data_thread = None

    @property  # asset  # {{{
    def asset(self):
        return self.__asset

    # }}}
    @property  # figi  # {{{
    def figi(self):
        return self.__asset.figi

    # }}}

    def setClient(self, client: ti.services.Services) -> None:  # {{{
        self.__client = client

    # }}}
    def setDataThread(self, thread: QtCore.QThread) -> None:  # {{{
        self.__data_thread = thread

    # }}}
    def gchart(self, tf: TimeFrame) -> GChart:  # {{{
        # try find in cache
        gchart = self.__gcharts_cache.get(tf, None)
        if gchart is not None:
            return gchart

        # load chart
        bars = self.__loadHistoricalBars(tf)
        bars = self.__getNewBarsFromBroker(bars, tf)
        chart = Chart(self.__asset, tf, bars)
        self.asset.setChart(chart)

        # create gchart
        gchart = GChart(chart, self)
        self.__gcharts_cache[tf] = gchart

        # try subscribe data stream
        self.__subscribeBar(tf)
        self.__subscribeTic()

        return gchart

    # }}}
    def receive(self, e: Event) -> None:  # {{{
        match e.type:
            case Event.Type.BAR:
                self.__receiveBar(e)
            case Event.Type.TIC:
                self.__receiveTic(e)
            case _:
                assert False, f"TODO_ME: Event={e}"

    # }}}
    def clearAll(self) -> None:
        # stop data stream
        for tf in TimeFrame.ALL:
            gchart = self.__gcharts_cache.get(tf, None)
            if gchart is not None:
                self.__unsubscibeBar(tf)
                self.__unsubscibeTic()

        self.__gcharts_cache.clear() 
        self.asset.clearCache() 

    def __loadHistoricalBars(self, tf: TimeFrame) -> pl.DataFrame:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawChart()")

        end = now()
        begin = now() - tf * Chart.DEFAULT_BARS_COUNT
        bars = Thread.loadBars(self.__asset, tf, begin, end)

        return bars

    # }}}
    def __getNewBarsFromBroker(  # {{{
        self,
        bars: pl.DataFrame,
        tf: TimeFrame,
    ) -> pl.DataFrame:
        assert len(bars) != 0

        if self.__client is None:
            logger.warning("No connection, used only historical data")
            return bars

        last_dt = bars.item(-1, "dt")
        begin = last_dt + tf
        end = now()

        try:
            candles = self.__client.get_all_candles(
                figi=self.__asset.figi,
                from_=begin,
                to=end,
                interval=Tinkoff.av_to_ti(tf, ti.CandleInterval),
            )
            for candle in candles:
                if candle.is_complete:
                    bar = Tinkoff.ti_to_av(candle)
                    bars.extend(bar.to_df())
            bars.rechunk()

        except ti.exceptions.AioRequestError as err:
            logger.exception(err)

        return bars

    # }}}
    def __subscribeBar(self, tf: TimeFrame) -> None:  # {{{
        if self.__data_thread is None:
            return

        stream = self.__data_thread.stream
        figi = self.__asset.figi
        interval = Tinkoff.av_to_ti(tf, ti.SubscriptionInterval)

        subscription = ti.CandleInstrument(figi, interval)
        stream.candles.subscribe([subscription])

    # }}}
    def __subscribeTic(self) -> None:  # {{{
        if self.__data_thread is None:
            return

        stream = self.__data_thread.stream
        figi = self.__asset.figi

        subscription = ti.TradeInstrument(figi)
        stream.trades.subscribe([subscription])

    # }}}
    def __unsubscibeBar(self, tf: TimeFrame) -> None:  # {{{
        if self.__data_thread is None:
            return

        stream = self.__data_thread.stream
        figi = self.__asset.figi
        interval = Tinkoff.av_to_ti(tf, ti.SubscriptionInterval)

        subscription = ti.CandleInstrument(figi, interval)
        stream.candles.unsubscribe([subscription])

    # }}}
    def __unsubscibeTic(self) -> None:  # {{{
        if self.__data_thread is None:
            return

        stream = self.__data_thread.stream
        figi = self.__asset.figi

        subscription = ti.TradeInstrument(figi)
        stream.trades.unsubscribe([subscription])

    # }}}
    def __receiveBar(self, event: BarEvent) -> None:  # {{{
        # select gchart
        timeframe = event.timeframe
        gchart = self.gchart(timeframe)

        # send event to gchart
        gchart.receive(event)

    # }}}
    def __receiveTic(self, event: TicEvent) -> None:  # {{{
        assert event.type == Event.Type.TIC
        assert event.figi == self.figi

        # send event to asset
        self.__asset.receive(event)

    # }}}


if __name__ == "__main__":
    ...
