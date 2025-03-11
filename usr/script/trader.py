#!/usr/bin/env  python3

import asyncio

from avin import *

"""Запуск трейдера в боевом режиме"""


async def main():
    trader = Trader()
    try:
        await trader.initialize()
        await trader.run()
    except Exception as e:
        logger.exception(e)
        exit(9999)


if __name__ == "__main__":
    asyncio.run(main())
