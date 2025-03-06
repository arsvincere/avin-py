#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import abc

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin import Account, Broker, Tinkoff, logger
from gui.broker.tree import AccountTree, BrokerTree
from gui.custom import Css


class BrokerDockWidget(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QDockWidget.__init__(self, "Broker", parent)

        self.widget = BrokerWidget(self)
        self.setWidget(self.widget)
        self.setStyleSheet(Css.DOCK_WIDGET)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        feat = QtWidgets.QDockWidget.DockWidgetFeature
        self.setFeatures(
            feat.DockWidgetMovable
            | feat.DockWidgetClosable
            | feat.DockWidgetFloatable
        )

        # }}}


# }}}
class BrokerWidget(QtWidgets.QWidget):  # {{{
    accountChanged = QtCore.pyqtSignal(Account)
    brokerConnected = QtCore.pyqtSignal(abc.ABCMeta)
    brokerDisconnected = QtCore.pyqtSignal(abc.ABCMeta)

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserBrokers()

    # }}}

    def currentBroker(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.currentBroker()")

        return self.__broker_tree.currentBroker()

    # }}}
    def currentAccount(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.currentBroker()")

        return self.__account_tree.currentAccount()

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.STYLE)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__broker_tree = BrokerTree(self)
        self.__account_tree = AccountTree(self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.__broker_tree)
        vbox.addWidget(self.__account_tree)
        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        self.__broker_tree.connected.connect(self.__onBrokerConnected)
        self.__broker_tree.disconnected.connect(self.__onBrokerDisconnected)
        self.__account_tree.clicked.connect(self.__onAccountTreeClicked)

    # }}}
    def __loadUserBrokers(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadUserBrokers()")

        # NOTE: ну пока брокер один так что напрямую создаю
        # когда будет несколько тогда и решу где и как хранить их список
        self.__broker_tree.addBroker(Tinkoff)

    # }}}

    @QtCore.pyqtSlot()  # __onAccountTreeClicked  # {{{
    def __onAccountTreeClicked(self) -> None:
        logger.debug(f"{self.__class__.__name__}.__onAccountTreeClicked()")

        item = self.__account_tree.currentItem()
        account = item.account
        self.accountChanged.emit(account)

        logger.info(f"Account changed: {account.name}")

    # }}}
    @QtCore.pyqtSlot(Broker)  # __onBrokerConnected  # {{{
    def __onBrokerConnected(self, connected_broker: Broker) -> None:
        logger.debug(f"{self.__class__.__name__}.__onBrokerConnected()")

        self.__account_tree.clear()

        accounts = connected_broker.getAllAccounts()
        for i in accounts:
            self.__account_tree.addAccount(i)

        self.brokerConnected.emit(connected_broker)

    # }}}
    @QtCore.pyqtSlot(Broker)  # __onBrokerDisconnected  # {{{
    def __onBrokerDisconnected(self, disconnected_broker) -> None:
        logger.debug(f"{self.__class__.__name__}.__onBrokerDisconnected()")

        self.__account_tree.clear()
        self.brokerDisconnected.emit(disconnected_broker)

        print(self.__account_tree.currentAccount())

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = BrokerWidget()
    w.show()
    app.exec()
