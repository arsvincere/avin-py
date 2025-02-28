#!/usr/bin/env  python3

import asyncio

from avin import *


async def main():
    test = await Test.load("Vawe_5M_MTerm_Follow-l-0-quarter_1-AFKS")
    test = await Test.load("Vawe_5M_MTerm_Follow-l-0-2023_4-AFKS")
    await Test.loadTrades(test)

    # await filteringType(test)
    # await filteringDelta(test)
    # await filteringDeltaSimple(test)
    # await filteringPeriod(test)
    # await filteringSpeed(test)
    # await filteringVolume(test)
    await printResult(test)


async def filteringType(test):  # {{{
    logger.info(":: Trend filtering type")

    await TrendAnalytic.filtering(
        test, TimeFrame("5M"), Term.STERM, TrendAnalytic.Analyse.TYPE, 0
    )
    await TrendAnalytic.filtering(
        test, TimeFrame("1H"), Term.STERM, TrendAnalytic.Analyse.TYPE, 0
    )
    await TrendAnalytic.filtering(
        test, TimeFrame("D"), Term.STERM, TrendAnalytic.Analyse.TYPE, 0
    )

    await TrendAnalytic.filtering(
        test, TimeFrame("5M"), Term.MTERM, TrendAnalytic.Analyse.TYPE, 0
    )
    await TrendAnalytic.filtering(
        test, TimeFrame("1H"), Term.MTERM, TrendAnalytic.Analyse.TYPE, 0
    )
    await TrendAnalytic.filtering(
        test, TimeFrame("D"), Term.MTERM, TrendAnalytic.Analyse.TYPE, 0
    )

    await TrendAnalytic.filtering(
        test, TimeFrame("5M"), Term.LTERM, TrendAnalytic.Analyse.TYPE, 0
    )
    await TrendAnalytic.filtering(
        test, TimeFrame("1H"), Term.LTERM, TrendAnalytic.Analyse.TYPE, 0
    )
    await TrendAnalytic.filtering(
        test, TimeFrame("D"), Term.LTERM, TrendAnalytic.Analyse.TYPE, 0
    )


# }}}
async def filteringDelta(test):  # {{{
    logger.info(":: Trend filtering delta")

    timeframes = [
        # TimeFrame("5M"),
        TimeFrame("1H"),
        TimeFrame("D"),
    ]
    termes = [
        Term.STERM,
    ]
    numbers = [0]
    analyse = TrendAnalytic.Analyse.DELTA

    for tf in timeframes:
        for term in termes:
            for n in numbers:
                await TrendAnalytic.filtering(test, tf, term, n, analyse)


# }}}
async def filteringDeltaSimple(test):  # {{{
    logger.info(":: Trend filtering delta")

    timeframes = [
        TimeFrame("5M"),
        TimeFrame("1H"),
        TimeFrame("D"),
    ]
    termes = [
        Term.STERM,
    ]
    numbers = [0, 1, 2]
    analyse = TrendAnalytic.Analyse.DELTA

    for tf in timeframes:
        for term in termes:
            for n in numbers:
                await TrendAnalytic.filteringDeltaSimple(
                    test.trade_list, tf, term, n
                )


# }}}
async def filteringPeriod(test):  # {{{
    logger.info(":: Trend filtering period")

    timeframes = [
        # TimeFrame("5M"),
        # TimeFrame("1H"),
        TimeFrame("D"),
    ]
    termes = [
        Term.STERM,
    ]
    numbers = [1]
    analyse = TrendAnalytic.Analyse.PERIOD

    for tf in timeframes:
        for term in termes:
            for n in numbers:
                await TrendAnalytic.filtering(test, tf, term, n, analyse)


# }}}
async def filteringSpeed(test):  # {{{
    logger.info(":: Trend filtering speed")

    timeframes = [
        # TimeFrame("5M"),
        # TimeFrame("1H"),
        TimeFrame("D"),
    ]
    termes = [
        Term.STERM,
    ]
    numbers = [1]
    analyse = TrendAnalytic.Analyse.SPEED

    for tf in timeframes:
        for term in termes:
            for n in numbers:
                await TrendAnalytic.filtering(test, tf, term, n, analyse)


# }}}
async def filteringVolume(test):  # {{{
    logger.info(":: Trend filtering volume")

    timeframes = [
        # TimeFrame("5M"),
        # TimeFrame("1H"),
        TimeFrame("D"),
    ]
    termes = [
        Term.STERM,
    ]
    numbers = [1]
    analyse = TrendAnalytic.Analyse.VOLUME

    for tf in timeframes:
        for term in termes:
            for n in numbers:
                await TrendAnalytic.filtering(test, tf, term, n, analyse)


# }}}
async def printResult(test):  # {{{
    trade_list = test.trade_list
    summary = Summary(trade_list)
    df = summary.data_frame
    print(df)

    print("-" * 80)
    df = df.sort_values("%", ascending=False)
    print(df)
    file_path = Cmd.path(Usr.RESEARCH, f"{test.name}.csv")
    df.to_csv(file_path, sep=";")


# }}}

if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
