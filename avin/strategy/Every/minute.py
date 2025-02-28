#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from datetime import timedelta

from avin import (
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
    def __init__(self):  # {{{
        name = Cmd.dirName(__file__)
        version = Cmd.name(__file__)
        Strategy.__init__(self, name, version)

    # }}}
    def timeframes(self):  # {{{
        tflist = TimeFrameList(
            [
                TimeFrame("1M"),
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
    async def __processLong(self, asset, chart):  # {{{
        if chart.now is None:
            return

        # если время бара не четное количество минут - отмена
        if chart.now.dt.minute % 2 != 0:
            return

        # если время бара четное, создаем трейд
        trade = await super().createTrade(
            dt=chart.now.dt,
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
    async def __processOpenedTrades(self, asset: Asset, chart: Chart):  # {{{
        trades = self.active_trades.selectAsset(asset)
        opened_trades = trades.selectStatus(Trade.Status.OPENED)
        for trade in opened_trades:
            open_dt = trade.openDateTime()
            if (chart.now.dt - open_dt) >= timedelta(seconds=50):
                await super().closeTrade(trade)

        # closing_trades = trades.selectStatus(Trade.Status.CLOSING)
        # for trade in closing_trades:
        #     open_dt = trade.openDateTime()
        #     if (chart.now.dt - open_dt) >= timedelta(seconds=50):
        #         await super().closeTrade(trade)

    # }}}
