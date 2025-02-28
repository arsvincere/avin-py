#!/usr/bin/env python3

import asyncio

from tinkoff.invest import (
    CandleInstrument,
    Client,
    SubscriptionInterval,
)
from tinkoff.invest.services import MarketDataStreamManager

from avin import *

TOKEN = Tinkoff.TOKEN


async def main():
    afks = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "AFKS")
    sber = await Asset.byTicker(AssetType.SHARE, Exchange.MOEX, "SBER")
    with Client(TOKEN) as client:
        market_data_stream: MarketDataStreamManager = (
            client.create_market_data_stream()
        )
        market_data_stream.candles.waiting_close().subscribe(
            [
                CandleInstrument(
                    figi=afks.figi,
                    interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                ),
                CandleInstrument(
                    figi=sber.figi,
                    interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                ),
            ]
        )
        for marketdata in market_data_stream:
            # print(marketdata)

            candle = marketdata.candle
            print(candle)
            # if candle is not None:
            #     bar = Tinkoff._getBar(candle)
            #     print(bar)
            #
            # print("do something")

            # market_data_stream.info.subscribe([InfoInstrument(figi="BBG004730N88")])
            # if marketdata.subscribe_info_response:
            #     market_data_stream.stop()


if __name__ == "__main__":
    asyncio.run(main())
