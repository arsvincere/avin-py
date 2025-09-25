# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from avin.gui.custom import Css


class AssetListTree(QtWidgets.QTreeWidget):
    def __init__(self, parent):
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()

    def __config(self) -> None:
        self.setHeaderLabels(["Ticker", "Name"])

        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        self.setStyleSheet(Css.TREE)
        self.header().setStyleSheet(Css.TREE_HEADER)  # type: ignore
        self.setContentsMargins(0, 0, 0, 0)

        self.setColumnWidth(0, 80)
        self.setColumnWidth(1, 250)
        self.setMinimumHeight(400)


if __name__ == "__main__":
    ...
