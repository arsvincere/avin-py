# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import time

from PyQt6 import QtCore

from avin.connect import Tinkoff
from avin.core import Asset, AssetList, BarEvent, TicEvent
from avin.utils import CFG, AvinError


class Terminal(QtCore.QObject):
    asset_changed = QtCore.pyqtSignal(Asset)

    def __init__(self):
        QtCore.QObject.__init__(self)

        self.__load_asset_list()
        self.__load_broker()
        self.__subscribe_market_data()

    def set_current_asset(self, asset: Asset) -> None:
        if asset not in self.asset_list:
            raise AvinError(f"Asset not found: {asset}")

        self.current_asset = asset
        self.asset_changed.emit(asset)

    def __load_asset_list(self) -> None:
        name = CFG.Core.default_asset_list

        self.asset_list = AssetList.load(name)

        self.current_asset = self.asset_list[0]

    def __load_broker(self) -> None:
        self.broker = Tinkoff(self)
        self.broker.new_bar.connect(self.__on_new_bar)
        self.broker.new_tic.connect(self.__on_new_tic)

        self.broker.start()
        time.sleep(5)

    def __subscribe_market_data(self) -> None:
        for asset in self.asset_list:
            self.broker.subscribe_bar(asset)
            self.broker.subscribe_tic(asset)

    @QtCore.pyqtSlot(BarEvent)
    def __on_new_bar(self, e: BarEvent):
        print(e)

    @QtCore.pyqtSlot(TicEvent)
    def __on_new_tic(self, e: TicEvent):
        print(e)


if __name__ == "__main__":
    ...
