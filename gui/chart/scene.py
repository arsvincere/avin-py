#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore, QtWidgets

from avin.utils import logger
from gui.chart.gchart import GChart
from gui.chart.gcross import GCross
from gui.chart.glabels import BarInfo, ChartLabels, VolumeInfo
from gui.chart.gtest import GTradeList
from gui.custom import Theme
from gui.indicator.item import Indicator


class ChartScene(QtWidgets.QGraphicsScene):
    # QGraphicsItem::ItemIgnoresTransformations
    flags = QtWidgets.QGraphicsItem.GraphicsItemFlag
    ignore_transformation = flags.ItemIgnoresTransformations

    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsScene.__init__(self, parent)

        self.__config()
        self.__createEmpyRect()
        self.__createGraphicsWidgets()
        self.__createChartGroup()
        self.__createTListGroup()

    # }}}

    def mouseMoveEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.mouseMoveEvent()")
        # super().mouseMoveEvent(e)

        if not self.__has_chart:
            return e.ignore()

        x = e.scenePos().x()

        self.bar_info.update(x)
        self.vol_info.update(x)

        return e.ignore()

    # }}}
    def mousePressEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.mousePressEvent()")
        super().mousePressEvent(e)

        if not self.__has_chart:
            return e.ignore()

        x = e.scenePos().x()

        for label in self.top:
            label.update(x)

        return e.ignore()

    # }}}
    def mouseReleaseEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):  # {{{
        logger.debug(f"{self.__class__.__name__}.mouseReleaseEvent()")
        super().mouseReleaseEvent(e)

        return e.ignore()

    # }}}
    def mouseDoubleClickEvent(  # {{{
        self, e: QtWidgets.QGraphicsSceneMouseEvent
    ):
        logger.debug(f"{self.__class__.__name__}.mouseReleaseEvent()")
        """
        загрузить новый график, именно за этот период (бар)
        стереть станый график.
        нарисовать главный график до выделенного бара
        нарисовать раскрытый бар
        продолжить рисовать главный график.
        """
        # if self.chart is None:
        #     return e.ignore()
        # n = self._nFromPos(e.scenePos())
        # bar_items = self.gchart.childItems()
        # zoom_bar = bar_items[n].bar
        # ID = self.chart.ID
        # begin = zoom_bar.dt
        # end = zoom_bar.dt + self.chart.timeframe
        # self.zoom_chart = Chart(ID, TimeFrame("5M"), begin, end)
        # ###
        # self.removeChart()
        # ###
        # scene_x0 = 0
        # n1 = self.chart.getBarsCount() - 1
        # n2 = self.zoom_chart.getBarsCount()
        # scene_x1 = (n1 + n2) * self.SCALE_X
        # scene_y0 = 0
        # scene_y1 = self.chart.highestHigh() * self.SCALE_Y
        # height = scene_y1 - scene_y0 #+ 2 * self.SCENE_INDENT
        # width = scene_x1 - scene_x0 #+ 2 * self.SCENE_INDENT
        # self.setSceneRect(0, 0, width, height)
        # ###
        # i = 0
        # for big_bar in self.chart:
        #     if big_bar.dt != zoom_bar.dt:
        #         bar_item = GraphicsBarItem(big_bar, i, self)
        #         self.gchart.addToGroup(bar_item)
        #         i += 1
        #     else:
        #         bar_item = GraphicsBarItem(big_bar, i, self)
        #         self.gchart.addToGroup(bar_item)
        #         i += 1
        #         for small_bar in self.zoom_chart:
        #             bar_item = GraphicsZoomBarItem(small_bar, i, self)
        #             self.gchart.addToGroup(bar_item)
        #             i += 1

    # }}}

    def setGChart(self, gchart: GChart) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setGChart()")

        self.removeGChart()
        self.setSceneRect(gchart.rect)

        self.gchart = gchart
        self.volumes = gchart.gvols
        self.cross = GCross(gchart)
        self.cross.setFlag(self.ignore_transformation)

        self.addItem(self.gchart)
        self.addItem(self.cross)
        # XXX: когда вынесешь volumes в отдельный индикатор
        # self.addItem(self.volumes)

        self.__has_chart = True

        for lable in self.top:
            lable.setGChart(gchart)

        self.gchart.indicators_updated.connect(self.__onIndicatorsUpdated)

    # }}}
    def removeGChart(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeGChart()")

        if self.__has_chart:
            self.removeItem(self.gchart)
            self.removeItem(self.cross)
            self.__has_chart = False

    # }}}
    def currentGChart(self) -> GChart:  # {{{
        logger.debug(f"{self.__class__.__name__}.currentChart()")

        return self.gchart

    # }}}

    def setGTradeList(self, gtrade_list: GTradeList) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setGTradeList()")

        self.setGChart(gtrade_list.gchart)

        self.removeGTrades()
        self.gtrades = gtrade_list.gtrades
        self.addItem(self.gtrades)
        self.__has_gtrades = True

        # TODO: это порно код, подумай как лучше сделать
        view = self.views()[0]
        view.resetCurrentGTrade()

    # }}}
    def removeGTrades(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeGTrades()")

        if self.__has_gtrades:
            self.removeItem(self.gtrades)
            self.__has_gtrades = False

    # }}}

    def setIndList(self, ind_list) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.setIndList()")

        # add labels
        for i in ind_list:
            label = i.label()
            self.top.add(label)

        # add pinned indicators
        for i in ind_list:
            if i.position == Indicator.Position.FOOTER:
                self.footer.append(i)
            if i.position == Indicator.Position.LEFT:
                self.left.append(i)

    # }}}
    def removeIndicators(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.removeIndicators()")

        # пересоздаем график виджеты в левом верхнем углу
        self.top.clear()
        self.__createGraphicsWidgets()

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setBackgroundBrush(Theme.Chart.BG)

    # }}}
    def __createEmpyRect(self):  # {{{
        """Инициализируем сцену произвольным прямоугольником

        Просто для того чтобы потом scene.labels нормально в верхнем
        углу расположить.
        """
        logger.debug(f"{self.__class__.__name__}.__createEmpyRect()")

        rect = QtCore.QRectF(0, 0, 800, 600)
        self.setSceneRect(rect)

    # }}}
    def __createGraphicsWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createGraphicsWidgets()")

        # create widgets
        self.bar_info = BarInfo()
        self.vol_info = VolumeInfo()

        # create QtWidgets.QGraphicsProxyWidget
        self.top = ChartLabels()
        self.top.add(self.bar_info)
        self.top.add(self.vol_info)
        self.top.setFlag(self.ignore_transformation)

        self.addItem(self.top)

    # }}}
    def __createChartGroup(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createChartGroup()")

        self.__has_chart = False
        self.gchart = None
        self.cross = QtWidgets.QGraphicsItemGroup()
        self.volumes = QtWidgets.QGraphicsItemGroup()
        self.footer = list()
        self.left = list()
        self.right = list()

    # }}}
    def __createTListGroup(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createTListGroup()")

        self.__has_gtrades = False
        self.gtrades = None

    # }}}
    def __onIndicatorsUpdated(self):  # {{{
        # XXX: говнокод...
        # суть. График после получения нового исторического бара
        # обновляет индикаторы, они создают новые график итемы.
        # Обновить старые не получется... сцена их не видит...
        # Новые график итемы панельных индикаторов будут иметь
        # дефолтные координаты. Поэтому дергаем view порт, чтобы
        # он их разместил правильно.
        view = self.views()[0]
        view._movePinnedPanels()
        print("moved_pinned_panels")

    # }}}


if __name__ == "__main__":
    ...
