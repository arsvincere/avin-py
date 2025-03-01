#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtCore, QtWidgets

from avin.company import Broker
from avin.const import BROKER_DIR
from avin.gui.account import IAccount
from avin.gui.custom import Palette
from avin.utils import Cmd


class BrokerWidget(QtWidgets.QWidget):  # {{{
    """Signal"""  # {{{

    connectEnabled = QtCore.pyqtSignal(Broker)
    accountSetUp = QtCore.pyqtSignal(IAccount)
    connectDisabled = QtCore.pyqtSignal(Broker)

    # }}}
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__loadBrokers()
        self.__current_broker = None
        self.__current_account = None

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tree = Tree(self)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)

    # }}}
    def __loadBrokers(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__loadBrokers()")
        dirs = Cmd.getDirs(BROKER_DIR, full_path=True)
        for d in dirs:
            name = Cmd.name(d)
            if name == "Sandbox":
                ibroker = ISandbox(d)
            if name == "Tinkoff":
                ibroker = ITinkoff(d)
            self.tree.addTopLevelItem(ibroker)
        self.tree.expandAll()

    # }}}
    def currentToken(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.currentToken()")
        return self.tree.current_itoken

    # }}}
    def currentBroker(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.currentBroker()")
        return self.tree.current_ibroker

    # }}}
    def currentAccount(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.currentBroker()")
        return self.tree.current_account


# }}}
# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    user_palette = Palette()
    app.setPalette(user_palette)
    w = BrokerWidget()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    # w.showMaximized()
    w.show()
    sys.exit(app.exec())
