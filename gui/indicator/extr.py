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

from avin import (
    ExtremumList,
    Signal,
    Term,
    Tree,
    Trend,
    TrendAnalytic,
    logger,
)
from gui.chart.gchart import GBar, GChart
from gui.custom import Css, Icon, Label, MonoLabel, Theme, ToolButton
from gui.indicator._indicator import GIndicator


class GExtremumIndicator(GIndicator):  # {{{
    name = "Extremum"
    position = GIndicator.Position.CHART
    graphics_updated = Signal(QtWidgets.QGraphicsItemGroup)

    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.indicator = ExtremumList()
        self.gitem = None
        self.__label = None
        self.__settings = None

    # }}}

    def label(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.label()")

        if self.__label is None:
            self.__label = _Label(self)

        return self.__label

    # }}}
    def graphics(self, gchart: GChart):  # {{{
        logger.debug(f"{self.__class__.__name__}.graphics()")

        self.gitem = _Graphics(self, gchart)
        if self.__settings is None:
            self.__settings = _Settings(self)
        self.__settings.configureSilent(self.gitem)
        return self.gitem

    # }}}
    def configure(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure()")

        if self.__settings is None:
            self.__settings = _Settings(self)

        self.__settings.configure(self.gitem)

    # }}}


# }}}
class _Label(QtWidgets.QWidget):  # {{{
    def __init__(self, gind, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__gindicator = gind
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    # }}}

    @property  # gindicator  # {{{
    def gindicator(self):
        return self.__gindicator

    # }}}

    def updateInfo(self, pos: QtCore.QPointF):  # {{{
        x = pos.x()
        gitem = self.__gindicator.gitem
        if gitem is None:
            return

        string = gitem.getInfo(x)
        self.info.setText(string)

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.label_name = QtWidgets.QLabel("Extremum")
        self.btn_hide = ToolButton(Icon.HIDE, width=16, height=16)
        self.btn_settings = ToolButton(Icon.CONFIG, width=16, height=16)
        self.btn_delete = ToolButton(Icon.DELETE, width=16, height=16)

        self.info = Label("")
        self.t1 = ToolButton(text="T1", width=24, height=24)
        self.t2 = ToolButton(text="T2", width=24, height=24)
        self.t3 = ToolButton(text="T3", width=24, height=24)
        self.t4 = ToolButton(text="T4", width=24, height=24)
        self.t5 = ToolButton(text="T5", width=24, height=24)
        self.t1.setCheckable(True)
        self.t2.setCheckable(True)
        self.t3.setCheckable(True)
        self.t4.setCheckable(True)
        self.t5.setCheckable(True)

        self.info.setStyleSheet(Css.CHART_LABEL)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox_title = QtWidgets.QHBoxLayout()
        hbox_title.addWidget(self.label_name)
        hbox_title.addWidget(self.btn_hide)
        hbox_title.addWidget(self.btn_settings)
        hbox_title.addWidget(self.btn_delete)
        hbox_title.addStretch()
        hbox_title.setContentsMargins(0, 0, 0, 0)

        hbox_info = QtWidgets.QHBoxLayout()
        hbox_info.addWidget(self.t1)
        hbox_info.addWidget(self.t2)
        hbox_info.addWidget(self.t3)
        hbox_info.addWidget(self.t4)
        hbox_info.addWidget(self.t5)
        hbox_info.addWidget(self.info)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox_title)
        vbox.addLayout(hbox_info)

        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_settings.clicked.connect(self.__onSettings)

        self.t1.clicked.connect(self.__onT1)
        self.t2.clicked.connect(self.__onT2)
        self.t3.clicked.connect(self.__onT3)
        self.t4.clicked.connect(self.__onT4)
        self.t5.clicked.connect(self.__onT5)

    # }}}

    @QtCore.pyqtSlot()  # __onSettings  # {{{
    def __onSettings(self):
        logger.debug(f"{self.__class__.__name__}.__onSettings()")

        self.gindicator.configure()

    # }}}
    @QtCore.pyqtSlot()  # __onT1  # {{{
    def __onT1(self):
        state = self.t1.isChecked()
        self.gindicator.gitem.setTrendVisible(Term.T1, state)

    # }}}
    @QtCore.pyqtSlot()  # __onT2  # {{{
    def __onT2(self):
        state = self.t2.isChecked()
        self.gindicator.gitem.setTrendVisible(Term.T2, state)

    # }}}
    @QtCore.pyqtSlot()  # __onT3  # {{{
    def __onT3(self):
        state = self.t3.isChecked()
        self.gindicator.gitem.setTrendVisible(Term.T3, state)

    # }}}
    @QtCore.pyqtSlot()  # __onT4  # {{{
    def __onT4(self):
        state = self.t4.isChecked()
        self.gindicator.gitem.setTrendVisible(Term.T4, state)

    # }}}
    @QtCore.pyqtSlot()  # __onT5  # {{{
    def __onT5(self):
        state = self.t5.isChecked()
        self.gindicator.gitem.setTrendVisible(Term.T5, state)

    # }}}


# }}}
class _Settings(QtWidgets.QDialog):  # {{{
    def __init__(self, gindicator, parent=None):  # {{{
        QtWidgets.QDialog.__init__(self, parent)
        self.__gindicator = gindicator

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    # }}}

    @property  # gindicator  # {{{
    def gindicator(self):
        return self.__gindicator

    # }}}

    def configureSilent(self, gextr: _Graphics):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure")

        gextr.setTrendVisible(Term.T1, self.t1.isChecked())
        gextr.setTrendVisible(Term.T2, self.t2.isChecked())
        gextr.setTrendVisible(Term.T3, self.t3.isChecked())
        gextr.setTrendVisible(Term.T4, self.t4.isChecked())
        gextr.setTrendVisible(Term.T5, self.t5.isChecked())

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
            f"| {self.gindicator.name} settings:", parent=self
        )
        self.title_label.setStyleSheet(Css.TITLE)
        self.ok_btn = ToolButton(Icon.OK)
        self.cancel_btn = ToolButton(Icon.CANCEL)

        self.t1 = QtWidgets.QCheckBox("T1")
        self.t2 = QtWidgets.QCheckBox("T2")
        self.t3 = QtWidgets.QCheckBox("T3")
        self.t4 = QtWidgets.QCheckBox("T4")
        self.t5 = QtWidgets.QCheckBox("T5")

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox_title = QtWidgets.QHBoxLayout()
        hbox_title.addWidget(self.title_label)
        hbox_title.addStretch()
        hbox_title.addWidget(self.ok_btn)
        hbox_title.addWidget(self.cancel_btn)

        hbox_term = QtWidgets.QHBoxLayout()
        hbox_term.addWidget(MonoLabel("Term: "))
        hbox_term.addWidget(self.t1)
        hbox_term.addWidget(self.t2)
        hbox_term.addWidget(self.t3)
        hbox_term.addWidget(self.t4)
        hbox_term.addWidget(self.t5)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(hbox_title)
        vbox.addSpacing(10)
        vbox.addLayout(hbox_term)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

        pass

    # }}}


# }}}
class _Graphics(QtWidgets.QGraphicsItemGroup):  # {{{
    def __init__(self, gindicator, gchart: GChart, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gindicator = gindicator
        self.gchart = gchart
        self.cache_trend = Tree()
        self.cache_now = Tree()
        self.state = Tree()

        self.elist = self.gchart.chart.getInd(self.gindicator.indicator.name)
        self.elist.new_trend.connect(self.__onNewTrend)
        self.elist.upd_trend.connect(self.__onUpdTrend)

    # }}}

    def setTrendVisible(  # {{{
        self, term: Term, visible: bool
    ) -> None:
        # PERF: если не отрисованы эти линии, и приходит настройка
        # visible=False - то ничего не делаем.
        if not self.__isExist(term) and not visible:
            return

        gtrends = self.getGTrends(term)
        gtrends.setVisible(visible)

        gtrend_now = self.getGTrendNow(term)
        gtrend_now.setVisible(visible)

        self.state[term] = visible  # used in __onUpdExtr __onNewExtr

    # }}}
    def getGTrends(self, term) -> QtWidgets.QGraphicsItemGroup:  # {{{
        # try find in cache
        gtrends = self.cache_trend[term]
        if gtrends:
            return gtrends

        # get trends (historical)
        trends = self.elist.getAllTrends(term)
        gtrends = self.__createGTrends(self.gchart, trends)

        # save in cache
        self.cache_trend[term] = gtrends

        # add to group
        self.addToGroup(gtrends)

        return gtrends

    # }}}
    def getGTrendNow(self, term) -> QtWidgets.QGraphicsItemGroup:  # {{{
        # try find in cache
        gtrend_now = self.cache_now[term]
        if gtrend_now:
            return gtrend_now

        # get trend now
        trend = self.elist.trend(term, 0)
        gtrend = _GTrend(self.gchart, trend)

        # save in cache
        self.cache_now[term] = gtrend

        # add to group
        self.addToGroup(gtrend)

        return gtrend

    # }}}
    def getInfo(self, x: float):  # {{{
        string = ""
        for term in Term:
            if not self.__isExist(term):
                break

            gtrends = self.getGTrends(term)
            for gtrend in gtrends.childItems():
                if gtrend.isIn(x):
                    string += gtrend.getTextInfo()

        return string

    # }}}

    def __isExist(self, term) -> bool:  # {{{
        # try find in cache
        gtrends = self.cache_trend[term]
        return bool(gtrends)

    # }}}
    def __getGMove(self, tf, term) -> QtWidgets.QGraphicsItemGroup:  # {{{
        pass

    # }}}
    def __createGTrends(  # {{{
        self, gchart, trends
    ) -> QtWidgets.QGraphicsItemGroup:
        gtrends = QtWidgets.QGraphicsItemGroup()
        for trend in trends:
            # INFO: так как я делаю совмещения трендов с разных
            # таймфреймов, на дневном графике будут бары допустим
            # с 2020 г, а на 5М графике только с 2025г (последние 5000 баров)
            # соответственно, если тренд не умещается на текущем графике
            # пропускаем его.
            if trend.begin.dt < self.gchart.chart.first.dt:
                continue

            gtrend = _GTrend(gchart, trend)
            gtrends.addToGroup(gtrend)

        return gtrends

    # }}}

    def __onNewTrend(self, trend: Trend):
        assert isinstance(trend, Trend)
        if not self.__isExist(trend.term):
            return

        # create new
        new_gtrend = _GTrend(self.gchart, trend)

        # # set visible
        # state = self.state[trend.term]
        # new_gtrend.setVisible(state)

        # add to cache group  (group already added in self)
        gtrends = self.cache_trend[trend.term]
        gtrends.addToGroup(new_gtrend)

    def __onUpdTrend(self, trend: Trend):
        assert isinstance(trend, Trend)
        if not self.__isExist(trend.term):
            return

        # remove old
        old_gtrend = self.cache_now[trend.term]
        old_gtrend.setVisible(False)
        self.removeFromGroup(old_gtrend)

        # create new
        new_gtrend = _GTrend(self.gchart, trend)

        # # set visible
        # state = self.state[trend.term]
        # new_gtrend.setVisible(state)

        # add to cache and self
        self.cache_now[trend.term] = new_gtrend
        self.addToGroup(new_gtrend)

    # }}}


class _GTrend(QtWidgets.QGraphicsItemGroup):  # {{{
    WIDTH_1M = 0.5
    WIDTH_5M = 1
    WIDTH_1H = 2
    WIDTH_D = 3
    WIDTH_W = 4
    WIDTH_M = 5

    COLOR_T1 = Theme.Chart.TREND_T1
    COLOR_T2 = Theme.Chart.TREND_T2
    COLOR_T3 = Theme.Chart.TREND_T3
    COLOR_T4 = Theme.Chart.TREND_T4
    COLOR_T5 = Theme.Chart.TREND_T5

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
        # 󰜷 󰜮 󰁆 󰁞 󱦳 󱦲  󰁃󰁜  󱦴󱦷 󰧆󰦺    "

        t = self.trend
        tf = str(t.timeframe)
        term = str(t.term)
        typ = "" if t.isBull() else ""

        p = t.period()
        d = t.deltaPercent()
        s = t.speedPercent()
        v_total = f"{(t.volumeTotal() / 1_000_000):.2f}m"
        v_bear = f"{(t.volumeBear() / 1_000_000):.2f}m"
        v_bull = f"{(t.volumeBull() / 1_000_000):.2f}m"

        p_sz = TrendAnalytic.periodSize(t)
        d_sz = TrendAnalytic.deltaSize(t)
        s_sz = TrendAnalytic.speedSize(t)
        v_total_sz = TrendAnalytic.volumeTotalSize(t)
        v_bear_sz = TrendAnalytic.volumeBearSize(t)
        v_bull_sz = TrendAnalytic.volumeBullSize(t)

        p_sz = p_sz.simple() if p_sz else "--"
        d_sz = d_sz.simple() if d_sz else "--"
        s_sz = s_sz.simple() if s_sz else "--"
        v_total_sz = v_total_sz.simple() if v_total_sz else "--"
        v_bear_sz = v_bear_sz.simple() if v_bear_sz else "--"
        v_bull_sz = v_bull_sz.simple() if v_bull_sz else "--"

        string = (
            f"\n{tf:<2} "
            f"{term:<2} "
            f"{typ} "
            f"p:{p_sz:<2} {p:<6} "
            f"d:{d_sz:<2} {d:<6} "
            f"s:{s_sz:<2} {s:<6} "
            f"v:{v_total_sz:<2} {v_total:<6} "
            f"(󰜷{v_bull_sz} {v_bull} 󰜮{v_bear_sz} {v_bear})"
        )
        return string

    # }}}
    def isIn(self, x: float) -> bool:  # {{{
        if self.begin_pos.x() < x < self.end_pos.x():
            return True

        return False

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
                width = self.WIDTH_1M
            case "5M":
                width = self.WIDTH_5M
            case "1H":
                width = self.WIDTH_1H
            case "D":
                width = self.WIDTH_D
            case "W":
                width = self.WIDTH_W
            case "M":
                width = self.WIDTH_M
            case _:
                assert False, f"TODO_ME??? {self.trend.timeframe}"

        match self.trend.term:
            case Term.T1:
                color = self.COLOR_T1
                opacity = 0.2
            case Term.T2:
                color = self.COLOR_T2
                opacity = 0.4
            case Term.T3:
                color = self.COLOR_T3
                opacity = 0.6
            case Term.T4:
                color = self.COLOR_T4
                opacity = 0.8
            case Term.T5:
                color = self.COLOR_T5
                opacity = 1
            case _:
                assert False, f"TODO_ME??? {self.trend.term}"

        self.line = QtWidgets.QGraphicsLineItem(
            self.begin_pos.x(),
            self.begin_pos.y(),
            self.end_pos.x(),
            self.end_pos.y(),
        )
        pen = QtGui.QPen(color, width)
        self.line.setPen(pen)
        self.line.setOpacity(opacity)

        self.addToGroup(self.line)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    indicator = GExtremumIndicator()
    w = _Settings(indicator)
    w.show()
    sys.exit(app.exec())
