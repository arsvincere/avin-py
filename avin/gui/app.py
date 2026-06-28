# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import sys

from PyQt6.QtWidgets import QApplication

from avin.gui.app_controller import AppController
from avin.gui.app_state import AppState
from avin.gui.main_window import MainWindow
from avin.service.asset.list_manager import AssetListManager
from avin.system.conf import cfg


class AvinApp:
    def __init__(self) -> None:
        self._qapp = QApplication(sys.argv)

        asset_list = AssetListManager.load_default_or_empty()
        source = cfg.default_source

        state = AppState(
            asset_list=asset_list,
            source=source,
        )

        self._controller = AppController(state)
        self._main_window = MainWindow(self._controller)

    def run(self) -> int:
        self._main_window.show()
        return self._qapp.exec()


def run() -> int:
    app = AvinApp()
    return app.run()
