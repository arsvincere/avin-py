#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

import polars as pl
import tinkoff.invest as ti
from PyQt6 import QtCore, QtWidgets

from avin import (
    Asset,
    BarEvent,
    Chart,
    DateTime,
    Test,
    TicEvent,
    TimeFrame,
    Tinkoff,
    Trade,
    TradeList,
    logger,
    now,
)
from gui.chart.gchart import GChart, ViewType
from gui.chart.gtest import GTradeList
from gui.chart.scene import ChartScene
from gui.chart.thread import Thread
from gui.chart.toolbar import ChartToolBar
from gui.chart.view import ChartView
from gui.custom import Css
from gui.marker import MarkList


class ChartWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

        self.__client = None
        self.__data_thread = None

        self.__asset = None
        self.__timeframe_1 = self.toolbar.firstTimeFrame()
        self.__trade_list = None
        self.__mark_list = None
        self.__ind_list = None

    # }}}

    def setClient(self, client: ti.services.Services) -> None:  # {{{
        self.__client = client

    # }}}
    def setDataThread(self, thread: QtCore.QThread) -> None:  # {{{
        self.__data_thread = thread
        self.__data_thread.new_bar.connect(self.__onNewBar)
        self.__data_thread.new_tic.connect(self.__onNewTic)

    # }}}
    def setAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")

        # clear all & draw chart
        self.clearAll()
        self.__asset = asset
        self.toolbar.setAsset(asset)
        self.__drawChart()
        self.__subscribeDataStream()

    # }}}
    def setTradeList(self, trade_list: TradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setTradeList()")

        self.clearAll()
        self.__trade_list = trade_list
        self.__drawTradeList()

    # }}}
    def showTrade(self, trade: Trade) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.showTrade()")

        self.view.centerOnTrade(trade)

    # }}}
    def clearAll(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearAll()")

        self.__tryUnsubscribe()
        self.scene.removeGChart()
        self.scene.removeGTrades()
        self.scene.removeIndicators()
        self.view.resetTransform()

        self.__mark_list = None
        self.__ind_list = None

        self.toolbar.resetSecondTimeFrames()

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.STYLE)

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.toolbar = ChartToolBar(self)
        self.view = ChartView(self)
        self.scene = ChartScene(self)

        self.view.setScene(self.scene)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.toolbar)
        vbox.addWidget(self.view)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.toolbar.firstTimeFrameChanged.connect(self.__onTimeframe1)
        self.toolbar.secondTimeFrameChanged.connect(self.__onTimeframe2)
        self.toolbar.barViewSelected.connect(self.__onBarView)
        self.toolbar.cundleViewSelected.connect(self.__onCundleView)
        self.toolbar.indListChanged.connect(self.__onIndicatorList)
        self.toolbar.markListChanged.connect(self.__onMarkList)
        self.toolbar.periodChanged.connect(self.__onPeriod)

    # }}}
    def __drawChart(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawChart()")

        timeframe = self.__timeframe_1
        end = now()
        begin = now() - timeframe * Chart.DEFAULT_BARS_COUNT
        bars = Thread.loadBars(self.__asset, timeframe, begin, end)
        bars = self.__getNewBarsFromBroker(bars)

        chart = Chart(self.__asset, timeframe, bars)
        gchart = GChart(chart)

        self.scene.setGChart(gchart)
        self.view.centerOnLast()

    # }}}
    def __drawTradeList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawTradeList()")

        trade_list = self.__trade_list
        test = trade_list.owner
        assert isinstance(test, Test)
        asset = test.asset
        timeframe = self.__timeframe_1
        gtrade_list = GTradeList.fromSelected(test, trade_list, timeframe)

        self.toolbar.resetSecondTimeFrames()
        self.toolbar.setAsset(asset)
        self.scene.setGTradeList(gtrade_list)
        self.view.centerOnFirst()

        self.__asset = asset

    # }}}

    def __getNewBarsFromBroker(  # {{{
        self, bars: pl.DataFrame
    ) -> pl.DataFrame:
        assert len(bars) != 0

        last_dt = bars.item(-1, "dt")
        timeframe = self.__timeframe_1
        begin = last_dt + timeframe
        end = now()

        try:
            candles = self.__client.get_all_candles(
                figi=self.__asset.figi,
                from_=begin,
                to=end,
                interval=Tinkoff.av_to_ti(timeframe, ti.CandleInterval),
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
    def __tryUnsubscribe(self):  # {{{
        if self.__data_thread is None:
            return

        if self.__asset is not None:
            stream = self.__data_thread.stream
            figi = self.__asset.figi
            tf = self.__timeframe_1
            interval = Tinkoff.av_to_ti(tf, ti.SubscriptionInterval)

            subscription = ti.CandleInstrument(figi, interval)
            stream.candles.unsubscribe([subscription])

            subscription = ti.TradeInstrument(figi)
            stream.trades.unsubscribe([subscription])

    # }}}
    def __subscribeDataStream(self):  # {{{
        # subscribe candles & tics
        stream = self.__data_thread.stream
        figi = self.__asset.figi
        tf = self.__timeframe_1
        interval = Tinkoff.av_to_ti(tf, ti.SubscriptionInterval)

        subscription = ti.CandleInstrument(figi, interval)
        stream.candles.subscribe([subscription])

        subscription = ti.TradeInstrument(figi)
        stream.trades.subscribe([subscription])

    # }}}

    @QtCore.pyqtSlot(TimeFrame)  # __onTimeframe1  # {{{
    def __onTimeframe1(self, timeframe: TimeFrame):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe1()")

        self.clearAll()
        self.__timeframe_1 = timeframe

        if self.__trade_list is not None:
            self.__drawTradeList()
            return

        if self.__asset is not None:
            self.__drawChart()
            self.__subscribeDataStream()
            return

    # }}}
    @QtCore.pyqtSlot(TimeFrame, bool)  # __onTimeframe2  # {{{
    def __onTimeframe2(self, timeframe: TimeFrame, endbled: bool):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe2()")

        gchart = self.scene.currentGChart()
        if gchart is None:
            return

        if endbled:
            gchart.drawBack(timeframe)
        else:
            gchart.clearBack(timeframe)

    # }}}
    @QtCore.pyqtSlot()  # __onBarView  # {{{
    def __onBarView(self):
        logger.debug(f"{self.__class__.__name__}.__onBarView()")

        gchart = self.scene.currentGChart()
        if gchart is None:
            return

        gchart.setViewType(ViewType.BAR)

    # }}}
    @QtCore.pyqtSlot()  # __onCundleView  # {{{
    def __onCundleView(self):
        logger.debug(f"{self.__class__.__name__}.__onCundleView()")

        gchart = self.scene.currentGChart()
        if gchart is None:
            return

        gchart.setViewType(ViewType.CUNDLE)

    # }}}
    @QtCore.pyqtSlot(list)  # __onIndicatorList  # {{{
    def __onIndicatorList(self, ind_list: MarkList):
        logger.debug(f"{self.__class__.__name__}.__onIndicatorList()")

        if self.__asset is None:
            return

        self.__ind_list = ind_list

        # добавляем графику индикатора на gchart
        gchart = self.scene.currentGChart()
        for indicator in self.__ind_list:
            gchart.addIndicator(indicator)

        # добавляем график виджет лейблы на сцену в левый верхний угол
        self.scene.setIndList(ind_list)

    # }}}
    @QtCore.pyqtSlot(MarkList)  # __onMarkList  # {{{
    def __onMarkList(self, mark_list: MarkList):
        logger.debug(f"{self.__class__.__name__}.__onMarkList()")

        if self.__asset is None:
            return

        self.__mark_list = mark_list

        gchart = self.scene.currentGChart()
        for mark in mark_list:
            gchart.addMark(mark)

    # }}}
    @QtCore.pyqtSlot(DateTime, DateTime)  # __onPeriod  # {{{
    def __onPeriod(self, begin: DateTime, end: DateTime):
        logger.debug(f"{self.__class__.__name__}.__onPeriod()")

        # NOTE:
        # если перерисовать трейд лист - трейды поедут по датам
        # пока эта функция особо не нужна для трейд листов
        # так что работать будет только если на виджете
        # отображается только график, установлен только ассет
        if self.__trade_list is not None:
            return
        if self.__asset is None:
            return

        timeframe = self.__timeframe_1
        chart = Thread.loadChart(self.__asset, timeframe, begin, end)
        gchart = GChart(chart)

        self.scene.setGChart(gchart)
        self.view.centerOnLast()

    # }}}

    @QtCore.pyqtSlot(BarEvent)  # __onNewBar  # {{{
    def __onNewBar(self, e: BarEvent):
        logger.debug(f"{self.__class__.__name__}.__onNewBar()")

        # INFO:
        # подписка отписка от Т срабатывает с задержкой, может
        # прилететь бар от прошлого графика в момент переключения
        # поэтому проверяем figi и TimeFrame
        if self.__asset.figi != e.figi:
            return
        gchart = self.scene.currentGChart()
        if gchart.chart.timeframe != e.timeframe:
            return

        gchart.receive(e)

    # }}}
    @QtCore.pyqtSlot(BarEvent)  # __onNewTic  # {{{
    def __onNewTic(self, e: TicEvent):
        logger.debug(f"{self.__class__.__name__}.__onNewBar()")
        assert self.__asset.figi == e.figi

        self.__asset.receive(e)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget()
    w.show()
    sys.exit(app.exec())
