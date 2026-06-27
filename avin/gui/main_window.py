# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow

from avin.gui.app_controller import AppController
from avin.gui.widgets.asset_list_dock import AssetListDock
from avin.gui.widgets.state_dock import StateDock


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._controller = AppController()

        self.setWindowTitle("AVIN")
        self.resize(1400, 900)

        self._init_docks()
        self._connect_controller()

    def _init_docks(self) -> None:
        self._asset_list_dock = AssetListDock(self._controller)
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self._asset_list_dock,
        )

        self._state_dock = StateDock()
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self._state_dock,
        )

    def _connect_controller(self) -> None:
        self._controller.state_changed.connect(
            self._asset_list_dock.set_state
        )
        self._controller.state_changed.connect(self._state_dock.set_state)

        self._asset_list_dock.set_state(self._controller.state)
        self._state_dock.set_state(self._controller.state)
