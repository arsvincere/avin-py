#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""Trend_5M_STerm_Toward-s-0

== Toward trend BULL 5M# {{{
AFKS 5M STERM BULL DELTA sizes:
{<Size.BLACKSWAN_SMALL: -7>: Range(0.01, 0.06),
 <Size.ANOMAL_SMALL: -6>: Range(0.06, 0.09),
 <Size.EXTRA_SMALL: -5>: Range(0.09, 0.11),
 <Size.VERY_SMALL: -4>: Range(0.11, 0.14),
 <Size.SMALLEST: -3>: Range(0.14, 0.21),
 <Size.SMALLER: -2>: Range(0.21, 0.27),
 <Size.SMALL: -1>: Range(0.27, 0.34),
 <Size.NORMAL: 0>: Range(0.34, 0.51),

 <Size.BIG: 1>: Range(0.51, 0.62),
 <Size.BIGGER: 2>: Range(0.62, 0.81),
 <Size.BIGGEST: 3>: Range(0.81, 1.14),
 <Size.VERY_BIG: 4>: Range(1.14, 1.5),
 <Size.EXTRA_BIG: 5>: Range(1.5, 1.82),
 <Size.ANOMAL_BIG: 6>: Range(1.82, 2.66),
 <Size.BLACKSWAN_BIG: 7>: Range(2.66, 16.32)}

 Глядя на эту хуйню напрашивается такая логика, бросается в глаза
 что биг тренды начинаются (грубо) с 0.5% и идут до 2.7%
 И лишь 1% случаев черные лебеди, не обращаем пока на них внимание.

 Что если взять и начать торговать на встречу начиная от 0.5

 То есть - идентифицирую любой минимум на графике.
 И сразу ставлю лимитку на +0.5% от него.
 И сразу ставлю стоп на 3%

 Далее нужно увеличивать позицию.
 Ну давай пока грубо глядя на размеры трендов, на границы размеров:
 Ну там примерно 0.3 шаги идут...
 0.5 - вход  10тр
 0.8 - 20тр
 1.1 - 40тр
 1.4 - 80тр
 1.7 - 160тр
 2.0 - 320тр
 2.3 - 640тр
 2.6 - 1280тр

 И допустим тейк делаем на минимальный нормальный размер медвежьего тренда
AFKS 5M STERM BEAR DELTA sizes:
{<Size.BLACKSWAN_SMALL: -7>: Range(0.01, 0.06),
 <Size.ANOMAL_SMALL: -6>: Range(0.06, 0.09),
 <Size.EXTRA_SMALL: -5>: Range(0.09, 0.11),
 <Size.VERY_SMALL: -4>: Range(0.11, 0.14),
 <Size.SMALLEST: -3>: Range(0.14, 0.2),
 <Size.SMALLER: -2>: Range(0.2, 0.27),
 <Size.SMALL: -1>: Range(0.27, 0.33),
 <Size.NORMAL: 0>: Range(0.33, 0.5),
 <Size.BIG: 1>: Range(0.5, 0.62),
 <Size.BIGGER: 2>: Range(0.62, 0.79),
 <Size.BIGGEST: 3>: Range(0.79, 1.12),
 <Size.VERY_BIG: 4>: Range(1.12, 1.5),
 <Size.EXTRA_BIG: 5>: Range(1.5, 1.82),
 <Size.ANOMAL_BIG: 6>: Range(1.82, 2.68),
 <Size.BLACKSWAN_BIG: 7>: Range(2.68, 9.4)}

То есть 0.3 короче ставим.
И надо при этом каждый раз еще сокрашать тейк? Или не надо?
Да давай пока не надо. Пока вот просто прогоним с 0.3 тейком.
А вообще - хорошая идея каждый раз тейк пересчитывать на увеличение.
Но не сильно. Допустим на каждом шаге увеличивать тейк по 0.1%.
Вот это кажется будет ахуенно. Или еще сложнее -
на каждый докупленный кусок ставить свою отдельную лимитку
с тейком +0.1
Да. Вот это будет интересно!
Но сначала давай базовую прогоним.

Вычислял что если идет бычий тренд, с симпл сайз L-XL
а их в 2023г имеется 1368 штук.
то потом, следующий медвежий тренд идет:
Counter({'L': 339, 'XL': 323, 'M': 307, 'S': 275, 'XS': 124})
969 штук размером L-XL-M
399 штук S-XS
Соотношение получается ахуенное! 0.70 / 0.29

Итак. Логика.
Пробуем торговать каждый STerm-MIN
ееееееееебать. Тут ахуеешь писать логику...
Ну давай пробовать...
Значит смотрим на прошлый STerm.
Если это минимум - запоминаем эту дату.
ставим лимитку на продажу +0.5% от этого минимума.
Ждем.
Если заявка исполнилась - ставим флаг что есть сделка и
не рыпаемся больше.
Если время идет, видим следующий максимум, а потом следующий минимум
а заявка так и не выполнилась - отменяем ее и ставим новую
от уже текущего минимума.# }}}
== Test s-0# {{{
Ну чудо опять не произошло.
Однажды стратегия упирается в накопление перед мощным бычьим движением.
Это мощное движение, может быть сильно больше 3%. Там стратегия делает
минус, и этот минус как правило перекрывает всю или почти всю прибыль.
Точнее тут сказать нельзя, надо на протяжении многих лет тест делать.
Но в общем суть такая - большинство трейдов - копейки. Вообще не
влияют на результат. Деньги получаются только там где позиция большая.
Но во время проигрыша позиция САМАЯ большая. И дает соответственно
самый большой проигрыш. На автопилот такую стратегию тяжело будет
положить, тут надо хорошо чувствовать тренд, соотноситься со
старшими таймфреймами и с уровнями поддержки сопротивления.
Учитывать глобальный л-терм дневной тренд. И избегать накоплений
перед пробоем. Все это реализовать в одной стратегии - для меня
сейчас слишком сложная задача. Надо что то попроще. Надо
двигаться последовательно. Мои стратегии с каждой итерицией
усложняются. Нарабатываются приемы, инструменты, аналитика, core
дописывается. Но до такой сложности еще далеко. Займись пока
другими вариантами стратегий. Не знаю какими - продолжай
изучать 5М тренды и думать.
# }}}
"""

from avin import *


class UStrategy(Strategy):
    MIN_STOP = 0.3
    MAX_STOP = 5
    START_LOTS = 10

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

        self.__last_trade_dt = None

    # }}}
    async def finish(self):  # {{{
        await super().finish()

    # }}}
    async def connect(self, asset: Asset, long: bool, short: bool):  # {{{
        await super().connect(asset, long, short)

        if short:
            asset.newBar5M.aconnect(self.__processShort)

    # }}}
    async def onTradeOpened(self, trade: Trade):  # {{{
        await super().onTradeOpened(trade)

        await self.__createStopLoss(trade)
        await self.__createTakeProfit(trade)
        await self.__createStairs(trade)

    # }}}
    async def onTradeClosed(self, trade: Trade):  # {{{
        await super().onTradeClosed(trade)

    # }}}

    async def __processShort(self, asset: Asset, chart_5M: Chart):  # {{{
        # проверяем последний STerm-экстремум
        elist = ExtremumList(chart_5M)
        e = elist.extr(Term.STERM, 1)
        if not self.__checkExtr(e):
            return

        # создаем трейд
        trade = await self.__createTrade(asset, e)

        # опен трейд
        if trade is not None:
            await self.__openTrade(trade)

    # }}}

    def __checkExtr(self, extr: Extremum):  # {{{
        if extr is None:
            return False

        # проверяем нет ли уже открытого трейда по этому инструменту
        if self.__hasActiveTrade(extr.asset):
            return False

        # последний экстремум - минимум, сейчас идет бычий тренд
        if not extr.isMin():
            return False

        # проверяем дату последнего экстремума
        # торгуем каждый extremum только один раз
        if self.__last_trade_dt == extr.dt:
            return False

        # обновляем дату последнего обработанного тренда
        self.__last_trade_dt = extr.dt

        return True

    # }}}
    def __hasActiveTrade(self, asset):  # {{{
        for trade in self.active_trades:
            if trade.instrument == asset:
                return True

        return False

    # }}}
    async def __createTrade(self, asset, extr):  # {{{
        # open = +0.5% от минимума
        open = round_price(extr.price * 1.005, asset.min_price_step)

        # stop = +3% от минимума
        stop = round_price(extr.price * 1.03, asset.min_price_step)

        # создаем трейд
        trade = await super().createTrade(
            dt=asset.chart("1M").now.dt,
            trade_type=Trade.Type.SHORT,
            instrument=asset,
        )
        trade.info["open_price"] = open
        trade.info["stop_price"] = stop

        return trade

    # }}}
    async def __openTrade(self, trade):  # {{{
        # создаем ордер и постим ордер
        order = await super().createLimitOrder(
            trade=trade,
            direction=Direction.SELL,
            lots=self.START_LOTS,
            price=trade.info["open_price"],
        )
        await super().postOrder(order)

    # }}}
    async def __createStopLoss(self, trade):  # {{{
        stop_loss = await super().createStopLoss(
            trade,
            stop_price=trade.info["stop_price"],
        )
        await super().postStopLoss(stop_loss)

    # }}}
    async def __createTakeProfit(self, trade):  # {{{
        # на случай если тем временем уже стоп сработал,
        # тогда не имеет смысла делать лимитки дополнительные лесенкой
        if trade.status == Trade.Status.CLOSED:
            return

        open = trade.openPrice()
        take = round_price(open * 0.997, trade.instrument.min_price_step)
        trade.info["take_price"] = take
        take_profit = await super().createTakeProfit(
            trade,
            take_price=take,
        )
        await super().postTakeProfit(take_profit)

    # }}}
    async def __createStairs(self, trade: Trade):  # {{{
        # на случай если тем временем уже стоп сработал,
        # тогда не имеет смысла делать лимитки дополнительные лесенкой
        if trade.status == Trade.Status.CLOSED:
            return

        open = trade.openPrice()
        stop = trade.stopPrice()
        min_price_step = trade.instrument.min_price_step

        step = open * 0.003  # 0.2%
        stair = round_price(open + step, min_price_step)
        n = 1
        while stair < stop:
            order = await super().createLimitOrder(
                trade=trade,
                direction=Direction.SELL,
                lots=abs(trade.lots() * n),
                price=stair,
            )
            order.executed.aconnect(self.__onStrait)
            await super().postOrder(order)

            n *= 2
            stair = round_price(stair + step, min_price_step)

    # }}}
    async def __onStrait(self, order, operation):  # {{{
        trade = self.active_trades.find(order.trade_id)

        # update stop loss
        sl = trade.stopLoss()
        await super().cancelOrder(sl)
        sl.lots = abs(trade.lots())
        sl.quantity = abs(trade.quantity())
        await Order.update(sl)
        await super().postStopLoss(sl)

        # update take profit
        tp = trade.takeProfit()
        await super().cancelOrder(tp)

        tp.lots = abs(trade.lots())
        tp.quantity = abs(trade.quantity())

        avg = trade.sellAverage()
        n = self.__getStraitNumber(trade)
        new_take_price = avg * (0.997 - n * 0.001)
        new_take_price = round_price(
            new_take_price, trade.instrument.min_price_step
        )
        tp.stop_price = new_take_price
        tp.exec_price = new_take_price
        await Order.update(tp)

        await super().postTakeProfit(tp)

    def __getStraitNumber(self, trade):
        # n = 1   -> вход, удвоений не было - strait 0
        # n = 2   -> 1 удвоение было - strait 1
        # n = 4   -> 2 удвоение было - strait 2
        # n = 8   -> 3 удвоение было - strait 3
        # n = 16  -> 4 удвоение было - strait 4
        # ...
        n = round(abs(trade.lots()) / self.START_LOTS)

        match n:
            case 1:
                return 0
            case 2:
                return 1
            case 4:
                return 2
            case 8:
                return 3
            case 16:
                return 4
            case 32:
                return 5
            case 64:
                return 6
            case 128:
                return 7
            case 256:
                return 8
            case 512:
                return 9
            case 1024:
                return 10


# }}}
