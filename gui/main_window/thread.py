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
    BarEvent,
    TicEvent,
    Tinkoff,
    logger,
)


class TDataStream(QtCore.QThread):  # {{{
    new_tic = QtCore.pyqtSignal(TicEvent)
    new_bar = QtCore.pyqtSignal(BarEvent)

    def __init__(  # {{{
        self,
        data_stream: ti.services.MarketDataStreamManager,
        parent=None,
    ):
        QtCore.QThread.__init__(self, parent)

        self.stream = data_stream

    # }}}
    def run(self):  # {{{
        for response in self.stream:
            if response.trade:
                figi = response.trade.figi
                tic = Tinkoff.ti_to_av(response.trade)
                event = TicEvent(figi, tic)
                self.new_tic.emit(event)

            if response.candle:
                figi = response.candle.figi
                timeframe = Tinkoff.ti_to_av(response.candle.interval)
                bar = Tinkoff.ti_to_av(response.candle)
                event = BarEvent(figi, timeframe, bar)
                self.new_bar.emit(event)

                logger.info(event)

    # }}}


# }}}


if __name__ == "__main__":
    ...
