# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import sys

from PyQt6 import QtCore, QtWidgets

from avin.gui.asset.item import AssetItem
from avin.gui.asset.tree import AssetListTree
from avin.gui.custom import Css
from avin.terminal import Terminal


class AssetListWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__create_widgets()
        self.__create_layots()
        self.__connect()

    def set_terminal(self, terminal: Terminal) -> None:
        self.tree.clear()

        asset_list = terminal.asset_list
        if len(asset_list) == 0:
            return

        # create first asset item and set as current item
        i = 0
        asset = asset_list[i]
        item = AssetItem(asset, None)
        self.tree.addTopLevelItem(item)
        self.tree.setCurrentItem(item)
        i += 1

        # create other asset items
        while i < len(asset_list):
            asset = asset_list[i]
            item = AssetItem(asset, None)
            self.tree.addTopLevelItem(item)
            i += 1

        self.terminal = terminal

    def __config(self) -> None:
        self.setStyleSheet(Css.STYLE)

    def __create_widgets(self) -> None:
        self.tree = AssetListTree(self)

    def __create_layots(self) -> None:
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.tree)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    def __connect(self) -> None:
        self.tree.itemClicked.connect(self.__on_item_clicked)

    @QtCore.pyqtSlot()
    def __on_item_clicked(self):
        item = self.tree.currentItem()
        asset = item.asset
        self.terminal.set_current_asset(asset)


if __name__ == "__main__":
    terminal = Terminal()
    app = QtWidgets.QApplication(sys.argv)
    w = AssetListWidget(parent=None)

    w.set_terminal(terminal)

    w.setWindowTitle("AVIN")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.show()
    sys.exit(app.exec())
