#!/usr/bin/env  python3
# FILE:         tmp.py
# CREATED:      2023.09.24
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

import logging
logger = logging.getLogger("LOGGER")
console_log = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
    )
console_log.setFormatter(formatter)
console_log.setLevel(logging.INFO)
logger.addHandler(console_log)
logger.setLevel(logging.INFO)

import sys
sys.path.append("/home/yandex/avin-dev/avin")
sys.path.append("/usr/lib/python3.11/site-packages")
sys.path.append("/home/alex/.local/lib/python3.11/site-packages/tinkoff")
sys.path.append("/home/alex/.local/lib/python3.11/site-packages/tinkoff/invest")
import json
import uuid
import bisect
import typing
import importlib
import dataclasses
import collections
import time as timer
import pandas as pd
import numpy as np
from datetime import datetime, date, time, timedelta
from avin.utils import *
from avin.const import *
from avin.core import *
from avin.company import *
from avin.gui import *

from tinkoff.invest import (
    CandleInstrument,
    Client,
    InfoInstrument,
    SubscriptionInterval,
)

TOKEN = ("t.ft4wS11u1nCcPALQeW59yJxH3cwXqVBy0DEdwoGE00kPlF5U-7ZX0p_"
         "E2uGuFELbvya9r8vTGKDi22svrIKDcw")
# ----------------------------------------------------------------------------

import asyncio
import os

from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    InfoInstrument,
    SubscriptionInterval,
)
from tinkoff.invest.async_services import AsyncMarketDataStreamManager
from tinkoff.invest.services import MarketDataStreamManager

from avin.company import Tinkoff
import time as timer

async def main():

# # получить объект, допускающий ожидание, выполнив один шаг итератора
#     awaitable = anext(it)
# # выполнить один шаг итератора и получить результат
#     result = await awaitable

    async with AsyncClient(TOKEN) as client:
        market_data_stream: AsyncMarketDataStreamManager = (
            client.create_market_data_stream()
        )
        market_data_stream.candles.waiting_close().subscribe(
            [
                CandleInstrument(
                    figi="BBG004730N88",
                    interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                )
            ]
        )

        # it = market_data_stream.__aiter__()
        # nxt = market_data_stream.__anext__()
        awaitable = anext(market_data_stream)

        # print("stream:", market_data_stream)
        # print("it", it)
        # print("nxt", nxt)
        print("awaitable", awaitable)
        result = await awaitable
        print(result)

        # async for marketdata in market_data_stream:
        #     # print(marketdata)
        #
        #     candle = marketdata.candle
        #     # print(candle)
        #     if candle is not None:
        #         bar = Tinkoff._getBar(candle)
        #         print(bar)
        #
        #     print("do something")



        awaitable = anext(market_data_stream)
        result = await awaitable
        print(result)

        awaitable = anext(market_data_stream)
        result = await awaitable
        print(result)

        awaitable = anext(market_data_stream)
        result = await awaitable
        print(result)


if __name__ == "__main__":
    asyncio.run(main())


