# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import sys

from PyQt6.QtWidgets import QApplication

from avin.gui.main_window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    return app.exec()
