# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from PyQt6 import QtWidgets

from avin.gui.chart.gchart import GChart
from avin.gui.chart.gcross import GCross
from avin.gui.chart.labels import BarInfo, ChartLabels
from avin.utils import CFG

FLAGS = QtWidgets.QGraphicsItem.GraphicsItemFlag
IGNORE_TRANSFORMATION = FLAGS.ItemIgnoresTransformations


class ChartScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent):
        QtWidgets.QGraphicsScene.__init__(self, parent)

        self.__config()
        self.__create_graphics_widgets()

        self.gchart = None

    def mouseMoveEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent | None):
        # super().mouseMoveEvent(e)

        if e is None:
            return

        if self.gchart is None:
            return e.ignore()

        x = e.scenePos().x()
        self.bar_info.update_info(int(x))

        return e.ignore()

    def set_gchart(self, gchart: GChart) -> None:
        self.remove_gchart()
        self.setSceneRect(gchart.rect)

        self.gchart = gchart
        self.cross = GCross(gchart)
        self.cross.setFlag(IGNORE_TRANSFORMATION)

        self.addItem(self.gchart)
        self.addItem(self.cross)

        for lable in self.top:
            lable.set_gchart(gchart)

    def remove_gchart(self) -> None:
        if self.gchart is not None:
            self.removeItem(self.gchart)
            self.gchart = None

    def current_gchart(self) -> GChart | None:
        return self.gchart

    def __config(self):
        self.setBackgroundBrush(CFG.Chart.bg)

    def __create_graphics_widgets(self) -> None:
        # create widgets
        self.bar_info = BarInfo()

        # create QtWidgets.QGraphicsProxyWidget
        self.top = ChartLabels()
        self.top.add(self.bar_info)
        self.top.setFlag(IGNORE_TRANSFORMATION)

        self.addItem(self.top)


if __name__ == "__main__":
    ...
