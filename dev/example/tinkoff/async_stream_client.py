#!/usr/bin/env python3

import asyncio

from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
)

from avin import Tinkoff

TOKEN = Tinkoff.TOKEN
"""
    на основе этого кода можно сделать запрос последней реал-тайм свечи
    и обновлять ее, перерисовывая, а когда приходит новая свеча (смотрим
    по времени свечи) тогда старую добавляем в историческую а новую
    рисуем
"""


async def main():
    async def request_iterator():
        yield MarketDataRequest(
            subscribe_candles_request=SubscribeCandlesRequest(
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                instruments=[
                    CandleInstrument(
                        figi="BBG004730N88",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    )
                ],
            )
        )
        while True:
            await asyncio.sleep(1)

    async with AsyncClient(TOKEN) as client:
        async for marketdata in client.market_data_stream.market_data_stream(
            request_iterator()
        ):
            print(marketdata)

            candle = marketdata.candle
            print(candle)
            # if candle is not None:
            #     bar = Tinkoff._getBar(candle)
            #     print(bar)


if __name__ == "__main__":
    asyncio.run(main())
