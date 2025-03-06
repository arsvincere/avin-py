#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin import Asset, Broker, TicEvent, logger
from gui.custom import Css
from gui.tic.tree import TicTree


class TicDockWidget(QtWidgets.QDockWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        QtWidgets.QDockWidget.__init__(self, "Tic", parent)

        self.widget = TicWidget(self)
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
class TicWidget(QtWidgets.QWidget):  # {{{
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

        self.__asset = None
        self.__broker = None

    # }}}

    def setAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")

        self.__asset = asset

        if self.__broker is not None:
            self.__broker.createTicStream(self.__asset)
            self.__broker.startDataStream()

    # }}}
    def setBroker(self, broker: Broker) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setBroker()")

        self.__broker = broker
        broker.new_tic.connect(self.__onNewTicEvent)

        if self.__asset is not None:
            self.__broker.createTicStream(self.__asset)
            self.__broker.startDataStream()

    # }}}
    def clearAll(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearAll()")

        self.__broker = None
        self.__asset = None
        self.__tic_tree.clear()

    # }}}

    def __config(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.STYLE)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.__tic_tree = TicTree(self)

    # }}}
    def __createLayots(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.__tic_tree)
        self.setLayout(vbox)

    # }}}
    def __connect(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

    # }}}

    @QtCore.pyqtSlot(TicEvent)  # __onNewTicEvent  # {{{
    def __onNewTicEvent(self, tic_event: TicEvent) -> None:
        logger.debug(f"{self.__class__.__name__}.__onNewTicEvent()")

        tic = tic_event.tic
        self.__tic_tree.addTic(tic)

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = TicWidget()
    w.show()
    app.exec()
