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
            f"asset_list: {state.asset_list.name}\n"
            f"assets: {len(state.asset_list)}\n"
            f"selected_asset_code: {state.selected_asset_code}\n"
            f"last_message: {state.last_message}\n"
        )
