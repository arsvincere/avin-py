# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import QGraphicsScene

from avin.gui.app_state import AppState


class CentralScene(QGraphicsScene):
    def __init__(self) -> None:
        super().__init__()

        self.setSceneRect(0, 0, 1000, 700)

    def set_state(self, state: AppState) -> None:
        self.clear()

        if state.current_asset_code is None:
            text = "Select asset"
        else:
            text = f"Selected asset: {state.current_asset_code}"

        item = self.addText(text)
        item.setPos(20, 20)
