#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt, pyqtSlot

from avin.config import Usr
from avin.const import Dir
from avin.core import Account, Asset, Broker, Trade, TradeList
from avin.tester import Test
from avin.utils import Cmd, logger
from gui.asset import AssetListDockWidget
from gui.broker import BrokerDockWidget
from gui.chart import ChartWidget
from gui.console import ConsoleDockWidget
from gui.custom import Css
from gui.data import DataDockWidget
from gui.filter import FilterDockWidget
from gui.main_window.thread import TDataStream
from gui.main_window.toolbar import LeftToolBar, RightToolBar
from gui.strategy import StrategyDockWidget
from gui.summary import SummaryDockWidget
from gui.tester import TesterDockWidget
from gui.tic import TicDockWidget
from gui.trade import TradeDockWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, client=None, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QMainWindow.__init__(self, parent)

        # save client, create data_stream, create & start thread data stream
        self.client = client
        self.data_stream = client.create_market_data_stream()
        self.data_thread = TDataStream(self.data_stream)
        self.data_thread.start()

        # create main window
        self.__splash()
        self.__config()
        # self.__createMdiArea()
        # self.__configMdiArea()
        self.__createToolBars()
        self.__createWidgets()
        self.__connect()
        self.__initUI()

    # }}}

    # def __createMdiArea(self):  # {{{
    #     logger.debug(f"{self.__class__.__name__}.__createMdiArea()")
    #     self.area = QtWidgets.QMdiArea(self)
    #     self.tab1 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab2 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab3 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab4 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab5 = QtWidgets.QMdiSubWindow(self.area)
    #     self.area.addSubWindow(self.tab1)
    #     self.area.addSubWindow(self.tab2)
    #     self.area.addSubWindow(self.tab3)
    #     self.area.addSubWindow(self.tab4)
    #     self.area.addSubWindow(self.tab5)
    #     self.tab1.setWindowTitle("Tester")
    #     self.tab2.setWindowTitle("Sandbox")
    #     self.tab3.setWindowTitle("General")
    #     self.tab4.setWindowTitle("Terminal")
    #     self.tab5.setWindowTitle("Documentation")
    #
    #     self.area.setViewMode(QtWidgets.QMdiArea.ViewMode.TabbedView)
    #     self.area.setTabsMovable(True)
    #     self.area.setTabsClosable(False)
    #     self.area.setActiveSubWindow(self.tab1)
    #
    # }}}
    def __splash(self):  # {{{
        # HACK: хз че за херня, но если тут тоже не вызвать заставку
        # то в hyprland она не отображается. Ее нужно в 2 местах
        # вызвать здесь и в main.py
        # Причем настройки тянутся именно из main.py и заставка
        # от сюда по факту не отображается, но без этого вызова .show()
        # никак. Наверное дело в цикле событий. Нужно как то
        # принудительно сначала вывести заставку а потом грузить дальше
        # но пример из доков Qt с вызовом app.processEvents() не
        # срабатывает.
        # Возможно баг в hyprland, в xfce4 вроде работало из main.py
        # без проблем
        splash = QtWidgets.QSplashScreen()
        splash.show()

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setStyleSheet(Css.STYLE)
        self.setWindowTitle("AVIN  -  Ars  Vincere")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.showMaximized()

        # config dock area
        opt = QtWidgets.QMainWindow.DockOption
        self.setDockOptions(
            opt.AnimatedDocks | opt.AllowNestedDocks | opt.AllowTabbedDocks
            # | opt.ForceTabbedDocks
            # | opt.VerticalTabs
            # | opt.GroupedDragging
        )

        # config dock tab position
        self.setTabPosition(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            QtWidgets.QTabWidget.TabPosition.North,
        )
        self.setTabPosition(
            Qt.DockWidgetArea.RightDockWidgetArea,
            QtWidgets.QTabWidget.TabPosition.North,
        )
        self.setTabPosition(
            Qt.DockWidgetArea.TopDockWidgetArea,
            QtWidgets.QTabWidget.TabPosition.North,
        )
        self.setTabPosition(
            Qt.DockWidgetArea.BottomDockWidgetArea,
            QtWidgets.QTabWidget.TabPosition.North,
        )

        # config the corner of dock areas
        self.setCorner(
            Qt.Corner.TopLeftCorner,
            Qt.DockWidgetArea.LeftDockWidgetArea,
        )
        self.setCorner(
            Qt.Corner.BottomLeftCorner,
            Qt.DockWidgetArea.LeftDockWidgetArea,
        )
        self.setCorner(
            Qt.Corner.TopRightCorner,
            Qt.DockWidgetArea.RightDockWidgetArea,
        )
        self.setCorner(
            Qt.Corner.BottomRightCorner,
            Qt.DockWidgetArea.RightDockWidgetArea,
        )

    # }}}
    def __createToolBars(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createToolBars()")

        self.ltool = LeftToolBar(self)
        self.ltool.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.ltool)

        self.rtool = RightToolBar(self)
        self.rtool.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.rtool)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLeftWidgets()")

        # left
        self.data_widget = None
        self.asset_widget = None
        self.filter_widget = None
        self.strategy_widget = None
        self.tester_widget = None
        self.trade_widget = None
        self.summary_widget = None
        self.console_widget = None

        # right
        self.broker_widget = None
        self.chart_widget = None
        self.tic_widget = None

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        # left tools
        self.ltool.data.triggered.connect(self.__onData)
        self.ltool.asset.triggered.connect(self.__onAsset)
        # self.ltool.analytic.triggered.connect(self.__onAnalytic)
        self.ltool.filter.triggered.connect(self.__onFilter)
        self.ltool.strategy.triggered.connect(self.__onStrategy)
        self.ltool.note.triggered.connect(self.__onNote)
        self.ltool.tester.triggered.connect(self.__onTester)
        self.ltool.trade.triggered.connect(self.__onTrade)
        self.ltool.summary.triggered.connect(self.__onSummary)
        self.ltool.console.triggered.connect(self.__onConsole)
        self.ltool.config.triggered.connect(self.__onConfig)
        self.ltool.shutdown.triggered.connect(self.__onShutdown)

        # right tools
        self.rtool.broker.triggered.connect(self.__onBroker)
        self.rtool.chart.triggered.connect(self.__onChart)
        # self.rtool.book.triggered.connect(self.__onBook)
        self.rtool.tic.triggered.connect(self.__onTic)
        # self.rtool.order.triggered.connect(self.__onOrder)
        # self.rtool.account.triggered.connect(self.__onAccount)
        # self.rtool.trader.triggered.connect(self.__onTrader)
        # self.rtool.report.triggered.connect(self.__onReport)

        # widget signals
        # self.widget_broker.accountSetUp.connect(self.__onAccountSetup)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        # self.ltool.asset.trigger()
        # self.ltool.tester.trigger()
        # self.ltool.console.trigger()
        # self.ltool.summary.trigger()
        self.rtool.chart.trigger()

    # }}}

    @pyqtSlot()  # __onData  # {{{
    def __onData(self):
        logger.debug(f"{self.__class__.__name__}.__onData()")

        if self.data_widget is None:
            self.data_widget = DataDockWidget(self)
            area = Qt.DockWidgetArea.LeftDockWidgetArea
            self.addDockWidget(area, self.data_widget)
            return

        state = self.data_widget.isVisible()
        self.data_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onAsset  # {{{
    def __onAsset(self):
        logger.debug(f"{self.__class__.__name__}.__onAsset()")

        if self.asset_widget is None:
            # create dock widget
            self.asset_widget = AssetListDockWidget(self)
            area = Qt.DockWidgetArea.LeftDockWidgetArea
            self.addDockWidget(area, self.asset_widget)

            # connect signal
            self.asset_widget.widget.assetChanged.connect(
                self.__onAssetChanged
            )
            return

        state = self.asset_widget.isVisible()
        self.asset_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onNote  # {{{
    def __onNote(self):
        logger.debug(f"{self.__class__.__name__}.__onNote()")

        command = (
            Usr.TERMINAL,
            *Usr.OPT,
            Usr.EXEC,
            Usr.EDITOR,
            Usr.NOTE,
        )
        Cmd.subprocess(command)

        btn = self.ltool.widgetForAction(self.ltool.note)
        btn.setChecked(False)

    # }}}
    @pyqtSlot()  # __onFilter  # {{{
    def __onFilter(self):
        logger.debug(f"{self.__class__.__name__}.__onFilter()")

        if self.filter_widget is None:
            self.filter_widget = FilterDockWidget(self)
            area = Qt.DockWidgetArea.LeftDockWidgetArea
            self.addDockWidget(area, self.filter_widget)
            return

        state = self.filter_widget.isVisible()
        self.filter_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onStrategy  # {{{
    def __onStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__onStrategy()")

        if self.strategy_widget is None:
            self.strategy_widget = StrategyDockWidget(self)
            area = Qt.DockWidgetArea.LeftDockWidgetArea
            self.addDockWidget(area, self.strategy_widget)
            return

        state = self.strategy_widget.isVisible()
        self.strategy_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onTester  # {{{
    def __onTester(self):
        logger.debug(f"{self.__class__.__name__}.__onTester()")

        if self.tester_widget is None:
            # create dock widget
            self.tester_widget = TesterDockWidget(self)
            area = Qt.DockWidgetArea.LeftDockWidgetArea
            self.addDockWidget(area, self.tester_widget)

            # connect signal
            self.tester_widget.widget.testChanged.connect(
                self.__onTestChanged
            )
            return

        state = self.tester_widget.isVisible()
        self.tester_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onTrade  # {{{
    def __onTrade(self):
        logger.debug(f"{self.__class__.__name__}.__onTrade()")

        if self.trade_widget is None:
            self.trade_widget = TradeDockWidget(self)
            # area = Qt.DockWidgetArea.LeftDockWidgetArea
            # self.addDockWidget(area, self.tester_widget)
            self.tabifyDockWidget(self.console_widget, self.trade_widget)

            # connect signal
            self.trade_widget.widget.tradeChanged.connect(
                self.__onTradeChanged
            )
            return

        state = self.trade_widget.isVisible()
        self.trade_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onSummary  # {{{
    def __onSummary(self):
        logger.debug(f"{self.__class__.__name__}.__onSummary()")

        if self.summary_widget is None:
            self.summary_widget = SummaryDockWidget(self)
            # area = Qt.DockWidgetArea.BottomDockWidgetArea
            # self.addDockWidget(area, self.summary_widget)
            self.tabifyDockWidget(self.console_widget, self.summary_widget)

            # connect signal
            self.summary_widget.widget.tradeListChanged.connect(
                self.__onTradeListChanged
            )
            return

        state = self.summary_widget.isVisible()
        self.summary_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onConsole  # {{{
    def __onConsole(self):
        logger.debug(f"{self.__class__.__name__}.__onConsole()")

        if self.console_widget is None:
            self.console_widget = ConsoleDockWidget(self)
            area = Qt.DockWidgetArea.BottomDockWidgetArea
            self.addDockWidget(area, self.console_widget)
            return

        state = self.console_widget.isVisible()
        self.console_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onConfig  # {{{
    def __onConfig(self):
        logger.debug(f"{self.__class__.__name__}.__onConfig()")

        config_path = Cmd.path(Dir.LIB, "config.py")
        command = (
            Usr.TERMINAL,
            *Usr.OPT,
            Usr.EXEC,
            Usr.EDITOR,
            config_path,
        )
        Cmd.subprocess(command)

        btn = self.ltool.widgetForAction(self.ltool.config)
        btn.setChecked(False)

    # }}}
    @pyqtSlot()  # __onShutdown  # {{{
    def __onShutdown(self):
        logger.debug(f"{self.__class__.__name__}.__onShutdown()")

        QtWidgets.QApplication.instance().quit()

    # }}}

    @pyqtSlot()  # __onBroker  # {{{
    def __onBroker(self):
        logger.debug(f"{self.__class__.__name__}.__onBroker()")

        if self.broker_widget is None:
            # create dock widget
            self.broker_widget = BrokerDockWidget(self)
            area = Qt.DockWidgetArea.RightDockWidgetArea
            self.addDockWidget(area, self.broker_widget)

            # connect signal
            self.broker_widget.widget.brokerConnected.connect(
                self.__onBrokerConnect
            )
            self.broker_widget.widget.brokerDisconnected.connect(
                self.__onBrokerDisconnect
            )
            self.broker_widget.widget.accountChanged.connect(
                self.__onAccountChanged
            )
            return

        state = self.broker_widget.isVisible()
        self.broker_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onChart  # {{{
    def __onChart(self):
        logger.debug(f"{self.__class__.__name__}.__onChart()")

        if self.chart_widget is None:
            self.chart_widget = ChartWidget(self)
            self.chart_widget.setClient(self.client)
            self.chart_widget.setDataThread(self.data_thread)
            self.setCentralWidget(self.chart_widget)

        state = self.chart_widget.isVisible()
        self.chart_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onTic  # {{{
    def __onTic(self):
        logger.debug(f"{self.__class__.__name__}.__onBroker()")

        if self.tic_widget is None:
            # create dock widget
            self.tic_widget = TicDockWidget(self)
            self.tic_widget.widget.setClient(self.client)
            self.tic_widget.widget.setStream(self.data_stream)
            self.tic_widget.widget.setDataThread(self.data_thread)

            area = Qt.DockWidgetArea.RightDockWidgetArea
            self.addDockWidget(area, self.tic_widget)

            return

        state = self.tic_widget.isVisible()
        self.tic_widget.setVisible(not state)

    # }}}
    @pyqtSlot()  # __onAccount  # {{{
    def __onAccount(self):
        logger.debug(f"{self.__class__.__name__}.__onAccount()")

        assert False

    # }}}
    @pyqtSlot()  # __onOrder  # {{{
    def __onOrder(self):
        logger.debug(f"{self.__class__.__name__}.__onOrder()")

        assert False

    # }}}
    @pyqtSlot()  # __onGeneral  # {{{
    def __onGeneral(self):
        logger.debug(f"{self.__class__.__name__}.__onGeneral()")

        assert False

    # }}}

    @pyqtSlot(Asset)  # __onAssetChanged  # {{{
    def __onAssetChanged(self, asset: Asset):
        logger.debug(f"{self.__class__.__name__}.__onAssetChanged()")
        assert isinstance(asset, Asset)

        if self.chart_widget is not None:
            self.chart_widget.setAsset(asset)

        if self.tic_widget is not None:
            self.tic_widget.widget.setAsset(asset)

    # }}}
    @pyqtSlot(Test)  # __onTestChanged # {{{
    def __onTestChanged(self, test: Test):
        logger.debug(f"{self.__class__.__name__}.__onTestChanged()")

        if self.chart_widget is not None:
            self.chart_widget.clearAll()

        if self.summary_widget is not None:
            self.summary_widget.setTest(test)

    # }}}
    @pyqtSlot(TradeList)  # __onTradeListChanged # {{{
    def __onTradeListChanged(self, trade_list: TradeList):
        logger.debug(f"{self.__class__.__name__}.__onTradeListChanged()")

        if self.chart_widget is not None:
            self.chart_widget.setTradeList(trade_list)

        if self.trade_widget is not None:
            self.trade_widget.setTradeList(trade_list)

    # }}}
    @pyqtSlot(Trade)  # __onTradeChanged  # {{{
    def __onTradeChanged(self, trade: Trade):
        logger.debug(f"{self.__class__.__name__}.__onTradeChanged()")

        if self.chart_widget is not None:
            self.chart_widget.showTrade(trade)

    # }}}
    @pyqtSlot(Broker)  # __onBrokerConnect  # {{{
    def __onBrokerConnect(self, broker: Broker):
        logger.debug(f"{self.__class__.__name__}.__onBrokerConnect()")

        if self.tic_widget is not None:
            self.tic_widget.widget.setBroker(broker)

    # }}}
    @pyqtSlot(Broker)  # __onBrokerDisconnect  # {{{
    def __onBrokerDisconnect(self, broker: Broker):
        logger.debug(f"{self.__class__.__name__}.__onBrokerDisconnect()")

        if self.tic_widget is not None:
            self.tic_widget.widget.clearAll()

        # self.widget_order.disconnectAccount(iaccount)

    # }}}
    @pyqtSlot(Account)  # __onAccountChanged  # {{{
    def __onAccountChanged(self, account: Account):
        logger.debug(f"{self.__class__.__name__}.__onAccountChanged()")

        # self.widget_order.connectAccount(account)
        # self.widget_account.connectAccount(account)

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
