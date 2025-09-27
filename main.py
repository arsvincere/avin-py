# ============================================================================
# FILE:         main.py
# CREATED:      2023.07.23 15:06
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import sys

from PyQt6 import QtWidgets

from avin.gui.main_window import MainWindow


def main():
    # start app
    app = QtWidgets.QApplication(sys.argv)

    # show main window
    w = MainWindow()
    w.show()
    code = app.exec()

    # before quit actions
    ...

    sys.exit(code)


if __name__ == "__main__":
    main()
