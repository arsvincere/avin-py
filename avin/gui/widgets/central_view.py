# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import QGraphicsView

from avin.gui.app_state import AppState
from avin.gui.widgets.central_scene import CentralScene


class CentralView(QGraphicsView):
    def __init__(self) -> None:
        super().__init__()

        self._scene = CentralScene()
        self.setScene(self._scene)

    def set_state(self, state: AppState) -> None:
        self._scene.set_state(state)
