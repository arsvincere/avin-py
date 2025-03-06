#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtCore, QtGui, QtWidgets

from avin import Tic, logger
from gui.custom import Css, Menu
from gui.tic.item import TicItem


class TicTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenu()
        self.__connect()

    # }}}

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")

        self.__current_item = self.itemAt(e.pos())
        self.__menu.exec(QtGui.QCursor.pos())

        return e.ignore()

    # }}}
    def addTic(self, tic: Tic):  # {{{
        item = TicItem(tic)
        self.addTopLevelItem(item)

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        # config style
        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.TREE)
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

        # config header
        labels = list()
        for l in TicItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config width
        self.setColumnWidth(TicItem.Column.Time, 100)
        self.setMinimumWidth(200)

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.__menu = _TicMenu(parent=self)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__menu.info.triggered.connect(self.__onInfo)

    # }}}

    @QtCore.pyqtSlot()  # __onInfo  # {{{
    def __onInfo(self):
        logger.debug(f"{self.__class__.__name__}.__onInfo()")

    # }}}


# }}}


class _TicMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.info = QtGui.QAction("Info", self)

        self.addAction(self.info)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = TicTree()
    w.show()
    app.exec()
