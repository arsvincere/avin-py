#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import sys

import pandas as pd
from PyQt6 import QtCore, QtWidgets

from avin import Cfg, Cmd, DataType, Tics, TimeFrame, logger
from gui.chart.gchart import GChart
from gui.chart.indicator_item import IndicatorItem
from gui.custom import Css, Icon, Label, Theme, ToolButton
from gui.indicator._indicator import Indicator


class QuantIndicator:  # {{{
    name = "Quant"
    position = Indicator.Position.LEFT

    def __init__(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")

        self.gitem = None
        self.__item = None
        self.__label = None
        self.__settings = None

    # }}}

    def item(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.item()")

        if self.__item is None:
            self.__item = IndicatorItem(self)

        return self.__item

    # }}}
    def label(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.label()")

        if self.__label is None:
            self.__label = _QuantLabel(self)

        return self.__label

    # }}}
    def graphics(self, gchart: GChart):  # {{{
        logger.debug(f"{self.__class__.__name__}.graphics()")

        self.gchart = gchart
        self.gitem = _QuantGraphics(self)

        if self.__settings is None:
            self.__settings = _QuantSettings(self)
        self.__settings.configureSilent(self)

        return self.gitem

    # }}}
    def configure(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure()")

        if self.__settings is None:
            self.__settings = _QuantSettings(self)

        self.__settings.configure(self.gitem)

    # }}}


# }}}
class _QuantLabel(QtWidgets.QWidget):  # {{{
    def __init__(self, indicator, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QWidget.__init__(self, parent)

        self.__indicator = indicator
        self.__createWidgets()
        self.__createLayots()
        self.__connect()

    # }}}

    @property  # indicator  # {{{
    def indicator(self):
        return self.__indicator

    # }}}

    # def setGChart(self, gchart):  # {{{
    #     self.gchart = gchart
    #
    # # }}}
    def updateInfo(self, x):  # {{{
        pass

    # }}}

    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.label_name = QtWidgets.QLabel(self.__indicator.name)
        self.btn_hide = ToolButton(Icon.HIDE, width=16, height=16)
        self.btn_settings = ToolButton(Icon.CONFIG, width=16, height=16)
        self.btn_delete = ToolButton(Icon.DELETE, width=16, height=16)

        self.info_5m = Label("5M")
        self.info_1h = Label("1H")
        self.info_d = Label("D")

        self.info_5m.setStyleSheet(Css.CHART_LABEL)
        self.info_1h.setStyleSheet(Css.CHART_LABEL)
        self.info_d.setStyleSheet(Css.CHART_LABEL)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.label_name)
        hbox.addWidget(self.btn_hide)
        hbox.addWidget(self.btn_settings)
        hbox.addWidget(self.btn_delete)
        hbox.addStretch()
        hbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(hbox)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")
        self.btn_settings.clicked.connect(self.__onSettings)

    # }}}

    @QtCore.pyqtSlot()  # __onSettings  # {{{
    def __onSettings(self):
        logger.debug(f"{self.__class__.__name__}.__onSettings()")

        self.indicator.configure()

    # }}}


# }}}
class _QuantSettings(QtWidgets.QDialog):  # {{{
    def __init__(self, indicator, parent=None):  # {{{
        QtWidgets.QDialog.__init__(self, parent)
        self.__indicator = indicator

        self.__config()
        self.__createWidgets()
        self.__createLayots()
        self.__connect()
        self.__initUI()

    # }}}

    @property  # indicator  # {{{
    def indicator(self):
        return self.__indicator

    # }}}

    def configureSilent(self, indicator: QuantIndicator):  # {{{
        logger.debug(f"{self.__class__.__name__}.configure")

    # }}}
    def configure(self, indicator):  # {{{
        logger.debug(f"{self.__class__.__name__}.showSettings")

    # }}}

    def __config(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__config()")

        self.setWindowTitle("AVIN")
        self.setStyleSheet(Css.DIALOG)
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)

    # }}}
    def __createWidgets(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createWidgets()")

        self.title_label = Label("| Extremum settings:", parent=self)
        self.title_label.setStyleSheet(Css.TITLE)

        self.ok_btn = ToolButton(Icon.OK)
        self.cancel_btn = ToolButton(Icon.CANCEL)

    # }}}
    def __createLayots(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__createLayots()")

        hbox_btn = QtWidgets.QHBoxLayout()
        hbox_btn.addWidget(self.title_label)
        hbox_btn.addStretch()
        hbox_btn.addWidget(self.ok_btn)
        hbox_btn.addWidget(self.cancel_btn)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(hbox_btn)

    # }}}
    def __connect(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__connect()")

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    # }}}
    def __initUI(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__initUI()")

    # }}}


# }}}
class _QuantGraphics(QtWidgets.QGraphicsItemGroup):  # {{{
    WIDTH = 150
    INDENT = Cfg.Chart.QUANT_INDENT

    flags = QtWidgets.QGraphicsItem.GraphicsItemFlag
    ignore_transformation = flags.ItemIgnoresTransformations

    def __init__(self, indicator: QuantIndicator, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtWidgets.QGraphicsItemGroup.__init__(self, parent)

        self.indicator = indicator
        self.gchart = indicator.gchart

        # self.__loadQuant()
        self.__getTics()
        self.__calcMaxAmount()
        self.__createFrame()
        self.__createQuant()

        # TODO: здесь надо только одну ось игнорить...
        # self.setFlag(self.ignore_transformation)

    # }}}

    def __getTics(self) -> None:  # {{{
        asset = self.gchart.chart.asset
        # TODO: пока строю только дневной квант
        self.quant = asset.tics.quant(TimeFrame("D"))

    # }}}
    def __calcMaxAmount(self) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.__calcCoordinates()")

        if self.quant is None:
            return

        # XXX: пока работаю только с одним дневным квантом
        assert len(self.quant) == 1
        q = self.quant.iloc[0]

        max_amount_buy = q["buy"].max()
        max_amount_sell = q["sell"].max()
        self.max_amount = max(max_amount_buy, max_amount_sell)

    # }}}
    def __createFrame(self) -> None:  # {{{
        x0 = 0
        y0 = 0
        width = self.WIDTH
        height = self.gchart.rect.height()

        frame = QtWidgets.QGraphicsRectItem(x0, y0, width, height)
        frame.setPen(Theme.Chart.BG_FOOTER)
        frame.setBrush(Theme.Chart.BG_FOOTER)
        self.addToGroup(frame)

    # }}}
    def __createQuant(self) -> None:  # {{{
        if self.quant is None:
            return

        # XXX: пока работаю только с одним дневным квантом
        assert len(self.quant) == 1
        q = self.quant.iloc[0]

        for i, row in q.iterrows():
            self.__createQuantLevel(row)

    # }}}
    def __createQuantLevel(self, quant_level: pd.Series) -> None:  # {{{
        # alias
        gchart = self.gchart
        min_price_step = gchart.chart.asset.min_price_step
        price = quant_level["price"]
        buy = quant_level["buy"]
        sell = quant_level["sell"]

        # coordinate
        y0 = gchart.yFromPrice(price)
        y1 = gchart.yFromPrice(price + min_price_step)
        height = y1 - y0

        x = self.WIDTH / 2  # середина столбца кванта
        width_buy = (buy / self.max_amount) * self.WIDTH / 2
        width_sell = (sell / self.max_amount) * self.WIDTH / 2

        # graphics item
        buy_body = QtWidgets.QGraphicsRectItem(x, y0, -width_buy, height)
        buy_body.setPen(Theme.Chart.BULL)
        buy_body.setBrush(Theme.Chart.BULL)

        sell_body = QtWidgets.QGraphicsRectItem(x, y0, width_sell, height)
        sell_body.setPen(Theme.Chart.BEAR)
        sell_body.setBrush(Theme.Chart.BEAR)

        self.addToGroup(buy_body)
        self.addToGroup(sell_body)

    # }}}

    def __loadQuant(self) -> None:  # {{{
        """quant = pd.Series of DataFrame like:
           price    buy   sell
        0  320.5  32050      0
        1  321.0      0  96300

        Series key = dt of bar of quant
        """

        # XXX: говнокод,
        # Да еще и дубль из _HistGraphics, надо это все в ассет выносить
        # и везде чтобы был один и тот же ассет в рантайме.
        last_date = self.gchart.chart.now.dt.date()
        file_name = f"{last_date} tic.parquet"
        file_path = Cmd.path(
            self.gchart.chart.asset.path,
            DataType.TIC.name,
            file_name,
        )
        if not Cmd.isExist(file_path):
            self.tics = None
            self.quant = None
            logger.warning(f"Tic data not found: {file_path}")
            return

        df = pd.read_parquet(file_path)
        self.tics = Tics(self.gchart.chart.asset, df)

        # XXX: пока только один квант - дневной
        # tf = self.gchart.chart.timeframe
        self.quant = self.tics.quant(TimeFrame("D"))

    # }}}


# }}}

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    indicator = ExtremumIndicator()
    w = _HistSettings(indicator)
    w.show()
    sys.exit(app.exec())
