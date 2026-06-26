# ============================================================================
# URL:          http://arsvincjre.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from PyQt6.QtWidgets import QDockWidget, QPlainTextEdit


class StateDock(QDockWidget):
    def __init__(self) -> None:
        super().__init__("State")

        self.setObjectName("state_dock")

        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)

        self.setWidget(self._text)
        self.set_state_text(self._default_text())

    def set_state_text(self, text: str) -> None:
        self._text.setPlainText(text)

    def _default_text(self) -> str:
        return (
            "AppState\n"
            "--------\n"
            "current_iid: None\n"
            "source: None\n"
            "timeframe: None\n"
            "ticks_loaded: 0\n"
            "footprint_clusters: 0\n"
            "selected_cluster: None\n"
            "selected_price: None\n"
            "last_action: AppStarted\n"
        )
