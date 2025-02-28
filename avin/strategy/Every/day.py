#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from datetime import time

from avin.core import (
    Asset,
    Chart,
    Direction,
    Strategy,
    TimeFrame,
    TimeFrameList,
    Trade,
)
from avin.utils import Cmd


class UStrategy(Strategy):
    """Doc
    Тупо на открытии продает или покупает, на закрытии закрывает
    Используется в тест юнитах, и для отладки других стратегий
    """

    def __init__(self):  # {{{
        name = Cmd.dirName(__file__)
        version = Cmd.name(__file__)
        Strategy.__init__(self, name, version)

    # }}}
    def timeframes(self):  # {{{
        tflist = TimeFrameList(
            [
                TimeFrame("1M"),
                TimeFrame("D"),
            ]
        )
        return tflist

    # }}}
    async def start(self):  # {{{
        await super().start()

    # }}}
    async def finish(self):  # {{{
        await super().finish()

    # }}}
    async def connect(self, asset: Asset, long: bool, short: bool):  # {{{
        await super().connect(asset, long, short)

        if long:
            asset.newBar1M.aconnect(self.__processLong)

        if short:
            asset.newBar1M.aconnect(self.__processShort)

        asset.updated.aconnect(self.__processOpenedTrades)

    # }}}
    async def onTradeOpened(self, trade: Trade):  # {{{
        await super().onTradeOpened(trade)

    # }}}
    async def onTradeClosed(self, trade: Trade):  # {{{
        await super().onTradeClosed(trade)

    # }}}
    async def __processLong(self, asset: Asset, chart: Chart):  # {{{
        assert chart.timeframe == "1M"
        if chart.now is None:
            return
        if chart.now.dt.time() != time(7, 0):
            return

        # Каждое утро создаем трейд
        trade = await super().createTrade(
            dt=chart.now.dt,
            trade_type=Trade.Type.LONG,
            instrument=asset,
        )

        # создаем ордер по цене открытия дня
        order = await super().createLimitOrder(
            trade=trade,
            direction=Direction.BUY,
            lots=1,
            price=chart.now.open,
        )

        # связываем этот ордер с трейдом
        await trade.attachOrder(order)

        # постим этот ордер
        await super().postOrder(order)

    # }}}
    async def __processShort(self, asset: Asset, chart: Chart):  # {{{
        pass

    # }}}
    async def __processOpenedTrades(self, asset: Asset, chart: Chart):  # {{{
        if chart.timeframe != "1M":
            return

        bar = chart.now
        if bar.dt.time() != time(15, 45):
            return

        assert len(self.active_trades) == 1
        trade = self.active_trades[0]

        # создаем ордер по цене закрытия дня
        order = await super().createLimitOrder(
            trade=trade,
            direction=Direction.SELL,
            lots=1,
            price=chart.now.close,
        )

        # связываем этот ордер с трейдом
        await trade.attachOrder(order)

        # постим этот ордер
        await super().postOrder(order)
