#!/usr/bin/env  python3

import asyncio

from avin import *
from usr import *


async def main():
    # conf
    ASSETS = await AssetList.load("XX5")
    STRATEGY = await Strategy.load("Vawe_5M_MTerm_Follow", "l-0")
    BEGIN = Date(2020, 1, 1)
    END = Date(2023, 1, 1)
    NAME = f"{STRATEGY.name}-{STRATEGY.version} {BEGIN} -> {END}"

    # create & save test list
    # await createTestList(NAME, ASSETS, STRATEGY, BEGIN, END)

    # run tests
    test_list = await TestList.load(NAME)
    tester = Tester()
    for test in test_list:
        if test.status != Test.Status.COMPLETE:
            await tester.run(test)


async def createTestList(name, assets, strategy, begin, end) -> list:  # {{{
    tests = list()
    for asset in assets:
        info = await Data.info(asset, DataType.BAR_1M)
        first = info.first_dt.date()
        if first >= end:
            # YDEX - данные только с 2024 г, соответственно в тестах
            # на данных до 2024г тестировать нечего, и вообще любой актив
            # получается если для него нет данных - пропускаем
            continue

        test_name = f"{name}-{asset.ticker}"
        logger.info(f"Create test {test_name}")
        test = Test(test_name)
        test.asset = asset
        test.strategy = strategy
        test.begin = begin
        test.end = end

        tests.append(test)

    logger.info(f":: Create TestList {name}")
    test_list = TestList(name, tests)
    await TestList.save(test_list)
    logger.info(f"   {test_list} saved")


# }}}


if __name__ == "__main__":
    configureLogger(debug=False, info=True)
    asyncio.run(main())
