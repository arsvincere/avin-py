#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.utils import logger
from gui.chart.gchart import GChart
from gui.custom import Theme


class GCross(QtWidgets.QGraphicsItemGroup):
    WIDTH = 1
    COLOR = Theme.Chart.CROSS
    STYLE = Qt.PenStyle.DashLine
    __pen = QtGui.QPen(COLOR, WIDTH, STYLE)

    def __init__(self, gchart: GChart):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self)

        self.gchart = gchart
        w = gchart.rect.width()
        h = gchart.rect.height()

        x0 = -w
        x1 = w
        y0 = 0
        y1 = 0
        hline = QtWidgets.QGraphicsLineItem(x0, y0, x1, y1)

        x0 = 0
        x1 = 0
        y0 = -h
        y1 = h
        vline = QtWidgets.QGraphicsLineItem(x0, y0, x1, y1)

        hline.setPen(self.__pen)
        vline.setPen(self.__pen)

        self.addToGroup(hline)
        self.addToGroup(vline)

    # }}}


if __name__ == "__main__":
    ...
