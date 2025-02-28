#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """
import sys
sys.path.append("/usr/lib/python3.11/site-packages")
sys.path.append("/home/alex/.local/lib/python3.11/site-packages")
sys.path.append("/home/alex/yandex/avin-dev/")
import os
import enum
import logging
import time as timer
from datetime import datetime, date, time
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from tinkoff.invest import (
    Client,
    AsyncClient,
    )

from tinkoff.invest.services import (
    Services
    )

from tinkoff.invest.constants import (
    INVEST_GRPC_API,
    INVEST_GRPC_API_SANDBOX,
    )

from avin import const
from avin.core import (
    DataNotFound,
    TinkoffData,
    TimeFrame,
    Bar,
    Data,
    Extremum,
    Chart,
    Exchange,
    Type,
    Asset,
    Share,
    Index,
    AssetList,
    Signal,
    Strategy,
    Trade,
    TradeList,
    Test,
    Report,
    Filter,
    Indicator,
    Order,
    Operation,
    Position,
    Portfolio,
    )

from avin.company import (
    Analytic,
    Tester,
    Scout,
    Broker,
    Tinkoff,
    Sandbox,
    Account,
    )

from avin.utils import (
    now,
    binarySearch,
    Cmd,
    findLeft,
    findRight,
    )

logger = logging.getLogger("LOGGER")

class GuiError(Exception): pass
# class GraphicsZoomBarItem(GraphicsBarItem):
#     def __init__(self, bar, n, scene, draw_body=True, parent=None):
#         QtWidgets.QGraphicsItemGroup.__init__(self, parent)
#         self.bar = bar
#         self.n = n
#         self.scene = scene
#         super()._calcCoordinates()
#         self._setColor()
#         if draw_body:
#             super()._createBody()
#         else:
#             super()._createOpenLine()
#             super()._createCloseLine()
#         super()._createShadowLine()
#
#     def _setColor(self):
#         if self.bar.isBull():
#             self.color = COLOR.ZOOM_BULL
#         elif self.bar.isBear():
#             self.color = COLOR.ZOOM_BEAR
#         else:
#             self.color = COLOR.WHITE
#
#
# class GraphicsMarkItem(QtWidgets.QGraphicsItemGroup):
#     """ -- Doc
#     Графическая метка над баром - прямоугольник COLOR.MARK цвета
#     """
#
#     def __init__(self, bar_item, parent=None):
#         QtWidgets.QGraphicsItemGroup.__init__(self, parent)
#         self.bar_item = bar_item
#         self._createShape()
#
#     def _createShape(self):
#         x0 = self.bar_item.x0
#         x1 = self.bar_item.x1
#         y0 = self.bar_item.y_hgh - 100
#         y1 = self.bar_item.y_hgh - 200
#         width = x1 - x0
#         height = y1 - y0
#         mark = QtWidgets.QGraphicsRectItem(x0, y0, width, height)
#         mark.setPen(COLOR.MARK)
#         mark.setBrush(COLOR.MARK)
#         self.addToGroup(mark)
#
#
# class GraphicsTradeItem(QtWidgets.QGraphicsItemGroup):
#     def __init__(self,
#             itrade: TradeItem,
#             scene: QtWidgets.QGraphicsScene,
#             parent=None
#             ):
#         QtWidgets.QGraphicsItemGroup.__init__(self, parent)
#         self.itrade = itrade
#         itrade.gtrade = self
#         self.scene = scene
#         self.__calcCoordinates()
#         self.__crateTradeShape()
#         self.__createOpenItem()
#         self.__createStopLossItem()
#         self.__createTakeProfitItem()
#         self.__createAnnotation()
#
#     def __calcCoordinates(self):
#         trade = self.itrade.trade
#         self.x_opn = (
#             self.scene._xFromDatetime(trade.open_dt)
#             )
#         self.x_cls = (
#             self.scene._xFromDatetime(trade.close_dt)
#             )
#         gbar = self.scene._barItemFromDatetime(trade.open_dt)
#         gbar.gtrade = self
#         y_hgh = gbar.high_pos.y()
#         self.y0 = y_hgh - 50
#         self.trade_pos = QtCore.QPointF(self.x_opn, self.y0)
#
#     def __crateTradeShape(self):
#         x0 = self.x_opn
#         x1 = x0 + self.scene.SCALE_X
#         x_center = (x0 + x1) / 2
#         y0 = self.y0
#         y1 = y0 - self.scene.SCALE_X
#         trade = self.itrade.trade
#         if trade.type == LONG:
#             p1 = QtCore.QPointF(x0, y0)
#             p2 = QtCore.QPointF(x1, y0)
#             p3 = QtCore.QPointF(x_center, y1)
#             triangle = QtGui.QPolygonF([p1, p2, p3])
#         else:
#             p1 = QtCore.QPointF(x0, y1)
#             p2 = QtCore.QPointF(x1, y1)
#             p3 = QtCore.QPointF(x_center, y0)
#             triangle = QtGui.QPolygonF([p1, p2, p3])
#         triangle = QtWidgets.QGraphicsPolygonItem(triangle)
#         if trade.isWin():
#             triangle.setPen(COLOR.TRADE_WIN)
#             triangle.setBrush(COLOR.TRADE_WIN)
#         else:
#             triangle.setPen(COLOR.TRADE_LOSS)
#             triangle.setBrush(COLOR.TRADE_LOSS)
#         self.addToGroup(triangle)
#
#     def __createOpenItem(self):
#         trade = self.itrade.trade
#         open_price = float(trade.strategy["open price"])
#         self.y_opn = self.scene._yFromPrice(open_price)
#         open_item = QtWidgets.QGraphicsLineItem(
#             self.x_opn,
#             self.y_opn,
#             self.x_cls + self.scene.SCALE_X,
#             self.y_opn
#             )
#         pen = QtGui.QPen()
#         pen.setWidth(self.scene.POS_OPEN_WIDTH)
#         pen.setColor(COLOR.OPEN)
#         open_item.setPen(pen)
#         self.addToGroup(open_item)
#
#     def __createStopLossItem(self):
#         trade = self.itrade.trade
#         stop_loss_price = float(trade.strategy["stop price"])
#         self.y_stop = self.scene._yFromPrice(stop_loss_price)
#         stop_loss = QtWidgets.QGraphicsLineItem(
#             self.x_opn,
#             self.y_stop,
#             self.x_cls + self.scene.SCALE_X,
#             self.y_stop,
#             )
#         pen = QtGui.QPen()
#         pen.setWidth(self.scene.POS_STOP_WIDTH)
#         pen.setColor(COLOR.STOP)
#         stop_loss.setPen(pen)
#         self.addToGroup(stop_loss)
#
#     def __createTakeProfitItem(self):
#         trade = self.itrade.trade
#         take_profit_price = float(trade.strategy["take price"])
#         self.y_take = self.scene._yFromPrice(take_profit_price)
#         take_profit = QtWidgets.QGraphicsLineItem(
#             self.x_opn,
#             self.y_take,
#             self.x_cls + self.scene.SCALE_X,
#             self.y_take,
#             )
#         pen = QtGui.QPen()
#         pen.setWidth(self.scene.POS_TAKE_WIDTH)
#         pen.setColor(COLOR.TAKE)
#         take_profit.setPen(pen)
#         self.addToGroup(take_profit)
#
#     def __createAnnotation(self):
#         trade = self.itrade.trade
#         msk_dt = trade.dt + MSK_TIME_DIF
#         str_dt = msk_dt.strftime("%Y-%m-%d  %H:%M")
#         text = (
#             f"{str_dt}\n"
#             f"Result: {trade.result}\n"
#             f"Days: {trade.holding}\n"
#             f"% / day: {trade.percent_per_day}"
#             )
#         label = QtWidgets.QLabel(text)
#         self.__annotation = self.scene.addWidget(label)
#         self.__annotation.setPos(self.x_opn, self.y0 - 200)
#         self.__annotation.hide()
#
#     def showAnnotation(self):
#         self.__annotation.show()
#
#     def hideAnnotation(self):
#         self.__annotation.hide()
#
#
# class GraphicsTradeListItem(QtWidgets.QGraphicsItemGroup):
#     def __init__(self, itlist: TradeListItem, scene, parent=None):
#         logger.debug(f"{self.__class__.__name__}.__init__({itlist.name})")
#         QtWidgets.QGraphicsItemGroup.__init__(self, parent)
#         self.itlist = itlist
#         self.scene = scene
#         self.__createGraphicsTradeItems()
#         # сохраним в TradeListItem ссылку на GraphicsTradeListItem
#         itlist.gtlist = self
#
#     def __createGraphicsTradeItems(self):
#         for i in range(self.itlist.childCount()):
#             itrade = self.itlist.child(i)
#             gtrade = GraphicsTradeItem(itrade, self.scene)
#             self.addToGroup(gtrade)
#
#
# class GraphicsExtremumItem(QtWidgets.QGraphicsItemGroup):
#     """ -- Doc
#     Конструктор принимает список экстремумов и сцену.
#     Создает из них QGraphicsItemGroup - линии соединяющие экстремумы
#     и точки - графические метки у среднесрочных и долгосрочных
#     экстремумов. Работает в масштабе полученной сцены.
#     """
#
#     """ Const """
#     LONGTERM_LINE_WIDTH =  4
#     MIDTERM_LINE_WIDTH =   2
#     SHORTTERM_LINE_WIDTH = 1
#
#     """ Data index """
#     EXTR_POS = 0
#     SHAPE_POS = 1
#
#     def __init__(self,
#             elist: list,
#             scene: QtWidgets.QGraphicsScene,
#             parent=None
#             ):
#         QtWidgets.QGraphicsItemGroup.__init__(self, parent)
#         self.elist = elist
#         self.scene = scene
#         points = self.__createPoints()
#         lines = self.__createLines(points)
#         self.addToGroup(points)
#         self.addToGroup(lines)
#
#     def __createPoints(self):
#         points = QtWidgets.QGraphicsItemGroup()
#         for e in self.elist:
#             shape = self.__createPointShape(e)
#             points.addToGroup(shape)
#         return points
#
#     def __createPointShape(self, extr):
#         """
#         (x, y)   - точка экстремума на графике 'epos'
#         (x0, y0) - точка начала QGraphicsEllipseItem, графической
#                    метки экстремума, 'spos'
#         """
#         shape = QtWidgets.QGraphicsItemGroup()
#         x0 = self.scene._xFromDatetime(extr.dt)
#         y = self.scene._yFromPrice(extr.price)
#         x = x0 + self.scene.SCALE_X / 2
#         y0 = y * 0.98 if extr.isMax() else y * 1.02
#         epos = QtCore.QPointF(x, y)
#         spos = QtCore.QPointF(x0, y0)
#         width = height = self.scene.SCALE_X
#         shape.setData(GraphicsExtremumItem.EXTR_POS, epos)
#         shape.setData(GraphicsExtremumItem.SHAPE_POS, spos)
#         if extr.isLongterm():
#             circle = QtWidgets.QGraphicsEllipseItem(x0, y0, width, height)
#             circle.setPen(COLOR.LONGTERM)
#             circle.setBrush(COLOR.LONGTERM)
#             shape.addToGroup(circle)
#         elif extr.isMidterm():
#             circle = QtWidgets.QGraphicsEllipseItem(x0, y0, width, height)
#             circle.setPen(COLOR.MIDTERM)
#             circle.setBrush(COLOR.MIDTERM)
#             shape.addToGroup(circle)
#         else:
#             # для short-term-extremum метку не рисуем
#             pass
#         return shape
#
#     def __createLines(self, points_group: QtWidgets.QGraphicsItemGroup):
#         lines = QtWidgets.QGraphicsItemGroup()
#         points = points_group.childItems()
#         if len(points) < 2:
#             return
#         pen = self.__createPen()
#         i = 0
#         while i < len(points) - 1:
#             e1 = points[i].data(GraphicsExtremumItem.EXTR_POS)
#             e2 = points[i + 1].data(GraphicsExtremumItem.EXTR_POS)
#             l = QtWidgets.QGraphicsLineItem(e1.x(), e1.y(), e2.x(), e2.y())
#             l.setPen(pen)
#             lines.addToGroup(l)
#             i += 1
#         return lines
#
#     def __createPen(self):
#         pen = QtGui.QPen()
#         if len(self.elist) == 0:
#             return
#         extr = self.elist[0]
#         if extr.isLongterm():
#             pen.setWidth(self.LONGTERM_LINE_WIDTH)
#             pen.setColor(COLOR.LONGTERM)
#         elif extr.isMidterm():
#             pen.setWidth(self.MIDTERM_LINE_WIDTH)
#             pen.setColor(COLOR.MIDTERM)
#         else:
#             pen.setWidth(self.SHORTTERM_LINE_WIDTH)
#             pen.setColor(COLOR.SHORTTERM)
#         return pen
#
#
# class ChartScene(QtWidgets.QGraphicsScene):
#     """ Signal """
#     sceneClicked = QtCore.pyqtSignal(Bar)
#
#     """ Const """
#     SCALE_X =            20
#     SCALE_Y =            20
#     WIDTH_BAR =          20
#     HEIGHT_PERCENT =     20
#     BAR_INDENT =         SCALE_X / 5
#     SCENE_INDENT =       50
#     SHADOW_WIDTH =       2
#     OPN_CLS_WIDTH =      3
#     POS_OPEN_WIDTH =     1
#     POS_STOP_WIDTH =     1
#     POS_TAKE_WIDTH =     1
#     IGNORE_TRANSFORMATIONS = QtWidgets.QGraphicsItem.\
#         GraphicsItemFlag.ItemIgnoresTransformations
#
#     def __init__(self, parent=None):
#         QtWidgets.QGraphicsScene.__init__(self, parent)
#         self.setBackgroundBrush(COLOR.BG)
#         self.chart = None
#         self.gchart = QtWidgets.QGraphicsItemGroup()
#         self.gtlist = QtWidgets.QGraphicsItemGroup()
#         self.gindicators = QtWidgets.QGraphicsItemGroup()
#         self.gmarks = QtWidgets.QGraphicsItemGroup()
#         self.addItem(self.gchart)
#         self.addItem(self.gtlist)
#         self.addItem(self.gindicators)
#         self.addItem(self.gmarks)
#         self.__createWidgets()
#
#     def __createWidgets(self):
#         self.label_barinfo = QtWidgets.QLabel("BAR INFO")
#         self.label_volinfo = QtWidgets.QLabel("VOL INFO")
#         graphic_widget_barinfo = self.addWidget(self.label_barinfo)
#         graphic_widget_volinfo = self.addWidget(self.label_volinfo)
#         layot = QtWidgets.QGraphicsLinearLayout()
#         layot.addItem(graphic_widget_barinfo)
#         layot.addItem(graphic_widget_volinfo)
#         self.bar_info = QtWidgets.QGraphicsWidget()
#         self.bar_info.setLayout(layot)
#         self.addItem(self.bar_info)
#
#     def _barItemFromDatetime(self, dt):
#         """ засада, если бар раскрытый... надо поддумать как лучше
#         реализовать отрисовку трейда на раскрытом баре """
#         timeframe = self.chart.timeframe
#         bars = self.chart.getBars()
#         if timeframe != TimeFrame("1M"):
#             bar1 = bars[0]
#             bar2 = bars[1]
#             i = 1
#             while bar2 is not None:
#                 if bar1.dt <= dt < bar2.dt:
#                     break
#                 bar1 = bars[i]
#                 i += 1
#                 bar2 = bars[i]
#             for item in self.gchart.childItems():
#                 if bar1 == item.bar:
#                     return item
#         else:
#             assert "Не написан код"
#         return None
#
#     def _barItemFromBar(self, bar):
#         bars = self.chart.getBars()
#         index = binarySearch(bars, bar.dt, lambda bar: bar.dt)
#         if index is not None:
#             gbars = self.gchart.childItems()
#             return gbars[index]
#         else:
#             return None
#
#     def _xFromDatetime(self, dt):
#         item = self._barItemFromDatetime(dt)
#         n = item.n
#         x = self._xFromNumber(n)
#         return x
#
#     def _xFromNumber(self, n):
#         return n * ChartScene.SCALE_X
#
#     def _yFromPrice(self, price):
#         return self.height() - price * self.SCALE_Y
#
#     def _nFromPos(self, pos):
#         x = pos.x()
#         n = int(x / self.SCALE_X)
#         return n
#
#     def mouseMoveEvent(self, e):
#         # print("MOVE", type(e))
#         # print(e.pos())
#         # print(e.scenePos())
#         # print(e.screenPos())
#         # print(e.lastPos())
#         # print(e.lastScenePos())
#         # print(e.lastScreenPos())
#         # self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
#         return e.ignore()
#
#     def mousePressEvent(self, e):
#         # print("PRESS", type(e))
#         # print(e.pos())
#         # print(e.scenePos())
#         # print(e.screenPos())
#         # print(e.lastPos())
#         # print(e.lastScenePos())
#         # print(e.lastScreenPos())
#         left_button = QtCore.Qt.MouseButton.LeftButton
#         if e.button() != left_button:
#             return e.ignore()
#         if self.chart is None:
#             return e.ignore()
#         n = self._nFromPos(e.scenePos())
#         bar_items = self.gchart.childItems()
#         bar = bar_items[n].bar
#         self.sceneClicked.emit(bar)
#         return e.ignore()
#
#     def mouseReleaseEvent(self, e):
#         # print("RELEASE", type(e))
#         # print(e.pos())
#         # print(e.scenePos())
#         # print(e.screenPos())
#         # print(e.lastPos())
#         # print(e.lastScenePos())
#         # print(e.lastScreenPos())
#         # self.bar_info = QtWidgets.QGraphicsTextItem(str(bar))
#         view = self.views()[0]
#         p = view.mapToScene(0, 0)
#         self.removeItem(self.bar_info)
#         self.bar_info.setPos(p)
#         self.addItem(self.bar_info)
#         return e.ignore()
#
#     def mouseDoubleClickEvent(self, e):
#         """
#         загрузить новый график, именно за этот период (бар)
#         стереть станый график.
#         нарисовать главный график до выделенного бара
#         нарисовать раскрытый бар
#         продолжить рисовать главный график.
#         """
#         if self.chart is None:
#             return e.ignore()
#         n = self._nFromPos(e.scenePos())
#         bar_items = self.gchart.childItems()
#         zoom_bar = bar_items[n].bar
#         ID = self.chart.ID
#         begin = zoom_bar.dt
#         end = zoom_bar.dt + self.chart.timeframe
#         self.zoom_chart = Chart(ID, TimeFrame("5M"), begin, end)
#         ###
#         self.removeChart()
#         ###
#         scene_x0 = 0
#         n1 = self.chart.getBarsCount() - 1
#         n2 = self.zoom_chart.getBarsCount()
#         scene_x1 = (n1 + n2) * self.SCALE_X
#         scene_y0 = 0
#         scene_y1 = self.chart.highestHigh() * self.SCALE_Y
#         height = scene_y1 - scene_y0 #+ 2 * self.SCENE_INDENT
#         width = scene_x1 - scene_x0 #+ 2 * self.SCENE_INDENT
#         self.setSceneRect(0, 0, width, height)
#         ###
#         i = 0
#         for big_bar in self.chart:
#             if big_bar.dt != zoom_bar.dt:
#                 bar_item = GraphicsBarItem(big_bar, i, self)
#                 self.gchart.addToGroup(bar_item)
#                 i += 1
#             else:
#                 bar_item = GraphicsBarItem(big_bar, i, self)
#                 self.gchart.addToGroup(bar_item)
#                 i += 1
#                 for small_bar in self.zoom_chart:
#                     bar_item = GraphicsZoomBarItem(small_bar, i, self)
#                     self.gchart.addToGroup(bar_item)
#                     i += 1
#
#     def calcScale(self):
#         price = self.chart.last.close
#         one_percent = price * 0.01
#         # бар 1% будет высотой <HEIGHT_PERCENT> пикселей
#         self.SCALE_Y = self.HEIGHT_PERCENT / one_percent
#         self.SCENE_INDENT = self.SCALE_Y * 2
#
#     def createSceneRect(self):
#         chart = self.chart
#         scene_x0 = 0
#         scene_x1 = len(chart.getBars()) * self.SCALE_X
#         scene_y0 = 0
#         scene_y1 = Bar.highestHigh(self.chart.getBars()) * self.SCALE_Y
#         height = scene_y1 - scene_y0 #+ self.SCENE_INDENT
#         width = scene_x1 - scene_x0
#         self.setSceneRect(0, 0, width, height)
#
#     def addChart(self, chart):
#         logger.debug(
#             f"ChartScene.addChart(chart)"
#             )
#         self.chart = chart
#         self.calcScale()
#         self.createSceneRect()
#         i = 0
#         for n, bar in enumerate(chart, 0):
#             bar_item = GraphicsBarItem(bar, n, self)
#             self.gchart.addToGroup(bar_item)
#
#     def setGTradeList(self, gtlist: GraphicsTradeListItem):
#         logger.debug(f"ChartScene.setGTradeList(trades)")
#         assert isinstance(gtlist, GraphicsTradeListItem)
#         self.removeItem(self.gtlist)
#         self.addItem(gtlist)
#         self.gtlist = gtlist
#
#     def addIndicator(self, gindicator: QtWidgets.QGraphicsItem):
#         logger.debug(
#             f"ChartScene.addIndicator(indicator)"
#             )
#         self.gindicators.addToGroup(gindicator)
#
#     def addMark(self, func):
#         """ надо где то и кому создавать график итем промаркированного
#         графика и сюда принимать уже готовый итем гроуп.
#         сцена должна только хранить объекты и управлять ими
#         а не создавать все возможные виды объектов
#         """
#         chart = self.chart
#         chart.setNowIndex(0)
#         while chart.nextHead():
#             if func(chart):
#                 gbar = self._barItemFromBar(chart.last)
#                 item = GraphicsMarkItem(gbar)
#                 self.gmarks.addToGroup(item)
#
#     def removeChart(self):
#         logger.debug(
#             f"ChartScene.removeChart()"
#             )
#         self.removeItem(self.gchart)
#         self.gchart = QtWidgets.QGraphicsItemGroup()
#         self.addItem(self.gchart)
#
#     def removeTradeList(self):
#         logger.debug(
#             f"ChartScene.removeTradeList()"
#             )
#         self.removeItem(self.gtlist)
#         self.gtlist = QtWidgets.QGraphicsItemGroup()
#         self.addItem(self.gtlist)
#
#     def removeIndicator(self):
#         logger.debug(
#             f"ChartScene.removeExtr()"
#             )
#         self.removeItem(self.gindicators)
#         self.gindicators = QtWidgets.QGraphicsItemGroup()
#         self.addItem(self.gindicators)
#
#     def removeMark(self):
#         logger.debug(
#             f"ChartScene.removeExtr()"
#             )
#         self.removeItem(self.gmarks)
#         self.gmarks = QtWidgets.QGraphicsItemGroup()
#         self.addItem(self.gmarks)
#
#
# class ChartView(QtWidgets.QGraphicsView):
#     def __init__(self, parent=None):
#         QtWidgets.QGraphicsView.__init__(self, parent)
#         # включает режим перетаскивания сцены внутри QGraphicsView
#         # мышкой с зажатой левой кнопкой
#         self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
#         self.current_gtrade = None
#
#     def wheelEvent(self, e):
#         ctrl = QtCore.Qt.KeyboardModifier.ControlModifier
#         no = QtCore.Qt.KeyboardModifier.NoModifier
#         if e.modifiers() == no:
#             if e.angleDelta().y() < 0:
#                 self.scale(0.9, 1)
#             else:
#                 self.scale(1.1, 1)
#         if e.modifiers() == ctrl:
#             if e.angleDelta().y() < 0:
#                 self.scale(1, 0.9)
#             else:
#                 self.scale(1, 1.1)
#
#     # def mouseMoveEvent(self, e):
#         # return e.accept()
#
#     def centerOnFirst(self):
#         logger.debug(
#             f"ChartView.centerOnFirst()"
#             )
#         scene = self.scene()
#         first_bar_item = scene.gchart.childItems()[0]
#         pos = first_bar_item.close_pos
#         self.centerOn(pos)
#
#     def centerOnLast(self):
#         scene = self.scene()
#         last_bar_item = scene.gchart.childItems()[-1]
#         pos = last_bar_item.close_pos
#         self.centerOn(pos)
#
#     def centerOnBar(self, bar):
#         ...
#
#     def centerOnTrade(self, gtrade: GraphicsTradeItem):
#         logger.debug(
#             f"ChartView.centerOnTrade(trade)"
#             f"trade.dt = {gtrade.itrade.trade.dt}"
#             )
#         if self.current_gtrade is not None:
#             self.current_gtrade.hideAnnotation()
#         self.current_gtrade = gtrade
#         gtrade.showAnnotation()
#         scene = self.scene()
#         pos = gtrade.trade_pos
#         self.centerOn(pos)
#
#
# class ChartWidget(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         QtWidgets.QWidget.__init__(self, parent)
#         self.asset = None
#         self.view = ChartView(self)
#         self.scene = ChartScene(self)
#         self.view.setScene(self.scene)
#         self.__createWidgets()
#         self.__createLayots()
#         self.__connect()
#
#     def __createWidgets(self):
#         self.btn_settings = QtWidgets.QPushButton("...")
#         self.combobox_timeframe = QtWidgets.QComboBox()
#         for timeframe in TimeFrame.ALL:
#             self.combobox_timeframe.addItem(str(timeframe))
#         self.combobox_timeframe.setCurrentIndex(3)
#         self.__timeframe = TimeFrame("D")
#         self.dateedit_begin = QtWidgets.QDateEdit()
#         self.dateedit_begin.setMinimumDate(QtCore.QDate(2018, 1, 1))
#         self.dateedit_begin.setMaximumDate(now().date() - ONE_DAY)
#         self.dateedit_end = QtWidgets.QDateEdit(now().date())
#         self.dateedit_end.setMinimumDate(QtCore.QDate(2018, 1, 1))
#         self.dateedit_end.setMaximumDate(now().date())
#         self.btn_indicator = QtWidgets.QPushButton("Indicator")
#         self.btn_mark = QtWidgets.QPushButton("Mark")
#         self.label_barinfo = QtWidgets.QLabel()
#         self.indicator_dialog = IndicatorDialog()
#
#     def __createLayots(self):
#         hbox1 = QtWidgets.QHBoxLayout()
#         hbox1.addWidget(self.btn_settings)
#         hbox1.addWidget(self.combobox_timeframe)
#         hbox1.addWidget(self.dateedit_begin)
#         hbox1.addWidget(QtWidgets.QLabel("-"))
#         hbox1.addWidget(self.dateedit_end)
#         hbox1.addWidget(self.btn_indicator)
#         hbox1.addWidget(self.btn_mark)
#         hbox1.addWidget(self.label_barinfo)
#         hbox1.addStretch()
#         vbox = QtWidgets.QVBoxLayout()
#         vbox.addLayout(hbox1)
#         vbox.addWidget(self.view)
#         self.setLayout(vbox)
#
#     def __connect(self):
#         self.scene.sceneClicked.connect(self.__onSceneClicked)
#         self.btn_settings.clicked.connect(self.__onButtonSettings)
#         self.combobox_timeframe.currentTextChanged.connect(
#             self.__onTimeframeChanged
#             )
#         self.dateedit_begin.dateChanged.connect(self.__onChangeBeginDate)
#         self.dateedit_end.dateChanged.connect(self.__onChangeEndDate)
#         self.btn_indicator.clicked.connect(self.__onButtonIndicator)
#         self.btn_mark.clicked.connect(self.__onButtonMark)
#
#     def __onSceneClicked(self, bar):
#         msk_time = bar.dt + MSK_TIME_DIF
#         msk_time = msk_time.strftime("%Y-%m-%d  %H:%M")
#         day = DAYS_NAME[bar.dt.weekday()]
#         atr = bar.body.percent
#         s = (f"Open: {bar.open}   High: {bar.high}   Low: {bar.low}   "
#              f"Close: {bar.close}   Vol: {bar.vol}   {msk_time}   "
#              f"{day}   (ATR: {atr:.2f}%)"
#             )
#         self.label_barinfo.setText(s)
#
#     def __onButtonSettings(self):
#         self.view.scale(1, 1.01)
#
#     def __onButtonIndicator(self):
#         logger.debug(f"ChartWidget.__onButtonIndicator()")
#         chart = self.scene.chart
#         if chart is None:
#             return
#         selected = self.indicator_dialog.selectIndicators()
#         if selected:
#             self.scene.removeIndicator()
#             for i in selected:
#                 item = i.createGraphicsItem(chart, self.scene)
#                 self.scene.addIndicator(item)
#
#     def __onButtonMark(self):
#         logger.debug(f"ChartWidget.__onButtonMark()")
#         chart = self.scene.chart
#         if chart is None:
#             return
#         self.scene.removeMark()
#         self.scene.addMark(MARK_FUNCTION)
#         self.view.centerOnFirst()
#
#     def __onTimeframeChanged(self):
#         text = self.combobox_timeframe.currentText()
#         self.__timeframe = TimeFrame(text)
#         self.showChart()
#
#     def __onChangeBeginDate(self):
#         ...
#
#     def __onChangeEndDate(self):
#         ...
#
#     def __readBeginDate(self):
#         date = self.dateedit_begin.date()
#         year = date.year()
#         month = date.month()
#         day = date.day()
#         return datetime(year, month, day, tzinfo=UTC)
#
#     def __readEndDate(self):
#         date = self.dateedit_end.date()
#         year = date.year()
#         month = date.month()
#         day = date.day()
#         return datetime(year, month, day, tzinfo=UTC)
#
#     def __readTimeframe(self):
#         text = self.combobox_timeframe.currentText()
#         self.__timeframe = TimeFrame(text)
#
#     def setAsset(self, asset):
#         self.asset = asset
#
#     def setBegin(self, dt):
#         self.dateedit_begin.setDate(dt.date())
#
#     def setEnd(self, dt):
#         self.dateedit_end.setDate(dt.date())
#
#     def setTimeframe(self, timeframe):
#         assert isinstance(timeframe, TimeFrame)
#         self.combobox_timeframe.setCurrentText(str(timeframe))
#         self.__timeframe = timeframe
#
#     def showChart(self):
#         logger.debug(
#             f"ChartWidget.showChart()"
#             )
#         if self.asset is None:
#             return
#         begin = self.__readBeginDate()
#         end = self.__readEndDate()
#         timeframe = self.__timeframe
#         self.asset.loadChart(timeframe, begin, end)
#         chart = self.asset.chart[str(timeframe)]
#         if self.scene.chart is not None:
#             self.scene.removeChart()
#         self.scene.addChart(chart)
#         # костыль, делаю изначально QGraphicsScene сильно большой,
#         # чтобы потом масштабирование лучше работало при маленькой сцене.
#         # Масштибирование через QGraphicsView искажает график
#         # self.view.scale(0.5, 0.5)
#         self.view.centerOnLast()
#
#     def showTradeList(self, itlist):
#         logger.debug(f"ChartWidget.showTradeList()")
#         test = itlist.parent().test
#         ticker = itlist.name
#         share = Share(ticker)
#         self.clearAll()
#         self.setAsset(share)
#         self.setTimeframe(test.timeframe)
#         self.setBegin(test.back_begin)
#         self.setEnd(test.forward_end)
#         self.showChart()
#         if len(self.scene.gtlist.childItems()) > 0:
#             self.scene.removeTradeList()
#         gtlist = GraphicsTradeListItem(itlist, self.scene)
#         self.scene.setGTradeList(gtlist)
#         self.view.centerOnFirst()
#
#     def clearAll(self):
#         logger.debug(
#             f"ChartWidget.clearAll()"
#             )
#         self.asset = None
#         self.scene.removeChart()
#         self.scene.removeTradeList()
#         self.scene.removeIndicator()
#         self.scene.removeMark()
#         self.view.resetTransform()
#
#

# -------------------------------- Enum
class UColor():
    # common color
    BLACK =             QtGui.QColor("#000000")
    WHITE =             QtGui.QColor("#FFFFFF")
    RED =               QtGui.QColor("#AA0000")
    GREEN =             QtGui.QColor("#00AA00")
    GREEN =             QtGui.QColor("#0000AA")
    YELLOW =            QtGui.QColor("#AAAA00")
    # Window palette
    DARK =              QtGui.QColor("#0F0F0F")  #5
    NORMAL =            QtGui.QColor("#323232")
    INACTIVE =          QtGui.QColor("#373737")  #4
    HIGHLIGHT =         QtGui.QColor("#5D5E60")  #3
    DISABLED_TEXT =     QtGui.QColor("#848388")  #2
    TEXT =              QtGui.QColor("#B7B7AF")  #1
    BUTTON_TEXT =       QtGui.QColor("#CCCCCC")
    WINDOW_TEXT =       QtGui.QColor("#EEEEEE")
    HIGHLIGHT_TEXT =    QtGui.QColor("#FAFAFA")
    # Bar
    BG =                QtGui.QColor("#181616")  # nvim background
    BULL =              QtGui.QColor("#98BB6C")  # kanagawa 4.2
    BEAR =              QtGui.QColor("#FF5D62")  # kanagawa 5.3
    UNDEFINE =          QtGui.QColor("#000000")
    # BG =                QtGui.QColor("#242424")
    # BULL =              QtGui.QColor("#BBBBBB")
    # BEAR =              QtGui.QColor("#646464")
    # UNDEFINE =          QtGui.QColor("#FFFFFF")
    ZOOM_BULL =         QtGui.QColor("#00FF00")
    ZOOM_BEAR =         QtGui.QColor("#FF0000")
    # Trade
    STOP =              QtGui.QColor("#FF0000")
    TAKE =              QtGui.QColor("#00FF00")
    OPEN =              QtGui.QColor("#AAAAAA")
    TRADE_WIN =         QtGui.QColor("#00AA00")
    TRADE_LOSS =        QtGui.QColor("#AA0000")
    # Mark
    MARK =              QtGui.QColor("#0000AA")
    # Extremum
    SHORTTERM =         QtGui.QColor("#FFFFFF")
    MIDTERM =           QtGui.QColor("#AAAA00")
    LONGTERM =          QtGui.QColor("#AA0000")
    INSIDE_BG =         QtGui.QColor("#AA000000")
    OUTSIDE_BG =        QtGui.QColor("#44FFFFFF")
    # Button
    BUY =               QtGui.QColor("#98BB6C")  # kanagawa 4.2
    SELL =              QtGui.QColor("#FF5D62")  # kanagawa 5.3

class UFont():
    MONO = QtGui.QFont("monospace")
    SANS = QtGui.QFont("sans")

class UIcon():
    # Files
    DIR =       QtGui.QIcon(Cmd.join(const.ICON_DIR, "dir.svg"))
    FILE =      QtGui.QIcon(Cmd.join(const.ICON_DIR, "file.svg"))
    ARCHIVE =   QtGui.QIcon(Cmd.join(const.ICON_DIR, "archive.svg"))
    ASSET =     QtGui.QIcon(Cmd.join(const.ICON_DIR, "asset.svg"))
    BIN =       QtGui.QIcon(Cmd.join(const.ICON_DIR, "bin.svg"))
    CONFIG =    QtGui.QIcon(Cmd.join(const.ICON_DIR, "config.svg"))
    CSV =       QtGui.QIcon(Cmd.join(const.ICON_DIR, "csv.svg"))
    JSON =      QtGui.QIcon(Cmd.join(const.ICON_DIR, "json.svg"))
    MARKDOWN =  QtGui.QIcon(Cmd.join(const.ICON_DIR, "markdown.svg"))
    SCRIPT =    QtGui.QIcon(Cmd.join(const.ICON_DIR, "script.svg"))
    TXT =       QtGui.QIcon(Cmd.join(const.ICON_DIR, "text.svg"))
    TIMEFRAME = QtGui.QIcon(Cmd.join(const.ICON_DIR, "timeframe.svg"))
    # Left panel
    DATA =      QtGui.QIcon(Cmd.join(const.ICON_DIR, "data.svg"))
    LIST =      QtGui.QIcon(Cmd.join(const.ICON_DIR, "list.svg"))
    CHART =     QtGui.QIcon(Cmd.join(const.ICON_DIR, "chart.svg"))
    STRATEGY =  QtGui.QIcon(Cmd.join(const.ICON_DIR, "strategy.svg"))
    TEST =      QtGui.QIcon(Cmd.join(const.ICON_DIR, "test.svg"))
    REPORT =    QtGui.QIcon(Cmd.join(const.ICON_DIR, "report.svg"))
    CONSOLE =   QtGui.QIcon(Cmd.join(const.ICON_DIR, "console.svg"))
    SHUTDOWN =  QtGui.QIcon(Cmd.join(const.ICON_DIR, "shutdown.svg"))
    # Right panel
    BABLO =     QtGui.QIcon(Cmd.join(const.ICON_DIR, "BABLO.svg"))
    BROKER =    QtGui.QIcon(Cmd.join(const.ICON_DIR, "broker.svg"))
    ACCOUNT =   QtGui.QIcon(Cmd.join(const.ICON_DIR, "account.svg"))
    ORDER =     QtGui.QIcon(Cmd.join(const.ICON_DIR, "order.svg"))
    ANALYTIC =  QtGui.QIcon(Cmd.join(const.ICON_DIR, "analytic.svg"))
    SANDBOX =   QtGui.QIcon(Cmd.join(const.ICON_DIR, "sandbox.svg"))
    GENERAL =   QtGui.QIcon(Cmd.join(const.ICON_DIR, "general.svg"))
    KEEPER =    QtGui.QIcon(Cmd.join(const.ICON_DIR, "keeper.svg"))
    # Buttons
    ADD =       QtGui.QIcon(Cmd.join(const.ICON_DIR, "add.svg"))
    APPLY =     QtGui.QIcon(Cmd.join(const.ICON_DIR, "apply.svg"))
    CANCEL =    QtGui.QIcon(Cmd.join(const.ICON_DIR, "cancel.svg"))
    CLOSE =     QtGui.QIcon(Cmd.join(const.ICON_DIR, "close.svg"))
    DOWNLOAD =  QtGui.QIcon(Cmd.join(const.ICON_DIR, "download.svg"))
    EXTRACT =   QtGui.QIcon(Cmd.join(const.ICON_DIR, "extract.svg"))
    NO =        QtGui.QIcon(Cmd.join(const.ICON_DIR, "no.svg"))
    OK =        QtGui.QIcon(Cmd.join(const.ICON_DIR, "ok.svg"))
    CONVERT =   QtGui.QIcon(Cmd.join(const.ICON_DIR, "convert.svg"))
    DELETE =    QtGui.QIcon(Cmd.join(const.ICON_DIR, "delete.svg"))
    UPDATE =    QtGui.QIcon(Cmd.join(const.ICON_DIR, "update.svg"))
    SAVE =      QtGui.QIcon(Cmd.join(const.ICON_DIR, "save.svg"))
    SEARCH =    QtGui.QIcon(Cmd.join(const.ICON_DIR, "search.svg"))
    SETTINGS =  QtGui.QIcon(Cmd.join(const.ICON_DIR, "settings.svg"))
    YES =       QtGui.QIcon(Cmd.join(const.ICON_DIR, "yes.svg"))

class UPalette(QtGui.QPalette):
    def __init__(self):
        QtGui.QPalette.__init__(self)
        g = QtGui.QPalette.ColorGroup
        r = QtGui.QPalette.ColorRole
        c = UColor
        self.setColor(g.Normal,    r.Window,           c.NORMAL)
        self.setColor(g.Inactive,  r.Window,           c.INACTIVE)
        self.setColor(g.Normal,    r.Base,             c.NORMAL)
        self.setColor(g.Inactive,  r.Base,             c.INACTIVE)
        self.setColor(g.Normal,    r.Button,           c.NORMAL)
        self.setColor(g.Inactive,  r.Button,           c.INACTIVE)
        self.setColor(g.Disabled,  r.Button,           c.NORMAL)
        self.setColor(g.Normal,    r.Highlight,        c.HIGHLIGHT)
        self.setColor(g.Inactive,  r.Highlight,        c.HIGHLIGHT)
        self.setColor(g.Normal,    r.HighlightedText,  c.HIGHLIGHT_TEXT)
        self.setColor(g.Inactive,  r.HighlightedText,  c.HIGHLIGHT_TEXT)
        self.setColor(g.Normal,    r.WindowText,       c.WINDOW_TEXT)
        self.setColor(g.Inactive,  r.WindowText,       c.WINDOW_TEXT)
        self.setColor(g.Disabled,  r.WindowText,       c.DISABLED_TEXT)
        self.setColor(g.Normal,    r.ButtonText,       c.BUTTON_TEXT)
        self.setColor(g.Inactive,  r.ButtonText,       c.BUTTON_TEXT)
        self.setColor(g.Disabled,  r.ButtonText,       c.DISABLED_TEXT)
        self.setColor(g.Normal,    r.Text,             c.TEXT)
        self.setColor(g.Inactive,  r.Text,             c.TEXT)
        self.setColor(g.Disabled,  r.Text,             c.DISABLED_TEXT)


# -------------------------------- Mini widget
class USpacer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
            )


class UHLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)


class UVLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        QtWidgets.QFrame.__init__(self, parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        # self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)


class UProgress(QtWidgets.QProgressBar):
    def __init__(self, parent=None):
        QtWidgets.QProgressBar.__init__(self, parent)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setMaximumHeight(20)
        self.setFont(UFont.MONO)


class UToolLeft(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__configButtons()
        self.__connect()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setIconSize(QtCore.QSize(32, 32))
        p = self.palette()
        p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#484848"))
        self.setPalette(p)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.data = QtGui.QAction(UIcon.DATA, "Data", self)
        self.asset = QtGui.QAction(UIcon.LIST, "Asset", self)
        self.chart = QtGui.QAction(UIcon.CHART, "Chart", self)
        self.strategy = QtGui.QAction(UIcon.STRATEGY, "Strategy", self)
        self.test = QtGui.QAction(UIcon.TEST, "Test", self)
        self.report = QtGui.QAction(UIcon.REPORT, "Report", self)
        self.console = QtGui.QAction(UIcon.CONSOLE, "Console", self)
        self.shutdown = QtGui.QAction(UIcon.SHUTDOWN, "Shutdown", self)
        self.addAction(self.data)
        self.addAction(self.asset)
        self.addAction(self.chart)
        self.addAction(self.strategy)
        self.addAction(self.test)
        self.addAction(self.report)
        self.addAction(self.console)
        self.addWidget(USpacer(self))
        self.addAction(self.shutdown)

    def __configButtons(self):
        self.widgetForAction(self.data).setCheckable(True)
        self.widgetForAction(self.asset).setCheckable(True)
        self.widgetForAction(self.chart).setCheckable(True)
        self.widgetForAction(self.strategy).setCheckable(True)
        self.widgetForAction(self.test).setCheckable(True)
        self.widgetForAction(self.report).setCheckable(True)
        self.widgetForAction(self.console).setCheckable(True)
        self.widgetForAction(self.shutdown).setCheckable(True)

    def __connect(self):
        self.actionTriggered.connect(self.__onTriggered)

    def __onTriggered(self, action: QtGui.QAction):
        btn = self.widgetForAction(action)
        state = btn.isChecked()
        btn.setChecked(not state)


class UToolRight(QtWidgets.QToolBar):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QToolBar.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__configButtons()
        self.__connect()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setIconSize(QtCore.QSize(32, 32))
        p = self.palette()
        p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#484848"))
        self.setPalette(p)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.broker = QtGui.QAction(UIcon.BROKER, "Broker", self)
        self.account = QtGui.QAction(UIcon.ACCOUNT, "Account", self)
        self.order = QtGui.QAction(UIcon.ORDER, "Order", self)
        self.analytic = QtGui.QAction(UIcon.ANALYTIC, "Analytic", self)
        self.sandbox = QtGui.QAction(UIcon.SANDBOX, "Sandbox", self)
        self.general = QtGui.QAction(UIcon.GENERAL, "General", self)
        self.keeper = QtGui.QAction(UIcon.KEEPER, "Keeper", self)
        self.addAction(self.broker)
        self.addAction(self.account)
        self.addAction(self.order)
        self.addAction(self.analytic)
        self.addAction(self.sandbox)
        self.addAction(self.general)
        self.addAction(self.keeper)

    def __configButtons(self):
        for i in self.actions():
            self.widgetForAction(i).setCheckable(True)
        self.addWidget(USpacer(self))
        # self.widgetForAction(self.broker).setCheckable(True)
        # self.widgetForAction(self.account).setCheckable(True)
        # self.widgetForAction(self.order).setCheckable(True)
        # self.widgetForAction(self.order).setCheckable(True)

    def __connect(self):
        self.actionTriggered.connect(self.__onTriggered)

    def __onTriggered(self, action: QtGui.QAction):
        btn = self.widgetForAction(action)
        state = btn.isChecked()
        btn.setChecked(not state)


# -------------------------------- Items
class IData(QtWidgets.QTreeWidgetItem):
    def __init__(self, name: str, path: str, parent=None):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        if Cmd.isFile(path):
            self.__createFileItem(name, path)
        elif Cmd.isDir(path):
            self.__createDirItem(name, path)
        types = (
            UDataTree.Type.DIR,
            UDataTree.Type.SHARES_DIR,
            UDataTree.Type.DATA,
            UDataTree.Type.ANALYTIC
            )
        if self.type in types:
            self.__createChilds()

    def __createChilds(self):
        # logger.debug(f"{self.__class__.__name__}.__createChilds()")
        dir_path = self.path
        dirs_files = Cmd.contents(dir_path, full_path=True)
        for path in dirs_files:
            name = Cmd.name(path)
            item = IData(name, path)
            self.addChild(item)

    def __createDirItem(self, name: str, path: str):
        logger.debug(f"{self.__class__.__name__}.__createDirItem()")
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsAutoTristate |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        types = {
            TinkoffData.DOWNLOAD_DIR_NAME:  UDataTree.Type.TINKOFF_ARCHIVES,
            TinkoffData.DIR_NAME:           UDataTree.Type.TINKOFF,
            "analytic":                     UDataTree.Type.ANALYTIC,
            "SHARES":                       UDataTree.Type.SHARES_DIR,
            "1M":                           UDataTree.Type.DATA,
            "5M":                           UDataTree.Type.DATA,
            "1H":                           UDataTree.Type.DATA,
            "D":                            UDataTree.Type.DATA,
            }
        self.__type = types.get(name, UDataTree.Type.DIR)
        self.setIcon(UDataTree.Column.Name, UIcon.DIR)
        self.setText(UDataTree.Column.Name, name)
        self.setText(UDataTree.Column.Type, self.__type.name.lower())
        self.setText(UDataTree.Column.Path, path)

    def __createFileItem(self, name: str, path: str):
        # logger.debug(f"{self.__class__.__name__}.__createFileItem()")
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsAutoTristate |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(UDataTree.Column.Name, name)
        self.setText(UDataTree.Column.Path, path)
        if name == "asset":
            self.__type = UDataTree.Type.ASSET
            self.setIcon(UDataTree.Column.Name, UIcon.ASSET)
            self.setText(
                UDataTree.Column.Type, UDataTree.Type.ASSET.name.lower()
                )
        elif name == "timeframe":
            self.__type = UDataTree.Type.TIMEFRAME
            self.setIcon(UDataTree.Column.Name, UIcon.TIMEFRAME)
            self.setText(
                UDataTree.Column.Type, UDataTree.Type.TIMEFRAME.name.lower()
                )
        elif path.endswith(".csv"):
            self.__type = UDataTree.Type.CSV
            self.setIcon(UDataTree.Column.Name, UIcon.CSV)
            self.setText(
                UDataTree.Column.Type, UDataTree.Type.CSV.name.lower()
                )
        elif path.endswith(".json"):
            self.__type = UDataTree.Type.JSON
            self.setIcon(UDataTree.Column.Name, UIcon.JSON)
            self.setText(
                UDataTree.Column.Type, UDataTree.Type.JSON.name.lower()
                )
        elif path.endswith(".zip"):
            self.__type = UDataTree.Type.ARCHIVE
            self.setIcon(UDataTree.Column.Name, UIcon.ARCHIVE)
            self.setText(
                UDataTree.Column.Type, UDataTree.Type.ARCHIVE.name.lower()
                )
        elif path.endswith(".sh"):
            self.__type = UDataTree.Type.SCRIPT
            self.setIcon(UDataTree.Column.Name, UIcon.SCRIPT)
            self.setText(
                UDataTree.Column.Type, UDataTree.Type.SCRIPT.name.lower()
                )
        elif path.endswith(".txt"):
            self.__type = UDataTree.Type.TXT
            self.setIcon(UDataTree.Column.Name, UIcon.TXT)
            self.setText(
                UDataTree.Column.Type, UDataTree.Type.TXT.name.lower()
                )
        else:
            self.__type = UDataTree.Type.FILE
            self.setIcon(UDataTree.Column.Name, UIcon.FILE)
            self.setText(
                UDataTree.Column.Type, UDataTree.Type.FILE.name.lower()
                )

    @property  #name
    def name(self):
        return self.text(UDataTree.Column.Name)

    @property  #path
    def path(self):
        return self.text(UDataTree.Column.Path)

    @property  #type
    def type(self):
        return self.__type


class IShare(Share, QtWidgets.QTreeWidgetItem):
    def __init__(self, ticker, exchange=Exchange.MOEX, parent=None):
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Share.__init__(self, ticker, exchange, parent)
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(UAssetTree.Column.Ticker, self.ticker)
        self.setText(UAssetTree.Column.Name, self.name)
        self.setText(UAssetTree.Column.Type, self.type.name)
        self.setText(UAssetTree.Column.Exchange, self.exchange.name)

    @property
    def last_price(self):
        price = Tinkoff.getLastPrice(self)
        return price


class IAssetList(AssetList, QtWidgets.QTreeWidgetItem):
    def __init__(self, name="unnamed", parent=None):
        logger.debug("IAssetList.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        AssetList.__init__(self, name, parent)
        self.__parent = parent
        self.setFlags(
            Qt.ItemFlag.ItemIsAutoTristate |
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.__updateText()

    def __updateText(self):
        logger.debug(f"{self.__class__.__name__}.__updateText()")
        self.setText(UAssetTree.Column.ListName, self.name)
        self.setText(UAssetTree.Column.ListCount, str(self.count))

    @staticmethod  #load
    def load(name, parent=None):
        logger.debug("IAssetList.load()")
        path = name if Cmd.isFile(name) else Cmd.join(const.ASSET_DIR, name)
        name = Cmd.name(path, extension=True)
        ialist = IAssetList(name, parent=parent)
        obj = Cmd.loadJSON(path)
        for ID in obj:
            assert eval(ID["type"]) == Type.SHARE
            ishare = IShare(ID["ticker"])
            ialist.add(ishare)
        return ialist

    def parent(self):
        logger.debug("IAssetList.parent()")
        return self.__parent

    def add(self, iasset: IShare):
        logger.debug("IAssetList.add()")
        assert isinstance(iasset, IShare)
        AssetList.add(self, iasset)
        self.__updateText()

    def remove(self, iasset):
        logger.debug("IAssetList.remove()")
        AssetList.remove(self, iasset)
        self.removeChild(iasset)
        self.__updateText()

    def clear(self):
        logger.debug(f"{self.__class__.__name__}.clear()")
        AssetList.clear(self)
        while self.takeChild(0): pass
        self.__updateText()


class IStrategy(QtWidgets.QTreeWidgetItem):
    ASSET = 0x0101  # user data role

    def __init__(self, name, path, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.setFlags(
            Qt.ItemFlag.ItemIsUserCheckable |
            Qt.ItemFlag.ItemIsAutoTristate |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.name = name
        self.path = path
        self.long_list_path = self.path + ".long"
        self.short_list_path = self.path + ".short"
        self.__loadLongList()
        self.__loadShortList()
        self.setText(UStrategyTree.Column.Name, self.name)
        self.setCheckState(UStrategyTree.Column.Long, Qt.CheckState.Unchecked)
        self.setCheckState(UStrategyTree.Column.Short, Qt.CheckState.Unchecked)
        self.__createChilds()

    def __loadLongList(self):
        logger.debug(f"{self.__class__.__name__}.__loadLongList()")
        try:
            self.long_list = IAssetList.load(self.long_list_path)
        except FileNotFoundError:
            self.long_list = IAssetList("long")
            IAssetList.save(self.long_list, self.long_list_path)

    def __loadShortList(self):
        logger.debug(f"{self.__class__.__name__}.__loadShortList()")
        try:
            self.short_list = IAssetList.load(self.short_list_path)
        except FileNotFoundError:
            self.short_list = IAssetList(f"short")
            IAssetList.save(self.short_list, self.short_list_path)

    def __createChilds(self):
        logger.debug(f"{self.__class__.__name__}.__createChilds()")
        self.assets = IAssetList.load("XX5")
        for asset in self.assets:
            item = self.__createAssetItem(asset)
            self.__setCheckState(item)
            self.addChild(item)

    def __createAssetItem(self, asset):
            item = QtWidgets.QTreeWidgetItem()
            item.setFlags(
                Qt.ItemFlag.ItemIsUserCheckable |
                Qt.ItemFlag.ItemIsDragEnabled |
                Qt.ItemFlag.ItemIsDropEnabled |
                Qt.ItemFlag.ItemIsSelectable |
                Qt.ItemFlag.ItemIsEnabled
                )
            item.setText(UStrategyTree.Column.Name, asset.ticker)
            item.setData(UStrategyTree.Column.Name, IStrategy.ASSET, asset)
            return item

    def __setCheckState(self, item):
        asset = item.data(UStrategyTree.Column.Name, IStrategy.ASSET)
        if asset in self.long_list:
            item.setCheckState(
                UStrategyTree.Column.Long,
                Qt.CheckState.Checked,
                )
        else:
            item.setCheckState(
                UStrategyTree.Column.Long,
                Qt.CheckState.Unchecked,
                )
        if asset in self.short_list:
            item.setCheckState(
                UStrategyTree.Column.Short,
                Qt.CheckState.Checked,
                )
        else:
            item.setCheckState(
                UStrategyTree.Column.Short,
                Qt.CheckState.Unchecked,
                )

    def saveAssetSettings(self):
        long_list = AssetList("long", parent=self)
        short_list = AssetList("short", parent=self)
        for i in range(self.childCount()):
            item = self.child(i)
            long_state = item.checkState(UStrategyTree.Column.Long)
            short_state = item.checkState(UStrategyTree.Column.Short)
            asset = item.data(UStrategyTree.Column.Name, IStrategy.ASSET)
            if long_state == Qt.CheckState.Checked:
                long_list.add(asset)
            if short_state == Qt.CheckState.Checked:
                short_list.add(asset)
        AssetList.save(long_list, self.long_list_path)
        AssetList.save(short_list, self.short_list_path)

    def delete(istrategy):
        Cmd.delete(istrategy.path)
        Cmd.delete(istrategy.long_list_path)
        Cmd.delete(istrategy.short_list_path)


class ITrade(Trade, QtWidgets.QTreeWidgetItem):
    def __init__(self, info: dict, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Trade.__init__(self, info, parent)
        self.__config()
        self.gtrade = None  # link to GTrade

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        dt = self.dt + const.MSK_TIME_DIF
        dt = dt.strftime("%Y-%m-%d  %H:%M")
        self.setText(UTradeTree.Column.Date, dt)
        self.setText(UTradeTree.Column.Result, str(self.result))


class ITradeList(TradeList, QtWidgets.QTreeWidgetItem):
    def __init__(self, name, trades=None, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        TradeList.__init__(self, name, trades, parent)
        self.__config()
        self.updateText()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setTextAlignment(
            UTestTree.Column.Trades,
            Qt.AlignmentFlag.AlignRight
            )
        self.setTextAlignment(
            UTestTree.Column.Block,
            Qt.AlignmentFlag.AlignRight
            )
        self.setTextAlignment(
            UTestTree.Column.Allow,
            Qt.AlignmentFlag.AlignRight
            )

    def _createChild(self, trades, suffix):
        logger.debug(f"{self.__class__.__name__}.__createChild()")
        child_name = "-" + self.name.replace("tlist", "") + f" {suffix}"
        child = ITradeList(
            name = child_name,
            trades = trades,
            parent = self
            )
        child._asset = self.asset
        self._childs.append(child)
        return child

    @staticmethod  #load
    def load(file_path, parent=None):
        logger.debug(f"{__class__.__name__}.load()")
        obj = Cmd.loadJSON(file_path)
        name = obj["name"]
        itlist = ITradeList(name, parent=parent)
        for info in obj["trades"]:
            itrade = ITrade(info)
            itlist.add(itrade)
        itlist.updateText()
        return itlist

    def updateText(self):
        logger.debug(f"{self.__class__.__name__}.__updateText()")
        self.setText(UTestTree.Column.Name, self.name)
        self.setText(UTestTree.Column.Trades, str(self.count))

    def selectAsset(self, asset: Asset):
        logger.debug(f"{self.__class__.__name__}.selectAsset()")
        selected = list()
        for trade in self._trades:
            if trade.asset.figi == asset.figi:
                selected.append(trade)
        child = self._createChild(selected, asset.ticker)
        child._asset = asset
        return child

    def selectLong(self):
        logger.debug(f"{self.__class__.__name__}.selectLong()")
        selected = list()
        for trade in self._trades:
            if trade.isLong():
                selected.append(trade)
        child = self._createChild(selected, "long")
        return child

    def selectShort(self):
        logger.debug(f"{self.__class__.__name__}.selectShort()")
        selected = list()
        for trade in self._trades:
            if trade.isShort():
                selected.append(trade)
        child = self._createChild(selected, "short")
        return child

    def selectWin(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        selected = list()
        for trade in self._trades:
            if trade.isWin():
                selected.append(trade)
        child = self._createChild(selected, "win")
        return child

    def selectLoss(self):
        logger.debug(f"{self.__class__.__name__}.selectLoss()")
        selected = list()
        for trade in self._trades:
            if trade.isLoss():
                selected.append(trade)
        child = self._createChild(selected, "loss")
        return child

    def selectYear(self, year):
        logger.debug(f"{self.__class__.__name__}.selectYear()")
        selected = list()
        for trade in self._trades:
            trade_year = trade.dt.year
            if trade_year == year:
                selected.append(trade)
        child = self._createChild(selected, year)
        return child

    def selectBack(self):
        logger.debug(f"{self.__class__.__name__}.selectBack()")
        selected = list()
        for trade in self._trades:
            if trade.isBack():
                selected.append(trade)
        child = self._createChild(selected, "back")
        return child

    def selectForward(self):
        logger.debug(f"{self.__class__.__name__}.selectForward()")
        selected = list()
        for trade in self._trades:
            if trade.isForward():
                selected.append(trade)
        child = self._createChild(selected, "forward")
        return child


class ITest(Test, QtWidgets.QTreeWidgetItem):
    def __init__(self, name, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Test.__init__(self, name)
        self.__parent = parent
        self.__createProgressBar()
        self.__config()
        self.updateText()

    def __createProgressBar(self):
        logger.debug(f"{self.__class__.__name__}.__createProgressBar()")
        self.progress = UProgress()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )

    def __createSubgroups(self):
        logger.debug(f"{self.__class__.__name__}.__createSubgroups()")
        back = self.tlist.selectBack()
        forward = self.tlist.selectForward()
        for asset in self.alist:
            back.selectAsset(asset)
            forward.selectAsset(asset)

    def _loadTrades(self):
        logger.debug(f"{self.__class__.__name__}._loadTrades()")
        file_path = Cmd.join(self.dir_path, "tlist")
        if Cmd.isExist(file_path):
            self._tlist = ITradeList.load(file_path, parent=self)
            return True
        else:
            self._tlist = ITradeList(name="tlist", parent=self)
            return False

    @staticmethod  #load
    def load(dir_path: str):
        if not Cmd.isExist(dir_path):
            logger.error(
                f"{__class__.__name__}.load:"
                f"directory not found: '{dir_path}'"
                )
            return None
        name = Cmd.name(dir_path)
        itest = ITest(name)
        itest._loadConfig()
        itest._loadAssetList()
        itest._loadTrades()
        itest._loadStatus()
        itest._loadReport()
        itest.__createSubgroups()
        itest.updateText()
        itest.updateProgressBar()
        return itest

    @staticmethod  #rename
    def rename(test, new_name):
        Test.rename(test, new_name)
        test.updateText()
        test.updateProgressBar()

    def parent(self):
        return self.__parent

    def setParent(self, parent):
        self.__parent = parent

    def updateText(self):
        self.setText(UTestTree.Column.Name, self.name)

    def updateProgressBar(self):
        logger.debug(f"{self.__class__.__name__}.updateProgressBar()")
        if self.status == Test.Status.UNDEFINE:
            self.progress.setValue(0)
            self.progress.setFormat("Undefine")
        elif self.status == Test.Status.NEW:
            self.progress.setValue(0)
            self.progress.setFormat("New")
        elif self.status == Test.Status.EDITED:
            self.progress.setValue(0)
            self.progress.setFormat("Edited")
        elif self.status == Test.Status.PROCESS:
            self.progress.setValue(0)
            self.progress.setFormat("%p%")
        elif self.status == Test.Status.COMPLETE:
            self.progress.setValue(100)
            self.progress.setFormat("Complete")
        tree = self.parent()
        if tree:
            tree.setItemWidget(self, UTestTree.Column.Progress, self.progress)


class IToken(QtWidgets.QTreeWidgetItem):
    def __init__(self, name, token, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__name = name
        self.__type = UBrokerTree.Type.TOKEN
        self.__token = token
        self.__config()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(UBrokerTree.Column.Broker, self.__name)

    @property  #name
    def name(self):
        return self.__name

    @property  #type
    def type(self):
        return self.__type

    @property  #token
    def token(self):
        return self.__token


class ISandbox(Sandbox, QtWidgets.QTreeWidgetItem):
    def __init__(self, path: str, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Sandbox.__init__(self)
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__path = path
        self.__name = Cmd.name(self.__path)
        self.__type = UBrokerTree.Type.BROKER
        self.__config()
        self.__createChilds()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(UBrokerTree.Column.Broker, self.__name.title())

    def __createChilds(self):
        logger.debug(f"{self.__class__.__name__}.__createChilds()")
        dir_path = self.__path
        files = Cmd.getFiles(dir_path, full_path=True)
        files = Cmd.select(files, ".txt")
        for file in files:
            name = Cmd.name(file, extension=False)
            token = Cmd.read(file).strip()
            itoken = IToken(name, token, self)

    @property  #name
    def name(self):
        return self.__name

    @property  #type
    def type(self):
        return self.__type

    @property  #path
    def path(self):
        return self.__path


class ITinkoff(Tinkoff, QtWidgets.QTreeWidgetItem):
    def __init__(self, path: str, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        Tinkoff.__init__(self)
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        self.__path = path
        self.__name = Cmd.name(self.__path)
        self.__type = UBrokerTree.Type.BROKER
        self.__config()
        self.__createChilds()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(UBrokerTree.Column.Broker, self.__name.title())

    def __createChilds(self):
        logger.debug(f"{self.__class__.__name__}.__createChilds()")
        dir_path = self.__path
        files = Cmd.getFiles(dir_path, full_path=True)
        files = Cmd.select(files, ".txt")
        for file in files:
            name = Cmd.name(file, extension=False)
            token = Cmd.read(file).strip()
            itoken = IToken(name, token, self)

    @property  #name
    def name(self):
        return self.__name

    @property  #type
    def type(self):
        return self.__type

    @property  #path
    def path(self):
        return self.__path


class IAccount(Account, QtWidgets.QTreeWidgetItem):
    def __init__(self, broker, account_info, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Account.__init__(self, broker, account_info)
        self.__config()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.type = UBrokerTree.Type.ACCOUNT
        self.setText(UBrokerTree.Column.Broker, self.name.title())

    def portfolio(self):
        logger.debug(f"{self.__class__.__name__}.portfolio()")
        p = super().portfolio()
        iportfolio = IPortfolio.fromPortfolio(self, p, parent=None)
        return iportfolio

    def operations(self, begin=None, end=None):
        logger.debug(f"{self.__class__.__name__}.operations")
        operations = super().operations(begin, end)
        items = list()
        for op in operations:
            iop = IOperation.fromOperation(op, parent=None)
            items.append(iop)
        return items

    def orders(self):
        logger.debug(f"{self.__class__.__name__}.orders")
        orders = super().orders()
        items = list()
        for i in orders:
            iorder = IOrder.fromOrder(i, parent=None)
            items.append(iorder)
        return items


class IPortfolio(Portfolio, QtWidgets.QTreeWidgetItem):
    class ICash(Portfolio.Cash, QtWidgets.QTreeWidgetItem):
        def __init__(self, pos, parent):
            QtWidgets.QTreeWidgetItem.__init__(self, parent)
            Portfolio.Cash.__init__(
                self,
                pos.currency,
                pos.value,
                pos.block,
                )
            self.__config()

        def __config(self):
            self.setFlags(
                Qt.ItemFlag.ItemIsSelectable |
                Qt.ItemFlag.ItemIsEnabled
                )
            self.setText(UPortfolioTree.Column.Name, self.currency)
            self.setText(UPortfolioTree.Column.Balance, str(self.value))
            self.setText(UPortfolioTree.Column.Block, str(self.block))


    class IShare(Portfolio.Share, QtWidgets.QTreeWidgetItem):
        def __init__(self, pos, parent):
            QtWidgets.QTreeWidgetItem.__init__(self, parent)
            Portfolio.Share.__init__(
                self,
                pos.share,
                pos.balance,
                pos.block,
                pos.ID,
                pos.full_responce,
                )
            self.__config()

        def __config(self):
            self.setFlags(
                Qt.ItemFlag.ItemIsSelectable |
                Qt.ItemFlag.ItemIsEnabled
                )
            self.setText(UPortfolioTree.Column.Name, self.share.ticker)
            self.setText(UPortfolioTree.Column.Balance, str(self.balance))
            self.setText(UPortfolioTree.Column.Block, str(self.block))
            self.setText(UPortfolioTree.Column.ID, self.ID)


    class IBound(Portfolio.Bound, QtWidgets.QTreeWidgetItem):
        def __init__(self, pos, parent):
            QtWidgets.QTreeWidgetItem.__init__(self, parent)
            Portfolio.Bound.__init__(self)
            self.__config()

        def __config(self):
            self.setFlags(
                Qt.ItemFlag.ItemIsSelectable |
                Qt.ItemFlag.ItemIsEnabled
                )
            self.setText(UPortfolioTree.Column.Name, "WRITE_ME")


    class IFuture(Portfolio.Future, QtWidgets.QTreeWidgetItem):
        def __init__(self, pos, parent):
            QtWidgets.QTreeWidgetItem.__init__(self, parent)
            Portfolio.Future.__init__(self)
            self.__config()

        def __config(self):
            self.setFlags(
                Qt.ItemFlag.ItemIsSelectable |
                Qt.ItemFlag.ItemIsEnabled
                )
            self.setText(UPortfolioTree.Column.Name, "WRITE_ME")


    class IOption(Portfolio.Option, QtWidgets.QTreeWidgetItem):
        def __init__(self, pos, parent):
            QtWidgets.QTreeWidgetItem.__init__(self, parent)
            Portfolio.Option.__init__(self)
            self.__config()

        def __config(self):
            self.setFlags(
                Qt.ItemFlag.ItemIsSelectable |
                Qt.ItemFlag.ItemIsEnabled
                )
            self.setText(UPortfolioTree.Column.Name, "WRITE_ME")


    def __init__(
            self,
            account: IAccount,
            money: list,
            shares: list,
            bounds: list,
            futures: list,
            options: list,
            parent=None
            ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Portfolio.__init__(
            self, money, shares, bounds, futures, options
            )
        self.__account = account
        self.__config()
        self.__createChilds()
        self.setExpanded(True)

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        title = f"{self.__account.name} (id={self.__account.ID})"
        self.setText(UPortfolioTree.Column.Name, title)

    def __createChilds(self):
        logger.debug(f"{self.__class__.__name__}.__createChilds()")
        self.__createMoney()
        self.__createShares()
        self.__createBounds()
        self.__createFutures()
        self.__createOptions()

    def __createMoney(self):
        logger.debug(f"{self.__class__.__name__}.__createMoney()")
        money_group = QtWidgets.QTreeWidgetItem(self)
        money_group.setText(UPortfolioTree.Column.Name, "Money")
        for pos in self.money:
            item = IPortfolio.ICash(pos, parent=money_group)

    def __createShares(self):
        logger.debug(f"{self.__class__.__name__}.__createMoney()")
        group = QtWidgets.QTreeWidgetItem(self)
        group.setText(UPortfolioTree.Column.Name, "Shares")
        for pos in self.shares:
            item = IPortfolio.IShare(pos, parent=group)

    def __createBounds(self):
        logger.debug(f"{self.__class__.__name__}.__createMoney()")
        group = QtWidgets.QTreeWidgetItem(self)
        group.setText(UPortfolioTree.Column.Name, "Bounds")
        for pos in self.bounds:
            item = IPortfolio.IBound(pos, parent=group)

    def __createFutures(self):
        logger.debug(f"{self.__class__.__name__}.__createMoney()")
        group = QtWidgets.QTreeWidgetItem(self)
        group.setText(UPortfolioTree.Column.Name, "Futures")
        for pos in self.futures:
            item = IPortfolio.IFuture(pos, parent=group)

    def __createOptions(self):
        logger.debug(f"{self.__class__.__name__}.__createMoney()")
        group = QtWidgets.QTreeWidgetItem(self)
        group.setText(UPortfolioTree.Column.Name, "Options")
        for pos in self.options:
            item = IPortfolio.IOption(pos, parent=group)

    @staticmethod  #fromPortfolio
    def fromPortfolio(iaccount, portfolio, parent=None):
        item = IPortfolio(
            account=iaccount,
            money=portfolio.money,
            shares=portfolio.shares,
            bounds=portfolio.bounds,
            futures=portfolio.futures,
            options=portfolio.options,
            parent=parent,
            )
        return item


class IOrder(Order, QtWidgets.QTreeWidgetItem):
    def __init__(
            self,
            signal,
            TYPE,
            direction,
            asset,
            lots,
            price,
            exec_price=None,
            timeout=None,
            status=Order.Status.NEW,
            ID=None,
            commission=None,
            parent=None
        ):
        logger.debug(f"{__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Order.__init__(
            self, signal, TYPE, direction, asset, lots, price,
            exec_price, timeout, status, ID, commission
            )
        self.__config()

    def __config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        self.setText(UOrderTree.Column.Signal,      "TODO")
        self.setText(UOrderTree.Column.Type,        self.type.name)
        self.setText(UOrderTree.Column.Direction,   self.direction.name)
        self.setText(UOrderTree.Column.Asset,       self.asset.ticker)
        self.setText(UOrderTree.Column.Lots,        str(self.lots))
        self.setText(UOrderTree.Column.Price,       str(self.price))
        self.setText(UOrderTree.Column.ExecPrice,   str(self.exec_price))
        self.setText(UOrderTree.Column.Timeout,     str(self.timeout))
        self.setText(UOrderTree.Column.Status,      str(self.status.name))
        self.setText(UOrderTree.Column.ID,          str(self.ID))
        self.setText(UOrderTree.Column.Commission,  str(self.commission))

    @staticmethod  #fromOrder
    def fromOrder(order: Order, parent=None):
        iorder = IOrder(
            signal=         order.signal,
            TYPE=           order.type,
            direction=      order.direction,
            asset=          order.asset,
            lots=           order.lots,
            price=          order.price,
            exec_price=     order.exec_price,
            timeout=        order.timeout,
            status=         order.status,
            ID=             order.ID,
            commission=     order.commission,
            parent=         parent
            )
        return iorder


class IOperation(Operation, QtWidgets.QTreeWidgetItem):
    def __init__(
            self,
            signal,
            dt,
            direction,
            asset,
            lots,
            price,
            quantity,
            amount,
            commission,
            broker_info=None,
            parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidgetItem.__init__(self, parent)
        Operation.__init__(
            self, signal, dt, direction,
            asset, lots, price, quantity, amount, commission, broker_info,
            )
        self.config()

    def fromOperation(op, parent=None):
        item = IOperation(
            signal=op.signal,
            dt=op.dt,
            direction=op.direction,
            asset=op.asset,
            lots=op.lots,
            price=op.price,
            quantity=op.quantity,
            amount=op.amount,
            commission=op.commission,
            broker_info=op.broker_info,
            parent=parent,
            )
        return item

    def config(self):
        self.setFlags(
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEnabled
            )
        msk_dt = self.dt + const.MSK_TIME_DIF
        str_dt = msk_dt.strftime("%Y-%m-%d  %H:%M")
        self.setText(UOperationTree.Column.Signal,      "TODO")
        self.setText(UOperationTree.Column.Datetime,    str_dt)
        self.setText(UOperationTree.Column.Direction,   self.direction.name)
        self.setText(UOperationTree.Column.Asset,       self.asset.ticker)
        self.setText(UOperationTree.Column.Lots,        str(self.lots))
        self.setText(UOperationTree.Column.Price,       str(self.price))
        self.setText(UOperationTree.Column.Quantity,    str(self.quantity))
        self.setText(UOperationTree.Column.Amount,      str(self.amount))
        self.setText(UOperationTree.Column.Commission,  str(self.commission))



# -------------------------------- Graphics item
class GBar(Bar, QtWidgets.QGraphicsItemGroup):
    """ Const """
    # DRAW_BODY =         False
    DRAW_BODY =         True
    WIDTH =             16
    # INDENT =            1
    INDENT =            4
    SHADOW_WIDTH =      1

    def __init__(self, dt, o, h, l, c, v, parent=None):
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        Bar.__init__(self, dt, o, h, l, c, v, parent)
        self.n = None

    def __calcCoordinates(self):
        gchart = self.parent()
        self.x = gchart.xFromNumber(self.n)
        self.x0 = self.x + self.INDENT
        self.x1 = self.x + self.WIDTH - self.INDENT
        self.x_center = int((self.x0 + self.x1) / 2)
        self.y_opn = gchart.yFromPrice(self.open)
        self.y_cls = gchart.yFromPrice(self.close)
        self.y_hgh = gchart.yFromPrice(self.high)
        self.y_low = gchart.yFromPrice(self.low)
        self.open_pos = QtCore.QPointF(self.x_center, self.y_opn)
        self.close_pos = QtCore.QPointF(self.x_center, self.y_cls)
        self.high_pos = QtCore.QPointF(self.x_center, self.y_hgh)
        self.low_pos = QtCore.QPointF(self.x_center, self.y_low)

    def __setColor(self):
        if self.isBull():
            self.color = UColor.BULL
        elif self.isBear():
            self.color = UColor.BEAR
        else:
            self.color = UColor.UNDEFINE

    def __createOpenLine(self):
        opn = QtWidgets.QGraphicsLineItem(
            self.x0,        self.y_opn,
            self.x_center,  self.y_opn
            )
        pen = QtGui.QPen()
        pen.setColor(self.color)
        pen.setWidth(GBar.SHADOW_WIDTH)
        opn.setPen(pen)
        self.addToGroup(opn)

    def __createCloseLine(self):
        cls = QtWidgets.QGraphicsLineItem(
            self.x_center,  self.y_cls,
            self.x1,        self.y_cls
            )
        pen = QtGui.QPen()
        pen.setColor(self.color)
        pen.setWidth(GBar.SHADOW_WIDTH)
        cls.setPen(pen)
        self.addToGroup(cls)

    def __createShadowLine(self):
        shadow = QtWidgets.QGraphicsLineItem(
            self.x_center,
            self.y_low,
            self.x_center,
            self.y_hgh
            )
        pen = QtGui.QPen()
        pen.setColor(self.color)
        pen.setWidth(GBar.SHADOW_WIDTH)
        shadow.setPen(pen)
        self.addToGroup(shadow)

    def __createBody(self):
        width = self.x1 - self.x0
        height = abs(self.y_opn - self.y_cls)
        y0 = self.y_cls if self.isBull() else self.y_opn
        x0 = self.x_center - width / 2
        body = QtWidgets.QGraphicsRectItem(x0, y0, width, height)
        body.setPen(self.color)
        body.setBrush(self.color)
        self.addToGroup(body)

    @staticmethod  #fromCSV
    def fromCSV(bar_str, parent):
        code = f"GBar({bar_str}, parent)"
        bar = eval(code)
        return bar

    def createGraphicsItem(self):
        self.__calcCoordinates()
        self.__setColor()
        self.__createShadowLine()
        if self.DRAW_BODY:
            self.__createBody()
        else:
            self.__createOpenLine()
            self.__createCloseLine()


class GChart(Chart, QtWidgets.QGraphicsItemGroup):
    """ Const """
    INDENT =            1000

    def __init__(
            self,
            asset: Asset,
            timeframe: TimeFrame,
            begin: datetime,
            end: datetime,
            constructor=GBar.fromCSV,
            ):
        QtWidgets.QGraphicsItemGroup.__init__(self)
        Chart.__init__(self, asset, timeframe, begin, end, constructor)
        self.price_step = asset.min_price_step
        self.__numerateBars()
        self.__createSceneRect()
        self.__createGBars()

    def __numerateBars(self):
        for n, bar in enumerate(self._bars, 0):
            bar.n = n

    def __createSceneRect(self):
        x0 = 0
        y0 = 0
        x1 = len(self._bars) * GBar.WIDTH
        y1 = int(self.highestHigh() / self.price_step)
        height = y1 - y0 + self.INDENT
        width = x1 - x0 + self.INDENT
        rect = QtCore.QRectF(0, 0, width, height)
        self.rect = rect

    def __createGBars(self):
        for bar in self._bars:
            bar.createGraphicsItem()

    def barFromDatetime(self, dt):
        index = findLeft(self._bars, dt, key=lambda x: x.dt)
        assert index is not None
        gbar = self._bars[index]
        return gbar

    def xFromNumber(self, n):
        return int(n * GBar.WIDTH)

    def xFromDatetime(self, dt):
        gbar = self.barFromDatetime(dt)
        return gbar.x

    def yFromPrice(self, price):
        return int(self.rect.height() - price / self.price_step + self.INDENT)

    def nFromX(self, x):
        n = int(x / GBar.WIDTH)
        return n

    def barAt(self, x):
        n = self.nFromX(x)
        if n < len(self._bars):
            return self._bars[n]
        else:
            return None

    def addIndicator(self, i):
        ...


class GTrade(Trade, QtWidgets.QGraphicsItemGroup):
    """ Const """
    OPEN_WIDTH =    1
    STOP_WIDTH =    1
    TAKE_WIDTH =    1
    __open_pen = QtGui.QPen()
    __open_pen.setWidth(OPEN_WIDTH)
    __open_pen.setColor(UColor.OPEN)
    __stop_pen = QtGui.QPen()
    __stop_pen.setWidth(STOP_WIDTH)
    __stop_pen.setColor(UColor.STOP)
    __take_pen = QtGui.QPen()
    __take_pen.setWidth(TAKE_WIDTH)
    __take_pen.setColor(UColor.TAKE)

    def __init__(self, itrade, parent):
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        Trade.__init__(self, itrade._info, parent)
        itrade.gtrade = self  # link to GTrade in ITrade item
        self.itrade = itrade  #  link to ITrade in GTrade item
        self.__parent = parent
        self.__gchart = parent.gchart
        self.__calcCoordinates()
        self.__crateTradeShape()
        self.__createOpenItem()
        self.__createStopLossItem()
        self.__createTakeProfitItem()

    def __calcCoordinates(self):
        gchart = self.__gchart
        self.x_opn = (gchart.xFromDatetime(self.open_dt))
        self.x_cls = (gchart.xFromDatetime(self.close_dt))
        gbar = gchart.barFromDatetime(self.open_dt)
        y_hgh = gbar.high_pos.y()
        self.y0 = y_hgh - 50
        self.trade_pos = QtCore.QPointF(self.x_opn, self.y0)

    def __crateTradeShape(self):
        x0 = self.x_opn
        x1 = x0 + GBar.WIDTH
        x_center = (x0 + x1) / 2
        y0 = self.y0
        y1 = y0 - GBar.WIDTH
        if self.isLong():
            p1 = QtCore.QPointF(x0, y0)
            p2 = QtCore.QPointF(x1, y0)
            p3 = QtCore.QPointF(x_center, y1)
            triangle = QtGui.QPolygonF([p1, p2, p3])
        else:
            p1 = QtCore.QPointF(x0, y1)
            p2 = QtCore.QPointF(x1, y1)
            p3 = QtCore.QPointF(x_center, y0)
            triangle = QtGui.QPolygonF([p1, p2, p3])
        triangle = QtWidgets.QGraphicsPolygonItem(triangle)
        if self.isWin():
            triangle.setPen(UColor.TRADE_WIN)
            triangle.setBrush(UColor.TRADE_WIN)
        else:
            triangle.setPen(UColor.TRADE_LOSS)
            triangle.setBrush(UColor.TRADE_LOSS)
        self.addToGroup(triangle)

    def __createOpenItem(self):
        open_price = float(self.strategy["open price"])
        self.y_opn = self.__gchart.yFromPrice(open_price)
        open_item = QtWidgets.QGraphicsLineItem(
            self.x_opn,                 self.y_opn,
            self.x_cls + GBar.WIDTH,    self.y_opn
            )
        open_item.setPen(self.__open_pen)
        self.addToGroup(open_item)

    def __createStopLossItem(self):
        stop_loss_price = float(self.strategy["stop price"])
        self.y_stop = self.__gchart.yFromPrice(stop_loss_price)
        stop_loss = QtWidgets.QGraphicsLineItem(
            self.x_opn,                 self.y_stop,
            self.x_cls + GBar.WIDTH,    self.y_stop,
            )
        stop_loss.setPen(self.__stop_pen)
        self.addToGroup(stop_loss)

    def __createTakeProfitItem(self):
        take_profit_price = float(self.strategy["take price"])
        self.y_take = self.__gchart.yFromPrice(take_profit_price)
        take_profit = QtWidgets.QGraphicsLineItem(
            self.x_opn,                 self.y_take,
            self.x_cls + GBar.WIDTH,    self.y_take,
            )
        take_profit.setPen(self.__take_pen)
        self.addToGroup(take_profit)

    def __createAnnotation(self):
        msk_dt = self.dt + const.MSK_TIME_DIF
        str_dt = msk_dt.strftime("%Y-%m-%d  %H:%M")
        text = (
            "<div style='background-color:#333333;'>"
            f"{str_dt}<br>"
            f"Result: {self.result}<br>"
            f"Days: {self.holding}<br>"
            f"Profitability: {self.percent_per_day}% "
            "</div>"
            )
        self.annotation = QtWidgets.QGraphicsTextItem()
        self.annotation.setHtml(text)
        self.annotation.setPos(self.x_opn, self.y0 - 200)
        self.annotation.hide()
        self.addToGroup(self.annotation)

    def parent(self):
        return self.__parent

    def showAnnotation(self):
        self.__createAnnotation()
        self.annotation.show()

    def hideAnnotation(self):
        self.annotation.hide()


class GTradeList(TradeList, QtWidgets.QGraphicsItemGroup):
    def __init__(self, itlist, parent=None):
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)
        TradeList.__init__(self, itlist.name, parent=itlist)
        self.__createGChart()
        self.__createGTrades()

    def __createGChart(self):
        if self.asset is None:
            self.gchart = None
            return
        self.gchart = GChart(
            self.asset,
            TimeFrame("D"),
            self.begin,
            self.end,
            )

    def __createGTrades(self):
        if self.gchart is None:
            return
        for t in self.parent():
            gtrade = GTrade(t, parent=self)
            self.add(gtrade)         # Trade.add
            self.addToGroup(gtrade)  # QGraphicsItemGroup.addToGroup

    @property  #begin
    def begin(self):
        return self.test.back_begin

    @property  #end
    def end(self):
        return self.test.forward_end


class GIndicator(Indicator, QtWidgets.QGraphicsItemGroup):
    ...

class GMark(QtWidgets.QGraphicsItemGroup):
    ...


# -------------------------------- Thread
class TTest(QtCore.QThread):
    def __init__(self, test, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.tester = Tester()
        self.test = test
        self.tester.progress.connect(
            self.__updateProgress,
            Qt.ConnectionType.QueuedConnection,
            )
        self.tester.message.connect(
            self.__writeLogMessage,
            Qt.ConnectionType.QueuedConnection,
            )

    @QtCore.pyqtSlot(int)  #__updateProgress
    def __updateProgress(self, progress):
        self.test.progress.setValue(progress)

    @QtCore.pyqtSlot(str)  #__writeLogMessage
    def __writeLogMessage(self, message):
        logger.info(message)

    def run(self):
        self.tester.setTest(self.test)
        self.test.updateProgressBar()
        self.tester.runTest()


class TDownload(QtCore.QThread):
    def __init__(self, alist, from_year, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.alist = alist
        self.from_year = from_year
        self.tinkoff = TinkoffData()
        self.tinkoff.message.connect(
            self.__writeLogMessage,
            Qt.ConnectionType.QueuedConnection,
            )

    @QtCore.pyqtSlot(str)  #__writeLogMessage
    def __writeLogMessage(self, message):
        logger.info(message)

    def run(self):
        for asset in self.alist:
            self.tinkoff.download(asset, self.from_year)


class TExtract(QtCore.QThread):
    def __init__(self, dir_path, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.dir_path = dir_path
        self.tinkoff = TinkoffData()
        self.tinkoff.message.connect(
            self.__writeLogMessage,
            Qt.ConnectionType.QueuedConnection,
            )

    @QtCore.pyqtSlot(str)  #__writeLogMessage
    def __writeLogMessage(self, message):
        logger.info(message)

    def run(self):
        files = sorted(Cmd.getFiles(self.dir_path, full_path=True))
        files = Cmd.select(files, ".zip")
        for file in files:
            self.tinkoff.extractArchive(file)


class TConvert(QtCore.QThread):
    def __init__(self, timeframe_list, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.timeframe_list = timeframe_list
        self.tinkoff = TinkoffData()
        self.tinkoff.message.connect(
            self.__writeLogMessage,
            Qt.ConnectionType.QueuedConnection,
            )

    @QtCore.pyqtSlot(str)  #__writeLogMessage
    def __writeLogMessage(self, message):
        logger.info(message)

    def run(self):
        for root, dirs, files in os.walk(const.MOEX_DIR):
            if root.endswith(TinkoffData.DIR_NAME):
                for timeframe in self.timeframe_list:
                    self.tinkoff.exportData(root, timeframe)


class TUpdate(QtCore.QThread):
    def __init__(self, asset_dir_items, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.asset_dir_items = asset_dir_items
        self.scout = Scout()
        self.scout.message.connect(
            self.__writeLogMessage,
            Qt.ConnectionType.QueuedConnection,
            )

    @QtCore.pyqtSlot(str)  #__writeLogMessage
    def __writeLogMessage(self, message):
        logger.info(message)

    def run(self):
        for d in self.asset_dir_items:
            dir_path = d.path
            asset_path = Cmd.join(dir_path, "asset")
            timeframe_path = Cmd.join(dir_path, "timeframe")
            if Cmd.isExist(asset_path) and Cmd.isExist(timeframe_path):
                asset = Data.loadAsset(asset_path)
                timeframe = Data.loadTimeFrame(timeframe_path)
                self.scout.updateData(asset, timeframe)


class TConnect(QtCore.QThread):
    """ Signal """
    brokerConnected = QtCore.pyqtSignal(Services)

    def __init__(self, ibroker, itoken, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.ibroker = ibroker
        self.itoken = itoken
        self.iaccount = None
        self.work = True

    def run(self):
        token = self.itoken.token
        target = self.ibroker.TARGET
        with Client(token, target=target) as client:
            self.brokerConnected.emit(client)
            while self.work:
                timer.sleep(1)
                pass

    def closeConnection(self):
        self.work = False



# -------------------------------- Tree
class UDataTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Name = 0
        Type = 1
        Path = 2

    class Type(enum.Enum):
        DIR =               enum.auto()
        SHARES_DIR =        enum.auto()
        DATA =              enum.auto()
        ANALYTIC =          enum.auto()
        TINKOFF_ARCHIVES =  enum.auto()
        TINKOFF =           enum.auto()
        FILE =              enum.auto()
        ARCHIVE =           enum.auto()
        ASSET =             enum.auto()
        BIN =               enum.auto()
        CONFIG =            enum.auto()
        CSV =               enum.auto()
        JSON =              enum.auto()
        MARKDOWN =          enum.auto()
        SCRIPT =            enum.auto()
        TXT =               enum.auto()
        TIMEFRAME =         enum.auto()

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createDialogs()
        self.__createActions()
        self.__createMenu()
        self.__connect()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(UDataTree.Column.Name, Qt.SortOrder.AscendingOrder)
        self.setColumnWidth(UDataTree.Column.Name, 250)
        self.setColumnWidth(UDataTree.Column.Type, 80)
        self.setColumnWidth(UDataTree.Column.Path, 100)
        self.setFont(UFont.MONO)

    def __createDialogs(self):
        logger.debug(f"{self.__class__.__name__}.__createDialogs()")
        self.download_dialog = UDialogDataDownload()
        self.extract_dialog = UDialogDataExtract()
        self.convert_dialog = UDialogDataConvert()
        self.delete_dialog = UDialogDataDelete()
        self.update_dialog = UDialogDataUpdate()
        self.download_dialog.hide()
        self.extract_dialog.hide()
        self.convert_dialog.hide()
        self.delete_dialog.hide()
        self.update_dialog.hide()

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.__open = QtGui.QAction("Open as text")
        self.__show = QtGui.QAction("Show in explorer")
        self.__download = QtGui.QAction(UIcon.DOWNLOAD, "Download...")
        self.__extract = QtGui.QAction(UIcon.EXTRACT, "Extract...")
        self.__convert = QtGui.QAction(UIcon.CONVERT, "Convert...")
        self.__delete = QtGui.QAction(UIcon.DELETE, "Delete...")
        self.__update = QtGui.QAction(UIcon.UPDATE, "Update...")

    def __createMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.__open)
        self.menu.addAction(self.__show)
        self.menu.addSeparator()
        self.menu.addAction(self.__download)
        self.menu.addAction(self.__extract)
        self.menu.addAction(self.__convert)
        self.menu.addAction(self.__delete)
        self.menu.addAction(self.__update)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.__open.triggered.connect(self.openFile)
        self.__show.triggered.connect(self.showInExplorer)
        self.__download.triggered.connect(self.download)
        self.__extract.triggered.connect(self.extract)
        self.__convert.triggered.connect(self.convert)
        self.__delete.triggered.connect(self.delete)
        self.__update.triggered.connect(self.update)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        self.__open.setEnabled(False)
        self.__show.setEnabled(False)
        self.__download.setEnabled(False)
        self.__extract.setEnabled(False)
        self.__convert.setEnabled(False)
        self.__delete.setEnabled(False)
        self.__update.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.__download.setEnabled(True)
            self.__extract.setEnabled(True)
            self.__convert.setEnabled(True)
            self.__delete.setEnabled(True)
            self.__update.setEnabled(True)
        elif item.type == UDataTree.Type.DIR:
            self.__show.setEnabled(True)
            self.__download.setEnabled(True)
            self.__extract.setEnabled(True)
            self.__convert.setEnabled(True)
            self.__delete.setEnabled(True)
            self.__update.setEnabled(True)
        else:
            self.__open.setEnabled(True)
            self.__show.setEnabled(True)
            self.__download.setEnabled(True)
            self.__extract.setEnabled(True)
            self.__convert.setEnabled(True)
            self.__delete.setEnabled(True)
            self.__update.setEnabled(True)

    def __selectUserData(self, item: IData):
        logger.debug(f"{self.__class__.__name__}.__selectUserData()")
        for i in range(item.childCount()):
            child = item.child(i)
            if child.type == UDataTree.Type.DIR:
                self.__selectUserData(child)
            if child.type == UDataTree.Type.DATA:
                self.selected.append(child)

    @QtCore.pyqtSlot()  #__onFinish
    def __onFinish(self):
        logger.info("Complete!")

    def contextMenuEvent(self, e):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.currentItem()
        self.__resetActions()
        self.__setVisibleActions(item)
        action  = self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    def setRoot(self, root_dir):
        logger.debug(f"{self.__class__.__name__}.setRoot({root_dir})")
        self.__root_dir = root_dir
        dirs = Cmd.getDirs(root_dir, full_path=True)
        for path in dirs:
            name = Cmd.name(path)
            item = IData(name, path)
            self.addTopLevelItem(item)

    def openFile(self):
        logger.debug(f"{self.__class__.__name__}.__openFile()")
        item = self.currentItem()
        path = item.path
        command = ("xfce4-terminal", "-x", "nvim", path)
        Cmd.subprocess(command)

    def showInExplorer(self):
        logger.debug(f"{self.__class__.__name__}.__showInExplorer()")
        item = self.currentItem()
        path = item.path
        command = ("thunar", path)
        Cmd.subprocess(command)

    def download(self):
        logger.debug(f"{self.__class__.__name__}.download")
        alist, year = self.download_dialog.exec()
        if alist:
            self.thread = TDownload(alist, year)
            self.thread.finished.connect(self.__onFinish)
            self.thread.start()

    def extract(self):
        logger.debug(f"{self.__class__.__name__}.extract")
        if not self.extract_dialog.exec():
            return
        dir_path = Cmd.join(const.DOWNLOAD_DIR, TinkoffData.DOWNLOAD_DIR_NAME)
        self.thread = TExtract(dir_path)
        self.thread.finished.connect(self.__onFinish)
        self.thread.start()

    def convert(self):
        logger.debug(f"{self.__class__.__name__}.convert")
        timeframe_list = self.convert_dialog.exec()
        if timeframe_list:
            self.thread = TConvert(timeframe_list)
            self.thread.finished.connect(self.__onFinish)
            self.thread.start()

    def delete(self):
        logger.debug(f"{self.__class__.__name__}.delete")
        self.delete_dialog.exec()
        td = TinkoffData()

    def update(self):
        logger.debug(f"{self.__class__.__name__}.update")
        if not self.update_dialog.exec():
            return
        self.selected = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            self.__selectUserData(item)
        self.thread = TUpdate(self.selected)
        self.thread.finished.connect(self.__onFinish)
        self.thread.start()


class UAssetTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Ticker =     0
        Name =       1
        Type =       2
        Exchange =   3
        ListName =   0
        ListCount =  1

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__createMenu()
        self.__connect()

    def __iter__(self):
        items = list()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            items.append(item)
        return iter(items)

    def __config(self):
        self.setHeaderLabels(["Ticker"])
        self.setSortingEnabled(True)
        self.sortByColumn(
            UAssetTree.Column.Ticker,
            Qt.SortOrder.AscendingOrder
            )
        self.setFont(UFont.MONO)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.menu = QtWidgets.QMenu(self)
        self.action_add =      QtGui.QAction("Add", self)
        self.action_remove =   QtGui.QAction("Remove", self)
        self.action_info =     QtGui.QAction("Info", self)

    def __createMenu(self):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_add)
        self.menu.addAction(self.action_remove)
        self.menu.addAction(self.action_info)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        self.action_add.setEnabled(False)
        self.action_remove.setEnabled(False)
        self.action_info.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.action_add.setEnabled(True)
            self.action_remove.setEnabled(True)
        if isinstance(item, Asset):
            self.action_add.setEnabled(True)
            self.action_remove.setEnabled(True)
            self.action_info.setEnabled(True)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_add.triggered.connect(self.__onAdd)
        self.action_remove.triggered.connect(self.__onRemove)
        self.action_info.triggered.connect(self.__onInfo)

    @QtCore.pyqtSlot()  #__onAdd
    def __onAdd(self):
        logger.debug(f"{self.__class__.__name__}.__onAdd()")
        item = self.currentItem()
        ialist = item.parent()
        editor = UAssetListConstructor()
        edited_list = editor.editAssetList(ialist)
        if edited_list:
            IAssetList.save(edited_list)
            self.parent().updateWidget()

    @QtCore.pyqtSlot()  #__onRemove
    def __onRemove(self):
        logger.debug(f"{self.__class__.__name__}.__onRemove()")
        item = self.currentItem()
        assert isinstance(item, IShare)
        ialist = item.parent()
        ialist.remove(item)
        IAssetList.save(ialist)

    @QtCore.pyqtSlot()  #__onInfo
    def __onInfo(self):
        logger.debug(f"{self.__class__.__name__}.__onInfo()")
        ...

    def contextMenuEvent(self, e):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.itemAt(e.pos())
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    def setAssetList(self, ialist: IAssetList):
        logger.debug("UAssetTree.setAssetList()")
        """ Если воспользовться функцией
        self.clear()
        то заодно будет вызван деструктор QTreeWidgetItem и в следующий
        раз когда снова выберу тот же самый лист в комбобоксе
        получится:
        RuntimeError: wrapped C/C++ object of type IShare has been deleted
        Aborted (core dumped)
        --
        Поэтому очищаю список через takeTopLevelItem
        """
        while self.takeTopLevelItem(0): pass
        for iasset in ialist:
            self.addTopLevelItem(iasset)


class UStrategyTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Name =      0
        Long =      1
        Short =     2

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.menu = UStrategyMenu(self)
        self.__config()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(
            UStrategyTree.Column.Name,
            Qt.SortOrder.AscendingOrder
            )
        self.setColumnWidth(UStrategyTree.Column.Name, 150)
        self.setColumnWidth(UStrategyTree.Column.Long, 50)
        self.setColumnWidth(UStrategyTree.Column.Short, 50)
        self.setFont(UFont.MONO)

    def contextMenuEvent(self, e):
        logger.debug("UStrategyTree.contextMenuEvent(e)")
        item = self.itemAt(e.pos())
        self.menu.exec(item, QtGui.QCursor.pos())
        return e.ignore()


class UTestTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Name =      0
        Progress =  1
        Trades =    2
        Block =     3
        Allow =     4

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createTestActions()
        self.__createTestMenu()
        self.__createYearActions()
        self.__createYearMenu()
        self.__createTradeListActions()
        self.__createTradeListMenu()
        self.__connect()
        self.constructor = UTestConstructor()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(self.Column.Name, Qt.SortOrder.AscendingOrder)
        self.setColumnWidth(self.Column.Name, 200)
        self.setColumnWidth(self.Column.Progress, 80)
        self.setColumnWidth(self.Column.Trades, 55)
        self.setColumnWidth(self.Column.Block, 50)
        self.setColumnWidth(self.Column.Allow, 50)
        self.setFont(UFont.MONO)

    def __createTestActions(self):
        self.action_run =      QtGui.QAction("Run", self)
        self.action_pause =    QtGui.QAction("Pause", self)
        self.action_stop =     QtGui.QAction("Stop", self)
        self.action_new =      QtGui.QAction("New", self)
        self.action_copy =     QtGui.QAction("Copy", self)
        self.action_edit =     QtGui.QAction("Edit", self)
        self.action_rename =   QtGui.QAction("Rename", self)
        self.action_delete =   QtGui.QAction("Delete", self)

    def __createTestMenu(self):
        self.test_menu = QtWidgets.QMenu(self)
        self.test_menu.addAction(self.action_run)
        self.test_menu.addAction(self.action_pause)
        self.test_menu.addAction(self.action_stop)
        self.test_menu.addSeparator()
        self.test_menu.addAction(self.action_new)
        self.test_menu.addAction(self.action_copy)
        self.test_menu.addAction(self.action_edit)
        self.test_menu.addAction(self.action_rename)
        self.test_menu.addAction(self.action_delete)

    def __createYearActions(self):
        self.action_select_2018 = QtGui.QAction("Select 2018", self)
        self.action_select_2019 = QtGui.QAction("Select 2019", self)
        self.action_select_2020 = QtGui.QAction("Select 2020", self)
        self.action_select_2021 = QtGui.QAction("Select 2021", self)
        self.action_select_2022 = QtGui.QAction("Select 2022", self)
        self.action_select_2023 = QtGui.QAction("Select 2023", self)
        self.action_select_2024 = QtGui.QAction("Select 2024", self)

    def __createYearMenu(self):
        self.year_menu = QtWidgets.QMenu("Select year...")
        self.year_menu.addAction(self.action_select_2018)
        self.year_menu.addAction(self.action_select_2019)
        self.year_menu.addAction(self.action_select_2020)
        self.year_menu.addAction(self.action_select_2021)
        self.year_menu.addAction(self.action_select_2022)
        self.year_menu.addAction(self.action_select_2023)
        self.year_menu.addAction(self.action_select_2024)

    def __createTradeListActions(self):
        self.action_select_long =    QtGui.QAction("Select long", self)
        self.action_select_short =   QtGui.QAction("Select short", self)
        self.action_select_win =     QtGui.QAction("Select win", self)
        self.action_select_loss =    QtGui.QAction("Select loss", self)
        self.action_select_filter =  QtGui.QAction("Select filter", self)

    def __createTradeListMenu(self):
        self.trade_list_menu = QtWidgets.QMenu(self)
        self.trade_list_menu.addAction(self.action_select_long)
        self.trade_list_menu.addAction(self.action_select_short)
        self.trade_list_menu.addAction(self.action_select_win)
        self.trade_list_menu.addAction(self.action_select_loss)
        self.trade_list_menu.addAction(self.action_select_filter)
        self.trade_list_menu.addMenu(self.year_menu)

    def __connect(self):
        self.action_run.triggered.connect(self.__onRun)
        self.action_pause.triggered.connect(self.__onPause)
        self.action_stop.triggered.connect(self.__onStop)
        self.action_new.triggered.connect(self.__onNew)
        self.action_copy.triggered.connect(self.__onCopy)
        self.action_edit.triggered.connect(self.__onEdit)
        self.action_rename.triggered.connect(self.__onRemove)
        self.action_delete.triggered.connect(self.__onDelete)
        self.action_select_long.triggered.connect(self.__onSelectLong)
        self.action_select_short.triggered.connect(self.__onSelectShort)
        self.action_select_win.triggered.connect(self.__onSelectWin)
        self.action_select_loss.triggered.connect(self.__onSelectLoss)
        self.action_select_filter.triggered.connect(self.__onSelectFilter)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.actions():
            i.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.__new.setEnabled(True)
        elif isinstance(item, ITest):
            self.__run.setEnabled(True)
            self.__pause.setEnabled(True)
            self.__stop.setEnabled(True)
            self.__new.setEnabled(True)
            self.__copy.setEnabled(True)
            self.__edit.setEnabled(True)
            self.__rename.setEnabled(True)
            self.__delete.setEnabled(True)
        elif isinstance(item, ITradeList):
            self.__select_year.setEnabled(True)
            self.__select_long.setEnabled(True)
            self.__select_short.setEnabled(True)
            self.__select_win.setEnabled(True)
            self.__select_loss.setEnabled(True)
            self.__select_filter.setEnabled(True)

    def __reloadTest(self):
        logger.debug(f"{self.__class__.__name__}.__reloadTest()")
        itest = self.thread.test
        path = itest.dir_path
        self.remove(itest)
        reloaded = ITest.load(path)
        self.add(reloaded)

    @QtCore.pyqtSlot()  #__onRun
    def __onRun(self):
        logger.debug(f"{self.__class__.__name__}.run()")
        itest = self.currentItem()
        self.thread = TTest(itest)
        self.thread.finished.connect(self.__onFinish)
        self.thread.start()

    @QtCore.pyqtSlot()  #__onPause
    def __onPause(self):
        logger.debug(f"{self.__class__.__name__}.pause()")

    @QtCore.pyqtSlot()  #__onStop
    def __onStop(self):
        logger.debug(f"{self.__class__.__name__}.stop()")

    @QtCore.pyqtSlot()  #__onFinish
    def __onFinish(self):
        logger.debug(f"{self.__class__.__name__}.__onFinish()")
        self.__reloadTest()
        logger.info(f"Test complete!")

    @QtCore.pyqtSlot()  #__onNew
    def __onNew(self):
        logger.debug(f"{self.__class__.__name__}.new()")
        test = self.constructor.newTest()
        if test:
            self.add(test)

    @QtCore.pyqtSlot()  #__onCopy
    def __onCopy(self):
        logger.debug(f"{self.__class__.__name__}.copy()")
        itest = self.currentItem()
        dial = UDialogName()
        new_name = dial.enterName(default=itest.name)
        if new_name:
            path = Cmd.join(const.TEST_DIR, new_name)
            Cmd.copyDir(itest.dir_path, path)
            copy = ITest.load(path)
            copy.name = new_name
            self.parent().addTopLevelItem(copy)

    @QtCore.pyqtSlot()  #__onEdit
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.addEdit()")

    @QtCore.pyqtSlot()  #__onRemove
    def __onRemove(self):
        logger.debug(f"{self.__class__.__name__}.addTest()")
        itest = self.currentItem()
        index = self.indexFromItem(itest).row()
        self.takeTopLevelItem(index)

    @QtCore.pyqtSlot()  #__onDelete
    def __onDelete(self):
        logger.debug(f"{self.__class__.__name__}.delete()")
        itest = self.currentItem()
        dialog = UDialogConfirm()
        if dialog.confirm():
            logger.info(f"Delete test '{itest.name}'")
            Test.delete(itest)
            self.remove(itest)
        else:
            logger.info(f"Cancel delete")

    @QtCore.pyqtSlot()  #__onSelectLong
    def __onSelectLong(self):
        logger.debug(f"{self.__class__.__name__}.selectLong()")
        itlist = self.currentItem()
        itlist.selectLong()

    @QtCore.pyqtSlot()  #__onSelectShort
    def __onSelectShort(self):
        logger.debug(f"{self.__class__.__name__}.selectShort()")
        itlist = self.currentItem()
        itlist.selectShort()

    @QtCore.pyqtSlot()  #__onSelectWin
    def __onSelectWin(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        itlist = self.currentItem()
        itlist.selectWin()

    @QtCore.pyqtSlot()  #__onSelectLoss
    def __onSelectLoss(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        itlist = self.currentItem()
        itlist.selectLoss()

    @QtCore.pyqtSlot()  #__onSelectFilter
    def __onSelectFilter(self):
        logger.debug(f"{self.__class__.__name__}.selectWin()")
        itlist = self.currentItem()
        itlist.selectFilter()

    def contextMenuEvent(self, e: QtGui.QContextMenuEvent):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent(e)")
        item = self.itemAt(e.pos())
        # if item is None:
        #     self.test_menu.exec()
        if isinstance(item, ITest):
            self.test_menu.exec(QtGui.QCursor.pos())
        elif isinstance(item, ITradeList):
            self.trade_list_menu.exec(QtGui.QCursor.pos())
        return e.ignore()

    def addTest(self, itest: ITest):
        logger.debug(f"{self.__class__.__name__}.addTest()")
        self.addTopLevelItem(itest)
        itest.setParent(self)
        itest.updateProgressBar()


class UTradeTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Date =      0
        Result =    1

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(UTradeTree.Column.Date, Qt.SortOrder.AscendingOrder)
        self.setColumnWidth(UTradeTree.Column.Date, 150)
        self.setColumnWidth(UTradeTree.Column.Result, 100)
        self.setFont(UFont.MONO)


class UBrokerTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Broker = 0

    class Type(enum.Enum):
        BROKER =   enum.auto()
        TOKEN =    enum.auto()
        ACCOUNT =  enum.auto()

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__createMenu()
        self.__connect()
        self.thread = None
        self.current_itoken = None
        self.current_iaccount = None
        self.current_ibroker = None

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setFont(UFont.MONO)
        self.setSortingEnabled(True)
        self.sortByColumn(self.Column.Broker, Qt.SortOrder.AscendingOrder)
        self.setItemsExpandable(True)
        self.setColumnWidth(UBrokerTree.Column.Broker, 250)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.action_connect = QtGui.QAction("Connect")
        self.action_set_account = QtGui.QAction("Set account")
        self.action_disconnect = QtGui.QAction("Disconnect")

    def __createMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_connect)
        self.menu.addAction(self.action_disconnect)
        self.menu.addSeparator()
        self.menu.addAction(self.action_set_account)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_connect.triggered.connect(self.__onConnect)
        self.action_set_account.triggered.connect(self.__onSetAccount)
        self.action_disconnect.triggered.connect(self.__onDisconnect)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        self.action_connect.setEnabled(False)
        self.action_set_account.setEnabled(False)
        self.action_disconnect.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            pass
        elif item.type == UBrokerTree.Type.TOKEN:
            self.action_connect.setEnabled(True)
            self.action_disconnect.setEnabled(True)
        elif item.type == UBrokerTree.Type.ACCOUNT:
            self.action_set_account.setEnabled(True)

    @QtCore.pyqtSlot()  #__onConnect
    def __onConnect(self):
        logger.debug(f"{self.__class__.__name__}.__onConnect()")
        self.current_itoken = self.currentItem()
        self.current_ibroker = self.current_itoken.parent()
        self.thread = TConnect(self.current_ibroker, self.current_itoken)
        self.thread.brokerConnected.connect(self.__threadBrokerConnected)
        self.thread.finished.connect(self.__threadFinish)
        self.thread.start()
        logger.info(f"Connection enabled: '{self.current_ibroker.name}'")

    @QtCore.pyqtSlot()  #__onSetAccount
    def __onSetAccount(self):
        logger.debug(f"{self.__class__.__name__}.__onSetAccount()")
        self.current_iaccount = self.currentItem()
        broker_widget = self.parent()
        broker_widget.accountSetUp.emit(
            self.current_iaccount,
            )
        logger.info(
            f"Broker '{self.current_ibroker.name}' "
            f"account '{self.current_iaccount.name}' is active, "
            f"account_id={self.current_iaccount.ID}"
            )

    @QtCore.pyqtSlot()  #__onDisconnect
    def __onDisconnect(self):
        logger.debug(f"{self.__class__.__name__}.__onDisconnect()")
        self.thread.work = False

    @QtCore.pyqtSlot(Services)  #__threadBrokerConnected
    def __threadBrokerConnected(self, client):
        logger.debug(f"{self.__class__.__name__}.__onBrokerConnected()")
        self.current_ibroker.activate(client)
        accounts = self.current_ibroker.getAllAccounts()
        for acc in accounts:
            iaccount = IAccount(self.current_ibroker, acc)
            self.current_itoken.addChild(iaccount)
        broker_widget = self.parent()
        broker_widget.connectEnabled.emit(
            self.current_ibroker,
            )

    @QtCore.pyqtSlot()  #__threadFinish
    def __threadFinish(self):
        logger.debug(f"{self.__class__.__name__}.__onFinish()")
        logger.info(
            f"Connection disabled: broker '{self.current_ibroker.name}'"
            )
        broker_widget = self.parent()
        broker_widget.connectDisabled.emit(self.current_ibroker)
        while self.current_itoken.takeChild(0):
            pass
        self.current_ibroker = None
        self.current_itoken = None
        self.current_iaccount = None

    def contextMenuEvent(self, e):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.currentItem()
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()


class UPortfolioTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Name =      0
        Balance =   1
        Block =     2
        ID =        3

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__createMenu()
        self.__connect()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        # self.setSortingEnabled(True)
        # self.sortByColumn(self.Column.Name, Qt.SortOrder.AscendingOrder)
        self.setColumnWidth(self.Column.Name, 150)
        self.setColumnWidth(self.Column.Balance, 100)
        self.setColumnWidth(self.Column.Block, 100)
        self.setColumnWidth(self.Column.ID, 100)
        self.setFont(UFont.MONO)
        self.setItemsExpandable(True)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.action_update = QtGui.QAction("Update")

    def __createMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_update)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_update.triggered.connect(self.__onUpdate)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        self.action_update.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        # if item is None:
        #     self.action_update.setEnabled(True)
        self.action_update.setEnabled(True)

    @QtCore.pyqtSlot()  #__onUpdate
    def __onUpdate(self):
        operation_widget = self.parent()
        operation_widget.updateWidget()

    def contextMenuEvent(self, e):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.currentItem()
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()


class UOperationTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Signal =     0
        Datetime =   1
        Direction =  2
        Asset =      3
        Lots =       4
        Price =      5
        Quantity =   6
        Amount =     7
        Commission = 8

    def __init__(self, parent=None):
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__createMenu()
        self.__connect()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(self.Column.Datetime, Qt.SortOrder.DescendingOrder)
        self.setColumnWidth(self.Column.Datetime, 150)
        # self.setColumnWidth(self.Column.Balance, 100)
        # self.setColumnWidth(self.Column.Block, 100)
        # self.setColumnWidth(self.Column.ID, 100)
        self.setFont(UFont.MONO)
        self.setItemsExpandable(True)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.action_update = QtGui.QAction("Update")

    def __createMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_update)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_update.triggered.connect(self.__onUpdate)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        self.action_update.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        # if item is None:
        #     self.action_update.setEnabled(True)
        self.action_update.setEnabled(True)

    @QtCore.pyqtSlot()  #__onUpdate
    def __onUpdate(self):
        operation_widget = self.parent()
        operation_widget.updateWidget()

    def contextMenuEvent(self, e):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.currentItem()
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()


class UOrderTree(QtWidgets.QTreeWidget):
    class Column(enum.IntEnum):
        Signal =     0
        Type =       1
        Direction =  2
        Asset =      3
        Lots =       4
        Price =      5
        ExecPrice =  6
        Amount =     7
        Commission = 8
        Timeout =    9
        Status =     10
        ID =         11

    def __init__(self, parent=None):
        QtWidgets.QTreeWidget.__init__(self, parent)
        self.__config()
        self.__createActions()
        self.__createMenu()
        self.__connect()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        labels = list()
        for l in self.Column:
            labels.append(l.name)
        self.setHeaderLabels(labels)
        self.setSortingEnabled(True)
        self.sortByColumn(self.Column.Type, Qt.SortOrder.DescendingOrder)
        # self.setColumnWidth(self.Column.Datetime, 150)
        self.setFont(UFont.MONO)
        self.setItemsExpandable(True)

    def __createActions(self):
        logger.debug(f"{self.__class__.__name__}.__createActions()")
        self.action_update = QtGui.QAction("Update")
        self.action_edit = QtGui.QAction("Edit")
        self.action_remove = QtGui.QAction("Remove")

    def __createMenu(self):
        logger.debug(f"{self.__class__.__name__}.__createMenu()")
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction(self.action_update)
        self.menu.addSeparator()
        self.menu.addAction(self.action_edit)
        self.menu.addAction(self.action_remove)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.action_update.triggered.connect(self.__onUpdate)
        self.action_edit.triggered.connect(self.__onEdit)
        self.action_remove.triggered.connect(self.__onRemove)

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        for i in self.actions():
            i.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.action_update.setEnabled(True)
        elif isinstance(item, IOrder):
            self.action_update.setEnabled(True)
            self.action_edit.setEnabled(True)
            self.action_remove.setEnabled(True)

    @QtCore.pyqtSlot()  #__onUpdate
    def __onUpdate(self):
        logger.debug(f"{self.__class__.__name__}.__onUpdate()")
        order_widget = self.parent()
        order_widget.updateWidget()

    @QtCore.pyqtSlot()  #__onEdit
    def __onEdit(self):
        logger.debug(f"{self.__class__.__name__}.__onUpdate()")
        ...

    @QtCore.pyqtSlot()  #__onRemove
    def __onRemove(self):
        logger.debug(f"{self.__class__.__name__}.__onRemove()")
        iorder = self.currentItem()
        acc: IAccount = self.parent().currentAccount()
        acc.cancel(iorder)

    def contextMenuEvent(self, e):
        logger.debug(f"{self.__class__.__name__}.contextMenuEvent()")
        item = self.currentItem()
        self.__resetActions()
        self.__setVisibleActions(item)
        self.menu.exec(QtGui.QCursor.pos())
        return e.ignore()



# -------------------------------- Dialog
class UDialogConfirm(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configButton()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.__message_label = QtWidgets.QLabel()
        self.__btn_yes = QtWidgets.QToolButton(self)
        self.__btn_no = QtWidgets.QToolButton(self)

    def __createLayots(self):
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_yes)
        btn_box.addWidget(self.__btn_no)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__message_label)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    def __configButton(self):
        self.__btn_yes.setFixedSize(32, 32)
        self.__btn_yes.setIcon(UIcon.YES)
        self.__btn_yes.setIconSize(QtCore.QSize(32, 32))
        self.__btn_no.setFixedSize(32, 32)
        self.__btn_no.setIcon(UIcon.NO)
        self.__btn_no.setIconSize(QtCore.QSize(32, 32))

    def __config(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.__btn_yes.clicked.connect(self.accept)
        self.__btn_no.clicked.connect(self.reject)

    def confirm(self, message=None):
        if message is None:
            message = "Ты хорошо подумал?"
        self.__message_label.setText(message)
        result = QtWidgets.QDialog.exec(self)
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            return True
        else:
            return False


class UDialogName(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configButton()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.__lineedit = QtWidgets.QLineEdit("Enter name")
        self.__btn_yes = QtWidgets.QToolButton(self)
        self.__btn_no = QtWidgets.QToolButton(self)

    def __createLayots(self):
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.__btn_yes)
        btn_box.addWidget(self.__btn_no)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.__lineedit)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    def __configButton(self):
        self.__btn_yes.setFixedSize(32, 32)
        self.__btn_yes.setIcon(UIcon.YES)
        self.__btn_yes.setIconSize(QtCore.QSize(32, 32))
        self.__btn_no.setFixedSize(32, 32)
        self.__btn_no.setIcon(UIcon.NO)
        self.__btn_no.setIconSize(QtCore.QSize(32, 32))

    def __config(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.__btn_yes.clicked.connect(self.accept)
        self.__btn_no.clicked.connect(self.reject)

    def enterName(self, default="Enter name"):
        self.__lineedit.setText(default)
        result = QtWidgets.QDialog.exec(self)
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            name = self.__lineedit.text()
            return name
        else:
            return False


class UDialogDataDownload(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.widget_asset = UAssetWidget(self)
        self.spinbox_begin = QtWidgets.QSpinBox(self)
        self.spinbox_end = QtWidgets.QSpinBox(self)
        self.btn_download = QtWidgets.QPushButton("Download")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_download)
        h_btn_box.addWidget(self.btn_cancel)
        form = QtWidgets.QFormLayout()
        form.addRow("Begin year",       self.spinbox_begin)
        form.addRow("End year",         self.spinbox_end)
        grid = QtWidgets.QGridLayout()
        grid.addWidget(self.widget_asset, 0, 0, 2, 1)
        grid.addLayout(form, 0, 1)
        grid.addLayout(h_btn_box, 1, 1)
        self.setLayout(grid)

    def __config(self):
        self.setWindowTitle("Download Tinkoff data")
        year = date.today().year
        self.spinbox_begin.setMinimum(2017)
        self.spinbox_begin.setMaximum(year)
        self.spinbox_begin.setValue(2017)
        self.spinbox_end.setMinimum(2017)
        self.spinbox_end.setMaximum(year)
        self.spinbox_end.setValue(year)
        self.spinbox_end.setEnabled(False)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_download.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    @QtCore.pyqtSlot()  #__onFinish
    def __onFinish(self):
        logger.info("Download complete!")

    def exec(self):
        result = super().exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            alist = self.widget_asset.currentList()
            from_year = self.spinbox_begin.value()
            return alist, from_year
        else:
            logger.info(f"Cancel download")
            return False, False


class UDialogDataExtract(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.btn_extract = QtWidgets.QPushButton("Extract")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_extract)
        h_btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(h_btn_box)
        self.setLayout(vbox)

    def __config(self):
        self.setWindowTitle("Extract archives")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_extract.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    @QtCore.pyqtSlot()  #__onFinish
    def __onFinish(self):
        logger.info("Extract complete!")

    def exec(self):
        result = super().exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            return True
        else:
            logger.info(f"Cancel extract")
            return False


class UDialogDataConvert(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.groupbox_timeframe = QtWidgets.QGroupBox("TimeFrame")
        self.checkbox_1M = QtWidgets.QCheckBox("1M")
        self.checkbox_5M = QtWidgets.QCheckBox("5M")
        self.checkbox_1H = QtWidgets.QCheckBox("1H")
        self.checkbox_D = QtWidgets.QCheckBox("1D")
        self.btn_convert = QtWidgets.QPushButton("Convert")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_convert)
        h_btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.checkbox_1M)
        vbox.addWidget(self.checkbox_5M)
        vbox.addWidget(self.checkbox_1H)
        vbox.addWidget(self.checkbox_D)
        vbox.addLayout(h_btn_box)
        self.setLayout(vbox)

    def __config(self):
        self.setWindowTitle("Convert data")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_convert.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    @QtCore.pyqtSlot()  #__onFinish
    def __onFinish(self):
        logger.info("Convert complete!")

    def exec(self):
        result = super().exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            timeframe_list = list()
            if self.checkbox_1M.isChecked():
                timeframe_list.append(TimeFrame("1M"))
            if self.checkbox_5M.isChecked():
                timeframe_list.append(TimeFrame("5M"))
            if self.checkbox_1H.isChecked():
                timeframe_list.append(TimeFrame("1H"))
            if self.checkbox_D.isChecked():
                timeframe_list.append(TimeFrame("D"))
            return timeframe_list
        else:
            logger.info(f"Cancel convert")
            return False


class UDialogDataDelete(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.checkbox_archive = QtWidgets.QCheckBox("Archives")
        self.checkbox_tinkoff = QtWidgets.QCheckBox("Tinkoff data")
        self.checkbox_user = QtWidgets.QCheckBox("User data")
        self.btn_delete = QtWidgets.QPushButton("Delete")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_delete)
        h_btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.checkbox_archive)
        vbox.addWidget(self.checkbox_tinkoff)
        vbox.addWidget(self.checkbox_user)
        vbox.addLayout(h_btn_box)
        self.setLayout(vbox)

    def __config(self):
        self.setWindowTitle("Delete data")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_delete.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def exec(self):
        result = super().exec()
        if self.checkbox_archive.isChecked():
            logger.info(f"Delete Tinkoff archives")
            td.deleteArchives()
        if self.checkbox_tinkoff.isChecked():
            logger.info(f"Delete Tinkoff data")
            td.deleteTinkoffData()
        if self.checkbox_user.isChecked():
            logger.info(f"Delete User data")
            td.deleteUserData()
            return True
        else:
            logger.info(f"Cancel delete")
            return False


class UDialogDataUpdate(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        self.btn_extract = QtWidgets.QPushButton("Update")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

    def __createLayots(self):
        h_btn_box = QtWidgets.QHBoxLayout()
        h_btn_box.addWidget(self.btn_extract)
        h_btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(h_btn_box)
        self.setLayout(vbox)

    def __config(self):
        self.setWindowTitle("Update user data")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_extract.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def __selectUserData(self, item: IData):
        logger.debug(f"{self.__class__.__name__}.__selectUserData()")
        for i in range(item.childCount()):
            child = item.child(i)
            if child.type == UDataTree.Type.DIR:
                self.__selectUserData(child)
            if child.type == UDataTree.Type.DATA:
                self.selected.append(child)

    def exec(self):
        result = super().exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            return True
        else:
            logger.info(f"Cancel update")
            return False


class UAssetListConstructor(QtWidgets.QDialog):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__configTree()
        self.__configButton()
        self.__connect()
        self.__initUI()
        self.__loadAssets()

    def __config(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tree = UAssetTree(self)
        self.search_line = QtWidgets.QLineEdit(self)
        self.btn_search = QtWidgets.QToolButton(self)
        self.btn_apply = QtWidgets.QToolButton(self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.btn_search)
        hbox.addWidget(self.search_line)
        hbox.addStretch()
        hbox.addWidget(self.btn_apply)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)

    def __configTree(self):
        logger.debug(f"{self.__class__.__name__}.__configTree()")
        labels = list()
        for i in UAssetTree.Column:
            labels.append(i.name)
        self.tree.setHeaderLabels(labels)
        self.tree.setColumnWidth(UAssetTree.Column.Ticker, 100)
        self.tree.setColumnWidth(UAssetTree.Column.Name, 300)
        self.tree.setColumnWidth(UAssetTree.Column.Type, 70)
        self.tree.setColumnWidth(UAssetTree.Column.Exchange, 70)
        self.tree.setFixedWidth(600)
        self.tree.setMinimumHeight(400)

    def __configButton(self):
        self.btn_search.setIcon(UIcon.SEARCH)
        self.btn_search.setFixedSize(32, 32)
        self.btn_search.setIconSize(QtCore.QSize(30, 30))
        self.btn_apply.setIcon(UIcon.APPLY)
        self.btn_apply.setFixedSize(32, 32)
        self.btn_apply.setIconSize(QtCore.QSize(30, 30))

    def __connect(self):
        self.btn_apply.clicked.connect(self.accept)

    def __initUI(self):
        logger.debug(f"{self.__class__.__name__}.__initUI()")
        self.search_line.setText("Enter ticker...")

    def __loadAssets(self):
        logger.debug(f"{self.__class__.__name__}.__loadAssets()")
        # path = Cmd.join(const.RES_DIR, "share", "MOEX_ALL_ASSET_LIST")
        path = Cmd.join(const.RES_DIR, "share", "MOEX_TINKOFF_XX5")
        self.full_alist = IAssetList.load(path)
        self.tree.setAssetList(self.full_alist)

    def __clearMark(self):
        logger.debug(f"{self.__class__.__name__}.__clearMark()")
        for i in self.tree:
            i.setCheckState(UAssetTree.Column.Ticker, Qt.CheckState.Unchecked)

    def __markExisting(self, editable):
        logger.debug(f"{self.__class__.__name__}.__markExisting()")
        for asset in self.full_alist:
            if asset in editable:
                asset.setCheckState(
                    UAssetTree.Column.Ticker, Qt.CheckState.Checked
                    )

    def editAssetList(self, editable: IAssetList) -> bool:
        logger.debug(f"{self.__class__.__name__}.editAssetList()")
        self.__clearMark()
        self.__markExisting(editable)
        self.exec()
        editable.clear()
        for i in self.tree:
            state = i.checkState(UAssetTree.Column.Ticker)
            if state == Qt.CheckState.Checked:
                index = self.tree.indexOfTopLevelItem(i)
                item = self.tree.takeTopLevelItem(index)
                editable.add(item)
        # IAssetList.save(editable)  # DEBUG - попробуй тейками забрать итемы нужные
        return editable


class UStrategyConstructor(QtWidgets.QDialog):
    __TEMPLATE = Cmd.join(const.STRATEGY_DIR, ".template")

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configButton()
        self.__config()
        self.__connect()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.lineedit_name = QtWidgets.QLineEdit("Enter strategy name", self)
        self.btn_ok = QtWidgets.QToolButton(self)
        self.btn_cancel = QtWidgets.QToolButton(self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        btn_box = QtWidgets.QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(self.btn_ok)
        btn_box.addWidget(self.btn_cancel)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.lineedit_name)
        vbox.addLayout(btn_box)
        self.setLayout(vbox)

    def __configButton(self):
        logger.debug(f"{self.__class__.__name__}.__configButton()")
        self.btn_ok.setFixedSize(32, 32)
        self.btn_ok.setIcon(UIcon.OK)
        self.btn_ok.setIconSize(QtCore.QSize(32, 32))
        self.btn_cancel.setFixedSize(32, 32)
        self.btn_cancel.setIcon(UIcon.CANCEL)
        self.btn_cancel.setIconSize(QtCore.QSize(32, 32))

    def __config(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def newStrategy(self):
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            name = self.lineedit_name.text()
            new_strategy_path = Cmd.join(const.STRATEGY_DIR, f"{name}.py")
            code = Cmd.read(self.__TEMPLATE)
            code.replace("__STRATEGY_NAME__", name)
            Cmd.save(code, new_strategy_path)
            istrategy = IStrategy(name, new_strategy_path)
            logger.info(f"Create new strategy '{istrategy.name}'")
            return istrategy
        else:
            logger.info(f"Cancel new strategy")
            return False


class UTestConstructor(QtWidgets.QDialog):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__createForm()
        self.__configButton()
        self.__connect()
        self.__config()
        self.__loadUserStrategy()
        self.__loadUserTimeframes()
        self.__initUI()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.lineedit_testname = QtWidgets.QLineEdit()
        self.combobox_strategy = QtWidgets.QComboBox()
        self.combobox_version = QtWidgets.QComboBox()
        self.combobox_timeframe = QtWidgets.QComboBox()
        self.dblspinbox_deposit = QtWidgets.QDoubleSpinBox()
        self.dblspinbox_commission = QtWidgets.QDoubleSpinBox()
        self.groupbox_back = QtWidgets.QGroupBox("Back period")
        self.back_begin = QtWidgets.QDateEdit()
        self.back_end = QtWidgets.QDateEdit()
        self.groupbox_forward = QtWidgets.QGroupBox("Forward period")
        self.forward_begin = QtWidgets.QDateEdit()
        self.forward_end = QtWidgets.QDateEdit()
        self.description = QtWidgets.QPlainTextEdit()
        self.btn_alist = QtWidgets.QToolButton()
        self.btn_save = QtWidgets.QToolButton()
        self.btn_cancel = QtWidgets.QToolButton()

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        self.vbox_back = QtWidgets.QVBoxLayout()
        self.vbox_back.addWidget(self.back_begin)
        self.vbox_back.addWidget(self.back_end)
        self.groupbox_back.setLayout(self.vbox_back)
        self.vbox_forward = QtWidgets.QVBoxLayout()
        self.vbox_forward.addWidget(self.forward_begin)
        self.vbox_forward.addWidget(self.forward_end)
        self.groupbox_forward.setLayout(self.vbox_forward)
        self.hbox_btn = QtWidgets.QHBoxLayout()
        self.hbox_btn.addStretch()
        self.hbox_btn.addWidget(self.btn_save)
        self.hbox_btn.addWidget(self.btn_cancel)
        self.hbox_alist = QtWidgets.QHBoxLayout()
        self.hbox_alist.addStretch()
        self.hbox_alist.addWidget(self.btn_alist)

    def __createForm(self):
        logger.debug(f"{self.__class__.__name__}.__createForm()")
        form = QtWidgets.QFormLayout()
        form.addRow("Test name",        self.lineedit_testname)
        form.addRow("Strategy",         self.combobox_strategy)
        form.addRow("Version",          self.combobox_version)
        form.addRow("Timeframe",        self.combobox_timeframe)
        form.addRow("Asset list",       self.hbox_alist)
        form.addRow("Deposit",          self.dblspinbox_deposit)
        form.addRow("Commission %",     self.dblspinbox_commission)
        form.addRow(self.groupbox_back)
        form.addRow(self.groupbox_forward)
        form.addRow(QtWidgets.QLabel("Description"))
        form.addRow(self.description)
        form.addRow(self.hbox_btn)
        self.setLayout(form)

    def __configButton(self):
        logger.debug(f"{self.__class__.__name__}.__configButton()")
        self.btn_alist.setIcon(UIcon.ASSET)
        self.btn_alist.setFixedSize(32, 32)
        self.btn_alist.setIconSize(QtCore.QSize(30, 30))
        self.btn_save.setIcon(UIcon.SAVE)
        self.btn_save.setFixedSize(32, 32)
        self.btn_save.setIconSize(QtCore.QSize(30, 30))
        self.btn_cancel.setIcon(UIcon.CANCEL)
        self.btn_cancel.setFixedSize(32, 32)
        self.btn_cancel.setIconSize(QtCore.QSize(30, 30))

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.combobox_strategy.currentTextChanged.connect(self.__loadVersions)
        self.btn_alist.clicked.connect(self.__editAssetList)
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

    def __loadUserStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__loadUserStrategy()")
        for name in Strategy.ALL:
            self.combobox_strategy.addItem(name)

    def __loadVersions(self):
        logger.debug(f"{self.__class__.__name__}.__loadVersions()")
        name = self.combobox_strategy.currentText()
        versions = Strategy.versions(name)
        self.combobox_version.clear()
        self.combobox_version.addItems(versions)

    def __loadUserTimeframes(self):
        logger.debug(f"{self.__class__.__name__}.__loadUserTimeframes()")
        for timeframe in TimeFrame.ALL:
            self.combobox_timeframe.addItem(str(timeframe))

    def __initUI(self):
        self.combobox_timeframe.setCurrentText("1M")
        self.lineedit_testname.setText("unnamed")
        self.dblspinbox_deposit.setMinimum(0.0)
        self.dblspinbox_deposit.setMaximum(1_000_000_000.0)
        self.dblspinbox_deposit.setValue(100_000.0)
        self.dblspinbox_commission.setMinimum(0.0)
        self.dblspinbox_commission.setMaximum(1.0)
        self.dblspinbox_commission.setValue(0.05)
        self.back_begin.setDate(QtCore.QDate(2018, 1, 1))
        self.back_end.setDate(QtCore.QDate(2023, 1, 1))
        self.forward_begin.setDate(QtCore.QDate(2023, 1, 1))
        self.forward_end.setDate(QtCore.QDate(2023, 9, 1))

    def __editAssetList(self):
        editor = UAssetListConstructor()
        editor.editAssetList(self.alist)

    def __writeTestConfig(self, test):
        test.name =             self.lineedit_testname.text()
        test.description =      self.description.toPlainText()
        test.strategy =         self.combobox_strategy.currentText()
        test.version =          self.combobox_version.currentText()
        test.timeframe =        self.combobox_timeframe.currentText()
        test.alist =            self.alist
        test.deposit =          self.dblspinbox_deposit.value()
        test.commission =       self.dblspinbox_commission.value() / 100
        test.back_begin =       str(self.back_begin.date().toPyDate())
        test.back_end =         str(self.back_end.date().toPyDate())
        test.forward_begin =    str(self.forward_begin.date().toPyDate())
        test.forward_end =      str(self.forward_end.date().toPyDate())
        test.updateText()
        return test

    def __readTestConfig(self, test):
        self.lineedit_testname.setText(test.name)
        self.combobox_strategy.setCurrentText(test.strategy)
        self.combobox_version.setCurrentText(test.version)
        self.combobox_timeframe.setCurrentText(str(test.timeframe))
        self.dblspinbox_deposit.setValue(test.deposit)
        self.dblspinbox_commission.setValue(test.commission * 100)
        self.back_begin.setDate(test.back_begin.date())
        self.back_end.setDate(test.back_end.date())
        self.forward_begin.setDate(test.forward_begin.date())
        self.forward_end.setDate(test.forward_end.date())
        self.description.setPlainText(test.description)

    def newTest(self):
        new_test = ITest(name="")
        self.alist = IAssetList(".tmp", parent=new_test)
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            self.__writeTestConfig(new_test)
            ITest.save(new_test)
            logger.info(f"New test '{new_test.name}' created")
            return new_test
        else:
            logger.info(f"Cancel new test")
            return False

    def editTest(self, itest):
        self.__readTestConfig(itest)
        self.alist = itest.alist
        result = self.exec()
        if result == QtWidgets.QDialog.DialogCode.Accepted:
            ITest.delete(itest)
            edited = ITest(name="")
            edited = self.__writeTestConfig(edited)
            edited.status = Test.Status.EDITED
            ITest.save(edited)
            logger.info(f"Test edited")
            return edited
        else:
            logger.info(f"Cancel edit test")
            return False



# -------------------------------- REMOVE IT
class UStrategyMenu(QtWidgets.QMenu):
    def __init__(self, parent):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QMenu.__init__(self, parent)
        self.__new =     QtGui.QAction("New", self)
        self.__edit =    QtGui.QAction("Edit", self)
        self.__delete =  QtGui.QAction("Delete", self)
        self.addAction(self.__new)
        self.addAction(self.__edit)
        self.addAction(self.__delete)
        self.constructor = UStrategyConstructor()

    def __resetActions(self):
        logger.debug(f"{self.__class__.__name__}.__resetActions()")
        self.__new.setEnabled(False)
        self.__edit.setEnabled(False)
        self.__delete.setEnabled(False)

    def __setVisibleActions(self, item):
        logger.debug(f"{self.__class__.__name__}.__setVisibleActions()")
        if item is None:
            self.__new.setEnabled(True)
        if isinstance(item, IStrategy):
            self.__new.setEnabled(True)
            self.__edit.setEnabled(True)
            self.__delete.setEnabled(True)

    def exec(self, item, pos):
        logger.debug(f"{self.__class__.__name__}.exec()")
        self.__resetActions()
        self.__setVisibleActions(item)
        action = super().exec(QtGui.QCursor.pos())
        if action is None: return
        elif action.text() == "New": self.new()
        elif action.text() == "Edit": self.edit(item)
        elif action.text() == "Delete": self.delete(item)

    def add(self, istrategy: IStrategy):
        logger.debug(f"{self.__class__.__name__}.add()")
        tree = self.parent()
        tree.addTopLevelItem(istrategy)

    def new(self):
        logger.debug(f"{self.__class__.__name__}.new()")
        istrategy = self.constructor.newStrategy()
        if istrategy:
            self.add(istrategy)

    def edit(self, item):
        logger.debug(f"{self.__class__.__name__}.edit()")
        path = item.path
        Cmd.open("nvim", path)

    def delete(self, item):
        logger.debug(f"{self.__class__.__name__}.delete()")
        message = "Ты хорошо подумал?"
        dial = UDialogConfirm()
        if dial.confirm(message):
            tree = self.parent()
            row = tree.indexFromItem(item).row()
            tree.takeTopLevelItem(row)
            IStrategy.delete(item)



# -------------------------------- Left tool
class UDataWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__configButton()
        self.__setButtonsSize()
        self.__connect()
        self.__initUI()

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.data_tree = UDataTree()
        self.btn_download = QtWidgets.QToolButton()
        self.btn_extract = QtWidgets.QToolButton()
        self.btn_convert = QtWidgets.QToolButton()
        self.btn_delete = QtWidgets.QToolButton()
        self.btn_update = QtWidgets.QToolButton()

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.btn_download)
        hbox.addWidget(self.btn_extract)
        hbox.addWidget(self.btn_convert)
        hbox.addWidget(self.btn_delete)
        hbox.addWidget(self.btn_update)
        hbox.addStretch()
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(hbox)
        vbox.addWidget(self.data_tree)

    def __setButtonsSize(self):
        self.btn_download.setFixedSize(32, 32)
        self.btn_extract.setFixedSize(32, 32)
        self.btn_convert.setFixedSize(32, 32)
        self.btn_delete.setFixedSize(32, 32)
        self.btn_update.setFixedSize(32, 32)

    def __configButton(self):
        logger.debug("UAssetWidget.__configButton()")
        size = QtCore.QSize(30, 30)
        self.btn_download.setIcon(UIcon.DOWNLOAD)
        self.btn_download.setIconSize(size)
        self.btn_extract.setIcon(UIcon.EXTRACT)
        self.btn_extract.setIconSize(size)
        self.btn_convert.setIcon(UIcon.CONVERT)
        self.btn_convert.setIconSize(size)
        self.btn_delete.setIcon(UIcon.DELETE)
        self.btn_delete.setIconSize(size)
        self.btn_update.setIcon(UIcon.UPDATE)
        self.btn_update.setIconSize(size)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_download.clicked.connect(self.__onButtonDownload)
        self.btn_extract.clicked.connect(self.__onButtonExtract)
        self.btn_convert.clicked.connect(self.__onButtonConvert)
        self.btn_delete.clicked.connect(self.__onButtonDelete)
        self.btn_update.clicked.connect(self.__onButtonUpdate)

    def __initUI(self):
        logger.debug(f"{self.__class__.__name__}.__initUI()")
        self.data_tree.setRoot(const.DATA_DIR)

    def __onButtonDownload(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonDownload()")
        assert False

    def __onButtonExtract(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonExtract()")
        assert False

    def __onButtonConvert(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonConvert()")
        assert False

    def __onButtonDelete(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonDelete()")
        assert False

    def __onButtonUpdate(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonUpdate()")
        assert False


class UAssetWidget(QtWidgets.QWidget):
    """ Signal """
    assetChanged = QtCore.pyqtSignal(IShare)

    def __init__(self, parent=None):
        logger.debug("UAssetWidget.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__setButtonsSize()
        self.__configButton()
        self.__connect()
        self.__loadUserAssetLists()
        self.__initUI()

    def __createWidgets(self):
        logger.debug("UAssetWidget.__createWidgets()")
        self.combobox_listname = QtWidgets.QComboBox(self)
        self.btn_add = QtWidgets.QToolButton(self)
        self.btn_settings = QtWidgets.QToolButton(self)
        self.tree = UAssetTree(self)

    def __createLayots(self):
        logger.debug("UAssetWidget.__createLayots()")
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.combobox_listname)
        hbox.addWidget(self.btn_add)
        hbox.addWidget(self.btn_settings)
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(hbox)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)

    def __setButtonsSize(self):
        logger.debug("UAssetWidget.__setButtonsSize()")
        self.btn_add.setFixedSize(32, 32)
        self.btn_settings.setFixedSize(32, 32)

    def __configButton(self):
        logger.debug("UAssetWidget.__configButton()")
        self.btn_add.setIcon(UIcon.ADD)
        self.btn_settings.setIcon(UIcon.SETTINGS)
        self.btn_add.setIconSize(QtCore.QSize(32, 32))
        self.btn_settings.setIconSize(QtCore.QSize(32, 32))

    def __connect(self):
        logger.debug("UAssetWidget.__connect()")
        self.combobox_listname.currentTextChanged.connect(self.updateWidget)
        self.tree.itemClicked.connect(self.__onItemClicked)
        self.btn_add.clicked.connect(self.__onButtonAdd)
        self.btn_settings.clicked.connect(self.__onButtonSettings)

    def __loadUserAssetLists(self):
        logger.debug("UAssetWidget.__loadUserAssetLists()")
        files = sorted(Cmd.getFiles(const.ASSET_DIR))
        for file_name in files:
            self.combobox_listname.addItem(file_name)

    def __initUI(self):
        logger.debug("UAssetWidget.__initUI()")
        self.combobox_listname.setCurrentText("XX5")
        iasset = self.tree.topLevelItem(0)
        self.tree.setCurrentItem(iasset)

    @QtCore.pyqtSlot()  #__onButtonAdd
    def __onButtonAdd(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonAdd()")
        ialist = self.currentList()
        editor = UAssetListConstructor()
        edited_list = editor.editAssetList(ialist)
        if edited_list:
            IAssetList.save(edited_list)
            self.updateWidget()

    @QtCore.pyqtSlot()  #__onButtonSettings
    def __onButtonSettings(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonSettings()")
        ...

    @QtCore.pyqtSlot()  #__onItemClicked
    def __onItemClicked(self):
        logger.debug(f"{self.__class__.__name__}.__onItemClicked()")
        item = self.tree.currentItem()
        if isinstance(item, Asset):
            self.assetChanged.emit(item)

    def updateWidget(self):
        logger.debug("UAssetWidget.updateWidget()")
        name = self.combobox_listname.currentText()
        self.__current_list = IAssetList.load(name)
        self.tree.setAssetList(self.__current_list)

    def currentList(self):
        return self.__current_list

    def currentAsset(self):
        return self.tree.currentItem()


class UStrategyWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        logger.debug("UStrategyWidget.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserStrategy()

    def __createWidgets(self):
        logger.debug("UStrategyWidget.__createWidgets()")
        self.strategy_tree = UStrategyTree(self)

    def __createLayots(self):
        logger.debug("UStrategyWidget.__createLayots()")
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.strategy_tree)
        self.setLayout(vbox)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.strategy_tree.itemChanged.connect(self.__onItemChanged)

    def __loadUserStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__loadUserStrategy()")
        files = Cmd.getFiles(const.STRATEGY_DIR, full_path=True)
        files = Cmd.select(files, ".py")
        for file_path in files:
            name = Cmd.name(file_path)
            s = IStrategy(name, file_path)
            self.strategy_tree.menu.add(s)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)  #__onItemChanged
    def __onItemChanged(self, item: QtWidgets.QTreeWidgetItem, column: int):
        logger.debug(f"{self.__class__.__name__}.__onItemChanged()")
        if isinstance(item, IStrategy):
            return
        # else: item - ассет с измененным чек-стейт
        istrategy = item.parent()
        istrategy.saveAssetSettings()


class UTestWidget(QtWidgets.QWidget):
    """ Signal """
    testChanged = QtCore.pyqtSignal(ITest)
    tlistChanged = QtCore.pyqtSignal(ITradeList)
    tradeChanged = QtCore.pyqtSignal(ITrade)

    def __init__(self, parent=None):
        logger.debug( f"UTestWidget.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__loadUserTests()

    def __createWidgets(self):
        logger.debug( f"UTestWidget.__createWidgets()")
        self.test_tree = UTestTree(self)
        self.trade_tree = UTradeTree(self)
        self.vsplit = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical, self)
        self.vsplit.addWidget(self.test_tree)
        self.vsplit.addWidget(self.trade_tree)

    def __createLayots(self):
        logger.debug( f"UTestWidget.__createLayots()")
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.vsplit)
        self.setLayout(vbox)

    def __connect(self):
        logger.debug( f"UTestWidget.__connect()")
        self.test_tree.clicked.connect(self.__onTestTreeClicked)
        self.trade_tree.clicked.connect(self.__onTradeTreeClicked)

    def __loadUserTests(self):
        logger.debug( f"TestWidget.__loadUserTests()")
        dirs = Cmd.getDirs(const.TEST_DIR, full_path=True)
        for d in dirs:
            itest = ITest.load(d)
            self.test_tree.addTest(itest)

    @QtCore.pyqtSlot()  #__onTestTreeClicked
    def __onTestTreeClicked(self):
        logger.debug(f"{self.__class__.__name__}.__onItemClicked()")
        item = self.test_tree.currentItem()
        if   isinstance(item, ITest):
            while self.trade_tree.takeTopLevelItem(0): pass
            self.testChanged.emit(item)
        elif isinstance(item, ITradeList):
            while self.trade_tree.takeTopLevelItem(0): pass
            self.trade_tree.addTopLevelItems(item)
            self.tlistChanged.emit(item)

    @QtCore.pyqtSlot()  #__onTradeTreeClicked
    def __onTradeTreeClicked(self):
        logger.debug(f"{self.__class__.__name__}.__onTradeClicked()")
        itrade = self.trade_tree.currentItem()
        self.tradeChanged.emit(itrade)


class UChartScene(QtWidgets.QGraphicsScene):
    """ Signal """
    sceneClicked = QtCore.pyqtSignal(Bar)

    def __init__(self, parent=None):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsScene.__init__(self, parent)
        self.__config()
        self.__createWidgets()
        self.__has_chart = False
        self.__has_gtlist = False

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setBackgroundBrush(UColor.BG)

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.label_barinfo = QtWidgets.QLabel("BAR INFO")
        self.label_volinfo = QtWidgets.QLabel("VOL INFO")
        self.label_barinfo.setFont(UFont.MONO)
        self.label_volinfo.setFont(UFont.MONO)
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.label_barinfo)
        vbox.addWidget(self.label_volinfo)
        info = QtWidgets.QWidget()
        info.setLayout(vbox)
        self.info = self.addWidget(info)
        self.info.setScale(0.9)
        p = self.info.palette()
        p.setColor(QtGui.QPalette.ColorRole.Window, UColor.BG)
        self.info.setPalette(p)

    def mouseMoveEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):
        # print(e.pos())
        # print(e.scenePos())
        # print(e.screenPos())
        # print("l", e.lastPos())
        # print("l", e.lastScenePos())
        # print("l", e.lastScreenPos())
        # print("p", e.buttonDownPos(QtCore.Qt.MouseButton.LeftButton))
        # print("p", e.buttonDownScenePos(QtCore.Qt.MouseButton.LeftButton))
        # print("p", e.buttonDownScreenPos(QtCore.Qt.MouseButton.LeftButton))
        if not self.__has_chart:
            return e.ignore()
        bar = self.gchart.barAt(e.scenePos().x())
        if not bar:
            return e.ignore()
        msk_time = bar.dt + const.MSK_TIME_DIF
        msk_time = msk_time.strftime("%Y-%m-%d  %H:%M")
        day = const.DAYS_NAME[bar.dt.weekday()]
        body = bar.body.percent()
        self.label_barinfo.setText(
            f"{msk_time} {day} - Open: {bar.open:<6} High: {bar.high:<6} "
            f"Low: {bar.low:<6} Close: {bar.close:<6} (Body: {body:.2f}%)"
            )
        self.label_volinfo.setText(f"Vol: {bar.vol}")
        return e.ignore()

    def mousePressEvent(self, e: QtWidgets.QGraphicsSceneMouseEvent):
        ...
        return e.ignore()

    def mouseReleaseEvent(self, e):
        view = self.views()[0]
        p = view.mapToScene(0, 0)
        self.info.setPos(p)
        return e.ignore()

    def mouseDoubleClickEvent(self, e):
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

    def setGChart(self, gchart: GChart):
        logger.debug(f"{self.__class__.__name__}.setGChart()")
        self.removeGChart()
        self.setSceneRect(gchart.rect)
        self.addItem(gchart)
        self.gchart = gchart
        self.__has_chart = True
        return True

    def setGTradeList(self, gtlist: GTradeList):
        logger.debug(f"{self.__class__.__name__}.setGTradeList()")
        self.removeGTradeList()
        self.gchart = gtlist.gchart
        self.gtlist = gtlist
        self.__has_chart = True
        self.__has_gtlist = True
        self.setSceneRect(self.gchart.rect)
        self.addItem(self.gchart)
        self.addItem(self.gtlist)

    def removeGChart(self):
        logger.debug(f"{self.__class__.__name__}.removeGChart()")
        if self.__has_chart:
            self.removeItem(self.gchart)
            self.__has_chart = False

    def removeGTradeList(self):
        logger.debug(f"{self.__class__.__name__}.removeGTradeList()")
        if self.__has_chart:
            self.removeItem(self.gchart)
            self.__has_chart = False
        if self.__has_gtlist:
            self.removeItem(self.gtlist)
            self.__has_gtlist = False


class UChartView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        QtWidgets.QGraphicsView.__init__(self, parent)
        # включает режим перетаскивания сцены внутри QGraphicsView
        # мышкой с зажатой левой кнопкой
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
        self.current_gtrade = None

    def wheelEvent(self, e):
        ctrl = QtCore.Qt.KeyboardModifier.ControlModifier
        no = QtCore.Qt.KeyboardModifier.NoModifier
        if e.modifiers() == no:
            if e.angleDelta().y() < 0:
                self.scale(0.9, 1)
            else:
                self.scale(1.1, 1)
        if e.modifiers() == ctrl:
            if e.angleDelta().y() < 0:
                self.scale(1, 0.9)
            else:
                self.scale(1, 1.1)
        self.__resetTranformation()

    def __resetTranformation(self):
        tr = self.transform()
        tr = tr.inverted()[0]
        pos = self.mapToScene(0, 0)
        info = self.scene().info
        info.setTransform(tr)
        info.setPos(pos)
        if self.current_gtrade:
            self.current_gtrade.annotation.setTransform(tr)

    # def mouseMoveEvent(self, e: QtGui.QMouseEvent):
    #     ...
    #     super().mouseMoveEvent(e)
    #     return e.ignore()

    # def mousePressEvent(self, e: QtGui.QMouseEvent):
    #     ...
    #     super().mousePressEvent(e)
    #     return e.ignore()

    def centerOnFirst(self):
        logger.debug(
            f"ChartView.centerOnFirst()"
            )
        scene = self.scene()
        first_bar_item = scene.gchart.childItems()[0]
        pos = first_bar_item.close_pos
        self.centerOn(pos)

    def centerOnLast(self):
        scene = self.scene()
        last_bar_item = scene.gchart.childItems()[-1]
        pos = last_bar_item.close_pos
        self.centerOn(pos)

    def centerOnTrade(self, gtrade: GTrade):
        logger.debug(
            f"ChartView.centerOnTrade(trade)"
            f"trade.dt = {gtrade.dt}"
            )
        if self.current_gtrade is not None:
            self.current_gtrade.hideAnnotation()
        self.current_gtrade = gtrade
        gtrade.showAnnotation()
        pos = gtrade.trade_pos
        self.centerOn(pos)


class UChartWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    def __createWidgets(self):
        self.view = UChartView(self)
        self.scene = UChartScene(self)
        self.view.setScene(self.scene)
        self.btn_asset = QtWidgets.QPushButton("ASSET")
        self.combobox_timeframe1 = QtWidgets.QComboBox()
        self.combobox_timeframe2 = QtWidgets.QComboBox()
        self.dateedit_begin = QtWidgets.QDateEdit()
        self.dateedit_end = QtWidgets.QDateEdit(now().date())
        self.btn_indicator = QtWidgets.QPushButton("Indicator")
        self.btn_mark = QtWidgets.QPushButton("Mark")

    def __createLayots(self):
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.btn_asset)
        hbox1.addWidget(self.combobox_timeframe1)
        hbox1.addWidget(self.combobox_timeframe2)
        hbox1.addWidget(self.dateedit_begin)
        hbox1.addWidget(QtWidgets.QLabel("-"))
        hbox1.addWidget(self.dateedit_end)
        hbox1.addWidget(self.btn_indicator)
        hbox1.addWidget(self.btn_mark)
        hbox1.addStretch()
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addLayout(hbox1)
        vbox.addWidget(self.view)
        self.setLayout(vbox)

    def __connect(self):
        self.combobox_timeframe1.currentTextChanged.connect(
            self.__onTimeframe1Changed)
        self.combobox_timeframe2.currentTextChanged.connect(
            self.__onTimeframe2Changed)
        self.dateedit_begin.dateChanged.connect(self.__onBeginDateChanged)
        self.dateedit_end.dateChanged.connect(self.__onEndDateChanged)
        self.btn_asset.clicked.connect(self.__onButtonAsset)
        self.btn_indicator.clicked.connect(self.__onButtonIndicator)
        self.btn_mark.clicked.connect(self.__onButtonMark)
        self.scene.sceneClicked.connect(self.__onSceneClicked)

    def __initUI(self):
        for timeframe in TimeFrame.ALL:
            self.combobox_timeframe1.addItem(str(timeframe))
            self.combobox_timeframe2.addItem(str(timeframe))
        self.combobox_timeframe1.setCurrentIndex(3)
        self.combobox_timeframe2.setCurrentIndex(2)
        self.dateedit_begin.setMinimumDate(QtCore.QDate(2018, 1, 1))
        self.dateedit_begin.setMaximumDate(now().date() - const.ONE_DAY)
        self.dateedit_end.setMinimumDate(QtCore.QDate(2018, 1, 1))
        self.dateedit_end.setMaximumDate(now().date())

    def __readBeginDate(self):
        date = self.dateedit_begin.date()
        year, month, day = date.year(), date.month(), date.day()
        return datetime(year, month, day, tzinfo=const.UTC)

    def __readEndDate(self):
        date = self.dateedit_end.date()
        year, month, day = date.year(), date.month(), date.day()
        return datetime(year, month, day, tzinfo=const.UTC)

    def __readTimeframe1(self):
        text = self.combobox_timeframe1.currentText()
        return TimeFrame(text)

    def __readTimeframe2(self):
        text = self.combobox_timeframe2.currentText()
        return TimeFrame(text)

    def __setBegin(self, dt):
        self.dateedit_begin.setDate(dt.date())

    def __setEnd(self, dt):
        self.dateedit_end.setDate(dt.date())

    def __setTimeframe1(self, timeframe):
        assert isinstance(timeframe, TimeFrame)
        self.combobox_timeframe1.setCurrentText(str(timeframe))

    def __setTimeframe2(self, timeframe):
        assert isinstance(timeframe, TimeFrame)
        self.combobox_timeframe2.setCurrentText(str(timeframe))

    @QtCore.pyqtSlot(Bar)  #__onSceneClicked
    def __onSceneClicked(self, bar: Bar):
        logger.debug(f"{self.__class__.__name__}.__onSceneClicked()")
        ...

    @QtCore.pyqtSlot()  #__onButtonAsset
    def __onButtonAsset(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonAsset()")
        ...

    @QtCore.pyqtSlot()  #__onButtonIndicator
    def __onButtonIndicator(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonIndicator()")
        ...

    @QtCore.pyqtSlot()  #__onButtonMark
    def __onButtonMark(self):
        logger.debug(f"{self.__class__.__name__}.__onButtonMark()")
        ...

    @QtCore.pyqtSlot()  #__onTimeframe1Changed
    def __onTimeframe1Changed(self):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe1Changed()")
        text = self.combobox_timeframe1.currentText()
        self.__timeframe1 = TimeFrame(text)

    @QtCore.pyqtSlot()  #__onTimeframe2Changed
    def __onTimeframe2Changed(self):
        logger.debug(f"{self.__class__.__name__}.__onTimeframe2Changed()")
        text = self.combobox_timeframe2.currentText()
        self.__timeframe2 = TimeFrame(text)

    @QtCore.pyqtSlot()  #__onBeginDateChanged
    def __onBeginDateChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onBeginDateChanged()")
        ...

    @QtCore.pyqtSlot()  #__onEndDateChanged
    def __onEndDateChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onEndDateChanged()")
        ...

    def showChart(self, iasset: Asset):
        logger.debug(f"{self.__class__.__name__}.showChart()")
        timeframe = self.__readTimeframe1()
        end = now()
        begin = now() - timeframe * Chart.DEFAULT_BARS_COUNT
        gchart = GChart(iasset, timeframe, begin, end)
        self.scene.setGChart(gchart)
        # self.view.scale(1.00, 0.5)
        self.view.centerOnLast()
        self.btn_asset.setText(iasset.ticker)

    def showTradeList(self, itlist: ITradeList):
        logger.debug(f"{self.__class__.__name__}.showTradeList()")
        if itlist.asset is None:
            self.scene.removeGTradeList()
            return
        gtlist = GTradeList(itlist)
        self.__setTimeframe1(TimeFrame("D"))
        self.__setTimeframe2(TimeFrame("5M"))
        self.__setBegin(gtlist.begin)
        self.__setEnd(gtlist.end)
        self.scene.setGTradeList(gtlist)
        # self.view.scale(1.00, 0.25)
        self.view.centerOnFirst()

    def showTrade(self, itrade):
        gtrade = itrade.gtrade
        if gtrade:
            self.view.centerOnTrade(gtrade)

    def clearAll(self):
        logger.debug(
            f"ChartWidget.clearAll()"
            )
        self.scene.removeChart()
        self.scene.removeTradeList()
        self.scene.removeIndicator()
        self.scene.removeMark()
        self.view.resetTransform()


class UReportTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        QtWidgets.QTableWidget.__init__(self, parent)
        self.setFont(UFont.MONO)
        self.rows = 1
        self.setRowCount(1)
        self.current_row = 0
        self.__createHeader()
        self.__setColumnWidth()

    def __setColumnWidth(self):
        self.setColumnWidth(0, 150)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 50)
        self.setColumnWidth(3, 50)
        self.setColumnWidth(4, 50)
        self.setColumnWidth(5, 50)
        self.setColumnWidth(6, 50)
        self.setColumnWidth(7, 50)
        self.setColumnWidth(8, 70)
        self.setColumnWidth(9, 70)
        self.setColumnWidth(10, 70)
        self.setColumnWidth(11, 70)
        self.setColumnWidth(12, 70)
        self.setColumnWidth(13, 100)
        self.setColumnWidth(14, 100)
        self.setColumnWidth(15, 50)

    def __addNewRow(self):
        self.rows += 1
        self.current_row += 1
        self.setRowCount(self.rows)

    def __createHeader(self) -> None:
        header = Report.getHeader()
        self.setColumnCount(len(header))
        self.setHorizontalHeaderLabels(header)

    def __createLine(self, line: str) -> None:
        fields = line.split(";")
        for n, field in enumerate(fields, 0):
            item = QtWidgets.QTableWidgetItem()
            item.setText(field)
            self.setItem(self.current_row, n, item)
        self.__addNewRow()

    def __clear(self):
        self.rows = 1
        self.setRowCount(1)
        self.current_row = 0

    def showTradeListSummary(self, itlist: ITradeList):
        self.__clear()
        df = Report.calculate(itlist)
        for i in df.index:
            for n, val in enumerate(df.loc[i], 0):
                print(n, val)
                item = QtWidgets.QTableWidgetItem()
                if n != 0:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                item.setText(str(val))
                self.setItem(self.current_row, n, item)
            self.__addNewRow()


class ULogWidget(logging.StreamHandler, QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        logging.StreamHandler.__init__(self)
        QtWidgets.QPlainTextEdit.__init__(self, parent)
        self.setReadOnly(True)
        self.setFont(UFont.MONO)
        self.setContentsMargins(0, 0, 0, 0)

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText(msg)
        sb = self.verticalScrollBar()
        end_text = sb.maximum()
        sb.setValue(end_text)
        self.flush()


class UConsoleWidget(QtWidgets.QTabWidget):
    """ TAB """
    LOG = 0
    ERROR = 1
    REPORT = 2

    def __init__(self, parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.__createTest()
        self.__createSandbox()
        self.__createGeneral()
        self.setContentsMargins(0, 0, 0, 0)

    def __createTest(self):
        logger.debug(f"{self.__class__.__name__}.__createTester()")
        self.tester = ULogWidget(self)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
            )
        self.tester.setFormatter(formatter)
        self.tester.setLevel(logging.INFO)
        logger.addHandler(self.tester)
        self.addTab(self.tester, "Tester")
        logger.info("Welcome to AVIN Trade System!")

    def __createSandbox(self):
        logger.debug(f"{self.__class__.__name__}.__createSandbox()")
        self.sandbox = QtWidgets.QLabel("Sandbox")
        self.addTab(self.sandbox, "Sandbox")

    def __createGeneral(self):
        logger.debug(f"{self.__class__.__name__}.__createGeneral()")
        self.general = QtWidgets.QLabel("General")
        self.addTab(self.general, "General")



# -------------------------------- Right tool
class UBrokerWidget(QtWidgets.QWidget):
    """ Signal """
    connectEnabled = QtCore.pyqtSignal(Broker)
    accountSetUp = QtCore.pyqtSignal(IAccount)
    connectDisabled = QtCore.pyqtSignal(Broker)

    def __init__(self, parent):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__loadBrokers()
        self.__current_broker = None
        self.__current_account = None

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.tree = UBrokerTree(self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(self.tree)
        self.setLayout(vbox)

    def __loadBrokers(self):
        logger.debug( f"UBrokerWidget.__loadBrokers()")
        dirs = Cmd.getDirs(const.BROKER_DIR, full_path=True)
        for d in dirs:
            name = Cmd.name(d)
            if name == "Sandbox":
                ibroker = ISandbox(d)
            if name == "Tinkoff":
                ibroker = ITinkoff(d)
            self.tree.addTopLevelItem(ibroker)
        self.tree.expandAll()

    def currentToken(self):
        logger.debug( f"UBrokerWidget.currentToken()")
        return self.tree.current_itoken

    def currentBroker(self):
        logger.debug( f"UBrokerWidget.currentBroker()")
        return self.tree.current_ibroker

    def currentAccount(self):
        logger.debug( f"UBrokerWidget.currentBroker()")
        return self.tree.current_account


class UOrderDialog(QtWidgets.QDialog):
    class UAssetInfo(QtWidgets.QWidget):
        def __init__(self, parent=None):
            logger.debug(f"{self.__class__.__name__}.__init__()")
            QtWidgets.QWidget.__init__(self, parent)
            self.current_asset = None
            self.__createWidgets()
            self.__createLayots()
            self.__config()
            self.current_asset = None

        def __createWidgets(self):
            logger.debug(f"{self.__class__.__name__}.__createWidgets()")
            L = QtWidgets.QLabel
            self.asset = L("ASSET", self)
            self.margin = L("x5 x5", self)
            self.price = L("0.00 rub", self)

        def __createLayots(self):
            logger.debug(f"{self.__class__.__name__}.__createLayots()")
            hbox = QtWidgets.QHBoxLayout()
            hbox.addWidget(self.asset)
            hbox.addWidget(self.margin)
            hbox.addWidget(self.price)
            hbox.setContentsMargins(0, 0, 0, 0)
            self.setLayout(hbox)

        def __config(self):
            logger.debug(f"{self.__class__.__name__}.__config()")
            sp = QtWidgets.QSizePolicy.Policy.Minimum
            self.setSizePolicy(sp, sp)

        def setAsset(self, asset: Asset):
            logger.debug(f"{self.__class__.__name__}.__setAsset({asset})")
            self.current_asset = asset
            self.asset.setText(asset.ticker)
            self.margin.setText("none-none")
            self.price.setText(str(asset.last_price))

        def updateWidget(self):
            logger.debug(f"{self.__class__.__name__}.updateWidget()")


    class UOrderType(QtWidgets.QToolBar):
        def __init__(self, parent=None):
            logger.debug(f"{self.__class__.__name__}.__init__()")
            QtWidgets.QToolBar.__init__(self, parent)
            self.__config()
            self.__createActions()
            self.__configButtons()
            self.__connect()
            self.current_type = None

        def __config(self):
            logger.debug(f"{self.__class__.__name__}.__config()")
            p = self.palette()
            p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#484848"))
            self.setPalette(p)

        def __createActions(self):
            logger.debug(f"{self.__class__.__name__}.__createActions()")
            self.market = QtGui.QAction("Market", self)
            self.limit = QtGui.QAction("Limit", self)
            self.stop = QtGui.QAction("Stop", self)
            self.wait = QtGui.QAction("Wait", self)
            self.trailing = QtGui.QAction("Trailing", self)
            self.addAction(self.market)
            self.addAction(self.limit)
            self.addAction(self.stop)
            self.addAction(self.wait)
            self.addAction(self.trailing)

        def __configButtons(self):
            self.widgetForAction(self.market).setCheckable(True)
            self.widgetForAction(self.limit).setCheckable(True)
            self.widgetForAction(self.stop).setCheckable(True)
            self.widgetForAction(self.wait).setCheckable(True)
            self.widgetForAction(self.trailing).setCheckable(True)

        def __connect(self):
            logger.debug(f"{self.__class__.__name__}.__connect()")
            self.actionTriggered.connect(self.__onTriggered)
            self.market.triggered.connect(self.__onMarket)
            self.limit.triggered.connect(self.__onLimit)
            self.stop.triggered.connect(self.__onStop)
            self.wait.triggered.connect(self.__onWait)
            self.trailing.triggered.connect(self.__onTrailing)

        def __uncheckActions(self):
            for i in self.actions():
                btn = self.widgetForAction(i)
                btn.setChecked(False)

        @QtCore.pyqtSlot(QtGui.QAction)
        def __onTriggered(self, action: QtGui.QAction):
            self.__uncheckActions()
            btn = self.widgetForAction(action)
            state = btn.isChecked()
            btn.setChecked(not state)

        @QtCore.pyqtSlot()  #__onMarket
        def __onMarket(self):
            logger.debug(f"{self.__class__.__name__}.__onMarket()")
            self.current_type = Order.Type.MARKET
            self.parent().updateWidget()

        @QtCore.pyqtSlot()  #__onLimit
        def __onLimit(self):
            logger.debug(f"{self.__class__.__name__}.___onLimit()")
            self.current_type = Order.Type.LIMIT
            self.parent().updateWidget()

        @QtCore.pyqtSlot()  #__onStop
        def __onStop(self):
            logger.debug(f"{self.__class__.__name__}.___onLimit()")
            self.current_type = Order.Type.STOP
            self.parent().updateWidget()

        @QtCore.pyqtSlot()  #__onWait
        def __onWait(self):
            logger.debug(f"{self.__class__.__name__}.___onWait()")
            self.current_type = Order.Type.WAIT
            self.parent().updateWidget()

        @QtCore.pyqtSlot()  #__onTrailing
        def __onTrailing(self):
            logger.debug(f"{self.__class__.__name__}.___onTrailing()")
            self.current_type = Order.Type.TRAILING
            self.parent().updateWidget()


    class UOrderPrice(QtWidgets.QWidget):
        def __init__(self, parent=None):
            logger.debug(f"{self.__class__.__name__}.__init__()")
            QtWidgets.QGroupBox.__init__(self, parent)
            self.__createWidgets()
            self.__createLayots()
            self.__connect()
            self.__config()

        def __createWidgets(self):
            logger.debug(f"{self.__class__.__name__}.__createWidgets()")
            self.market_check = QtWidgets.QCheckBox("Market price", self)
            self.market_price = QtWidgets.QDoubleSpinBox(self)
            self.active_check = QtWidgets.QCheckBox("Price", self)
            self.active_price = QtWidgets.QDoubleSpinBox(self)
            self.execute_check = QtWidgets.QCheckBox("Execute price ", self)
            self.execute_price = QtWidgets.QDoubleSpinBox(self)
            self.timeout_check = QtWidgets.QCheckBox("Timeout", self)
            self.timeout_val = QtWidgets.QTimeEdit(time(1, 5), self)

        def __createLayots(self):
            logger.debug(f"{self.__class__.__name__}.__createLayots()")
            hbox1 = QtWidgets.QHBoxLayout()
            hbox1.addWidget(self.market_check)
            hbox1.addWidget(self.market_price)
            hbox1.addWidget(self.active_check)
            hbox1.addWidget(self.active_price)
            hbox2 = QtWidgets.QHBoxLayout()
            hbox2.addWidget(self.execute_check)
            hbox2.addWidget(self.execute_price)
            hbox3 = QtWidgets.QHBoxLayout()
            hbox3.addWidget(self.timeout_check)
            hbox3.addWidget(self.timeout_val)
            vbox = QtWidgets.QVBoxLayout()
            vbox.addLayout(hbox1)
            vbox.addLayout(hbox2)
            vbox.addLayout(hbox3)
            self.setLayout(vbox)

        def __connect(self):
            logger.debug(f"{self.__class__.__name__}.__connect()")
            self.execute_check.stateChanged.connect(self.__onCheckExecPrice)
            self.timeout_check.stateChanged.connect(self.__onCheckTimeout)

        def __config(self):
            logger.debug(f"{self.__class__.__name__}.__config()")
            self.market_check.setMaximumWidth(128)
            self.market_price.setRange(0, 1000000000)
            self.market_price.setMinimumWidth(100)
            self.market_price.setReadOnly(True)
            self.active_check.setMaximumWidth(128)
            self.active_price.setRange(0, 1000000000)
            self.active_price.setMinimumWidth(100)
            self.execute_check.setMaximumWidth(128)
            self.execute_price.setRange(0, 1000000000)
            self.execute_price.setSpecialValueText("market")
            self.execute_price.setValue(0)
            self.execute_price.setMinimumWidth(128)
            self.timeout_val.setMinimumWidth(100)
            self.timeout_check.setMaximumWidth(128)
            sp = QtWidgets.QSizePolicy.Policy.Minimum
            self.setSizePolicy(sp, sp)

        def __setStep(self):
            logger.debug(f"{self.__class__.__name__}.__setStep()")
            step = self.parent().currentAsset().min_price_step
            precision = len(str(step).split(".")[1])
            self.active_price.setSingleStep(step)
            self.active_price.setDecimals(precision)
            self.execute_price.setSingleStep(step)
            self.execute_price.setDecimals(precision)

        @QtCore.pyqtSlot()  #__forMarket
        def __forMarket(self):
            logger.debug(f"{self.__class__.__name__}.__onMarket()")
            self.market_check.setVisible(True)
            self.market_check.setEnabled(False)
            self.market_check.setChecked(True)
            self.market_price.setVisible(True)
            self.active_check.setVisible(False)
            self.active_check.setEnabled(False)
            self.active_check.setChecked(False)
            self.active_price.setVisible(False)
            self.execute_check.setChecked(False)
            self.execute_check.setEnabled(False)
            self.execute_price.setEnabled(False)
            self.timeout_check.setChecked(False)
            self.timeout_check.setEnabled(False)
            self.timeout_val.setEnabled(False)
            self.current_type = Order.Type.MARKET
            asset = self.parent().currentAsset()
            if asset:
                self.market_price.setSpecialValueText(f"~{asset.last_price}")

        @QtCore.pyqtSlot()  #__forLimit
        def __forLimit(self):
            logger.debug(f"{self.__class__.__name__}.___onLimit()")
            self.market_check.setVisible(False)
            self.market_check.setEnabled(False)
            self.market_check.setChecked(False)
            self.market_price.setVisible(False)
            self.active_check.setVisible(True)
            self.active_check.setEnabled(True)
            self.active_check.setChecked(True)
            self.active_price.setVisible(True)
            self.active_price.setFocus(Qt.FocusReason.MouseFocusReason)
            self.execute_check.setChecked(False)
            self.execute_check.setEnabled(False)
            self.execute_price.setEnabled(False)
            self.timeout_check.setEnabled(False)
            self.timeout_check.setChecked(False)
            self.timeout_val.setEnabled(False)
            self.current_type = Order.Type.LIMIT

        @QtCore.pyqtSlot()  #__forStop
        def __forStop(self):
            logger.debug(f"{self.__class__.__name__}.___onLimit()")
            self.market_check.setVisible(False)
            self.market_check.setEnabled(False)
            self.market_check.setChecked(False)
            self.market_price.setVisible(False)
            self.active_check.setVisible(True)
            self.active_check.setEnabled(True)
            self.active_check.setChecked(True)
            self.active_price.setVisible(True)
            self.active_price.setFocus(Qt.FocusReason.MouseFocusReason)
            self.execute_check.setEnabled(True)
            self.execute_check.setChecked(False)
            self.execute_price.setEnabled(False)
            self.timeout_check.setEnabled(False)
            self.timeout_check.setChecked(False)
            self.timeout_val.setEnabled(False)
            self.current_type = Order.Type.STOP

        @QtCore.pyqtSlot()  #__forWait
        def __forWait(self):
            logger.debug(f"{self.__class__.__name__}.___onWait()")
            self.market_check.setVisible(False)
            self.market_check.setEnabled(False)
            self.market_check.setChecked(False)
            self.market_price.setVisible(False)
            self.active_check.setVisible(True)
            self.active_check.setEnabled(True)
            self.active_check.setChecked(True)
            self.active_price.setVisible(True)
            self.active_price.setFocus(Qt.FocusReason.MouseFocusReason)
            self.execute_check.setEnabled(True)
            self.execute_check.setChecked(False)
            self.execute_price.setEnabled(False)
            self.timeout_check.setEnabled(True)
            self.timeout_check.setChecked(False)
            self.timeout_val.setEnabled(False)
            self.current_type = Order.Type.WAIT

        @QtCore.pyqtSlot()  #__forTrailing
        def __forTrailing(self):
            logger.debug(f"{self.__class__.__name__}.___onTrailing()")
            self.current_type = Order.Type.TRAILING

        @QtCore.pyqtSlot()  #__onCheckExecPrice
        def __onCheckExecPrice(self):
            logger.debug(f"{self.__class__.__name__}.__onCheckExecPrice()")
            state = self.execute_check.isChecked()
            self.execute_price.setEnabled(state)
            if state:
                val = self.active_price.value()
                self.execute_price.setValue(val)
            else:
                val = self.execute_price.minimum()
                self.execute_price.setValue(val)

        @QtCore.pyqtSlot()  #__onCheckTimeout
        def __onCheckTimeout(self):
            logger.debug(f"{self.__class__.__name__}.__onCheckTimeout()")
            state = self.timeout_check.isChecked()
            self.timeout_val.setEnabled(state)

        def setPrice(self, price):
            logger.debug(f"{self.__class__.__name__}.__setPrice()")
            last_price = self.parent().currentAsset().last_price
            if price is None:
                price = last_price
            self.active_price.setValue(price)
            if self.execute_check.isChecked():
                self.execute_price.setValue(price)
            self.market_price.setSpecialValueText(f"~{last_price}")
            self.__setStep()

        def updateWidget(self):
            order_type = self.parent().currentType()
            types = {
                Order.Type.MARKET:   self.__forMarket,
                Order.Type.LIMIT:    self.__forLimit,
                Order.Type.STOP:     self.__forStop,
                Order.Type.WAIT:     self.__forWait,
                Order.Type.TRAILING: self.__forTrailing,
                }
            types[order_type]()


    class UQuantity(QtWidgets.QGroupBox):
        def __init__(self, parent=None):
            logger.debug(f"{self.__class__.__name__}.__init__()")
            QtWidgets.QWidget.__init__(self, parent)
            self.__current_asset = None
            self.__config()
            self.__createWidgets()
            self.__createLayots()

        def __createWidgets(self):
            logger.debug(f"{self.__class__.__name__}.__createWidgets()")
            self.lots = QtWidgets.QSpinBox(self)
            self.lots.setRange(1, 1_000_000)
            self.lots_label = QtWidgets.QLabel("Lots", self)
            self.quantity = QtWidgets.QSpinBox(self)
            self.quantity.setRange(1, 1_000_000_000)
            self.quantity.setReadOnly(True)
            self.quantity_label = QtWidgets.QLabel("Quantity", self)
            self.amount = QtWidgets.QDoubleSpinBox(self)
            self.amount.setRange(1, 1_000_000_000)
            self.amount.setReadOnly(True)
            self.amount_label = QtWidgets.QLabel("Amount", self)
            self.max_buy = QtWidgets.QLabel("Max buy: n (N)", self)
            self.max_sell = QtWidgets.QLabel("Max sell: n (N)", self)

        def __createLayots(self):
            logger.debug(f"{self.__class__.__name__}.__createLayots()")
            hbox = QtWidgets.QHBoxLayout()
            hbox.addWidget(self.max_buy)
            hbox.addWidget(self.max_sell)
            grid = QtWidgets.QGridLayout()
            grid.addWidget(self.lots_label,     0, 0)
            grid.addWidget(self.quantity_label, 0, 1)
            grid.addWidget(self.amount_label,   0, 2)
            grid.addWidget(self.lots,           1, 0)
            grid.addWidget(self.quantity,       1, 1)
            grid.addWidget(self.amount,         1, 2)
            grid.addLayout(hbox,                2, 0, 1, 3)
            self.setLayout(grid)

        def __config(self):
            logger.debug(f"{self.__class__.__name__}.__config()")
            sp = QtWidgets.QSizePolicy.Policy.Minimum
            self.setSizePolicy(sp, sp)

        def updateWidget(self):
            asset = self.parent().currentAsset()
            if asset:
                price = self.parent().currentPrice()
                lots = self.lots.value()
                quantity = int(asset.lot * lots)
                amount = price * quantity
                self.lots_label.setText(f"Lots x{asset.lot}")
                self.quantity.setValue(quantity)
                self.amount.setValue(amount)


    class UStopTake(QtWidgets.QWidget):
        def __init__(self, parent=None):
            logger.debug(f"{self.__class__.__name__}.__init__()")
            QtWidgets.QWidget.__init__(self, parent)
            self.__createStopGroup()
            self.__createTakeGroup()
            self.__createLabels()
            self.__createLayots()
            self.__config()

        def __createStopGroup(self):
            logger.debug(f"{self.__class__.__name__}.__createStopGroup()")
            self.stop_percent = QtWidgets.QDoubleSpinBox(self)
            self.stop_price = QtWidgets.QDoubleSpinBox(self)
            self.stop_change = QtWidgets.QDoubleSpinBox(self)
            stop = QtWidgets.QVBoxLayout()
            stop.addWidget(self.stop_percent)
            stop.addWidget(self.stop_price)
            stop.addWidget(self.stop_change)
            self.group_stop = QtWidgets.QGroupBox("stop-loss", self)
            self.group_stop.setLayout(stop)
            self.group_stop.setCheckable(True)
            self.group_stop.setChecked(False)

        def __createTakeGroup(self):
            logger.debug(f"{self.__class__.__name__}.__createTakeGroup()")
            self.take_percent = QtWidgets.QDoubleSpinBox(self)
            self.take_price = QtWidgets.QDoubleSpinBox(self)
            self.take_change = QtWidgets.QDoubleSpinBox(self)
            take = QtWidgets.QVBoxLayout()
            take.addWidget(self.take_percent)
            take.addWidget(self.take_price)
            take.addWidget(self.take_change)
            self.group_take = QtWidgets.QGroupBox("take-profit", self)
            self.group_take.setLayout(take)
            self.group_take.setCheckable(True)
            self.group_take.setChecked(False)

        def __createLabels(self):
            logger.debug(f"{self.__class__.__name__}.__createLabels()")
            L = QtWidgets.QLabel
            labels = QtWidgets.QVBoxLayout()
            labels.addWidget(L("<center>%</center>", self))
            labels.addWidget(L("<center>Price</center>", self))
            labels.addWidget(L("<center>Change</center>", self))
            self.group_labels = QtWidgets.QGroupBox(" ", self)
            self.group_labels.setLayout(labels)

        def __createLayots(self):
            logger.debug(f"{self.__class__.__name__}.__createLayots()")
            grid = QtWidgets.QGridLayout()
            grid.addWidget(self.group_stop, 0, 0)
            grid.addWidget(self.group_labels, 0, 1)
            grid.addWidget(self.group_take, 0, 2)
            grid.setContentsMargins(0, 0, 0, 0)
            self.setLayout(grid)

        def __config(self):
            logger.debug(f"{self.__class__.__name__}.__config()")
            sp = QtWidgets.QSizePolicy.Policy.Minimum
            self.setSizePolicy(sp, sp)


    class UBuySellButton(QtWidgets.QWidget):
        def __init__(self, parent=None):
            logger.debug(f"{self.__class__.__name__}.__init__()")
            QtWidgets.QWidget.__init__(self, parent)
            self.__createWidgets()
            self.__createLayots()
            self.__configButtons()
            self.__connection = False

        def __createWidgets(self):
            logger.debug(f"{self.__class__.__name__}.__createWidgets()")
            self.buy = QtWidgets.QPushButton("Buy ____ lots\n0.00 rub", self)
            self.sell = QtWidgets.QPushButton("Sell ____ lots\n0.00 rub", self)

        def __createLayots(self):
            logger.debug(f"{self.__class__.__name__}.__createLayots()")
            grid = QtWidgets.QGridLayout()
            grid.addWidget(self.buy, 0, 0)
            grid.addWidget(self.sell, 0, 1)
            grid.setContentsMargins(0, 0, 0, 0)
            self.setLayout(grid)

        def __configButtons(self):
            logger.debug(f"{self.__class__.__name__}.__config()")
            self.buy.setStyleSheet(
                "QPushButton {"
                    "color: white;"
                    "padding: 1px;"
                    "border-width: 0px;"
                    "border-radius: 3px;"
                    "background-color: #AA98BB6C;"
                    "}"
                "QPushButton:hover {"
                    "color: white;"
                    "background-color: #CC98BB6C;"
                    "}"
                "QPushButton:pressed {"
                    "color: white;"
                    "background-color: #98BB6C;"
                    "}"
                "QPushButton:disabled {"
                    "color: #848388;"
                    "border-width: 1px;"
                    "border-style: solid;"
                    "border-color: #5d5e60;"
                    "background-color: #373737;"
                    "}"
                )
            self.sell.setStyleSheet(
                "QPushButton {"
                    "color: white;"
                    "padding: 1px;"
                    "border-width: 0px;"
                    "border-radius: 3px;"
                    "background-color: #AAFF5D62;"
                    "}"
                "QPushButton:hover {"
                    "color: white;"
                    "background-color: #CCFF5D62;"
                    "}"
                "QPushButton:pressed {"
                    "color: white;"
                    "background-color: #FF5D62"
                    "}"
                "QPushButton:disabled {"
                    "color: #848388;"
                    "border-style: solid;"
                    "border-width: 1px;"
                    "border-color: #5d5e60;"
                    "background-color: #373737;"
                    "}"
                )

        def updateWidget(self):
            logger.debug(f"{self.__class__.__name__}.updateWidget()")
            account = self.parent().currentAccount()
            asset = self.parent().currentAsset()
            if account is not None and asset is not None:
                self.buy.setEnabled(True)
                self.sell.setEnabled(True)
            else:
                self.buy.setEnabled(False)
                self.sell.setEnabled(False)
            lots = self.parent().currentLots()
            price = self.parent().currentPrice()
            ticker = asset.ticker if asset else "____"
            amount = lots * asset.lot * price if asset else 0.0
            self.buy.setText(f"Buy {ticker} {lots} lots\n {amount:.2f} rub")
            self.sell.setText(f"Sell {ticker} {lots} lots\n {amount:.2f} rub")



    """ Signal """
    newOrder = QtCore.pyqtSignal(Order)

    def __init__(self, parent):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QDialog.__init__(self, parent)
        self.__current_account = None
        self.__current_asset = None
        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    def __config(self):
        logger.debug(f"{self.__class__.__name__}.__config()")
        self.setFont(UFont.MONO)

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.asset = UOrderDialog.UAssetInfo(self)
        self.type = UOrderDialog.UOrderType(self)
        self.price = UOrderDialog.UOrderPrice(self)
        self.quantity = UOrderDialog.UQuantity(self)
        self.stop_take = UOrderDialog.UStopTake(self)
        self.button = UOrderDialog.UBuySellButton(self)

    def __createLayots(self):
        logger.debug(f"{self.__class__.__name__}.__createLayots()")
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.asset)
        vbox.addWidget(self.type)
        vbox.addWidget(self.price)
        vbox.addWidget(self.quantity)
        vbox.addWidget(self.stop_take)
        vbox.addWidget(self.button)
        vbox.addStretch()
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    def __connect(self):
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.price.market_price.valueChanged.connect(self.__onPriceChanged)
        self.price.active_price.valueChanged.connect(self.__onPriceChanged)
        self.price.execute_price.valueChanged.connect(self.__onPriceChanged)
        self.quantity.lots.valueChanged.connect(self.__onLotsChanged)
        self.button.buy.clicked.connect(self.__onBuy)
        self.button.sell.clicked.connect(self.__onSell)

    def __initUI(self):
        logger.debug(f"{self.__class__.__name__}.__initUI()")
        # self.button.buy.setDisabled(True)
        # self.button.sell.setDisabled(True)
        self.type.market.trigger()

    def __createBuyOrder(self):
        logger.debug(f"{self.__class__.__name__}.__createBuyOrder()")
        iorder = IOrder(
            signal= Signal.Type.MANUAL,
            TYPE= self.currentType(),
            direction= Order.Direction.BUY,
            asset= self.currentAsset(),
            lots= self.currentLots(),
            price= self.currentActivePrice(),
            exec_price= self.currentExecutePrice(),
            timeout= self.currentTimeout(),
            status= Order.Status.NEW,
            parent= None,
            )
        return iorder

    def __createSellOrder(self):
        logger.debug(f"{self.__class__.__name__}.__createSellOrder()")
        iorder = IOrder(
            signal= Signal.Type.MANUAL,
            TYPE= self.currentType(),
            direction= Order.Direction.SELL,
            asset= self.currentAsset(),
            lots= self.currentLots(),
            price= self.currentActivePrice(),
            exec_price= self.currentExecutePrice(),
            timeout= self.currentTimeout(),
            status= Order.Status.NEW,
            parent= None,
            )
        return iorder

    @QtCore.pyqtSlot()  #__onPriceChanged
    def __onPriceChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onPriceChanged()")
        self.quantity.updateWidget()
        self.button.updateWidget()

    @QtCore.pyqtSlot()  #__onLotsChanged
    def __onLotsChanged(self):
        logger.debug(f"{self.__class__.__name__}.__onLotsChanged()")
        self.quantity.updateWidget()
        self.button.updateWidget()

    @QtCore.pyqtSlot()  #__onBuy
    def __onBuy(self):
        logger.debug(f"{self.__class__.__name__}.__onBuy()")
        order = self.__createBuyOrder()
        self.newOrder.emit(order)
        self.__current_account.post(order)

    @QtCore.pyqtSlot()  #__onSell
    def __onSell(self):
        logger.debug(f"{self.__class__.__name__}.__onSell()")
        order = self.__createSellOrder()
        self.newOrder.emit(order)
        self.__current_account.post(order)

    def setAsset(self, asset, price=None):
        logger.debug(f"{self.__class__.__name__}.setAsset()")
        self.__current_asset = asset
        self.asset.setAsset(asset)
        self.price.setPrice(price)
        self.updateWidget()

    def connectAccount(self, iaccount):
        logger.debug(f"{self.__class__.__name__}.connectAccount()")
        self.__current_account = iaccount
        self.updateWidget()

    def disconnectAccount(self, iaccount):
        logger.debug(f"{self.__class__.__name__}.disconnectAccount()")
        self.__current_account = None
        self.updateWidget()

    def updateWidget(self):
        logger.debug(f"{self.__class__.__name__}.updateWidget()")
        self.asset.updateWidget()
        self.price.updateWidget()
        self.quantity.updateWidget()
        self.button.updateWidget()

    def currentAccount(self):
        logger.debug(f"{self.__class__.__name__}.currentAccount()")
        return self.__current_account

    def currentAsset(self):
        logger.debug(f"{self.__class__.__name__}.currentAsset()")
        return self.asset.current_asset

    def currentType(self):
        logger.debug(f"{self.__class__.__name__}.currentType()")
        return self.type.current_type

    def currentPrice(self):
        if self.currentAsset() is None:
            return
        if self.currentType() == Order.Type.MARKET:
            price = self.currentAsset().last_price
        elif self.price.execute_check.isChecked():
            price = float(self.price.execute_price.cleanText())
        elif self.price.active_check.isChecked():
            price = float(self.price.active_price.cleanText())
        else:
            price = 0.0
        return price

    def currentActivePrice(self):
        if self.price.active_check.isChecked():
            price = float(self.price.active_price.cleanText())
            return price
        else:
            return None

    def currentExecutePrice(self):
        if self.price.execute_check.isChecked():
            price = float(self.price.execute_price.cleanText())
            return price
        else:
            return None

    def currentTimeout(self):
        if self.price.timeout_check.isChecked():
            timeout = self.price.timeout_val.time
            print("TODO: РАЗБЕРИСЬ С ВИДЖЕТОМ ВРЕМЕНИ")
            print(timeout)
            return None
        else:
            return None

    def currentLots(self):
        logger.debug(f"{self.__class__.__name__}.currentLots()")
        return self.quantity.lots.value()


class UPortfolioWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__current_account = None

    def __createWidgets(self):
        self.tree = UPortfolioTree(self)

    def __createLayots(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.tree)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    def setAccount(self, acc: IAccount):
        self.__current_account = acc
        self.updateWidget()

    def updateWidget(self):
        if self.__current_account:
            p = self.__current_account.portfolio()
            self.tree.clear()
            self.tree.addTopLevelItem(p)
            self.tree.expandAll()


class UOperationWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__current_account = None

    def __createWidgets(self):
        self.tree = UOperationTree(self)

    def __createLayots(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.tree)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    def setAccount(self, acc: IAccount):
        self.__current_account = acc
        self.updateWidget()

    def updateWidget(self):
        if self.__current_account:
            op = self.__current_account.operations()
            self.tree.clear()
            self.tree.addTopLevelItems(op)


class UOrderWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.__createWidgets()
        self.__createLayots()
        self.__current_account = None

    def __createWidgets(self):
        self.tree = UOrderTree(self)

    def __createLayots(self):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.tree)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    def setAccount(self, acc: IAccount):
        self.__current_account = acc
        self.updateWidget()

    def updateWidget(self):
        if self.__current_account:
            orders = self.__current_account.orders()
            self.tree.clear()
            self.tree.addTopLevelItems(orders)

    def currentAccount(self):
        logger.debug(f"{self.__class__.__name__}.currentAccount()")
        return self.__current_account


class UAccountWidget(QtWidgets.QTabWidget):
    """ TAB """
    PORTFOLIO = 0
    ERROR = 1
    REPORT = 2

    def __init__(self, parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.__createWidgets()
        self.setContentsMargins(0, 0, 0, 0)

    def __createWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")
        self.portfolio = UPortfolioWidget(self)
        self.operation = UOperationWidget(self)
        self.order = UOrderWidget(self)
        self.addTab(self.portfolio, "Portfolio")
        self.addTab(self.operation, "Operation")
        self.addTab(self.order, "Order")

    def connectAccount(self, acc):
        logger.debug(f"{self.__class__.__name__}.connectAccount()")
        self.__current_account = acc
        self.portfolio.setAccount(acc)
        self.operation.setAccount(acc)
        self.order.setAccount(acc)

    def currentAccount(self):
        logger.debug(f"{self.__class__.__name__}.currentAccount()")
        return self.__current_account



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        # self.__createMdiArea()
        # self.__configMdiArea()
        self.__createToolBar()
        self.__createLeftWidgets()
        self.__createCenterWidgets()
        self.__createRightWidgets()
        self.__createSplitter()
        self.__setWidgetSize()
        self.__connect()
        self.__config()
        self.__initUI()

    # def __createMdiArea(self):
    #     self.area = QtWidgets.QMdiArea(self)
    #     self.tab1 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab2 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab3 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab4 = QtWidgets.QMdiSubWindow(self.area)
    #     self.tab5 = QtWidgets.QMdiSubWindow(self.area)
    #     self.area.addSubWindow(self.tab1)
    #     self.area.addSubWindow(self.tab2)
    #     self.area.addSubWindow(self.tab3)
    #     self.area.addSubWindow(self.tab4)
    #     self.area.addSubWindow(self.tab5)
    #     self.tab1.setWindowTitle("Tester")
    #     self.tab2.setWindowTitle("Sandbox")
    #     self.tab3.setWindowTitle("General")
    #     self.tab4.setWindowTitle("Terminal")
    #     self.tab5.setWindowTitle("Documentation")
    #
    # def __configMdiArea(self):
    #     self.area.setViewMode(QtWidgets.QMdiArea.ViewMode.TabbedView)
    #     self.area.setTabsMovable(True)
    #     self.area.setTabsClosable(False)
    #     self.area.setActiveSubWindow(self.tab1)
    #
    def __createToolBar(self):
        self.ltool = UToolLeft(self)
        self.ltool.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.ltool)
        self.rtool = UToolRight(self)
        self.rtool.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.rtool)

    def __createLeftWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createLeftWidgets()")
        self.widget_data = UDataWidget(self)
        self.widget_data.hide()
        self.widget_asset = UAssetWidget(self)
        self.widget_asset.hide()
        self.widget_strategy = UStrategyWidget(self)
        self.widget_strategy.hide()
        self.widget_test = UTestWidget(self)
        self.widget_test.hide()

    def __createCenterWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createCenterWidgets()")
        self.widget_chart = UChartWidget(self)
        self.widget_chart.hide()
        self.widget_report = UReportTable(self)
        self.widget_report.hide()
        self.widget_console = UConsoleWidget(self)
        self.widget_console.hide()
        self.widget_account = UAccountWidget(self)
        self.widget_account.hide()

    def __createRightWidgets(self):
        logger.debug(f"{self.__class__.__name__}.__createRightWidgets()")
        self.widget_broker = UBrokerWidget(self)
        self.widget_broker.hide()
        self.widget_order = UOrderDialog(self)
        self.widget_order.hide()

    def __createSplitter(self):
        logger.debug(f"{self.__class__.__name__}.__createSplitter()")
        # left
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.widget_data)
        self.splitter.addWidget(self.widget_asset)
        self.splitter.addWidget(self.widget_strategy)
        self.splitter.addWidget(self.widget_test)
        #center
        self.vsplit = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.vsplit.addWidget(self.widget_chart)
        self.vsplit.addWidget(self.widget_account)
        self.vsplit.addWidget(self.widget_report)
        self.vsplit.addWidget(self.widget_console)
        self.splitter.addWidget(self.vsplit)
        # right
        self.splitter.addWidget(self.widget_order)
        self.splitter.addWidget(self.widget_broker)

    def __setWidgetSize(self):
        logger.debug(f"{self.__class__.__name__}.__setWidgetSize()")
        self.splitter.setStretchFactor(0, 10)  # data
        self.splitter.setStretchFactor(1, 5)   # asset
        self.splitter.setStretchFactor(2, 5)   # strategy
        self.splitter.setStretchFactor(3, 10)  # test
        self.splitter.setStretchFactor(4, 13)  # central widgets
        self.vsplit.setStretchFactor(0, 10)  # chart
        self.vsplit.setStretchFactor(1, 2)  # account
        self.vsplit.setStretchFactor(2, 1)  # report
        self.vsplit.setStretchFactor(3, 1)  # console
        self.splitter.setStretchFactor(5, 5)  # order
        self.splitter.setStretchFactor(6, 5)  # broker

    def __connect(self):
        # left tools
        self.ltool.data.triggered.connect(self.__onData)
        self.ltool.asset.triggered.connect(self.__onAsset)
        self.ltool.chart.triggered.connect(self.__onChart)
        self.ltool.strategy.triggered.connect(self.__onStrategy)
        self.ltool.test.triggered.connect(self.__onTest)
        self.ltool.report.triggered.connect(self.__onReport)
        self.ltool.console.triggered.connect(self.__onConsole)
        self.ltool.shutdown.triggered.connect(self.__onShutdown)
        # right tools
        self.rtool.broker.triggered.connect(self.__onBroker)
        self.rtool.account.triggered.connect(self.__onAccount)
        self.rtool.order.triggered.connect(self.__onOrder)
        # widget signals
        self.widget_asset.assetChanged.connect(self.__onAssetChanged)
        self.widget_test.tlistChanged.connect(self.__onTradeListChanged)
        self.widget_test.tradeChanged.connect(self.__onTradeChanged)
        self.widget_broker.connectEnabled.connect(self.__onConnect)
        self.widget_broker.connectDisabled.connect(self.__onDisconnect)
        self.widget_broker.accountSetUp.connect(self.__onAccountSetUp)

    def __config(self):
        self.setWindowTitle("AVIN  -  Ars  Vincere")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        self.setCentralWidget(self.splitter)
        self.splitter.setContentsMargins(5, 5, 5, 5)
        self.splitter.setHandleWidth(10)
        self.vsplit.setHandleWidth(10)

    def __initUI(self):
        self.ltool.chart.trigger()
        self.ltool.test.trigger()
        self.ltool.console.trigger()
        # self.rtool.broker.trigger()
        # self.rtool.account.trigger()
        # self.rtool.order.trigger()
        # iasset = self.widget_asset.currentAsset()
        # self.widget_chart.showChart(iasset)
        # self.widget_order.setAsset(iasset)

    @QtCore.pyqtSlot()  #__onData
    def __onData(self):
        logger.debug(f"{self.__class__.__name__}.__onData()")
        state = self.widget_data.isVisible()
        self.widget_data.setVisible(not state)

    @QtCore.pyqtSlot()  #__onAsset
    def __onAsset(self):
        logger.debug(f"{self.__class__.__name__}.__onAsset()")
        state = self.widget_asset.isVisible()
        self.widget_asset.setVisible(not state)

    @QtCore.pyqtSlot()  #__onChart
    def __onChart(self):
        logger.debug(f"{self.__class__.__name__}.__onChart()")
        state = self.widget_chart.isVisible()
        self.widget_chart.setVisible(not state)

    def __onStrategy(self):
        logger.debug(f"{self.__class__.__name__}.__onStrategy()")
        state = self.widget_strategy.isVisible()
        self.widget_strategy.setVisible(not state)

    @QtCore.pyqtSlot()  #__onTest
    def __onTest(self):
        logger.debug(f"{self.__class__.__name__}.__onTest()")
        state = self.widget_test.isVisible()
        self.widget_test.setVisible(not state)

    @QtCore.pyqtSlot()  #__onReport
    def __onReport(self):
        logger.debug(f"{self.__class__.__name__}.__onReport()")
        state = self.widget_report.isVisible()
        self.widget_report.setVisible(not state)

    @QtCore.pyqtSlot()  #__onConsole
    def __onConsole(self):
        logger.debug(f"{self.__class__.__name__}.__onConsole()")
        state = self.widget_console.isVisible()
        self.widget_console.setVisible(not state)

    @QtCore.pyqtSlot()  #__onShutdown
    def __onShutdown(self):
        logger.debug(f"{self.__class__.__name__}.__onShutdown()")
        QtWidgets.QApplication.instance().quit()

    @QtCore.pyqtSlot()  #__onBroker
    def __onBroker(self):
        logger.debug(f"{self.__class__.__name__}.__onBroker()")
        state = self.widget_broker.isVisible()
        self.widget_broker.setVisible(not state)

    @QtCore.pyqtSlot()  #__onAccount
    def __onAccount(self):
        logger.debug(f"{self.__class__.__name__}.__onAccount()")
        state = self.widget_account.isVisible()
        self.widget_account.setVisible(not state)

    @QtCore.pyqtSlot()  #__onOrder
    def __onOrder(self):
        logger.debug(f"{self.__class__.__name__}.__onBroker()")
        state = self.widget_order.isVisible()
        self.widget_order.setVisible(not state)

    @QtCore.pyqtSlot(Asset)  #__onAssetChanged
    def __onAssetChanged(self, iasset: Asset):
        logger.debug(f"{self.__class__.__name__}.__onAssetChanged()")
        assert isinstance(iasset, IShare)
        self.widget_chart.showChart(iasset)
        self.widget_order.setAsset(iasset)

    @QtCore.pyqtSlot(ITradeList)  #__onTradeListChanged
    def __onTradeListChanged(self, itlist: ITradeList):
        logger.debug(f"{self.__class__.__name__}.__onTradeListChanged()")
        self.widget_chart.showTradeList(itlist)
        self.widget_report.showTradeListSummary(itlist)

    @QtCore.pyqtSlot(ITrade)  #__onTradeChanged
    def __onTradeChanged(self, itrade: ITrade):
        logger.debug(f"{self.__class__.__name__}.__onTradeChanged()")
        self.widget_chart.showTrade(itrade)

    @QtCore.pyqtSlot(ISandbox)  #__onConnect
    def __onConnect(self, ibroker: ISandbox):
        logger.debug(f"{self.__class__.__name__}.__onConnect()")
        ...

    @QtCore.pyqtSlot(IAccount)  #__onAccountSetUp
    def __onAccountSetUp(self, iaccount: IAccount):
        logger.debug(f"{self.__class__.__name__}.__onAccountSetUp()")
        self.widget_order.connectAccount(iaccount)
        self.widget_account.connectAccount(iaccount)

    @QtCore.pyqtSlot(ISandbox)  #__onDisconnect
    def __onDisconnect(self, iaccount: ISandbox):
        logger.debug(f"{self.__class__.__name__}.__onDisconnect()")
        self.widget_order.disconnectAccount(iaccount)





if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.setWindowTitle("AVIN  -  Ars  Vincere")
    w.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    w.showMaximized()
    w.show()
    sys.exit(app.exec())

