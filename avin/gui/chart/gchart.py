# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from PyQt6 import QtCore, QtWidgets

from avin.core import Bar, Chart
from avin.utils import CFG


class GBar(QtWidgets.QGraphicsItemGroup):
    WIDTH = CFG.Chart.bar_width

    def __init__(self, bar: Bar, n: int, parent):
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        self.bar = bar
        self.n = n

        self.__calc_coordinates()
        self.__set_color()
        self.__draw()

    def __calc_coordinates(self):
        self.x0 = self.n * self.WIDTH
        self.x1 = self.x0 + self.WIDTH
        self.x_center = (self.x0 + self.x1) / 2

        min_price_step = self.bar.chart.iid().step()
        self.y_opn = self.bar.o / min_price_step
        self.y_hgh = self.bar.h / min_price_step
        self.y_low = self.bar.l / min_price_step
        self.y_cls = self.bar.c / min_price_step

        self.open_pos = QtCore.QPointF(self.x_center, self.y_opn)
        self.close_pos = QtCore.QPointF(self.x_center, self.y_cls)
        self.high_pos = QtCore.QPointF(self.x_center, self.y_hgh)
        self.low_pos = QtCore.QPointF(self.x_center, self.y_low)

    def __set_color(self):
        if self.bar.is_bull():
            self.color = CFG.Chart.bull
        elif self.bar.is_bear():
            self.color = CFG.Chart.bear
        else:
            self.color = CFG.Chart.dodji

    def __draw(self):
        # create shadow, open, close lines
        shadow = QtWidgets.QGraphicsLineItem(
            self.x_center, self.y_low, self.x_center, self.y_hgh
        )
        open_line = QtWidgets.QGraphicsLineItem(
            self.x0, self.y_opn, self.x_center, self.y_opn
        )
        close_line = QtWidgets.QGraphicsLineItem(
            self.x_center, self.y_cls, self.x1, self.y_cls
        )

        # set color
        shadow.setPen(self.color)
        open_line.setPen(self.color)
        close_line.setPen(self.color)

        # add lines to group
        self.addToGroup(shadow)
        self.addToGroup(open_line)
        self.addToGroup(close_line)


class GChart(QtWidgets.QGraphicsItemGroup):
    def __init__(self, chart: Chart, parent):
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.chart = chart

        self.__connect()
        self.__create_scene_rect()
        self.__create_gbars()

    def first(self) -> GBar:
        return self.gbars[0]

    def last(self) -> GBar:
        return self.gbars[-1]

    def gbar_on_x(self, x: int) -> GBar | None:
        if x < 0:
            return None

        n = int(x / GBar.WIDTH)
        if n < len(self.gbars):
            return self.gbars[n]
        elif n == len(self.gbars):
            return self.gnow
        else:
            return None

    def __connect(self) -> None:
        pass
        # self.chart.upd_bar.connect(self.__on_real_time_bar)
        # self.chart.new_bar.connect(self.__on_historical_bar)

    def __create_scene_rect(self) -> None:
        x0 = 0
        y0 = 0
        x1 = len(self.chart) * GBar.WIDTH
        y1 = int(self.chart.highest_high() / self.chart.iid().step())

        self.x_indent = GBar.WIDTH * 1000  # отступ на 1000 баров
        self.y_indent = (y1 - y0) * 0.2  # отступ 20%

        height = y1 - y0 + self.y_indent
        width = x1 - x0 + self.x_indent

        self.rect = QtCore.QRectF(x0, y0, width, height)

    def __create_gbars(self) -> None:
        self.gbars = list()

        for n, bar in enumerate(self.chart, 0):
            gbar = GBar(bar, n, self)
            self.gbars.append(gbar)
            self.addToGroup(gbar)

        now_bar = self.chart.now()
        if now_bar is None:
            self.gnow = None
        else:
            self.gnow = GBar(now_bar, n=len(self.gbars), parent=self)
            self.addToGroup(self.gnow)


if __name__ == "__main__":
    ...
