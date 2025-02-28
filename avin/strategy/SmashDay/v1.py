#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================


from avin import *


class UStrategy(Strategy):
    CONFIRM = 0
    CANCEL = 1
    WAIT = 2

    def __init__(self):  # {{{
        name = Cmd.dirName(__file__)
        version = Cmd.name(__file__)
        Strategy.__init__(self, name, version)

    # }}}

    def timeframes(self):  # {{{
        tf_list = TimeFrameList(
            [
                TimeFrame("1M"),
                TimeFrame("D"),
            ]
        )
        return tf_list

    # }}}
    async def start(self):  # {{{
        await super().start()
        self.waiting_list = list()

    # }}}
    async def finish(self):  # {{{
        await super().finish()
        self.waiting_list.clear()

    # }}}
    async def connect(self, asset: Asset, long: bool, short: bool):  # {{{
        await super().connect(asset, long, short)

        if long:
            asset.newBarD.aconnect(self.__processLong)

        if short:
            asset.newBarD.aconnect(self.__processShort)

        asset.newBar1M.aconnect(self.__processWaitings)

    # }}}
    async def onTradeOpened(self, trade: Trade):  # {{{
        await super().onTradeOpened(trade)

        stop_loss = await super().createStopLoss(
            trade, stop_price=trade.info["stop_price"]
        )
        await trade.attachOrder(stop_loss)
        await super().postOrder(stop_loss)

        take_profit = await super().createTakeProfit(
            trade, take_price=trade.info["take_price"]
        )
        await trade.attachOrder(take_profit)
        await super().postOrder(take_profit)

    # }}}
    async def onTradeClosed(self, trade: Trade):  # {{{
        await super().onTradeClosed(trade)

    # }}}

    async def __processLong(self, asset: Asset, chart_D: Chart):  # {{{
        # chart_D - TimeFrame D
        if chart_D[2] is None:
            return

        b2: Bar = chart_D[2]
        b1: Bar = chart_D[1]
        b0: Bar = chart_D[0]  # now
        if not (
            # Позавчерашний бар бычий
            b2.isBull()
            # Вчера верхняя тень более 1%
            and b1.upper.percent() > 1
            # Вчера закрытие с повышением
            and b1.close > b2.close
            # Вчера закрытие в нижней половине
            and b1.close in b1.range.half(1)
        ):
            return

        # Базовые условия выполнены, создаем trade в waiting_list
        trade = await super().createTrade(
            dt=asset.chart("1M").now.dt,
            trade_type=Trade.Type.LONG,
            instrument=asset,
        )
        open_price = b1.high + asset.min_price_step
        stop_price = b1.low
        take_price = open_price + 3 * abs(open_price - stop_price)
        trade.info["open_price"] = open_price
        trade.info["stop_price"] = stop_price
        trade.info["take_price"] = take_price
        trade.info["confirm_price"] = open_price
        trade.info["cancel_price"] = stop_price

        # pprint(trade.info)
        # input("=== new long trade")

        self.waiting_list.append(trade)

    # }}}
    async def __processShort(self, asset: Asset, chart_D: Chart):  # {{{
        return

        b2 = chart_D[2]
        b1 = chart_D[1]
        # Позавчерашний бар медвежий
        if not (
            b2.isBear()
            # Вчера нижняя тень более 1%
            and b1.lshadow.percent() > 1
            # # Вчера закрытие с понижением
            and b1.close < b2.close
            # Вчера закрытие в верхней половине
            and b1.close in b1.range.half(2)
        ):
            return False

        # Базовые условия выполнены, создаем сигнал в waiting_list
        open_price = b1.low - asset.min_price_step
        stop_price = b1.high
        take_price = open_price - 3 * abs(open_price - stop_price)
        s = Signal(
            dt=asset.chart("1M").now.dt,
            strategy=self,
            signal_type=Signal.Type.SHORT,
            asset=asset,
            open_price=open_price,
            stop_price=stop_price,
            take_price=take_price,
            open_order_type=Order.Type.LIMIT,
            close_condition=Signal.Close.STOP_TAKE,
            status=Signal.Status.INITIAL,
        )
        confirm_price = s.open_price
        cancel_price = s.stop_price
        s.info["strategy"]["confirm_price"] = confirm_price
        s.info["strategy"]["cancel_price"] = cancel_price
        self.waiting_list.append(s)

    # }}}
    async def __processWaitings(self, asset, chart_1M):  # {{{
        i = 0
        while i < len(self.waiting_list):
            trade = self.waiting_list[i]
            result = self.__checkWaitingTrade(trade, chart_1M)

            match result:
                case UStrategy.CONFIRM:
                    await self.__openTrade(trade, asset, chart_1M)
                    self.waiting_list.pop(i)
                case UStrategy.CANCEL:
                    canceled_trade = self.waiting_list.pop(i)
                    await super().cancelTrade(canceled_trade)
                case UStrategy.WAIT:
                    i += 1

    # }}}
    def __checkWaitingTrade(self, trade, chart_1M):  # {{{
        bar: Bar = chart_1M.last
        cancel_price = trade.info["cancel_price"]
        confirm_price = trade.info["confirm_price"]

        # pprint(trade.info)
        # print("cancel=", cancel_price, cancel_price in bar)
        # print("confirm=", confirm_price, confirm_price in bar)
        # print(bar)

        # check price
        match trade.type:
            case Trade.Type.LONG:
                if bar.low < cancel_price:
                    return UStrategy.CANCEL
                if bar.high > confirm_price:
                    return UStrategy.CONFIRM
            case Trade.Type.SHORT:
                if bar.high > cancel_price:
                    return UStrategy.CANCEL
                if bar.low < confirm_price:
                    return UStrategy.CONFIRM

        # check datetime
        now_dt = bar.dt

        # print(now_dt.date(), trade.dt.date())
        # print(now_dt.date() != trade.dt.date())
        # input("=== check")

        if now_dt.date() != trade.dt.date():
            return UStrategy.CANCEL

        return UStrategy.WAIT

    # }}}
    async def __openTrade(self, trade, asset, chart_1M):  # {{{
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


if __name__ == "__main__":
    ...
