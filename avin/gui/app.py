# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import sys

from PyQt6.QtWidgets import QApplication

from avin.gui.main_window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()
