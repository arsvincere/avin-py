# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from PyQt6 import QtCore

from avin.core import Asset, AssetList
from avin.utils import CFG, AvinError


class Terminal(QtCore.QObject):
    asset_changed = QtCore.pyqtSignal(Asset)

    def __init__(self):
        QtCore.QObject.__init__(self)

        self.__load_asset_list()

    def set_current_asset(self, asset: Asset) -> None:
        if asset not in self.asset_list:
            raise AvinError(f"Asset not found: {asset}")

        self.current_asset = asset
        self.asset_changed.emit(asset)

    def __load_asset_list(self) -> None:
        name = CFG.Core.default_asset_list

        self.asset_list = AssetList.load(name)

        self.current_asset = self.asset_list[0]


if __name__ == "__main__":
    ...
