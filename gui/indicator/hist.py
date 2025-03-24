#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import sys

from PyQt6 import QtCore, QtWidgets

from avin import Cfg, Hist, logger
from gui.chart.gchart import GChart
from gui.custom import Css, Icon, Label, Theme, ToolButton
from gui.indicator._indicator import GIndicator


class GHist(GIndicator):  # {{{
    name = Hist.name
    position = GIndicator.Position.FOOTER

    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.indicator = Hist()
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

        self.gchart = gchart
        self.gitem = _Graphics(self)

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
    def __init__(self, indicator, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__indicator = indicator
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    # }}}

    @property  # gindicator  # {{{
    def gindicator(self):
        return self.__indicator

    # }}}

    # def setGChart(self, gchart):  # {{{
    #     self.gchart = gchart
    #
    # # }}}
    def updateInfo(self, x):  # {{{
        pass

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.label_name = QtWidgets.QLabel(self.__indicator.name)
        self.btn_hide = ToolButton(Icon.HIDE, width=16, height=16)
        self.btn_settings = ToolButton(Icon.CONFIG, width=16, height=16)
        self.btn_delete = ToolButton(Icon.DELETE, width=16, height=16)

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

        self.gindicator.configure()

    # }}}


# }}}
class _Settings(QtWidgets.QDialog):  # {{{
    def __init__(self, gindicator, parent=None):  # {{{
        QtWidgets.QDialog.__init__(self, parent)
        self.__indicator = gindicator

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    # }}}

    @property  # gindicator  # {{{
    def gindicator(self):
        return self.__indicator

    # }}}

    def configureSilent(self, gitem: _Graphics):  # {{{
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

        self.title_label = Label(
            f"| {self.gindicator.name} settings:", parent=self
        )
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
class _Graphics(QtWidgets.QGraphicsItemGroup):  # {{{
    HEIGHT = 100
    WIDTH = Cfg.Chart.BAR_WIDTH - 2 * Cfg.Chart.BAR_INDENT
    Y0 = -HEIGHT / 2
    SEGMENT = HEIGHT / 10

    B_COLOR = Theme.Chart.BULL
    S_COLOR = Theme.Chart.BEAR

    flags = QtWidgets.QGraphicsItem.GraphicsItemFlag
    ignore_transformation = flags.ItemIgnoresTransformations

    def __init__(self, gindicator: HistIndicator, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gindicator = gindicator
        self.gchart = gindicator.gchart
        self.hist = self.gchart.chart.getInd(self.gindicator.indicator.name)
        self.now_gitem = None
        self.historical_gitem = list()

        self.__createFrame()
        self.__createGraphics()

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
    def __createGraphics(self) -> None:  # {{{
        # create historical
        df = self.hist.historicalHist()
        for data in df.iter_rows(named=True):
            gitem = self.__createHistBar(data)
            self.addToGroup(gitem)
            self.historical_gitem.append(gitem)

        # create real time
        data = self.hist.nowHist()
        gitem = self.__createHistBar(data)
        self.addToGroup(gitem)
        self.now_gitem = gitem

    # }}}
    def __createHistBar(self, hist_bar: dict) -> None:  # {{{
        gitem = QtWidgets.QGraphicsItemGroup()
        if hist_bar is None:
            return gitem

        # alias
        gchart = self.gchart
        dt = hist_bar["dt"]
        b_size = hist_bar["b_lots_ssize"]
        s_size = hist_bar["s_lots_ssize"]
        b_fill = hist_bar["b_fill"]
        s_fill = hist_bar["s_fill"]

        # coordinate x0
        gbar = gchart.gbarFromDatetime(dt)
        x0 = gbar.x0_cundle

        # graphics item
        b_bar = self.__hist("buy", b_size, b_fill, x0)
        s_bar = self.__hist("sell", s_size, s_fill, x0)

        gitem.addToGroup(b_bar)
        gitem.addToGroup(s_bar)

        return gitem

    # }}}
    def __hist(  # {{{
        self, typ: str, size: str, fill: float, x0: float
    ) -> QtWidgets.QGraphicsItemGroup:
        """algorithm# {{{
        Если размер XS
            - рисуем кубик XS по масштабу
        Если размер S
            - рисуем кубик XS полный
            - рисуем кубик S по масштабу
        Если размер М
            - рисуем кубик XS полный
            - рисуем кубик S полный
            - рисуем кубик М по масштабу
                - определить % кубика
                - определить y1 = % * y0_M

        Пусть размеры например такие:
            XS  0       100
            S   100     1_000
            M   1_000   100_000

            например объем приходит 75
            значит нужно сделать 75% процентов от первого кубика

            например объем приходит 200
            значит нужно взять первый кубик полный
            а второй получается
                1000 - 100 = 900 это максимум
                200 / 900 = это заполненное количество

            например объем приходит 90_000
            1 кубик полный
            2 кубик полный
            3 кубик
                100_000 - 1_000 = 99_000 это максимум
                90_000 / 99_000 = это заполненное количество
        """  # }}}

        match typ:
            case "buy":
                color = self.B_COLOR
                k = 1
            case "sell":
                color = self.S_COLOR
                k = -1

        match size:
            case "XXS":
                quad1 = self.__quad(color, 1, k, x0, fill=fill)
                quad2 = None
                quad3 = None
                quad4 = None
                quad5 = None
            case "XS":
                quad1 = self.__quad(color, 1, k, x0, fill=fill)
                quad2 = None
                quad3 = None
                quad4 = None
                quad5 = None
            case "S":
                quad1 = self.__quad(color, 1, k, x0, fill=1)
                quad2 = self.__quad(color, 2, k, x0, fill=fill)
                quad3 = None
                quad4 = None
                quad5 = None
            case "M":
                quad1 = self.__quad(color, 1, k, x0, fill=1)
                quad2 = self.__quad(color, 2, k, x0, fill=1)
                quad3 = self.__quad(color, 3, k, x0, fill=fill)
                quad4 = None
                quad5 = None
            case "L":
                quad1 = self.__quad(color, 1, k, x0, fill=1)
                quad2 = self.__quad(color, 2, k, x0, fill=1)
                quad3 = self.__quad(color, 3, k, x0, fill=1)
                quad4 = self.__quad(color, 4, k, x0, fill=fill)
                quad5 = None
            case "XL":
                quad1 = self.__quad(color, 1, k, x0, fill=1)
                quad2 = self.__quad(color, 2, k, x0, fill=1)
                quad3 = self.__quad(color, 3, k, x0, fill=1)
                quad4 = self.__quad(color, 4, k, x0, fill=1)
                quad5 = self.__quad(color, 5, k, x0, fill=fill)
            case "XXL":
                quad1 = self.__quad(color, 1, k, x0, fill=1)
                quad2 = self.__quad(color, 2, k, x0, fill=1)
                quad3 = self.__quad(color, 3, k, x0, fill=1)
                quad4 = self.__quad(color, 4, k, x0, fill=1)
                quad5 = self.__quad(color, 5, k, x0, fill=fill)

        group = QtWidgets.QGraphicsItemGroup()
        for i in (quad1, quad2, quad3, quad4, quad5):
            if i is not None:
                group.addToGroup(i)

        return group

    # }}}
    def __quad(  # {{{
        self, color, n, k, x0, fill
    ) -> QtWidgets.QGraphicsRectItem:
        y0 = self.Y0 - (n - 1) * self.SEGMENT
        y1 = y0 + fill * self.SEGMENT
        height = y1 - y0

        quad = QtWidgets.QGraphicsRectItem(x0, y0, self.WIDTH, height)
        quad.setPen(color)
        quad.setBrush(color)

        return quad

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    indicator = GHist()
    w = _Settings(indicator)
    w.show()
    sys.exit(app.exec())
