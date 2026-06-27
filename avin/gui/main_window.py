# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow

from avin.gui.store import Store
from avin.gui.widgets.instrument_dock import InstrumentDock
from avin.gui.widgets.state_dock import StateDock


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._store = Store()

        self.setWindowTitle("AVIN")
        self.resize(1400, 900)

        self._init_docks()
        self._connect_store()

    def _init_docks(self) -> None:
        self._instrument_dock = InstrumentDock(self._store)
        self.addDockWidget(
            Qt.DockWidgetArea.LeftDockWidgetArea,
            self._instrument_dock,
        )

        self._state_dock = StateDock()
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea,
            self._state_dock,
        )

    def _connect_store(self) -> None:
        self._store.state_changed.connect(self._state_dock.set_state)
        self._state_dock.set_state(self._store.state)
