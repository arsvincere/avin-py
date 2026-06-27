# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import QDockWidget, QPushButton, QVBoxLayout, QWidget

from avin.gui.messages import SelectIid
from avin.gui.store import Store


class InstrumentDock(QDockWidget):
    def __init__(self, store: Store) -> None:
        super().__init__("Instruments")

        self.setObjectName("instrument_dock")
        self._store = store

        content = QWidget()
        layout = QVBoxLayout(content)

        sber_btn = QPushButton("TQBR/SBER")
        gazp_btn = QPushButton("TQBR/GAZP")
        lkoh_btn = QPushButton("TQBR/LKOH")

        sber_btn.clicked.connect(lambda: self._select_iid("TQBR/SBER"))
        gazp_btn.clicked.connect(lambda: self._select_iid("TQBR/GAZP"))
        lkoh_btn.clicked.connect(lambda: self._select_iid("TQBR/LKOH"))

        layout.addWidget(sber_btn)
        layout.addWidget(gazp_btn)
        layout.addWidget(lkoh_btn)
        layout.addStretch()

        self.setWidget(content)

    def _select_iid(self, iid: str) -> None:
        self._store.dispatch(SelectIid(iid))
