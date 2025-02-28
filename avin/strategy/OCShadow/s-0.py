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
                TimeFrame("D"),
            ]
        )
        return tflist

    # }}}
    async def start(self):  # {{{
        await super().start()

        filter_path = "/home/alex/AVIN/usr/filter/ocshadow/short-0/0.py"
        self.filter_fear = Filter.load(filter_path)

    # }}}
    async def finish(self):  # {{{
        await super().finish()

    # }}}
    async def connect(self, asset: Asset, long: bool, short: bool):  # {{{
        await super().connect(asset, long, short)

        if short:
            asset.newBarD.aconnect(self.__processShort)

    # }}}
    async def onTradeOpened(self, trade: Trade):  # {{{
        await super().onTradeOpened(trade)

        stop_loss = await super().createStopLoss(
            trade,
            stop_price=trade.info["stop_price"],
        )
        await trade.attachOrder(stop_loss)
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
        opn = trade.openPrice()
        stop = trade.stopPrice()
        risk = abs(stop - opn)
        take = opn - 2 * risk
        trade.info["take_price"] = take

        take_profit = await super().createTakeProfit(
            trade,
            take_price=trade.info["take_price"],
        )
        await trade.attachOrder(take_profit)
        await super().postTakeProfit(take_profit)

    # }}}
    async def onTradeClosed(self, trade: Trade):  # {{{
        await super().onTradeClosed(trade)

    # }}}

    async def __processShort(self, asset: Asset, chart_D: Chart):  # {{{
        # Проверяем фильтр
        check = await self.filter_fear.acheck(chart_D)
        if not check:
            return

        # если открылись над вчерашним хаем - отмена
        chart_1M = asset.chart("1M")
        opn = chart_1M.now.open
        stop = chart_D[1].high + asset.min_price_step  # stop = вчерашний хай
        if opn > stop:
            return

        # если стоп слишком длинный отмена
        risk = Range(opn, stop)
        if risk.percent() > self.MAX_STOP:
            return

        # если стоп слишком короткий, увеличим до минимального
        risk = Range(opn, stop)
        while risk.percent() < self.MIN_STOP:
            stop += asset.min_price_step
            risk = Range(opn, stop)

        # take = 2 stop
        take = opn - 2 * risk.abs()

        # Условия выполнены, создаем trade
        trade = await super().createTrade(
            dt=asset.chart("1M").now.dt,
            trade_type=Trade.Type.SHORT,
            instrument=asset,
        )
        trade.info["open_price"] = round_price(opn, asset.min_price_step)
        trade.info["stop_price"] = round_price(stop, asset.min_price_step)
        trade.info["take_price"] = round_price(take, asset.min_price_step)

        max_lots = super().maxLots(trade)

        # создаем ордер
        order = await super().createMarketOrder(
            trade=trade,
            direction=Direction.SELL,
            lots=max_lots,
        )

        # постим этот ордер
        await super().postOrder(order)

    # }}}
