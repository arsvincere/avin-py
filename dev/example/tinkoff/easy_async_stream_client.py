#!/usr/bin/env python3
import asyncio

from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    SubscriptionInterval,
)
from tinkoff.invest.async_services import AsyncMarketDataStreamManager

from avin import *

TOKEN = Tinkoff.TOKEN


async def main():
    async with AsyncClient(TOKEN) as client:
        market_data_stream: AsyncMarketDataStreamManager = (
            client.create_market_data_stream()
        )
        # market_data_stream.candles.waiting_close().subscribe(
        #     [
        #         CandleInstrument(
        #             figi="BBG004730N88",
        #             interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
        #         )
        #     ]
        # )
        market_data_stream.candles.subscribe(
            [
                CandleInstrument(
                    figi="BBG004S68CP5",
                    interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                ),
                CandleInstrument(
                    figi="BBG004730N88",
                    interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                ),
            ]
        )
        async for marketdata in market_data_stream:
            print(marketdata)

            candle = marketdata.candle
            print(candle)
            # if candle is not None:
            #     bar = Tinkoff._getBar(candle)
            #     print(bar)

            print("do something")


if __name__ == "__main__":
    asyncio.run(main())
