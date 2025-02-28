#!/usr/bin/env  python3
# FILE:         gui.py
# CREATED:      2023.10.08
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

""" Doc """

import sys
sys.path.append("/home/alex/.local/lib/python3.9/site-packages")
sys.path.append("/home/alex/.local/lib/python3.9/site-packages/PyQt6/")
from PyQt6.QtCore import (
    QSize,
    pyqtSignal,
    )

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMdiArea,
    QMdiSubWindow,
    QWidget,
    QTabWidget,
    QFrame,
    QScrollArea,
    QLabel,
    QPushButton,
    QToolButton,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    )

sys.path.append("/home/alex/AVIN/")
from avin.const import *
from avin.item import *
from avin.company import *
from avin.strategy import *


class GuiError(Exception): pass
class Console(QWidget):
    def __init__(self, pareent=None):
        QWidget.__init__(self, pareent)


class TesterUI(QWidget):
    def __init__(self, pareent=None):
        QWidget.__init__(self, pareent)
        self.__createConsole()
        self.__createCenterPanel()
        self.__createLeftPanel()
        self.__createRightPanel()
        self.__createOverallGrid()

    def __createConsole(self):
        self.console = QTabWidget()
        self.console.addTab(QLabel("Содержимое вкладки 1"), "Log")
        self.console.addTab(QLabel("Содержимое вкладки 2"), "Error")
        self.console.addTab(QLabel("Содержимое вкладки 3"), "...")
        self.console.setCurrentIndex(0)

    def __createCenterPanel(self):
        self.frame = QFrame()
        self.center = QLabel("Ars Vincere", self.frame)
        self.center.setMinimumSize(QSize(0, 400))
        self.central_panel = QVBoxLayout()
        self.central_panel.addWidget(self.center)
        self.central_panel.addWidget(self.console)

    def __createLeftPanel(self):
        self.btn_L1 = QPushButton("1")
        self.btn_L2 = QPushButton("2")
        self.btn_L3 = QPushButton("3")
        self.btn_L4 = QToolButton()
        self.btn_L1.setMinimumSize(QSize(50, 50))
        self.btn_L1.setMaximumSize(QSize(50, 50))
        self.btn_L2.setMinimumSize(QSize(50, 50))
        self.btn_L2.setMaximumSize(QSize(50, 50))
        self.btn_L3.setMinimumSize(QSize(50, 50))
        self.btn_L3.setMaximumSize(QSize(50, 50))
        self.btn_L4.setMinimumSize(QSize(50, 50))
        self.btn_L4.setMaximumSize(QSize(50, 50))

        btn_box = QVBoxLayout()
        btn_box.addWidget(self.btn_L1)
        btn_box.addWidget(self.btn_L2)
        btn_box.addWidget(self.btn_L3)
        btn_box.addWidget(self.btn_L4)
        btn_box.addStretch()

        self.left_scroll = QScrollArea()
        self.left_scroll.setMinimumSize(QSize(250, 0))
        self.left_scroll.setMaximumSize(QSize(250, 0))

        self.left_panel = QHBoxLayout()
        self.left_panel.addLayout(btn_box)
        self.left_panel.addWidget(self.left_scroll)

    def __createRightPanel(self):
        self.btn_R1 = QPushButton("21")
        self.btn_R2 = QPushButton("22")
        self.btn_R3 = QPushButton("23")
        self.btn_R1.setMinimumSize(QSize(50, 50))
        self.btn_R1.setMaximumSize(QSize(50, 50))
        self.btn_R2.setMinimumSize(QSize(50, 50))
        self.btn_R2.setMaximumSize(QSize(50, 50))
        self.btn_R3.setMinimumSize(QSize(50, 50))
        self.btn_R3.setMaximumSize(QSize(50, 50))

        btn_box = QVBoxLayout()
        btn_box.addWidget(self.btn_R1)
        btn_box.addWidget(self.btn_R2)
        btn_box.addWidget(self.btn_R3)
        btn_box.addStretch()

        self.right_scroll = QScrollArea()
        self.right_scroll.setMinimumSize(QSize(250, 0))
        self.right_scroll.setMaximumSize(QSize(250, 0))

        self.right_panel = QHBoxLayout()
        self.right_panel.addWidget(self.right_scroll)
        self.right_panel.addLayout(btn_box)

    def __createOverallGrid(self):
        self.grid = QGridLayout(self)
        self.grid.addLayout(self.left_panel, 0, 0)
        self.grid.addLayout(self.central_panel, 0, 1)
        self.grid.addLayout(self.right_panel, 0, 2)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.tester = TesterUI()
        self.tester2 = TesterUI()
        self.tester3 = TesterUI()
        self.tester4 = TesterUI()
        self.tester5 = TesterUI()

        self.area = QMdiArea()
        self.tab1 = QMdiSubWindow(self.area)
        self.tab2 = QMdiSubWindow(self.area)
        self.tab3 = QMdiSubWindow(self.area)
        self.tab4 = QMdiSubWindow(self.area)
        self.tab5 = QMdiSubWindow(self.area)
        self.tab6 = QMdiSubWindow(self.area)
        self.tab7 = QMdiSubWindow(self.area)

        self.tab1.setWidget(self.tester)
        self.tab2.setWidget(self.tester2)

        self.area.addSubWindow(self.tab1)
        self.area.addSubWindow(self.tab2)
        self.area.addSubWindow(self.tab3)
        self.area.addSubWindow(self.tab4)
        self.area.addSubWindow(self.tab5)
        self.area.addSubWindow(self.tab6)
        self.area.addSubWindow(self.tab7)

        self.tab1.setWindowTitle("Strategy")
        self.tab2.setWindowTitle("Tester")
        self.tab3.setWindowTitle("Report")
        self.tab4.setWindowTitle("Sandbox")
        self.tab5.setWindowTitle("General")
        self.tab6.setWindowTitle("Terminal")
        self.tab7.setWindowTitle("Documentation")

        self.area.setViewMode(QMdiArea.ViewMode.TabbedView)
        self.area.setActiveSubWindow(self.tab1)
        self.area.setTabsMovable(True)
        self.setCentralWidget(self.area)





if __name__ == "__main__":
    app = QApplication(sys.argv)
    # main_window = Console()
    # main_window = TesterUI()
    main_window = MainWindow()
    main_window.setWindowTitle("AVIN - Ars Vincere")
    main_window.showMaximized()
    main_window.show()
    sys.exit(app.exec())

