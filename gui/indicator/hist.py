#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

import pandas as pd
from PyQt6 import QtCore, QtWidgets

from avin import Cfg, logger
from gui.chart.gchart import GChart
from gui.custom import Css, Icon, Label, Theme, ToolButton
from gui.indicator.item import Indicator, IndicatorItem


class HistIndicator(Indicator):  # {{{
    name = "Hist"
    position = Indicator.Position.FOOTER

    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.gitem = None
        self.__item = None
        self.__label = None
        self.__settings = None

    # }}}

    def item(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.item()")

        if self.__item is None:
            self.__item = IndicatorItem(self)

        return self.__item

    # }}}
    def label(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.label()")

        if self.__label is None:
            self.__label = _HistLabel(self)

        return self.__label

    # }}}
    def graphics(self, gchart: GChart):  # {{{
        logger.debug(f"{self.__class__.__name__}.graphics()")

        self.gchart = gchart
        self.gitem = _HistGraphics(self)

        if self.__settings is None:
            self.__settings = _HistSettings(self)
        self.__settings.configureSilent(self.gitem)

        return self.gitem

    # }}}
    def configure(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure()")

        if self.__settings is None:
            self.__settings = _HistSettings(self)

        self.__settings.configure(self.gitem)

    # }}}


# }}}


class _HistGraphics(QtWidgets.QGraphicsItemGroup):  # {{{
    HEIGHT = 150
    INDENT = Cfg.Chart.BAR_INDENT
    WIDTH = Cfg.Chart.BAR_WIDTH

    flags = QtWidgets.QGraphicsItem.GraphicsItemFlag
    ignore_transformation = flags.ItemIgnoresTransformations

    def __init__(self, indicator: HistIndicator, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.indicator = indicator
        self.gchart = indicator.gchart

        self.__getTics()
        self.__calcMaxAmount()
        self.__createFrame()
        self.__createHist()

        # TODO: здесь надо только одну ось игнорить...
        # self.setFlag(self.ignore_transformation)

    # }}}

    def __getTics(self) -> None:  # {{{
        asset = self.gchart.chart.instrument
        self.hist = asset.tics.hist(self.gchart.chart.timeframe)

    # }}}
    def __calcMaxAmount(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")

        if self.hist is None:
            return

        max_amount_buy = self.hist["buy"].max()
        max_amount_sell = self.hist["sell"].max()
        self.max_amount = float(max(max_amount_buy, max_amount_sell))

    # }}}
    def __createFrame(self) -> None:  # {{{
        x0 = 0
        y0 = -self.HEIGHT
        width = self.gchart.rect.width()
        height = self.HEIGHT

        self.frame = QtWidgets.QGraphicsRectItem(x0, y0, width, height)
        self.frame.setPen(Theme.Chart.BG_FOOTER)
        self.frame.setBrush(Theme.Chart.BG_FOOTER)
        self.addToGroup(self.frame)

    # }}}
    def __createHist(self) -> None:  # {{{
        hist = self.hist
        if hist is None:
            return

        for i, row in hist.iterrows():
            self.__createHistBar(row)

    # }}}
    def __createHistBar(self, hist_bar: pd.Series) -> None:  # {{{
        # alias
        gchart = self.gchart
        dt = hist_bar["dt"]
        buy = hist_bar["buy"]
        sell = hist_bar["sell"]

        # coordinate
        gbar = gchart.gbarFromDatetime(dt)
        x0 = gbar.x0_cundle
        x1 = gbar.x1_cundle
        width = x1 - x0

        y0 = -self.HEIGHT / 2
        height_buy = float(buy) / self.max_amount * self.HEIGHT / 2
        height_sell = float(sell) / self.max_amount * self.HEIGHT / 2

        # graphics item
        buy_body = QtWidgets.QGraphicsRectItem(x0, y0, width, -height_buy)
        buy_body.setPen(Theme.Chart.BULL)
        buy_body.setBrush(Theme.Chart.BULL)

        sell_body = QtWidgets.QGraphicsRectItem(x0, y0, width, height_sell)
        sell_body.setPen(Theme.Chart.BEAR)
        sell_body.setBrush(Theme.Chart.BEAR)

        self.addToGroup(buy_body)
        self.addToGroup(sell_body)

    # }}}

    # def __loadHist(self) -> None:  # {{{
    #     """self.hist = DataFrame
    #                          dt          buy         sell
    #     0   2025-03-06 06:59:34    8421750.0    5790060.0
    #     """
    #
    #     # XXX: говнокод, график должен все таки ссылаться на Asset
    #     # а не на Instrument, и через Asset надо загружать тики
    #     # но пока похую, и не раскидывать тут детали в духе .parquet
    #     # мало ли как еще переименую файлы...
    #     last_date = self.gchart.chart.now.dt.date()
    #     file_name = f"{last_date} tic.parquet"
    #     file_path = Cmd.path(
    #         self.gchart.chart.instrument.path,
    #         DataType.TIC.name,
    #         file_name,
    #     )
    #     if not Cmd.isExist(file_path):
    #         self.hist = None
    #         logger.warning(f"Tic data not found: {file_path}")
    #         return
    #
    #     df = pd.read_parquet(file_path)
    #     tics = Tics(self.gchart.chart.instrument, df)
    #     tf = self.gchart.chart.timeframe
    #     self.hist = tics.hist(tf)
    #
    # # }}}


# }}}
class _HistLabel(QtWidgets.QWidget):  # {{{
    def __init__(self, indicator, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__indicator = indicator
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    # }}}

    @property  # indicator  # {{{
    def indicator(self):
        return self.__indicator

    # }}}

    def setGChart(self, gchart):  # {{{
        self.gchart = gchart

    # }}}
    def update(self, x):  # {{{
        pass

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.label_name = QtWidgets.QLabel(self.__indicator.name)
        self.btn_hide = ToolButton(Icon.HIDE, width=16, height=16)
        self.btn_settings = ToolButton(Icon.CONFIG, width=16, height=16)
        self.btn_delete = ToolButton(Icon.DELETE, width=16, height=16)

        self.info_5m = Label("5M")
        self.info_1h = Label("1H")
        self.info_d = Label("D")

        self.info_5m.setStyleSheet(Css.CHART_LABEL)
        self.info_1h.setStyleSheet(Css.CHART_LABEL)
        self.info_d.setStyleSheet(Css.CHART_LABEL)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.label_name)
        hbox.addWidget(self.btn_hide)
        hbox.addWidget(self.btn_settings)
        hbox.addWidget(self.btn_delete)
        hbox.addStretch()
        hbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(hbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_settings.clicked.connect(self.__onSettings)

    # }}}

    @QtCore.pyqtSlot()  # __onSettings  # {{{
    def __onSettings(self):
        logger.debug(f"{self.__class__.__name__}.__onSettings()")

        self.indicator.configure()

    # }}}


# }}}
class _HistSettings(QtWidgets.QDialog):  # {{{
    def __init__(self, indicator, parent=None):  # {{{
        QtWidgets.QDialog.__init__(self, parent)
        self.__indicator = indicator

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    # }}}

    @property  # indicator  # {{{
    def indicator(self):
        return self.__indicator

    # }}}

    def configureSilent(self, gextr: _HistGraphics):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure")

    # }}}
    def configure(self, gextr):  # {{{
        logger.debug(f"{self.__class__.__name__}.showSettings")

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.DIALOG)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.title_label = Label("| Extremum settings:", parent=self)
        self.title_label.setStyleSheet(Css.TITLE)

        self.ok_btn = ToolButton(Icon.OK)
        self.cancel_btn = ToolButton(Icon.CANCEL)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox_btn = QtWidgets.QHBoxLayout()
        hbox_btn.addWidget(self.title_label)
        hbox_btn.addStretch()
        hbox_btn.addWidget(self.ok_btn)
        hbox_btn.addWidget(self.cancel_btn)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(hbox_btn)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    indicator = ExtremumIndicator()
    w = _HistSettings(indicator)
    w.show()
    sys.exit(app.exec())
