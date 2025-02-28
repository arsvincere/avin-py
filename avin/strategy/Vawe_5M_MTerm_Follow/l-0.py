#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""Vawe_5M_MTerm-l-0

l-0 Смотрим волны. Если волна бычья:
    - и тренд two в ней медвежий - покупаем в начале отроста
    - и тренд two в ней бычий - ничего не делаем пока. Ждем
      следующую фазу, когда медвежий тренд завершится.
      на будущее конечно в этой фазе уже надо начинать покупки
      навстречу движению, но до этого дойдем постепенно.
    - ставим стоп на минимум медвежьего тренда последнего.
    - тейк делаем 2 стопа.
    = Хороший результат! Период 2023-01-01 - 2023-04-01
      profit 14.600     % 48.21      ratio 1.39    avg 261
      gross profit 52.000 27 trade
      gross loss 37.400 29 trade
      И это в самой базовой версии! Без подстройки стопов тейков!
      Без каких либо фильтров старших таймфреймов!!!
    = Фильтры D 1H s-m бывает неплохо улучшают точность. Хотя
      почему то неожиданные значения bear bull... то есть например
      на текущем медвежьем лучше идут лонги... Думаю это связано
      как раз с запоздалым определением истинного движения тренда.
      Но это похую, правильно или не правильно работает фильтр не
      важно, важно что на выходе точность увеличивается.
      Остается посмотреть будет ли результат устойчивым на больших
      сроках и большем количестве тикеров.
      И будет ли результат устойчив в форвард тесте.

"""

from usr.lib import *


class UStrategy(Strategy):
    MIN_STOP = 0.3
    MAX_STOP = 5

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
                TimeFrame("1H"),
                TimeFrame("D"),
            ]
        )
        return tflist

    # }}}
    async def start(self):  # {{{
        await super().start()

        # self.base_filter = Filter.load("_strategy Vawe D STerm l-base")
        self.__last_trade_dt = None

    # }}}
    async def finish(self):  # {{{
        await super().finish()

    # }}}
    async def connect(self, asset: Asset, long: bool, short: bool):  # {{{
        await super().connect(asset, long, short)

        if long:
            asset.newBar5M.aconnect(self.__processLong)

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

        # take profit пересчитываем в зависимости от фактического открытия
        # потому что открываемся по MarketOrder
        open = trade.openPrice()
        stop = trade.stopPrice()
        risk = abs(stop - open)
        take = open + 2 * risk
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

    async def __processLong(self, asset: Asset, chart_5M: Chart):  # {{{
        # проверяем последню m-term волну на 5M
        elist = ExtremumList(chart_5M)
        vawe = elist.vawe(Term.MTERM, 1)
        if not self.__checkVawe(vawe):
            return

        # создаем трейд
        trade = await self.__createTrade(asset, vawe)

        # опен трейд
        if trade is not None:
            await self.__openTrade(trade)

    # }}}

    def __checkVawe(self, vawe: Vawe):  # {{{
        if vawe is None:
            return False

        # Проверяем нет ли уже открытого трейда по этому инструменту
        if self.__hasActiveTrade(vawe.asset):
            return False

        # последняя завершенная m-term волна - бычья
        if not vawe.isBull():
            return False

        # последний завершенный тренд в ней - медвежий
        trend = vawe.two
        if not trend.isBear():
            return False

        # Проверяем дату последнего тренда в текущей волне
        # Торгуем каждую волну только один раз
        if self.__last_trade_dt == trend.end.dt:
            return False

        # обновляем дату последнего обработанного тренда
        self.__last_trade_dt = trend.end.dt

        return True

    # }}}
    def __hasActiveTrade(self, asset):  # {{{
        for trade in self.active_trades:
            if trade.instrument == asset:
                return True

        return False

    # }}}
    async def __createTrade(self, asset, vawe):  # {{{
        # open - 1М сейчас
        chart_1M = asset.chart("1M")
        open = chart_1M.now.open

        # stop - минимум последнего тренда
        trend = vawe.two
        stop = trend.end.price - asset.min_price_step

        if stop > open:
            return None

        # если стоп слишком длинный отмена
        risk = Range(stop, open)
        if risk.percent() > self.MAX_STOP:
            return None

        # если стоп слишком короткий, увеличим до минимального
        while risk.percent() < self.MIN_STOP:
            stop -= asset.min_price_step
            risk = Range(stop, open)

        # ну если со стопом все ок - создаем трейд
        trade = await super().createTrade(
            dt=asset.chart("1M").now.dt,
            trade_type=Trade.Type.LONG,
            instrument=asset,
        )
        trade.info["open_price"] = open
        trade.info["stop_price"] = round_price(stop, asset.min_price_step)

        return trade

    # }}}
    async def __openTrade(self, trade):  # {{{
        # создаем ордер и постим ордер
        order = await super().createMarketOrder(
            trade=trade,
            direction=Direction.BUY,
            lots=super().maxLots(trade),
        )
        await super().postOrder(order)

    # }}}
