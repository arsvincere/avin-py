#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtWidgets

from avin.gui.chart.gchart import GChart
from avin.gui.custom import Css
from avin.utils import WeekDays


class ChartLabels(QtWidgets.QGraphicsProxyWidget):
    def __init__(self, parent=None):
        QtWidgets.QGraphicsProxyWidget.__init__(self, parent)

        self.__labels = list()
        self.__vbox = QtWidgets.QVBoxLayout()
        self.__widget = QtWidgets.QWidget()
        self.__widget.setStyleSheet(Css.CHART_LABEL)
        self.__widget.setLayout(self.__vbox)

        self.setWidget(self.__widget)

    def __iter__(self):
        return iter(self.__labels)

    def add(self, widget: QtWidgets.QWidget) -> None:
        self.__labels.append(widget)
        self.__vbox.addWidget(widget)
        widget.show()

    def remove(self, widget: QtWidgets.QWidget) -> None:
        self.__labels.remove(widget)
        self.__vbox.removeWidget(widget)
        widget.hide()

    def clear(self):
        item = self.__vbox.takeAt(0)
        while item:
            item.widget().hide()
            item = self.__vbox.takeAt(0)

        self.__labels.clear()


class BarInfo(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QGraphicsWidget.__init__(self)

        self.__create_widgets()
        self.__create_layouts()

    def set_gchart(self, gchart: GChart):
        self.gchart = gchart

    def update_info(self, x: int) -> None:  # {{{
        if x < 0:
            return

        # get the grapthics bar on X coordinate
        gbar = self.gchart.gbar_on_x(x)
        if gbar is None:
            return

        # format datetime
        bar = gbar.bar
        local_time = bar.dt_local()
        day = WeekDays(bar.dt().weekday()).name

        # format volume
        vol = bar.v
        if vol > 1_000_000:
            m_vol = vol / 1_000_000
            vol_str = f"{m_vol:.2f}m"
        elif vol > 1_000:
            k_vol = vol / 1_000
            vol_str = f"{k_vol:.2f}k"
        else:
            vol_str = f"{vol}"

        # get body and full range in percent
        body_p = bar.body().delta_p()
        full_p = bar.full().delta_p()

        self.bar_info_label.setText(
            f"{local_time} {day} - "
            f"O: {bar.o:<6}  "
            f"H: {bar.h:<6}  "
            f"L: {bar.l:<6}  "
            f"C: {bar.c:<6}  "
            f"V: {vol_str:<7}  "
            f"(Full: {full_p:.2f} / "
            f"Body: {body_p:.2f})"
        )

    def __create_widgets(self):  # {{{
        self.bar_info_label = QtWidgets.QLabel()
        self.bar_info_label.setText(
            "[date-time] [day] - "
            "Open: ____ "
            "High: ____ "
            "Low: ____ "
            "Close: ____ "
            "(Full: __ / Body __)"
        )

    def __create_layouts(self):  # {{{
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.bar_info_label)


if __name__ == "__main__":
    ...
