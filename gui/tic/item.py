#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin import Tic, Usr
from gui.custom.theme import Theme


class TicItem(QtWidgets.QTreeWidgetItem):
    __buy_brush = QtGui.QBrush(Theme.Tic.BUY)
    __sell_brush = QtGui.QBrush(Theme.Tic.SELL)

    class Column(enum.IntEnum):  # {{{
        Time = 0
        Price = 1
        Lots = 2
        Amount = 3

    # }}}
    def __init__(self, tic: Tic, parent=None):  # {{{
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.tic = tic
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        )

        user_time = (tic.dt + Usr.TIME_DIF).time()
        str_time = user_time.isoformat(timespec="seconds")
        self.setText(self.Column.Time, str_time)
        self.setText(self.Column.Price, str(tic.price))
        self.setText(self.Column.Lots, str(tic.lots))
        self.setText(self.Column.Amount, str(tic.amount()))

        if tic.isBuy():
            self.setBackground(self.Column.Amount, self.__buy_brush)
        else:
            self.setBackground(self.Column.Amount, self.__sell_brush)

        # text align
        right = Qt.AlignmentFlag.AlignRight
        self.setTextAlignment(self.Column.Price, right)
        self.setTextAlignment(self.Column.Lots, right)
        self.setTextAlignment(self.Column.Amount, right)

    # }}}


if __name__ == "__main__":
    ...
