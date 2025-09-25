# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import enum

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from avin.core import Asset


class AssetItem(QtWidgets.QTreeWidgetItem):
    class Column(enum.IntEnum):  # {{{
        Ticker = 0
        Name = 1
        Exchange = 2
        Category = 3
        Figi = 4

    def __init__(self, asset: Asset, parent):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)

        self.asset = asset

        self.setFlags(
            Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        )

        self.setText(self.Column.Ticker, asset.ticker().name)
        self.setText(self.Column.Name, str(asset.name()))
        self.setText(self.Column.Exchange, asset.exchange().name)
        self.setText(self.Column.Category, asset.category().name)
        self.setText(self.Column.Category, asset.figi())


if __name__ == "__main__":
    ...
