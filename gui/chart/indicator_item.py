#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum
import sys

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from avin import logger
from avin.utils import logger


class IndicatorItem(QtWidgets.QTreeWidgetItem):  # {{{
    class Column(enum.IntEnum):  # {{{
        Name = 0

    # }}}

    def __init__(self, indicator_class, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.indicator_class = indicator_class

        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
        )
        self.setCheckState(self.Column.Name, Qt.CheckState.Unchecked)
        self.setText(self.Column.Name, indicator_class.name)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = IndicatorSelectDialog()
    w.show()
    sys.exit(app.exec())
