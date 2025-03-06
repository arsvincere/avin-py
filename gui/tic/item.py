#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from avin import Tic, Usr


class TicItem(QtWidgets.QTreeWidgetItem):
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

        user_time = tic.dt + Usr.TIME_DIF
        self.setText(self.Column.Time, str(user_time.time()))
        self.setText(self.Column.Price, str(tic.price))
        self.setText(self.Column.Lots, str(tic.lots))
        self.setText(self.Column.Amount, str(tic.amount()))

    # }}}


if __name__ == "__main__":
    ...
