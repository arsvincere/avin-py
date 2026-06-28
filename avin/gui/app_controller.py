# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtCore import QObject, pyqtSignal

from avin.domain.common.timeframe import TimeFrame
from avin.gui.app_state import AppState
from avin.gui.messages import (
    Message,
    SelectAsset,
)
from avin.service.asset_data_service import AssetDataService
from avin.utils.alias import UTC, DateTime

# dev
DEV_FOOTPRINT_BEGIN = DateTime(2026, 6, 1, tzinfo=UTC)
DEV_FOOTPRINT_END = DateTime(2026, 6, 2, tzinfo=UTC)
DEV_FOOTPRINT_TIMEFRAME = TimeFrame.M1


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
            case SelectAsset(code=code):
                asset = self._state.asset_list.asset(code)

                AssetDataService.ensure_time_footprint(
                    asset,
                    self._state.source,
                    DEV_FOOTPRINT_BEGIN,
                    DEV_FOOTPRINT_END,
                    DEV_FOOTPRINT_TIMEFRAME,
                )

                self._state.selected_asset_code = code
                self._state.last_message = "SelectAsset"

        self.state_changed.emit(self._state)
