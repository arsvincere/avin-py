#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import abc

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin import Account, Broker, logger
from gui.broker.item import AccountItem, BrokerItem
from gui.broker.thread import TConnect
from gui.custom import Css, Dialog, Menu


class BrokerTree(QtWidgets.QTreeWidget):  # {{{
    connected = QtCore.pyqtSignal(abc.ABCMeta)
    disconnected = QtCore.pyqtSignal(abc.ABCMeta)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenu()
        self.__connect()

        self.__thread = None
        self.__connected_broker = None

    # }}}

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")

        self.__current_item = self.itemAt(e.pos())
        self.__menu.exec(QtGui.QCursor.pos())

        return e.ignore()

    # }}}
    def addBroker(self, broker: Broker):  # {{{
        item = BrokerItem(broker)
        self.addTopLevelItem(item)

    # }}}
    def currentBroker(self):  # {{{
        return self.__connected_broker

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
        for l in BrokerItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(BrokerItem.Column.Name, Qt.SortOrder.AscendingOrder)

        # config width
        self.setColumnWidth(BrokerItem.Column.Name, 180)
        self.setMinimumWidth(200)

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.__menu = _BrokerMenu(parent=self)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__menu.connect.triggered.connect(self.__onConnect)
        self.__menu.disconnect.triggered.connect(self.__onDisconnect)

    # }}}

    @QtCore.pyqtSlot()  # __onConnect  # {{{
    def __onConnect(self):
        logger.debug(f"{self.__class__.__name__}.__onConnect()")

        self.__thread = TConnect(self.__current_item.broker)
        self.__thread.successful.connect(self.__threadSuccessful)
        self.__thread.failure.connect(self.__threadFailure)
        self.__thread.finished.connect(self.__threadFinished)
        self.__thread.start()

    # }}}
    @QtCore.pyqtSlot()  # __onDisconnect  # {{{
    def __onDisconnect(self):
        logger.debug(f"{self.__class__.__name__}.__onDisconnect()")

        self.__thread.stop()

    # }}}
    @QtCore.pyqtSlot(Broker)  # __threadSuccessful  # {{{
    def __threadSuccessful(self, connected_broker: Broker):
        logger.debug(f"{self.__class__.__name__}.__threadSuccessful()")

        self.__connected_broker = connected_broker
        self.connected.emit(connected_broker)

    # }}}
    @QtCore.pyqtSlot(Broker)  # __threadFailure  # {{{
    def __threadFailure(self, broker: Broker):
        logger.debug(f"{self.__class__.__name__}.__threadFailure()")

        self.__connected_broker = None

        Dialog.error(f"Fail to connect {broker.name}")

    # }}}
    @QtCore.pyqtSlot()  # __threadFinished  # {{{
    def __threadFinished(self):
        logger.debug(f"{self.__class__.__name__}.__threadFinished()")

        self.disconnected.emit(self.__connected_broker)
        self.__connected_broker = None

    # }}}


# }}}
class AccountTree(QtWidgets.QTreeWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.__config()
        self.__createMenu()
        self.__connect()

        self.__active_account = None

    # }}}

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")

        self.__current_item = self.itemAt(e.pos())
        self.__menu.exec(QtGui.QCursor.pos())

        return e.ignore()

    # }}}
    def addAccount(self, account: Account):  # {{{
        item = AccountItem(account)
        self.addTopLevelItem(item)

    # }}}
    def currentAccount(self):  # {{{
        return self.__active_account

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
        for l in AccountItem.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.header().setStyleSheet(Css.TREE_HEADER)

        # config sorting
        self.setSortingEnabled(True)
        self.sortByColumn(
            AccountItem.Column.Name, Qt.SortOrder.AscendingOrder
        )

        # config width
        self.setColumnWidth(AccountItem.Column.Name, 180)
        self.setMinimumWidth(200)

    # }}}
    def __createMenu(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createMenus()")

        self.__menu = _AccountMenu(parent=self)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.__menu.select.triggered.connect(self.__onSelect)

    # }}}

    @QtCore.pyqtSlot()  # __onSelect  # {{{
    def __onSelect(self):
        logger.debug(f"{self.__class__.__name__}.__onSelect()")

        self.__active_account = self.__current_item.account

    # }}}


# }}}


class _BrokerMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.connect = QtGui.QAction("Connect", self)
        self.disconnect = QtGui.QAction("Disconnect", self)

        self.addAction(self.connect)
        self.addAction(self.disconnect)

    # }}}


# }}}
class _AccountMenu(Menu):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Menu.__init__(self, parent=parent)

        self.select = QtGui.QAction("Select", self)

        self.addAction(self.select)

    # }}}

    # }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = BrokerTree()
    w.show()
    app.exec()
