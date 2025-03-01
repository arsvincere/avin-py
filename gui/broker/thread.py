#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import time as timer

from PyQt6 import QtCore
from tinkoff.invest import (
    Client,
)
from tinkoff.invest.services import Services


class TConnect(QtCore.QThread):  # {{{
    """Signal"""  # {{{

    brokerConnected = QtCore.pyqtSignal(Services)

    # }}}
    def __init__(self, ibroker, itoken, parent=None):  # {{{
        QtCore.QThread.__init__(self, parent)
        self.ibroker = ibroker
        self.itoken = itoken
        self.iaccount = None
        self.work = True

    # }}}
    def run(self):  # {{{
        token = self.itoken.token
        target = self.ibroker.TARGET
        with Client(token, target=target) as client:
            self.brokerConnected.emit(client)
            while self.work:
                timer.sleep(1)
                pass

    # }}}
    def closeConnection(self):  # {{{
        self.work = False


# }}}
# }}}

if __name__ == "__main__":
    ...
