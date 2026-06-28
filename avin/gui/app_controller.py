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
    Message,
    SelectAsset,
)


class AppController(QObject):
    state_changed = pyqtSignal(object)

    def __init__(self, state: AppState) -> None:
        super().__init__()

        self._state = state

    @property
    def state(self) -> AppState:
        return self._state

    def handle(self, message: Message) -> None:
        match message:
            case AppStarted():
                self._state.last_message = "AppStarted"

            case SelectAsset(code=code):
                if code not in self._state.asset_list:
                    raise ValueError(f"Asset not found: {code}")

                self._state.current_asset_code = code
                self._state.last_message = "SelectAsset"

        self.state_changed.emit(self._state)
