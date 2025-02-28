#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from avin import (
    FIVE_MINUTE,
    Asset,
    Direction,
    Strategy,
    TimeFrame,
    TimeFrameList,
    Trade,
)
from avin.utils import Cmd


class UStrategy(Strategy):
    def __init__(self):  # {{{
        name = Cmd.dirName(__file__)
        version = Cmd.name(__file__)
        Strategy.__init__(self, name, version)

    # }}}
    def timeframes(self):  # {{{
        tflist = TimeFrameList(
            [
                TimeFrame("1M"),
                TimeFrame("5M"),
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
            asset.newBar5M.aconnect(self.__processLong)
        if short:
            asset.newBar5M.aconnect(self.__processLong)

    # }}}
    async def onTradeOpened(self, trade: Trade):  # {{{
        await super().onTradeOpened(trade)

        stop_loss = await super().createStopLoss(trade, stop_percent=0.1)
        await trade.attachOrder(stop_loss)
        await super().postOrder(stop_loss)

        take_profit = await super().createTakeProfit(trade, take_percent=0.3)
        await trade.attachOrder(take_profit)
        await super().postOrder(take_profit)

    # }}}
    async def onTradeClosed(self, trade: Trade):  # {{{
        await super().onTradeClosed(trade)

    # }}}
    async def __processLong(self, asset, chart):  # {{{
        if chart.last is None:
            return

        # создаем трейд тупо каждый 5 минут
        trade = await super().createTrade(
            dt=chart.last.dt + FIVE_MINUTE,
            trade_type=Trade.Type.LONG,
            instrument=asset,
        )

        # создаем ордер
        order = await super().createMarketOrder(
            direction=Direction.BUY,
            instrument=asset,
            lots=1,
        )

        # связываем этот ордер с трейдом
        await trade.attachOrder(order)

        # постим этот ордер
        await super().postOrder(order)

    # }}}
    async def __processShort(self, asset, chart):  # {{{
        return

    # }}}
    # }}}
