#!/usr/bin/env  python3
# ============================================================================
# FILE:         main.py
# CREATED:      2023.07.23 15:06
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

import PyQt6
import tinkoff.invest as ti

from avin import Tinkoff, configureLogger, logger
from gui import MainWindow, Splash


def main():
    with ti.Client(Tinkoff.TOKEN, target=Tinkoff.TARGET) as client:
        response = client.users.get_accounts()
        if not response:
            logger.error("Connection failed!")
            return

        try:
            # start app
            app = PyQt6.QtWidgets.QApplication(sys.argv)

            # show splash
            splash = Splash()
            splash.show()

            # show main window
            w = MainWindow(client)
            w.show()
            splash.finish(w)
            code = app.exec()

            # before quit actions
            sys.exit(code)

        except Exception as e:
            logger.exception(e)


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    main()
