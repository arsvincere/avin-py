#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore, QtWidgets

from avin.config import Usr
from avin.const import WeekDays
from avin.utils import logger
from gui.custom import Css


class BarInfo(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsWidget.__init__(self, parent)

        self.__createWidgets()
        self.__createLayots()

    # }}}

    def setGChart(self, gchart):  # {{{
        self.gchart = gchart

    # }}}
    def updateInfo(self, pos: QtCore.QPointF):  # {{{
        logger.debug(f"{self.__class__.__name__}.set(bar)")

        x = pos.x()
        gbar = self.gchart.gbarOnX(x)
        if gbar is None:
            return

        bar = gbar.bar
        local_time = Usr.localTime(bar.dt)
        day = WeekDays(bar.dt.weekday()).name
        full_pct = bar.full.deltaP()
        body_pct = bar.body.deltaP()

        vol = bar.volume
        if vol > 1_000_000:
            m_vol = vol / 1_000_000
            value = f"{m_vol:.2f}m"
        elif vol > 1_000:
            k_vol = vol / 1_000
            value = f"{k_vol:.2f}k"
        else:
            value = f"{vol}"

        self.label_barinfo.setText(
            f"{local_time} {day} - "
            f"O: {bar.open:<6} "
            f"H: {bar.high:<6} "
            f"L: {bar.low:<6} "
            f"C: {bar.close:<6} "
            f"Vol: {value}   "
            f"[Full: {full_pct:.2f}% Body: {body_pct:.2f}%]"
        )

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.label_barinfo = QtWidgets.QLabel()
        self.label_barinfo.setText(
            "[date-time] [day] - "
            "Open: ____ "
            "High: ____ "
            "Low: ____ "
            "Close: ____ "
            "(Body: __%)"
        )

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.label_barinfo)

    # }}}


# }}}


class ChartLabels(QtWidgets.QGraphicsProxyWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsProxyWidget.__init__(self, parent)

        self.__labels = list()
        self.__vbox = QtWidgets.QVBoxLayout()
        self.__widget = QtWidgets.QWidget()
        self.__widget.setStyleSheet(Css.CHART_LABEL)
        self.__widget.setLayout(self.__vbox)

        self.setWidget(self.__widget)

    # }}}
    def __iter__(self):  # {{{
        return iter(self.__labels)

    # }}}

    def add(self, widget: QtWidgets.QWidget) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        self.__labels.append(widget)
        self.__vbox.addWidget(widget)
        widget.show()

    # }}}
    def remove(self, widget: QtWidgets.QWidget) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.remove()")

        self.__labels.remove(widget)
        self.__vbox.removeWidget(widget)
        widget.hide()

    # }}}
    def clear(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.clear()")

        item = self.__vbox.takeAt(0)
        while item:
            item.widget().hide()
            item = self.__vbox.takeAt(0)

        self.__labels.clear()

    # }}}


# QLayoutItem *child;
# while ((child = layout->takeAt(0)) != 0) {
#   ...
#   delete child;
# }


# }}}


if __name__ == "__main__":
    ...
