# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsTextItem

from avin.domain.asset.asset import Asset
from avin.domain.common.timeframe import TimeFrame
from avin.gui.app_state import AppState

# dev
DEV_FOOTPRINT_TIMEFRAME = TimeFrame.M1


class CentralScene(QGraphicsScene):
    def __init__(self) -> None:
        super().__init__()

        self.setSceneRect(0, 0, 1000, 700)

    def set_state(self, state: AppState) -> None:
        self.clear()

        if state.selected_asset_code is None:
            text = "Select asset"
        else:
            asset = state.asset_list.asset(state.selected_asset_code)
            text = self._asset_text(asset, state)

        item = QGraphicsTextItem(text)
        item.setPos(500, 50)

        self.addItem(item)

    def _asset_text(self, asset: Asset, state: AppState) -> str:
        return "\n".join(
            [
                f"Selected asset: {asset.code}",
                f"Name: {asset.name}",
                f"Source: {state.source}",
                f"Ticks: {self._ticks_text(asset)}",
                (
                    f"TimeFootprint {DEV_FOOTPRINT_TIMEFRAME}: "
                    f"{self._time_footprint_text(asset)}"
                ),
                f"Message: {state.last_message}",
            ]
        )

    def _ticks_text(self, asset: Asset) -> str:
        if not asset.has_ticks():
            return "No"

        return str(len(asset.ticks()))

    def _time_footprint_text(self, asset: Asset) -> str:
        if not asset.has_time_footprint(DEV_FOOTPRINT_TIMEFRAME):
            return "No"

        footprint = asset.time_footprint(DEV_FOOTPRINT_TIMEFRAME)
        return f"{len(footprint)} clusters"
