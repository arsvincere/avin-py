#!/usr/bin/env  python3

import asyncio

from avin import *

"""Загрузка биржевых данных с MOEX"""


async def main():
    await Data.cache()
    await Data.updateAll()
    return

    tickers = [  # {{{
        "AFKS",
        "AFLT",
        "ALRS",
        "ASTR",
        "BANE",
        "BANEP",
        "CHMF",
        "ENPG",
        "FEES",
        "FLOT",
        "GAZP",
        "HYDR",
        "IRAO",
        "LKOH",
        "LSRG",
        "MAGN",
        "MOEX",
        "MTLRP",
        "MTSS",
        "MVID",
        "NLMK",
        "NMTP",
        "NVTK",
        "OZON",
        "PIKK",
        "POSI",
        "RASP",
        "RNFT",
        "ROSN",
        "RTKM",
        "RTKMP",
        "RUAL",
        "SBER",
        "SBERP",
        "SELG",
        "SIBN",
        "SNGS",
        "SNGSP",
        "TATN",
        "TATNP",
        "TRMK",
        "UPRO",
        "VTBR",
        "YDEX",
    ]
    # }}}

    download_list = list()  # {{{
    for ticker in tickers:
        instrument = await Data.find(
            Exchange.MOEX,
            Instrument.Type.FUTURE,
            ticker,
        )
        instrument = instrument[0]
        download_list.append(instrument)

    # }}}

    # download D  # {{{
    data_types = [DataType.BAR_D]
    for instrument in download_list:
        dt = await Data.firstDateTime(
            DataSource.MOEX, instrument, DataType.BAR_D
        )
        begin_year = dt.year
        end_year = Date.today().year
        years = range(begin_year, end_year + 1)

        for data_type in data_types:
            for year in years:
                await Data.download(
                    DataSource.MOEX, instrument, data_type, year
                )
    # }}}

    # download 1M  # {{{
    data_types = [DataType.BAR_1M]
    for instrument in download_list:
        dt = await Data.firstDateTime(
            DataSource.MOEX, instrument, DataType.BAR_1M
        )
        begin_year = dt.year
        end_year = Date.today().year
        years = range(begin_year, end_year + 1)

        for data_type in data_types:
            for year in years:
                await Data.download(
                    DataSource.MOEX, instrument, data_type, year
                )
    # }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
