#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from avin import ExtremumList, Move, Term, TimeFrame, Tree, Trend, logger
from gui.chart.gchart import GBar, GChart
from gui.chart.indicator_item import IndicatorItem
from gui.custom import Css, Icon, Label, MonoLabel, Theme, ToolButton
from gui.indicator._indicator import Indicator


class ExtremumIndicator:  # {{{
    name = "Extremum"
    position = Indicator.Position.CHART

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
            self.__label = _ExtremumLabel(self)

        return self.__label

    # }}}
    def graphics(self, gchart: GChart):  # {{{
        logger.debug(f"{self.__class__.__name__}.graphics()")

        self.gitem = _ExtremumGraphics(gchart)

        if self.__settings is None:
            self.__settings = _ExtremumSettings(self)

        self.__settings.configureSilent(self.gitem)
        return self.gitem

    # }}}
    def configure(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure()")

        if self.__settings is None:
            self.__settings = _ExtremumSettings(self)

        self.__settings.configure(self.gitem)

    # }}}


# }}}
class _ExtremumLabel(QtWidgets.QWidget):  # {{{
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
        # 5M S p=5/BIG  d=15.5/NORMAL  s=3.1/SMALL  v=1000/VERY_BIG
        # 5M M p=5/BIG  d=15.5/NORMAL  s=3.1/SMALL  v=1000/VERY_BIG
        # 5M L p=5/BIG  d=15.5/NORMAL  s=3.1/SMALL  v=1000/VERY_BIG
        # 1H S p=5/BIG  d=15.5/NORMAL  s=3.1/SMALL  v=1000/VERY_BIG
        # 1H ...

        self.gitem = self.__indicator.gitem

        # if self.gitem.gelist_5m is not None:
        #     string = self.gitem.gelist_5m.getInfo(x)
        #     self.info_5m.setText(string)
        #
        # if self.gitem.gelist_1h is not None:
        #     string = self.gitem.gelist_1h.getInfo(x)
        #     self.info_1h.setText(string)
        #
        # if self.gitem.gelist_d is not None:
        #     string = self.gitem.gelist_d.getInfo(x)
        #     self.info_d.setText(string)

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.label_name = QtWidgets.QLabel("Extremum")
        self.btn_hide = ToolButton(Icon.HIDE, width=16, height=16)
        self.btn_settings = ToolButton(Icon.CONFIG, width=16, height=16)
        self.btn_delete = ToolButton(Icon.DELETE, width=16, height=16)

        self.info_5m = Label("1M")
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

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.info_5m)
        vbox.addWidget(self.info_1h)
        vbox.addWidget(self.info_d)

        self.setLayout(vbox)

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
class _ExtremumSettings(QtWidgets.QDialog):  # {{{
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

    def configureSilent(self, gextr: _ExtremumGraphics):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure")

        t1 = Term.T1
        t2 = Term.T2
        t3 = Term.T3
        t4 = Term.T4
        t5 = Term.T5

        tf = TimeFrame("1M")
        gextr.setTrend(tf, t1, self.trend_1m_t1.isChecked())
        gextr.setTrend(tf, t2, self.trend_1m_t2.isChecked())
        gextr.setTrend(tf, t3, self.trend_1m_t3.isChecked())
        gextr.setTrend(tf, t4, self.trend_1m_t4.isChecked())
        gextr.setTrend(tf, t5, self.trend_1m_t5.isChecked())

        tf = TimeFrame("5M")
        gextr.setTrend(tf, t1, self.trend_5m_t1.isChecked())
        gextr.setTrend(tf, t2, self.trend_5m_t2.isChecked())
        gextr.setTrend(tf, t3, self.trend_5m_t3.isChecked())
        gextr.setTrend(tf, t4, self.trend_5m_t4.isChecked())
        gextr.setTrend(tf, t5, self.trend_5m_t5.isChecked())

        tf = TimeFrame("1H")
        gextr.setTrend(tf, t1, self.trend_1h_t1.isChecked())
        gextr.setTrend(tf, t2, self.trend_1h_t2.isChecked())
        gextr.setTrend(tf, t3, self.trend_1h_t3.isChecked())
        gextr.setTrend(tf, t4, self.trend_1h_t4.isChecked())
        gextr.setTrend(tf, t5, self.trend_1h_t5.isChecked())

        tf = TimeFrame("D")
        gextr.setTrend(tf, t1, self.trend_d_t1.isChecked())
        gextr.setTrend(tf, t2, self.trend_d_t2.isChecked())
        gextr.setTrend(tf, t3, self.trend_d_t3.isChecked())
        gextr.setTrend(tf, t4, self.trend_d_t4.isChecked())
        gextr.setTrend(tf, t5, self.trend_d_t5.isChecked())

    # }}}
    def configure(self, gextr):  # {{{
        logger.debug(f"{self.__class__.__name__}.showSettings")

        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Rejected:
            return

        if gextr is None:
            return

        self.configureSilent(gextr)

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.DIALOG)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.title_label = Label(
            f"| {self.indicator.name} settings:", parent=self
        )
        self.title_label.setStyleSheet(Css.TITLE)
        self.ok_btn = ToolButton(Icon.OK)
        self.cancel_btn = ToolButton(Icon.CANCEL)

        self.trend_1m_t1 = QtWidgets.QCheckBox("T1")
        self.trend_1m_t2 = QtWidgets.QCheckBox("T2")
        self.trend_1m_t3 = QtWidgets.QCheckBox("T3")
        self.trend_1m_t4 = QtWidgets.QCheckBox("T4")
        self.trend_1m_t5 = QtWidgets.QCheckBox("T5")

        self.trend_5m_t1 = QtWidgets.QCheckBox("T1")
        self.trend_5m_t2 = QtWidgets.QCheckBox("T2")
        self.trend_5m_t3 = QtWidgets.QCheckBox("T3")
        self.trend_5m_t4 = QtWidgets.QCheckBox("T4")
        self.trend_5m_t5 = QtWidgets.QCheckBox("T5")

        self.trend_1h_t1 = QtWidgets.QCheckBox("T1")
        self.trend_1h_t2 = QtWidgets.QCheckBox("T2")
        self.trend_1h_t3 = QtWidgets.QCheckBox("T3")
        self.trend_1h_t4 = QtWidgets.QCheckBox("T4")
        self.trend_1h_t5 = QtWidgets.QCheckBox("T5")

        self.trend_d_t1 = QtWidgets.QCheckBox("T1")
        self.trend_d_t2 = QtWidgets.QCheckBox("T2")
        self.trend_d_t3 = QtWidgets.QCheckBox("T3")
        self.trend_d_t4 = QtWidgets.QCheckBox("T4")
        self.trend_d_t5 = QtWidgets.QCheckBox("T5")

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox_title = QtWidgets.QHBoxLayout()
        hbox_title.addWidget(self.title_label)
        hbox_title.addStretch()
        hbox_title.addWidget(self.ok_btn)
        hbox_title.addWidget(self.cancel_btn)

        hbox_trend_1m = QtWidgets.QHBoxLayout()
        hbox_trend_1m.addWidget(MonoLabel("Trend 1M: "))
        hbox_trend_1m.addWidget(self.trend_1m_t1)
        hbox_trend_1m.addWidget(self.trend_1m_t2)
        hbox_trend_1m.addWidget(self.trend_1m_t3)
        hbox_trend_1m.addWidget(self.trend_1m_t4)
        hbox_trend_1m.addWidget(self.trend_1m_t5)

        hbox_trend_5m = QtWidgets.QHBoxLayout()
        hbox_trend_5m.addWidget(MonoLabel("Trend 5M: "))
        hbox_trend_5m.addWidget(self.trend_5m_t1)
        hbox_trend_5m.addWidget(self.trend_5m_t2)
        hbox_trend_5m.addWidget(self.trend_5m_t3)
        hbox_trend_5m.addWidget(self.trend_5m_t4)
        hbox_trend_5m.addWidget(self.trend_5m_t5)

        hbox_trend_1h = QtWidgets.QHBoxLayout()
        hbox_trend_1h.addWidget(MonoLabel("Trend 1H: "))
        hbox_trend_1h.addWidget(self.trend_1h_t1)
        hbox_trend_1h.addWidget(self.trend_1h_t2)
        hbox_trend_1h.addWidget(self.trend_1h_t3)
        hbox_trend_1h.addWidget(self.trend_1h_t4)
        hbox_trend_1h.addWidget(self.trend_1h_t5)

        hbox_trend_d = QtWidgets.QHBoxLayout()
        hbox_trend_d.addWidget(MonoLabel("Trend  D: "))
        hbox_trend_d.addWidget(self.trend_d_t1)
        hbox_trend_d.addWidget(self.trend_d_t2)
        hbox_trend_d.addWidget(self.trend_d_t3)
        hbox_trend_d.addWidget(self.trend_d_t4)
        hbox_trend_d.addWidget(self.trend_d_t5)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(hbox_title)
        vbox.addSpacing(10)
        vbox.addLayout(hbox_trend_1m)
        vbox.addLayout(hbox_trend_5m)
        vbox.addLayout(hbox_trend_1h)
        vbox.addLayout(hbox_trend_d)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        # self.sshape_checkbox.setChecked(False)
        # self.mshape_checkbox.setChecked(False)
        # self.lshape_checkbox.setChecked(False)

    # }}}


# }}}
class _ExtremumGraphics(QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(self, gchart: GChart, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        # self.gchart = gchart
        # self.chart = gchart.chart
        self.gasset = gchart.gasset
        self.cache = Tree()

    # }}}

    def setTrend(  # {{{
        self, tf: TimeFrame, term: Term, visible: bool
    ) -> None:
        gtrends = self.__getGTrend(tf, term)
        gtrends.setVisible(visible)

    # }}}
    def setMove(  # {{{
        self, tf: TimeFrame, term: Term, visible: bool
    ) -> None:
        gmoves = self.__getGMove(tf, term)
        gmoves.setVisible(visible)

    # }}}
    def getInfo(self, x):  # {{{
        string = ""

        # TODO: binary search

        for line in self.gs_trends.childItems():
            if self.__xInLine(x, line):
                string += line.getTextInfo()

        for line in self.gm_trends.childItems():
            if self.__xInLine(x, line):
                string += "\n"
                string += line.getTextInfo()

        for line in self.gl_trends.childItems():
            if self.__xInLine(x, line):
                string += "\n"
                string += line.getTextInfo()

        return string

    # }}}

    def __getGTrend(self, tf, term) -> QtWidgets.QGraphicsItemGroup:  # {{{
        # try find in cache
        gtrends = self.cache[tf][term]
        if gtrends:
            return gtrends

        # load chart & create elist -> create graphic trends
        gchart = self.gasset.gchart(tf)
        elist = ExtremumList(gchart.chart)
        gtrends = self.__createGTrends(gchart, elist, term)

        # add to self, and save in cache
        self.addToGroup(gtrends)
        self.cache[tf][term] = gtrends

        return gtrends

    # }}}
    def __getGMove(self, tf, term) -> QtWidgets.QGraphicsItemGroup:  # {{{
        pass

    # }}}
    def __createGTrends(self, gchart, elist, term):  # {{{
        trends = elist.getAllTrends(term)

        gtrends = QtWidgets.QGraphicsItemGroup()
        for trend in trends:
            gtrend = _GTrend(gchart, trend)
            gtrends.addToGroup(gtrend)

        return gtrends

    # }}}
    def __createGMoves(self):  # {{{
        self.gs_moves = QtWidgets.QGraphicsItemGroup()
        self.s_moves = self.elist.getAllMoves(Term.T1)
        for move in self.s_moves:
            gmove = _GMove(self.gchart, move)
            self.gs_moves.addToGroup(gmove)

        self.gm_moves = QtWidgets.QGraphicsItemGroup()
        self.m_moves = self.elist.getAllMoves(Term.T2)
        for move in self.m_moves:
            gmove = _GMove(self.gchart, move)
            self.gm_moves.addToGroup(gmove)

        self.gl_moves = QtWidgets.QGraphicsItemGroup()
        self.l_moves = self.elist.getAllMoves(Term.T3)
        for move in self.l_moves:
            gmove = _GMove(self.gchart, move)
            self.gl_moves.addToGroup(gmove)

        self.addToGroup(self.gs_moves)
        self.addToGroup(self.gm_moves)
        self.addToGroup(self.gl_moves)

    # }}}

    def __xInLine(self, x, line: _GTrend):  # {{{
        logger.debug(f"{self.__class__.__name__}.__xInTrend()")

        if line.begin_pos.x() < x < line.end_pos.x():
            return True

        return False

    # }}}


# }}}
class _GMove(QtWidgets.QGraphicsItemGroup):  # {{{
    T1_WIDTH = 1
    T2_WIDTH = 2
    T3_WIDTH = 3

    COLOR_BEAR = Theme.Chart.VAWE_BEAR
    COLOR_BULL = Theme.Chart.VAWE_BULL

    def __init__(  # {{{
        self, gchart: GChart, move: Move, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gchart = gchart
        self.move = move

        self.__createLines()

    # }}}

    def __createLines(self):  # {{{
        match str(self.move.type.name):
            case "BEAR":
                color = self.COLOR_BEAR
            case "BULL":
                color = self.COLOR_BULL

        match self.move.term:
            case Term.T1:
                width = self.T1_WIDTH
            case Term.T2:
                width = self.T2_WIDTH
            case Term.T3:
                width = self.T3_WIDTH

        for trend in self.move.getTrends():
            gtrend = _GTrend(self.gchart, trend)
            gtrend.setPen(QtGui.QPen(color, width))
            self.addToGroup(gtrend)

    # }}}


# }}}
class _GTrend(QtWidgets.QGraphicsItemGroup):  # {{{
    T1_WIDTH = 1
    T2_WIDTH = 2
    T3_WIDTH = 3
    T4_WIDTH = 4
    T5_WIDTH = 5

    COLOR_1M = Theme.Chart.TREND_5M
    COLOR_5M = Theme.Chart.TREND_5M
    COLOR_1H = Theme.Chart.TREND_1H
    COLOR_D = Theme.Chart.TREND_D
    COLOR_W = Theme.Chart.TREND_D
    COLOR_M = Theme.Chart.TREND_D

    def __init__(  # {{{
        self, gchart: GChart, trend: Trend, parent=None
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gchart = gchart
        self.trend = trend

        self.__calcCoordinates()
        self.__createLine()

    # }}}

    def getTextInfo(self) -> str:  # {{{
        logger.debug(f"{self.__class__.__name__}.getTextInfo()")

        t = self.trend
        volume = t.volume()
        vol_str = f"{(t.volume() / 1_000_000):.2f}m"

        string = (
            f"{str(t.timeframe):<2} "
            f"{t.term.name[0:2]:<2} "
            f"{t.type.name} "
            f"p={t.period():<3} "
            f"d={t.deltaPercent():<6} "
            f"s={t.speedPercent():<6} "
            f"v={vol_str} "
            f"{t.strength.name[0:1]} "
        )
        return string

    # }}}
    def setPen(self, pen: QtGui.QPen):  # {{{
        self.line.setPen(pen)

    # }}}

    def __calcCoordinates(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")

        # begin pos
        x0 = self.gchart.xFromDatetime(self.trend.begin.dt)
        x = x0 + GBar.WIDTH / 2
        y = self.gchart.yFromPrice(self.trend.begin.price)
        self.begin_pos = QtCore.QPointF(x, y)

        # end pos
        x0 = self.gchart.xFromDatetime(self.trend.end.dt)
        x = x0 + GBar.WIDTH / 2
        y = self.gchart.yFromPrice(self.trend.end.price)
        self.end_pos = QtCore.QPointF(x, y)

    # }}}
    def __createLine(self):  # {{{
        match str(self.trend.timeframe):
            case "1M":
                color = self.COLOR_1M
            case "5M":
                color = self.COLOR_5M
            case "1H":
                color = self.COLOR_1H
            case "D":
                color = self.COLOR_D
            case "W":
                color = self.COLOR_W
            case "M":
                color = self.COLOR_M
            case _:
                assert False, f"TODO_ME??? {self.trend.timeframe}"

        match self.trend.term:
            case Term.T1:
                width = self.T1_WIDTH
            case Term.T2:
                width = self.T2_WIDTH
            case Term.T3:
                width = self.T3_WIDTH
            case Term.T4:
                width = self.T3_WIDTH
            case Term.T5:
                width = self.T3_WIDTH
            case _:
                assert False, f"??? {self.trend.term}"

        self.line = QtWidgets.QGraphicsLineItem(
            self.begin_pos.x(),
            self.begin_pos.y(),
            self.end_pos.x(),
            self.end_pos.y(),
        )
        pen = QtGui.QPen(color, width)
        self.line.setPen(pen)

        self.addToGroup(self.line)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    indicator = ExtremumIndicator()
    w = _ExtremumSettings(indicator)
    w.show()
    sys.exit(app.exec())
