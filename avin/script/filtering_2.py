#!/usr/bin/env  python3

import asyncio

from avin import *

configureLogger(debug=False, info=True)

# filtering_2 - create deep filter


async def main():
    TEST_LIST_NAME = "OCShadow-l-0"
    test_list = await TestList.load(TEST_LIST_NAME)
    # ####
    # test_list = TestList("blablabla")
    # test = await Test.load("OCShadow-l-0-AFKS")
    # test_list.add(test)
    # ####

    for test in test_list:
        await filteringGood(test)
        clearEmptySubLists(test.trade_list)
        await createDeepFilterList(test)


async def filteringGood(test):  # {{{
    logger.info(f":: Filtering good {test}")

    good_filter_list_name = (
        f"_auto "
        f"{test.strategy.name} "
        f"{test.strategy.version} "
        f"{test.asset.ticker} "
    )
    good_filter_list = FilterList.load(good_filter_list_name)
    trade_list = test.trade_list

    for filter_list in good_filter_list.childs:
        await filteringGoodAnyOf(trade_list, filter_list)


# }}}
async def filteringGoodAnyOf(trade_list, filter_list) -> list[Filter]:  # {{{
    logger.info(f"   Filtering any of {filter_list.full_name}")
    await trade_list.anyOfFilterList(filter_list)

    for child_filter_list in filter_list.childs:
        await filteringGoodAnyOf(trade_list, child_filter_list)


# }}}
def clearEmptySubLists(trade_list):  # {{{
    i = 0
    while i < len(trade_list.childs):
        child_trade_list = trade_list.childs[i]
        if len(child_trade_list) == 0:
            trade_list.removeChild(child_trade_list)
        else:
            i += 1

    for child in trade_list.childs:
        clearEmptySubLists(child)


# }}}
async def createDeepFilterList(test):  # {{{
    df = Summary.calculate(test.trade_list)
    df = df.sort_values("win", ascending=False)

    deep_list_name = (
        f"_deep "
        f"{test.strategy.name} "
        f"{test.strategy.version} "
        f"{test.asset.ticker} "
    )
    deep_filter_list = FilterList(deep_list_name)

    current = test.trade_list
    for i in df.index:
        if i == 0:
            continue  # это общий трейд лист без фильтров

        # загружаем фильтр лист
        # они в df отсортированы по количеству выигрышных трейдов
        name = df.loc[i]["name"]
        filter_list = FilterList.load(name)

        # достаем из него фильтры, и добавляем в новый фильтр лист
        # чтобы сменить родителя у фильтра
        sub_filter_list = FilterList("")
        for f in filter_list.filters:
            sub_filter_list.add(f)

        # применяем это фильтр лист пачкой, смотрим % успеха
        child = await current.anyOfFilterList(sub_filter_list)
        percent = int(Summary.percentProfitable(child))

        # присваиваем фильтр листу имя = %
        # для более правильной сортировки по имени меняем 100% -> 99%
        # и так даже правильнее, вероятность то не 100%, просто не было
        # ни одного проигрышного трейда
        if percent == 100:
            percent = 99
        sub_filter_list.name = str(percent)

        # добавляем его ребенком к главному deep фильтр лист
        deep_filter_list.addChild(sub_filter_list)

        # селектнутый этим фильтр листом трейд лист ставим текущим
        # следующая итерация будет фильтровать уже его
        current = child

    FilterList.save(deep_filter_list)


# }}}


if __name__ == "__main__":
    asyncio.run(main())
