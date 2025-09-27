# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt

SCROLL_OFF = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
CTRL = QtCore.Qt.KeyboardModifier.ControlModifier
NO = QtCore.Qt.KeyboardModifier.NoModifier


class ChartView(QtWidgets.QGraphicsView):
    def __init__(self, parent):
        QtWidgets.QGraphicsView.__init__(self, parent)

        self.__config()

        self.left_pressed = False
        self.right_pressed = False

    def wheelEvent(self, e):
        # super().wheelEvent(e)  # ломает позиционирование все нахер

        if e.modifiers() == NO:
            if e.angleDelta().y() < 0:
                self.scale(1 / 1.1, 1)
            else:
                self.scale(1.1, 1)

        if e.modifiers() == CTRL:
            if e.angleDelta().y() < 0:
                self.scale(1, 1 / 1.1)
            else:
                self.scale(1, 1.1)

    def enterEvent(self, e: QtGui.QEnterEvent | None):
        # super().enterEvent(e)

        if e is None:
            return

        self.__set_cross_cursor()
        return e.ignore()

    def mousePressEvent(self, e: QtGui.QMouseEvent | None):
        super().mousePressEvent(e)

        if e is None:
            return

        if e.button() == Qt.MouseButton.LeftButton:
            self.left_pressed = True
        elif e.button() == Qt.MouseButton.RightButton:
            self.right_pressed = True

        self.__set_cross_cursor()

        return e.ignore()

    def mouseReleaseEvent(self, e: QtGui.QMouseEvent | None):
        super().mouseReleaseEvent(e)

        if e is None:
            return

        if e.button() == Qt.MouseButton.LeftButton:
            self.left_pressed = False
        elif e.button() == Qt.MouseButton.RightButton:
            self.right_pressed = False

        self.__set_cross_cursor()

        return e.ignore()

    def mouseMoveEvent(self, e: QtGui.QMouseEvent | None):
        super().mouseMoveEvent(e)

        if e is None:
            return

        scene = self.scene()
        assert scene is not None

        # move cross
        cur_pos = e.pos()
        scene_pos = self.mapToScene(cur_pos.x(), cur_pos.y())
        scene.cross.setPos(scene_pos)  # type: ignore

        # move pinned
        if self.left_pressed:
            self.__move_pinned()

        return e.ignore()

    def center_on_last(self):
        scene = self.scene()
        last_bar_gitem = scene.gchart.last()
        pos = last_bar_gitem.close_pos

        self.centerOn(pos)

    def __config(self) -> None:
        # включает режим перетаскивания сцены внутри QGraphicsView
        # мышкой с зажатой левой кнопкой
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)

        # hide scroll bars
        self.setHorizontalScrollBarPolicy(SCROLL_OFF)
        self.setVerticalScrollBarPolicy(SCROLL_OFF)

        # flip vertically
        tr = QtGui.QTransform(1, 0, 0, -1, 0, 0)
        self.setTransform(tr)

    def __set_cross_cursor(self):
        port = self.viewport()
        assert port is not None

        port.setCursor(Qt.CursorShape.CrossCursor)

    def __move_pinned(self):
        scene = self.scene()
        assert scene is not None

        # move labels
        pos_0x0 = self.mapToScene(0, 0)
        scene.top.setPos(pos_0x0)


if __name__ == "__main__":
    ...
