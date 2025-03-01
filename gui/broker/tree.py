#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import enum

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from tinkoff.invest.services import Services

from avin.gui.account import IAccount
from avin.gui.custom import Font


class Tree(QtWidgets.QTreeWidget):  # {{{
    class Column(enum.IntEnum):  # {{{
        Broker = 0

    # }}}
    class Type(enum.Enum):  # {{{
        BROKER = enum.auto()
        TOKEN = enum.auto()
        ACCOUNT = enum.auto()

    # }}}
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__createMenu()
        self.__connect()
        self.thread = None
        self.current_itoken = None
        self.current_iaccount = None
        self.current_ibroker = None

    # }}}
    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setFont(Font.MONO)
        self.setSortingEnabled(True)
        self.sortByColumn(self.Column.Broker, Qt.SortOrder.AscendingOrder)
        self.setItemsExpandable(True)
        self.setColumnWidth(Tree.Column.Broker, 250)

    # }}}
    def __createActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.action_connect = QtGui.QAction("Connect")
        self.action_set_account = QtGui.QAction("Set account")
        self.action_disconnect = QtGui.QAction("Disconnect")

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_connect)
        self.menu.addAction(self.action_disconnect)
        self.menu.addSeparator()
        self.menu.addAction(self.action_set_account)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_connect.triggered.connect(self.__onConnect)
        self.action_set_account.triggered.connect(self.__onSetAccount)
        self.action_disconnect.triggered.connect(self.__onDisconnect)

    # }}}
    def __resetActions(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        self.action_connect.setEnabled(False)
        self.action_set_account.setEnabled(False)
        self.action_disconnect.setEnabled(False)

    # }}}
    def __setVisibleActions(self, item):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            pass
        elif item.type == Tree.Type.TOKEN:
            self.action_connect.setEnabled(True)
            self.action_disconnect.setEnabled(True)
        elif item.type == Tree.Type.ACCOUNT:
            self.action_set_account.setEnabled(True)

    # }}}
    @QtCore.pyqtSlot()  # __onConnect# {{{
    def __onConnect(self):
        logger.debug(f"{self.__class__.__name__}.__onConnect()")
        self.current_itoken = self.currentItem()
        self.current_ibroker = self.current_itoken.parent()
        self.thread = TConnect(self.current_ibroker, self.current_itoken)
        self.thread.brokerConnected.connect(self.__threadBrokerConnected)
        self.thread.finished.connect(self.__threadFinish)
        self.thread.start()
        logger.info(f"Connection enabled: '{self.current_ibroker.name}'")

    # }}}
    @QtCore.pyqtSlot()  # __onSetAccount# {{{
    def __onSetAccount(self):
        logger.debug(f"{self.__class__.__name__}.__onSetAccount()")
        self.current_iaccount = self.currentItem()
        broker_widget = self.parent()
        broker_widget.accountSetUp.emit(
            self.current_iaccount,
        )
        logger.info(
            f"Broker '{self.current_ibroker.name}' "
            f"account '{self.current_iaccount.name}' is active, "
            f"account_id={self.current_iaccount.ID}"
        )

    # }}}
    @QtCore.pyqtSlot()  # __onDisconnect# {{{
    def __onDisconnect(self):
        logger.debug(f"{self.__class__.__name__}.__onDisconnect()")
        self.thread.work = False

    # }}}
    @QtCore.pyqtSlot(Services)  # __threadBrokerConnected# {{{
    def __threadBrokerConnected(self, client):
        logger.debug(f"{self.__class__.__name__}.__onBrokerConnected()")
        self.current_ibroker.activate(client)
        accounts = self.current_ibroker.getAllAccounts()
        for acc in accounts:
            iaccount = IAccount(self.current_ibroker, acc)
            self.current_itoken.addChild(iaccount)
        broker_widget = self.parent()
        broker_widget.connectEnabled.emit(
            self.current_ibroker,
        )

    # }}}
    @QtCore.pyqtSlot()  # __threadFinish# {{{
    def __threadFinish(self):
        logger.debug(f"{self.__class__.__name__}.__onFinish()")
        logger.info(
            f"Connection disabled: broker '{self.current_ibroker.name}'"
        )
        broker_widget = self.parent()
        broker_widget.connectDisabled.emit(self.current_ibroker)
        while self.current_itoken.takeChild(0):
            pass
        self.current_ibroker = None
        self.current_itoken = None
        self.current_iaccount = None

    # }}}
    def contextMenuEvent(self, e):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.currentItem()
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()


# }}}
# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Tree()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())
