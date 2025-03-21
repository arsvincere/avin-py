#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

import tinkoff.invest as ti
from PyQt6 import QtCore, QtWidgets

from avin import (
    Asset,
    BarEvent,
    DateTime,
    Test,
    TicEvent,
    TimeFrame,
    Trade,
    TradeList,
    logger,
)
from gui.chart.gasset import GAsset
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

        self.__gasset = None
        self.__timeframe_1 = self.__toolbar.firstTimeFrame()
        self.__trade_list = None
        self.__mark_list = list()
        self.__ind_list = list()

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

        # clear asset (data stream, gcharts, charts)
        if self.__gasset is not None:
            self.__gasset.clearAll()
            self.__gasset = None

        # clear all: toolbar, scene, indicators, view reset transformation...
        self.clearAll()

        # set new asset
        self.__toolbar.setAsset(asset)
        self.__gasset = GAsset(asset)
        self.__gasset.setClient(self.__client)
        self.__gasset.setDataThread(self.__data_thread)

        # draw chart
        self.__drawChart()
        self.__drawIndicators()

    # }}}
    def setTradeList(self, trade_list: TradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setTradeList()")

        self.clearAll()
        self.__trade_list = trade_list
        self.__drawTradeList()

    # }}}
    def showTrade(self, trade: Trade) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.showTrade()")

        self.__view.centerOnTrade(trade)

    # }}}
    def clearAll(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearAll()")

        # clear indicators
        gchart = self.__scene.currentGChart()
        if gchart is not None:
            gchart.clearIndicators()

        self.__scene.removeAll()
        self.__view.resetTransform()
        self.__toolbar.resetSecondTimeFrames()
        self.__mark_list.clear()

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.STYLE)

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__toolbar = ChartToolBar(self)
        self.__view = ChartView(self)
        self.__scene = ChartScene(self)

        self.__view.setScene(self.__scene)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__toolbar)
        vbox.addWidget(self.__view)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__toolbar.firstTimeFrameChanged.connect(self.__onTimeframe1)
        self.__toolbar.secondTimeFrameChanged.connect(self.__onTimeframe2)
        self.__toolbar.barViewSelected.connect(self.__onBarView)
        self.__toolbar.cundleViewSelected.connect(self.__onCundleView)
        self.__toolbar.indListChanged.connect(self.__onIndicatorList)
        self.__toolbar.markListChanged.connect(self.__onMarkList)
        self.__toolbar.periodChanged.connect(self.__onPeriod)

    # }}}
    def __drawChart(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawChart()")

        timeframe = self.__timeframe_1
        gchart = self.__gasset.gchart(timeframe)

        self.__scene.setGChart(gchart)
        self.__view.centerOnLast()

    # }}}
    def __drawTradeList(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__drawTradeList()")

        trade_list = self.__trade_list
        test = trade_list.owner
        assert isinstance(test, Test)
        asset = test.asset
        timeframe = self.__timeframe_1
        gtrade_list = GTradeList.fromSelected(test, trade_list, timeframe)

        self.__toolbar.resetSecondTimeFrames()
        self.__toolbar.setAsset(asset)
        self.__scene.setGTradeList(gtrade_list)
        self.__view.centerOnFirst()

        self.__asset = asset

    # }}}
    def __drawIndicators(self) -> None:  # {{{
        # добавляем графику индикатора на gchart
        gchart = self.__scene.currentGChart()
        for indicator_class in self.__ind_list:
            indicator = indicator_class()
            gchart.addIndicator(indicator)

            # добавляем виджет лейблы на сцену
            self.__scene.addIndicator(indicator)

    # }}}

    @QtCore.pyqtSlot(TimeFrame)  # __onTimeframe1  # {{{
    def __onTimeframe1(self, timeframe: TimeFrame):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe1()")

        self.clearAll()
        self.__timeframe_1 = timeframe

        if self.__trade_list is not None:
            self.__drawTradeList()
            self.__drawIndicators()
            return

        if self.__gasset is not None:
            self.__drawChart()
            self.__drawIndicators()
            return

    # }}}
    @QtCore.pyqtSlot(TimeFrame, bool)  # __onTimeframe2  # {{{
    def __onTimeframe2(self, timeframe: TimeFrame, endbled: bool):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe2()")

        gchart = self.__scene.currentGChart()
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

        gchart = self.__scene.currentGChart()
        if gchart is None:
            return

        gchart.setViewType(ViewType.BAR)

    # }}}
    @QtCore.pyqtSlot()  # __onCundleView  # {{{
    def __onCundleView(self):
        logger.debug(f"{self.__class__.__name__}.__onCundleView()")

        gchart = self.__scene.currentGChart()
        if gchart is None:
            return

        gchart.setViewType(ViewType.CUNDLE)

    # }}}
    @QtCore.pyqtSlot(list)  # __onIndicatorList  # {{{
    def __onIndicatorList(self, ind_list: MarkList):
        logger.debug(f"{self.__class__.__name__}.__onIndicatorList()")

        self.clearAll()
        self.__ind_list = ind_list

        if self.__gasset is not None:
            self.__drawChart()
            self.__drawIndicators()
            return

    # }}}
    @QtCore.pyqtSlot(MarkList)  # __onMarkList  # {{{
    def __onMarkList(self, mark_list: MarkList):
        logger.debug(f"{self.__class__.__name__}.__onMarkList()")

        if self.__asset is None:
            return

        self.__mark_list = mark_list

        gchart = self.__scene.currentGChart()
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

        self.__scene.setGChart(gchart)
        self.__view.centerOnLast()

    # }}}

    @QtCore.pyqtSlot(BarEvent)  # __onNewBar  # {{{
    def __onNewBar(self, e: BarEvent):
        logger.debug(f"{self.__class__.__name__}.__onNewBar()")

        # INFO:
        # подписка отписка от Т срабатывает с задержкой, может
        # прилететь бар от прошлого графика в момент переключения
        # поэтому проверяем figi
        if self.__gasset.figi != e.figi:
            return

        self.__gasset.receive(e)

    # }}}
    @QtCore.pyqtSlot(BarEvent)  # __onNewTic  # {{{
    def __onNewTic(self, e: TicEvent):
        logger.debug(f"{self.__class__.__name__}.__onNewBar()")

        # INFO:
        # подписка отписка от Т срабатывает с задержкой, может
        # прилететь тик от прошлого ассета в момент переключения
        # поэтому проверяем figi
        if self.__gasset.figi != e.figi:
            return

        self.__gasset.receive(e)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget()
    w.show()
    sys.exit(app.exec())
