#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import tinkoff.invest as ti
from PyQt6 import QtCore

from avin import (
    Tic,
    Tinkoff,
)


class TTic(QtCore.QThread):  # {{{
    new_tic = QtCore.pyqtSignal(Tic)

    def __init__(  # {{{
        self,
        data_stream: ti.services.MarketDataStreamManager,
        parent=None,
    ):
        QtCore.QThread.__init__(self, parent)

        self.__data_stream = data_stream

    # }}}
    def run(self):  # {{{
        for response in self.__data_stream:
            if response.trade:
                figi = response.trade.figi
                tic = Tinkoff.ti_to_av(response.trade)
                self.new_tic.emit(tic)

    # }}}


# }}}


if __name__ == "__main__":
    ...
