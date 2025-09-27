# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import sys

from PyQt6 import QtWidgets

from avin.core import TimeFrame
from avin.gui.chart.gchart import GChart
from avin.gui.chart.scene import ChartScene
from avin.gui.chart.view import ChartView
from avin.gui.custom import Css
from avin.terminal import Terminal


class ChartWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.__config()
        self.__create_widgets()
        self.__create_layouts()

    def set_terminal(self, terminal: Terminal) -> None:
        self.terminal = terminal

        tf = TimeFrame.M1
        chart = terminal.current_asset.load_chart(tf)  # type: ignore
        gchart = GChart(chart, None)

        self.scene.set_gchart(gchart)
        self.view.center_on_last()

    def __config(self) -> None:
        self.setStyleSheet(Css.STYLE)

    def __create_widgets(self) -> None:
        self.view = ChartView(self)
        self.scene = ChartScene(self)

        self.view.setScene(self.scene)

    def __create_layouts(self) -> None:
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.view)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)


if __name__ == "__main__":
    terminal = Terminal()
    app = QtWidgets.QApplication(sys.argv)
    w = ChartWidget(parent=None)

    w.set_terminal(terminal)
    w.setWindowTitle("AVIN")
    w.show()

    sys.exit(app.exec())
