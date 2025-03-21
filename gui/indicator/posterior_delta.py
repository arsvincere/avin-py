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

from avin import (
    PosteriorDelta,
    Term,
    Tree,
    Trend,
    logger,
)
from gui.chart.gchart import GChart
from gui.custom import Css, Icon, Label, Theme, ToolButton
from gui.indicator._indicator import GIndicator


class GPosteriorDelta(GIndicator):  # {{{
    name = PosteriorDelta.name
    position = GIndicator.Position.RIGHT

    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.indicator = PosteriorDelta()
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
    def __init__(self, gindicator, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__gindicator = gindicator
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    # }}}

    @property  # gindicator  # {{{
    def gindicator(self):
        return self.__gindicator

    # }}}

    def updateInfo(self, x):  # {{{
        pass

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.label_name = QtWidgets.QLabel(self.gindicator.name)
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

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox_title = QtWidgets.QHBoxLayout()
        hbox_title.addWidget(self.title_label)
        hbox_title.addStretch()
        hbox_title.addWidget(self.ok_btn)
        hbox_title.addWidget(self.cancel_btn)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(hbox_title)

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
    WIDTH = -200
    BG = Theme.Chart.BG
    FRAME = Theme.Chart.BG_FOOTER

    def __init__(self, gindicator, gchart: GChart, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gindicator = gindicator
        self.gchart = gchart
        self.post = self.gchart.chart.getInd(self.gindicator.indicator.name)
        self.now_gitem = Tree()
        self.last_gitem = Tree()

        self.__createFrame()
        self.__createGraphics()

        self.post.new_posterior.connect(self.__onNewPosterior)
        self.post.upd_posterior.connect(self.__onUpdPosterior)

    # }}}
    def __createFrame(self) -> None:  # {{{
        x0 = 0
        y0 = 0
        width = self.WIDTH
        height = self.gchart.rect.height()

        frame = QtWidgets.QGraphicsRectItem(x0, y0, width, height)
        frame.setPen(self.FRAME)
        frame.setBrush(self.BG)
        self.addToGroup(frame)

    # }}}
    def __createGraphics(self):  # {{{
        for term in Term:
            # create last trend graphics
            trend, posterior = self.post.last(term)
            gitem = _GDeltaProbability(self.gchart, trend, posterior, "last")
            self.last_gitem[term] = gitem
            self.addToGroup(gitem)

            # create now trend graphics
            trend, posterior = self.post.now(term)
            gitem = _GDeltaProbability(self.gchart, trend, posterior, "now")
            self.now_gitem[term] = gitem
            self.addToGroup(gitem)

    # }}}

    def __onNewPosterior(self, trend, posterior):  # {{{
        print("new post", trend)
        # delete old
        term = trend.term
        old_item = self.last_gitem[term]
        old_item.hide()
        self.removeFromGroup(old_item)

        # create new
        gitem = _GDeltaProbability(self.gchart, trend, posterior, "last")
        self.last_gitem[term] = gitem
        self.addToGroup(gitem)

    # }}}
    def __onUpdPosterior(self, trend, posterior):  # {{{
        print("upd post", trend)
        # delete old
        term = trend.term
        old_item = self.now_gitem[term]
        old_item.hide()
        self.removeFromGroup(old_item)

        # create new
        gitem = _GDeltaProbability(self.gchart, trend, posterior, "now")
        self.now_gitem[term] = gitem
        self.addToGroup(gitem)

    # }}}


# }}}
class _GDeltaProbability(QtWidgets.QGraphicsItemGroup):  # {{{
    SEGMENT = -20
    INDENT = -1
    COLOR_BEAR = Theme.Chart.POSTERIOR_BEAR
    COLOR_BULL = Theme.Chart.POSTERIOR_BULL
    COLOR_NOW = Theme.Chart.POSTERIOR_NOW

    def __init__(  # {{{
        self,
        gchart: GChart,
        trend: Trend,
        posterior: pl.DataFrame,
        typ: str,
        parent=None,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.gchart = gchart
        self.trend = trend
        self.posterior = posterior
        self.type = typ

        if self.posterior is None:
            return

        self.__calcCoordinates()
        self.__selectColor()
        self.__createGraphics()
        self.__createText()

    # }}}

    def __calcCoordinates(self):  # {{{
        # calc x
        self.X0 = self.trend.term.value * self.SEGMENT * 2
        if self.type == "last":
            self.X0 += self.SEGMENT
        self.x0 = self.X0 + self.INDENT
        self.x1 = self.X0 + self.SEGMENT - self.INDENT
        self.width = self.x1 - self.x0

        # calc y0
        begin_price = self.trend.end.price
        self.y0 = self.gchart.yFromPrice(begin_price)

        # calc y1 for all term
        self.y1 = list()
        self.p = list()
        for row in self.posterior.iter_rows(named=True):
            end_price = row["price"]
            y = self.gchart.yFromPrice(end_price)
            p = row["cumulative"]

            self.y1.append(y)
            self.p.append(p)

    # }}}
    def __selectColor(self):  # {{{
        if self.type == "now":
            self.color = self.COLOR_NOW
        elif self.trend.isBull():
            self.color = self.COLOR_BEAR
        else:
            self.color = self.COLOR_BULL

    # }}}
    def __createGraphics(self):  # {{{
        # create rect
        for p, y in zip(self.p, self.y1):
            height = y - self.y0
            rect = QtWidgets.QGraphicsRectItem(
                self.x0, self.y0, self.width, height
            )
            rect.setPen(self.color)
            rect.setBrush(self.color)
            rect.setOpacity(p / 100 / 2)

            self.addToGroup(rect)

    # }}}
    def __createText(self):  # {{{
        for p, y in zip(self.p, self.y1):
            text = str(round(p))
            text = ".." if text == "100" else text
            text_item = QtWidgets.QGraphicsSimpleTextItem(text)
            if self.trend.isBear():
                text_item.setPos(self.x1, y)
            else:
                height = text_item.boundingRect().height()
                text_item.setPos(self.x1, y - height)
            self.addToGroup(text_item)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    indicator = GPosteriorDelta()
    w = _Settings(indicator)
    w.show()
    sys.exit(app.exec())
