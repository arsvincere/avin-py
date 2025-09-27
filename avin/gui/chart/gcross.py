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

from avin.gui.chart.gchart import GChart
from avin.utils import CFG

WIDTH = 1
COLOR = CFG.Chart.cross
STYLE = Qt.PenStyle.DashLine
PEN = QtGui.QPen(COLOR, WIDTH, STYLE)


class GCross(QtWidgets.QGraphicsItemGroup):
    def __init__(self, gchart: GChart):  # {{{
        QtWidgets.QGraphicsItemGroup.__init__(self)

        self.gchart = gchart
        w = gchart.rect.width()
        h = gchart.rect.height()

        x0 = -w
        x1 = w
        y0 = 0.0
        y1 = 0.0
        hline = QtWidgets.QGraphicsLineItem(x0, y0, x1, y1)

        x0 = 0
        x1 = 0
        y0 = -h
        y1 = h
        vline = QtWidgets.QGraphicsLineItem(x0, y0, x1, y1)

        hline.setPen(PEN)
        vline.setPen(PEN)

        self.addToGroup(hline)
        self.addToGroup(vline)

    # }}}


if __name__ == "__main__":
    ...
