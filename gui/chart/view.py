#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

from avin.core import Trade
from avin.utils import logger


class ChartView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsView.__init__(self, parent)

        self.__config()

        self.current_gtrade = None
        self.left_pressed = False
        self.right_pressed = False

    # }}}

    def wheelEvent(self, e):  # {{{
        logger.debug(f"{self.__class__.__name__}.wheelEvent()")
        # super().wheelEvent(e)  # ломает позиционирование все нахер

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

    # }}}
    def enterEvent(self, e: QtGui.QEnterEvent | None):  # {{{
        logger.debug(f"{self.__class__.__name__}.enterEvent()")
        # super().enterEvent(e)

        self.__setCrossCursor()
        return e.ignore()

    # }}}
    def mousePressEvent(self, e: QtGui.QMouseEvent | None):  # {{{
        logger.debug(f"{self.__class__.__name__}.mousePressEvent()")
        super().mousePressEvent(e)

        if e.button() == Qt.MouseButton.LeftButton:
            self.left_pressed = True
        elif e.button() == Qt.MouseButton.RightButton:
            self.right_pressed = True

        self.__setCrossCursor()
        return e.ignore()

    # }}}
    def mouseReleaseEvent(self, e: QtGui.QMouseEvent | None):  # {{{
        logger.debug(f"{self.__class__.__name__}.mouseReleaseEvent()")
        super().mouseReleaseEvent(e)

        if e.button() == Qt.MouseButton.LeftButton:
            self.left_pressed = False
        elif e.button() == Qt.MouseButton.RightButton:
            self.right_pressed = False

        self.__setCrossCursor()
        return e.ignore()

    # }}}
    def mouseMoveEvent(self, e: QtGui.QMouseEvent | None):  # {{{
        logger.debug(f"{self.__class__.__name__}.mouseMoveEvent()")
        super().mouseMoveEvent(e)

        scene = self.scene()
        assert scene is not None

        # move cross
        cur_pos = e.pos()
        scene.cross.setPos(self.mapToScene(cur_pos.x(), cur_pos.y()))

        # move panels
        if self.left_pressed:
            self.__movePinnedPanels()

        return e.ignore()

    # }}}

    def centerOnFirst(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.centerOnFirst()")

        scene = self.scene()
        first_bar_item = scene.gchart.first
        pos = first_bar_item.close_pos

        self.centerOn(pos)

    # }}}
    def centerOnLast(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.centerOnLast()")

        scene = self.scene()
        last_bar_item = scene.gchart.last
        pos = last_bar_item.close_pos

        self.centerOn(pos)

    # }}}
    def centerOnTrade(self, trade: Trade):  # {{{
        logger.debug(f"{self.__class__.__name__}.centerOnTrade()")

        if self.current_gtrade is not None:
            self.current_gtrade.hideAnnotation()

        # TODO: ебать тут порно код... с использованием переменных
        # связанных виджетов... надо это все через интерфейсы сделать
        gtrades: QtWidgets.QGraphicsItemGroup = self.scene().gtrades
        if gtrades is None:
            return

        for gtrade in gtrades.childItems():
            if gtrade.trade.dt == trade.dt:
                self.current_gtrade = gtrade
                gtrade.showAnnotation()
                self.centerOn(gtrade.trade_pos)
                return

    # }}}
    def resetCurrentGTrade(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.resetCurrentGTrade()")

        self.current_gtrade = None

    # }}}

    def __config(self):  # {{{
        # включает режим перетаскивания сцены внутри QGraphicsView
        # мышкой с зажатой левой кнопкой
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)

        scroll_off = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        self.setHorizontalScrollBarPolicy(scroll_off)
        self.setVerticalScrollBarPolicy(scroll_off)

    # }}}
    def __resetTranformation(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__resetTranformation()")

        trans = self.transform().inverted()[0]

        # chart labels: bar info, vol info, indicators
        # labels = self.scene().top
        # labels.setTransform(trans)
        # labels.setPos(self.mapToScene(0, 0))

        # current gtrade
        if self.current_gtrade:
            self.current_gtrade.annotation.setTransform(trans)

        # other ignore scale items on scene
        for item in self.scene().ignore_scale:
            item.setTransform(trans)

    # }}}
    def __setCrossCursor(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__setCrossCursor()")

        port = self.viewport()
        assert port is not None
        port.setCursor(Qt.CursorShape.CrossCursor)

    # }}}
    def __movePinnedPanels(self):  # {{{
        scene = self.scene()
        assert scene is not None
        height = self.size().height()

        # move labels
        pos_0x0 = self.mapToScene(150, 0)
        scene.top.setPos(pos_0x0)
        # move volumes
        pos = QtCore.QPointF(0, pos_0x0.y() + height)
        scene.volumes.setPos(pos)

        # move footer
        pos = QtCore.QPointF(0, pos_0x0.y() + height)
        for i in scene.footer:
            i.gitem.setPos(pos)

        # move left
        pos = self.mapToScene(0, 0)
        for i in scene.left:
            i.gitem.setPos(pos)


# }}}


if __name__ == "__main__":
    ...
