# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import QDockWidget, QPlainTextEdit

from avin.gui.app_state import AppState


class StateDock(QDockWidget):
    def __init__(self) -> None:
        super().__init__("State")

        self.setObjectName("state_dock")

        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)

        self.setWidget(self._text)

    def set_state(self, state: AppState) -> None:
        self._text.setPlainText(self._format_state(state))

    def _format_state(self, state: AppState) -> str:
        return (
            "AppState\n"
            "--------\n"
            f"assets: {len(state.assets)}\n"
            f"current_asset_code: {state.current_asset_code}\n"
            f"source: {state.source}\n"
            f"timeframe: {state.timeframe}\n"
            f"ticks_loaded: {state.ticks_loaded}\n"
            f"footprint_clusters: {state.footprint_clusters}\n"
            f"selected_cluster: {state.selected_cluster}\n"
            f"selected_price: {state.selected_price}\n"
            f"last_message: {state.last_message}\n"
        )
