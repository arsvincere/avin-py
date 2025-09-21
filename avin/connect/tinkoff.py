# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import asyncio

import tinkoff.invest as ti
from PyQt6 import QtCore

from avin.connect.ti_to_av import ti_to_av
from avin.core import BarEvent, TicEvent
from avin.utils import CFG, AvinError, Cmd, log

NAME = "Tinkoff"
TARGET = ti.constants.INVEST_GRPC_API
TOKEN = Cmd.read(CFG.Connect.tinkoff_token).strip()


class Tinkoff(QtCore.QThread):
    new_bar = QtCore.pyqtSignal(BarEvent)
    new_tic = QtCore.pyqtSignal(TicEvent)

    def __init__(self, parent):
        QtCore.QThread.__init__(self, parent)

        self.client = None
        self.data_stream = None

        self.__connect_task = None
        self.__data_task = None

    def run(self):
        asyncio.run(self.__main_loop())

    # loops
    async def __main_loop(self):
        await self.__ensure_connect()
        await self.__ensure_data_stream()

        while True:
            await asyncio.sleep(1)

    async def __connect_loop(self):
        async with ti.AsyncClient(TOKEN, target=TARGET) as client:
            self.client = client

            while True:
                await asyncio.sleep(2)

        self.client = None

    async def __data_loop(self):
        """Response example

        MarketDataResponse(
            subscribe_candles_response=None,
            subscribe_order_book_response=None,
            subscribe_trades_response=None,
            subscribe_info_response=None,
            subscribe_last_price_response=None,
            candle=Candle(
                figi='BBG004S68CP5',
                interval=
                  <SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE: 1>,
                open=Quotation(units=101, nano=700000000),
                high=Quotation(units=101, nano=900000000),
                low=Quotation(units=101, nano=700000000),
                close=Quotation(units=101, nano=900000000),
                volume=225,
                time=datetime.datetime(
                    2024, 9, 10, 11, 54,
                    tzinfo=datetime.timezone.utc
                ),
                last_trade_ts=datetime.datetime(
                    2024, 9, 10, 11, 54, 30, 770361,
                    tzinfo=datetime.timezone.utc),
                instrument_uid='cf1c6158-a303-43ac-89eb-9b1db8f96043'),
            trade=None,
            orderbook=None,
            trading_status=None,
            last_price=None
            ping=None,
            )
        """

        self.data_stream = self.client.create_market_data_stream()

        async for response in self.data_stream:
            if response.candle:
                figi = response.candle.figi
                bar = ti_to_av(response.candle)
                event = BarEvent(figi, bar)
                self.new_bar.emit(event)

            if response.trade:
                figi = response.trade.figi
                tic = ti_to_av(response.trade)
                event = TicEvent(figi, tic)
                self.new_tic.emit(event)

        # если цикл закончился
        self.data_stream = None

    # private
    async def __ensure_connect(self):
        # run connection loop
        self.__connect_task = asyncio.create_task(self.__connect_loop())

        # await connection
        seconds_elapsed = 0
        while self.client is None:
            log.info(f"- waiting connection... ({seconds_elapsed} sec)")
            await asyncio.sleep(1)
            seconds_elapsed += 1

            if seconds_elapsed == 5:
                raise AvinError("Fail to connect Tinkoff")

        log.info("Connection successfully started!")

    async def __ensure_data_stream(self):
        # run market data task
        self.__data_task = asyncio.create_task(self.__data_loop())

        seconds_elapsed = 0
        while self.data_stream is None:
            log.info(f"- waiting data stream... ({seconds_elapsed} sec)")
            await asyncio.sleep(1)
            seconds_elapsed += 1

            if seconds_elapsed == 5:
                raise AvinError("Fail to start data stream Tinkoff")

        log.info("Data stream successfully started!")
