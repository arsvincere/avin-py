# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtCore import QObject, pyqtSignal

from avin.gui.app_state import AppState
from avin.gui.messages import (
    AppStarted,
    ClearSelection,
    Message,
    SelectAsset,
    SelectCluster,
    SelectPrice,
    SelectTimeframe,
)
from avin.service.asset_list_service import AssetListService


class AppController(QObject):
    state_changed = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()

        self._state = AppState(assets=AssetListService.load_default())

    @property
    def state(self) -> AppState:
        return self._state

    def handle(self, message: Message) -> None:
        match message:
            case AppStarted():
                self._state.last_message = "AppStarted"

            case SelectAsset(code=code):
                if code not in self._state.assets:
                    raise ValueError(f"Asset not found: {code}")

                self._state.current_asset_code = code
                self._state.ticks_loaded = 0
                self._state.footprint_clusters = 0
                self._state.selected_cluster = None
                self._state.selected_price = None
                self._state.last_message = "SelectAsset"

            case SelectTimeframe(timeframe=timeframe):
                self._state.timeframe = timeframe
                self._state.footprint_clusters = 0
                self._state.selected_cluster = None
                self._state.selected_price = None
                self._state.last_message = "SelectTimeframe"

            case SelectCluster(cluster_index=cluster_index):
                self._state.selected_cluster = cluster_index
                self._state.last_message = "SelectCluster"

            case SelectPrice(price=price):
                self._state.selected_price = price
                self._state.last_message = "SelectPrice"

            case ClearSelection():
                self._state.selected_cluster = None
                self._state.selected_price = None
                self._state.last_message = "ClearSelection"

        self.state_changed.emit(self._state)
