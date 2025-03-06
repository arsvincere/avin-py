#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import collections
from abc import ABC

import pandas as pd

from avin.analytic.size import Size
from avin.config import Usr
from avin.core.asset import Asset
from avin.utils import Cmd, logger


class Analytic(ABC):  # {{{
    @classmethod  # save  # {{{
    def save(
        cls, asset: Asset, analyse_name: str, data_frame: pd.DataFrame
    ) -> None:
        logger.debug(f"{cls.__name__}.save()")

        file_path = cls.__getFilePath(asset, analyse_name)
        dir_path = Cmd.dirPath(file_path)
        Cmd.makeDirs(Cmd.dirPath(file_path))

        data_frame.to_parquet(file_path)

    # }}}
    @classmethod  # load  # {{{
    def load(cls, asset: Asset, analyse_name: str) -> pd.DataFrame | None:
        logger.debug(f"{cls.__name__}.load()")

        file_path = cls.__getFilePath(asset, analyse_name)
        if not Cmd.isExist(file_path):
            logger.error(f"Analyse file not found: {file_path}")
            return None

        df = pd.read_parquet(file_path)

        return df

    # }}}

    @classmethod  # _classifySizes  # {{{
    def _classifySizes(cls, value_list: list) -> pd.DataFrame:
        assert len(value_list) > 100

        df = cls.__createClassifyDataFrame(value_list)
        sizes_df = cls.__createSizesDataFrame(df)
        return sizes_df

    # }}}
    @classmethod  # _identifySize  # {{{
    def _identifySize(cls, value, sizes: pd.DataFrame) -> Size:
        s = sizes.loc[((sizes["begin"] <= value) & (value <= sizes["end"]))]

        if len(s) > 0:
            size = Size.fromStr(s.index[0])
            return size

        lowest = sizes["begin"]["GREATEST_SMALL"]
        if value < lowest:
            return Size.BLACKSWAN_SMALL

        highest = sizes["begin"]["GREATEST_BIG"]
        if value > highest:
            return Size.BLACKSWAN_BIG

        print(sizes)
        print(value)
        print(s)
        input("WTF")

    # }}}

    @classmethod  # __getFilePath  # {{{
    def __getFilePath(cls, asset: Asset, analyse_name: str):
        logger.debug(f"{cls.__name__}.__getFilePath()")

        path_parts = str(asset).split() + analyse_name.split()
        file_path = Cmd.path(Usr.ANALYSE, *path_parts)
        file_path += ".parquet"

        return file_path

    # }}}
    @classmethod  # __createClassifyDataFrame  # {{{
    def __createClassifyDataFrame(cls, value_list: list):
        amount = len(value_list)
        counter = collections.Counter(value_list)
        sorted_values_list = list()
        count_list = list()

        for i in sorted(counter):
            sorted_values_list.append(i)
            count_list.append(counter[i])

        df = pd.DataFrame(
            {
                "value": sorted_values_list,
                "count": count_list,
            }
        )
        df["percent"] = df["count"] / amount * 100

        return df

    # }}}
    @classmethod  # __createSizesDataFrame  #{{{
    def __createSizesDataFrame(cls, df: pd.DataFrame):
        # sizes_df = pd.DataFrame(columns=["size", "begin", "end"])
        sizes_df = pd.DataFrame(columns=["begin", "end"])

        percent = df["percent"]
        minimum = df.iloc[0]["value"]
        last = 1
        for size in Size:
            if size in (
                Size.BLACKSWAN_SMALL,  # не существующие еще черные лебеди
                Size.BLACKSWAN_BIG,  # не существующие еще черные лебеди
                Size.GREATEST_BIG,  # last value set up after cycle
            ):
                continue

            while percent[0:last].sum() < size.value:
                last += 1

            # иногда когда значений мало - заглючивает в последней
            # категории, не охота разбираться, просто возьму 1 значение
            # из предыдущей и запихаю его в GREATEST_BIG
            if last == len(percent):
                last -= 1

            maximum = df.iloc[last]["value"]
            # sizes_df.loc[len(sizes_df)] = (str(size), minimum, maximum)
            sizes_df.loc[str(size)] = (minimum, maximum)

            minimum = maximum

        # set last value GREATEST_BIG
        size = Size.GREATEST_BIG
        maximum = df["value"].max()
        sizes_df.loc[str(size)] = (minimum, maximum)

        return sizes_df

    # }}}

    # __AUTO_UPDATE = Auto.UPDATE_ANALYTIC
    # __UPDATE_PERIOD = Auto.UPDATE_ANALYTIC_PERIOD
    # __LAST_UPDATE_FILE = Cmd.path(Usr.ANALYTIC, "last_update")
    # __ANALYTIC_IS_UP_TO_DATE = False

    # @classmethod  # __checkUpdate  # {{{
    # async def __checkUpdate(cls):
    #     logger.debug(f"{cls.__name__}.checkUpdate()")
    #
    #     # check update flag
    #     if cls.__ANALYTIC_IS_UP_TO_DATE:
    #         return
    #
    #     # check update settings
    #     if not cls.__AUTO_UPDATE:
    #         return
    #
    #     # ckeck file with last update datetime
    #     if not Cmd.isExist(cls.__LAST_UPDATE_FILE):
    #         need_update = True
    #     else:
    #         # read file, check last update > month ago
    #         dt_str = Cmd.read(cls.__LAST_UPDATE_FILE)
    #         last_update = datetime.fromisoformat(dt_str)
    #         need_update = (now() - last_update) > cls.__UPDATE_PERIOD
    #
    #     if not need_update:
    #         return
    #
    #     # update all user analytics
    #     logger.info(":: Need update user analytic - starting update")
    #     await cls.updateAll()
    #
    #     # save update datetime
    #     dt = now().isoformat()
    #     Cmd.write(dt, cls.__LAST_UPDATE_FILE)
    #
    #     # set class flag
    #     cls.__ANALYTIC_IS_UP_TO_DATE = True
    #
    # # }}}


# }}}


class Indicator:  # {{{
    @staticmethod  # BEAR_LEN# {{{
    def BEAR_LEN(chart):
        assert chart.last is not None
        i = -1
        while chart[i] is not None and chart[i].isBear():
            i -= 1
        return abs(i + 1)

    # }}}
    @staticmethod  # BULL_LEN# {{{
    def BULL_LEN(chart):
        assert chart.last is not None
        i = -1
        while chart[i] is not None and chart[i].isBull():
            i -= 1
        return abs(i + 1)

    # }}}
    @staticmethod  # SPEED# {{{
    def SPEED(chart, period):
        assert chart.last is not None

        if chart[-1] is None or chart[-period - 1] is None:
            return None

        first = chart[-period - 1].body.mid()
        last = chart[-1].body.mid()
        delta = last - first

        percent = delta / first * 100
        speed = percent / period

        return speed

    # }}}
    @staticmethod  # MA# {{{
    def MA(chart, period, parameter="close"):
        assert chart.last is not None
        total = 0
        for i in range(-1, -period - 1, -1):
            if chart[i] == None:
                return None
            total += chart[i].close
        return total / period

    # }}}


# }}}


if __name__ == "__main__":
    ...
