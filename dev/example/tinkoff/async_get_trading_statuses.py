#!/usr/bin/env python3

import asyncio
import os

from tinkoff.invest import AsyncClient

token = os.environ["INVEST_TOKEN"]


async def main():
    async with AsyncClient(token) as client:
        statuses = await client.market_data.get_trading_statuses(
            instrument_ids=["BBG004730N88"]
        )
        print(statuses)

        trading_status = await client.market_data.get_trading_status(
            figi="BBG004730N88"
        )
        print(trading_status)

if __name__ == "__main__":
    asyncio.run(main())

