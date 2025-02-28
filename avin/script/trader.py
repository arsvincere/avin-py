#!/usr/bin/env  python3

import asyncio
from datetime import date

from avin import *


async def main():
    trader = Trader()
    try:
        await trader.initialize()
        await trader.run()
    except Exception as e:
        logger.exception(e)
        exit(9999)


    t = Test("_unittest")
    assert t.status == Test.Status.NEW
    assert t.name == "_unittest"

    t.description = "descr"
    t.strategy = "Every"
    t.version = "day"
    t.deposit = 100_000.0
    t.commission = 0.0005
    t.begin = date(2023, 08, 01)
    t.end = date(2023, 09, 01)
    await Test.save(t)

    loaded = Test.load(t._name)
    assert loaded.name == t.name
    assert loaded.status == t.status
    assert loaded.description == t.description
    assert loaded.strategy == t.strategy
    assert loaded.version == t.version
    assert loaded.deposit == t.deposit
    assert loaded.commission == t.commission
    assert loaded.begin == t.begin
    assert loaded.end == t.end

    await Test.rename(loaded, "_unittest_new_name")






if __name__ == "__main__":
    asyncio.run(main())
