#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""OCShadow-base verson

OC in upper shadow -> short
"""

from avin import *


class UStrategy(Strategy):
    MIN_STOP = 0.3
    MAX_STOP = 20

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
                TimeFrame("D"),
            ]
        )
        return tflist

    # }}}
    async def start(self):  # {{{
        await super().start()

        base = "/home/alex/AVIN/usr/filter/_strategy/OCShadow/s-base.py"
        self.base_filter = Filter.load(base)

        twitch = "/home/alex/AVIN/usr/filter/twitch/short.py"
        self.twitch_filter = Filter.load(twitch)

        twitch_hard = "/home/alex/AVIN/usr/filter/twitch/short_hard.py"
        self.twitch_hard_filter = Filter.load(twitch_hard)

    # }}}
    async def finish(self):  # {{{
        await super().finish()

    # }}}
    async def connect(self, asset: Asset, long: bool, short: bool):  # {{{
        await super().connect(asset, long, short)

        if short:
            asset.newBarD.aconnect(self.__processShort)
            asset.newBar5M.aconnect(self.__processInitial)

    # }}}
    async def onTradeOpened(self, trade: Trade):  # {{{
        await super().onTradeOpened(trade)

        stop_loss = await super().createStopLoss(
            trade,
            stop_price=trade.info["stop_price"],
        )
        await super().postStopLoss(stop_loss)

        # NOTE: тут такая фигня... там в 2014г в 1М таймфрейме
        # свеча идет 7%, так что стоп лосс и тейк профит
        # в текущих настройках срабатывают в рамках это свечи.
        # Далее тестер глючит если ему пихать тейкпрофит к уже
        # закрытому трейду. Пока не знаю как лучше обрабатывать
        # такие истории. Пока сделал ассерт в
        # core.Strategy.createStopLoss
        # core.Strategy.createTakeProfit
        # с проверкой не закрыт ли трейд
        # Тут пока локально - в рамках именно этой стратегии просто выхожу
        # какое придумать решение обобщенное для ядра пока не знаю
        if trade.status == Trade.Status.CLOSED:
            return

        # TODO:
        # take profit пересчитываем в зависимости от фактического открытия
        open = trade.openPrice()
        stop = trade.stopPrice()
        risk = abs(open - stop)
        take = open - 2 * risk
        trade.info["take_price"] = round_price(
            take, trade.instrument.min_price_step
        )

        take_profit = await super().createTakeProfit(
            trade,
            take_price=trade.info["take_price"],
        )
        await super().postTakeProfit(take_profit)

    # }}}
    async def onTradeClosed(self, trade: Trade):  # {{{
        await super().onTradeClosed(trade)

    # }}}

    async def __processShort(self, asset: Asset, chart_D: Chart):  # {{{
        # Проверяем фильтр
        check = await self.base_filter.acheck(chart_D)
        if not check:
            return

        # если открылись над вчерашним хаем - отмена
        # TODO: а вот это условие нужно еще раз проверить,
        # имеет ли оно смысл, какого хера оно в базу попало?
        chart_1M = asset.chart("1M")
        opn = chart_1M.now.open
        stop = chart_D[1].high + asset.min_price_step  # stop = вчерашний хай
        if opn > stop:
            return

        # Условия выполнены, создаем trade
        trade = await super().createTrade(
            dt=asset.chart("1M").now.dt,
            trade_type=Trade.Type.SHORT,
            instrument=asset,
        )

    # }}}
    async def __processInitial(self, asset, chart_5M):  # {{{
        for trade in self.active_trades:
            if trade.status != Trade.Status.INITIAL:
                continue

            check = await self.twitch_filter.acheck(chart_5M)
            if check:
                trade.info["twitch"] = True
                trade.info["twitch_hard"] = False
                trade.info["open_price"] = chart_5M.now.open
                trade.info["stop_price"] = (
                    chart_5M.todayHigh() + asset.min_price_step
                )
                await self.__openTrade(trade)
                continue

            check = await self.twitch_filter.acheck(chart_5M)
            if check:
                trade.info["twitch"] = False
                trade.info["twitch_hard"] = True
                trade.info["open_price"] = chart_5M.now.open
                trade.info["stop_price"] = (
                    chart_5M.todayHigh() + asset.min_price_step
                )
                await self.__openTrade(trade)

        # cancel old trades
        i = 0
        while i < len(self.active_trades):
            trade = self.active_trades[i]

            if trade.status != Trade.Status.INITIAL:
                i += 1
                continue

            if trade.dt.date() != chart_5M.now.dt.date():
                await trade.setStatus(Trade.Status.CANCELED)
                self.active_trades.remove(trade)
                continue

            i += 1

    # }}}
    async def __openTrade(self, trade: Trade):  # {{{
        open = trade.info["open_price"]
        stop = trade.info["stop_price"]

        # если стоп слишком короткий, увеличим до минимального
        risk = Range(open, stop)
        while risk.percent() < self.MIN_STOP:
            stop += trade.instrument.min_price_step
            risk = Range(open, stop)
        trade.info["stop_price"] = round_price(
            stop, trade.instrument.min_price_step
        )

        # создаем ордер
        order = await super().createMarketOrder(
            trade=trade,
            direction=Direction.SELL,
            lots=super().maxLots(trade),
        )
        # постим этот ордер
        await super().postOrder(order)

    # }}}
