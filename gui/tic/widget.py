#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt

from avin import (
    Asset,
    TicEvent,
    logger,
)
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

        self.__main_window = parent
        self.__asset = None
        self.__client = None  # TODO: dead code?
        self.__data_stream = None
        self.__data_thread = None
        self.__thread = None

    # }}}

    def setAsset(self, asset: Asset) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setAsset()")

        self.__asset = asset

        # TODO:
        # не те и не там занимаются... метод установить ассет
        # должен установить ассет... а не подписываться и отписывать
        # на данные...
        # сейчас еще чарт виджет подписывается на бари и тики...
        # это вообще должен делать какой то отдельный модуль, типо
        # DataServer
        # DataServer - должен получать к себе брокеров (пока одного)
        # а на выходе выдавать бары, тики... кому че надо. Он один.
        # он заведует всеми подписками и отписками.
        # пока просто закоменчу - помни этой хуйней сейчас занимается
        # чарт виджет

        # if self.__data_stream is None:
        #     self.__asset = asset
        #     return
        #
        # if self.__asset is not None:
        #     tic_subscription = ti.TradeInstrument(figi=self.__asset.figi)
        #     self.__data_stream.trades.unsubscribe([tic_subscription])
        #
        # self.__asset = asset
        # tic_subscription = ti.TradeInstrument(figi=self.__asset.figi)
        # self.__data_stream.trades.subscribe([tic_subscription])
        # self.__tic_tree.clear()

    # }}}
    def setClient(self, client) -> None:  # {{{
        # TODO: dead code?
        self.__client = client

    # }}}
    def setStream(self, data_stream) -> None:  # {{{
        self.__data_stream = data_stream

    # }}}
    def setDataThread(self, thread) -> None:  # {{{
        self.__data_thread = thread
        self.__data_thread.new_tic.connect(self.__onNewTic)

    # }}}
    def clearAll(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.clearAll()")

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

    @QtCore.pyqtSlot(TicEvent)  # __onNewTic  # {{{
    def __onNewTic(self, tic_event: TicEvent) -> None:
        logger.debug(f"{self.__class__.__name__}.__onNewTic()")
        assert self.__asset.figi == tic_event.figi

        tic = tic_event.tic
        tic.setAsset(self.__asset)
        self.__tic_tree.addTic(tic)

    # }}}

    # }}}


# }}}


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = TicWidget()
    w.show()
    app.exec()
