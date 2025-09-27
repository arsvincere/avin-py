# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================


from PyQt6 import QtWidgets

from avin import Terminal


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):  # {{{
        QtWidgets.QMainWindow.__init__(self, parent)

        self.terminal = Terminal()
