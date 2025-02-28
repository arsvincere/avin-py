#!/usr/bin/env python3

import sys
import asyncio
import logging
import os
from datetime import timedelta
sys.path.append("/home/alex/.local/lib/python3.9/site-packages")
from tinkoff.invest import CandleInterval
from tinkoff.invest.retrying.aio.client import AsyncRetryingClient
from tinkoff.invest.retrying.settings import RetryClientSettings
from tinkoff.invest.utils import now
sys.path.append("/home/alex/AVIN/")
from avin.const import (
    TOKEN_READ,
    )

logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.DEBUG)

retry_settings = RetryClientSettings(use_retry=True, max_retry_attempt=2)


async def main():

    async with AsyncRetryingClient(TOKEN_READ, settings=retry_settings) as client:
        async for candle in client.get_all_candles(
            figi="BBG004S68614",
            from_=now() - timedelta(minutes=2),
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            print(candle)


if __name__ == "__main__":
    asyncio.run(main())
