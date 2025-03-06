#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import abc
import asyncio

from PyQt6 import QtCore

from avin import Broker


class TConnect(QtCore.QThread):  # {{{
    successful = QtCore.pyqtSignal(abc.ABCMeta)
    failure = QtCore.pyqtSignal(abc.ABCMeta)

    def __init__(self, broker: Broker, parent=None):  # {{{
        QtCore.QThread.__init__(self, parent)

        self.__broker = broker
        self.__work = False

    # }}}
    def run(self):  # {{{
        asyncio.run(self.__aconnect())

    # }}}
    def stop(self):  # {{{
        self.__work = False

    # }}}

    async def __aconnect(self):  # {{{
        result = await self.__broker.connect()

        if result:
            self.__work = True
            self.successful.emit(self.__broker)
            while self.__work:
                await asyncio.sleep(1)
            self.__broker.disconnect()
        else:
            self.__work = False
            self.failure.emit(self.__broker)

    # }}}


# }}}


if __name__ == "__main__":
    ...
