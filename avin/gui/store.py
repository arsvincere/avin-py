# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from dataclasses import replace

from PyQt6.QtCore import QObject, pyqtSignal

from avin.gui.messages import (
    AppStarted,
    ClearSelection,
    Message,
    SelectCluster,
    SelectIid,
    SelectPrice,
    SelectTimeframe,
)
from avin.gui.state import AppState


class Store(QObject):
    state_changed = pyqtSignal(object)

    def __init__(self) -> None:
        super().__init__()
        self._state = AppState()

    @property
    def state(self) -> AppState:
        return self._state

    def dispatch(self, message: Message) -> None:
        self._state = self._update(self._state, message)
        self.state_changed.emit(self._state)

    def _update(self, state: AppState, message: Message) -> AppState:
        match message:
            case AppStarted():
                return replace(
                    state,
                    last_message="AppStarted",
                )

            case SelectIid(iid=iid):
                return replace(
                    state,
                    current_iid=iid,
                    ticks_loaded=0,
                    footprint_clusters=0,
                    selected_cluster=None,
                    selected_price=None,
                    last_message="SelectIid",
                )

            case SelectTimeframe(timeframe=timeframe):
                return replace(
                    state,
                    timeframe=timeframe,
                    footprint_clusters=0,
                    selected_cluster=None,
                    selected_price=None,
                    last_message="SelectTimeframe",
                )

            case SelectCluster(cluster_index=cluster_index):
                return replace(
                    state,
                    selected_cluster=cluster_index,
                    last_message="SelectCluster",
                )

            case SelectPrice(price=price):
                return replace(
                    state,
                    selected_price=price,
                    last_message="SelectPrice",
                )

            case ClearSelection():
                return replace(
                    state,
                    selected_cluster=None,
                    selected_price=None,
                    last_message="ClearSelection",
                )
