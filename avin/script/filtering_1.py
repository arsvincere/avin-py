#!/usr/bin/env  python3

import asyncio

from avin import *

configureLogger(debug=False, info=True)

TEST_LIST_NAME = "OCShadow-s-1"
FILTER_LIST_NAMES = (
    "size b1 body",
    "size b2 body",
    "size b1 upper",
    "volume D b1",
    "volume D b2",
    "time",
    "fear high",
)
PERCENT = None


async def main():
    test_list = await TestList.load(TEST_LIST_NAME)
    # ####
    # test_list = TestList("blablabla")
    # test = await Test.load("OCShadow-s-1-AFKS")
    # test_list.add(test)
    # ####

    for test in test_list:
        await filtering(test)


async def filtering(test):  # {{{
    logger.info(f":: Filtering {test}")

    all_filter_lists = list()
    for name in FILTER_LIST_NAMES:
        filter_list = FilterList.load(name)
        all_filter_lists.append(filter_list)

    trade_list = test.trade_list
    for filter_list in all_filter_lists:
        logger.info(f"   Filtering {filter_list.full_name} {test.asset}")
        good_filters = await filteringList(trade_list, filter_list)

        # load or create good filter list
        good_filter_list_name = (
            "_auto "
            f"{test.strategy.name} "
            f"{test.strategy.version} "
            f"{test.asset.ticker} "
            f"{filter_list.name}"
        )
        good_filter_list = FilterList(good_filter_list_name)

        # add new good filter
        for f in good_filters:
            good_filter_list.add(f)

        # save
        FilterList.save(good_filter_list)
        good_filters.clear()


# }}}
async def filteringList(trade_list, filter_list) -> list[Filter]:  # {{{
    if PERCENT is None:
        # если процент желаемой точности не задан, то выбираем
        # просто все что улушает точность по сравнению с нефильтрованным
        # полным трейд листом
        base_profitable = Summary.percentProfitable(trade_list)
    else:
        base_profitable = PERCENT

    good_filters = list()
    for f in filter_list:
        logger.info(f"   - apply filter: {f.full_name}")
        child = await trade_list.selectFilter(f)
        profitable = Summary.percentProfitable(child)

        if profitable > base_profitable:
            good_filters.append(f)

    return good_filters


# }}}


if __name__ == "__main__":
    asyncio.run(main())
