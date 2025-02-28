#!/usr/bin/env  python3
# LICENSE:      GNU GPL
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com

"""Doc"""

import datetime
import logging
import sys
from datetime import datetime

sys.path.append("/home/alex/.local/lib/python3.11/site-packages")
import pandas as pd

sys.path.append("/home/alex/AVIN")
from avin.const import (
    DAY_BEGIN,
    DAY_END,
    LOGGER_FORMAT,
    UTC,
)
from avin.utils import (
    Cmd,
)

logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CoreError(Exception):
    pass


class ___TinkoffDataFrame:
    def __init__(self):
        super().__init__()

    def exportData(self, root_dir, *timeframes):  # {{{
        data_dirs = Cmd.findDirs("Tinkoff", root_dir)
        for ticker_dir in sorted(data_dirs):
            year_dirs = Cmd.getDirs(ticker_dir, full_path=True)
            for path in sorted(year_dirs):
                self.__exportDir(path, timeframes)

    # }}}
    def __exportDir(self, dir_path, timeframes):  # {{{
        df = self.__readDir(dir_path)
        uid = df["uid"][0]
        ID = Id("share", "uid", uid)
        df = self.__format(df)
        for tf in timeframes:
            converted = self.__convertTimeframe(df, tf)
            Data.saveDF(ID, tf, converted, dir_path="auto")

    # }}}
    def __readDir(self, dir_path):  # {{{
        files = sorted(Cmd.getFiles(dir_path, full_path=True))
        year_df = pd.DataFrame()
        for file in files:
            df = self.__readFile(file)
            year_df = pd.concat([year_df, df], ignore_index=True)
        return year_df

    # }}}
    def __readFile(self, file_path: str) -> pd.DataFrame:  # {{{
        """-- Doc
        Тинькофф дата формат:
        "uid; datetime; open; close; high; low; volume;"
        """
        df = pd.read_csv(
            file_path,
            sep=";",
            header=None,
            names=["uid", "dt", "open", "close", "low", "high", "vol", None],
        )
        return df

    # }}}
    def __format(self, df: pd.DataFrame) -> pd.DataFrame:  # {{{
        df["dt"] = df["dt"].apply(datetime.fromisoformat)
        begin = df.iloc[0]["dt"].date()
        end = df.iloc[-1]["dt"].date()
        begin = datetime.combine(begin, DAY_BEGIN, tzinfo=UTC)
        end = datetime.combine(end, DAY_END, tzinfo=UTC)
        dti = pd.date_range(begin, end, freq="T")
        dti = pd.DataFrame(dti, columns=["dt"])
        df = dti.merge(
            df,
            left_on="dt",
            right_on="dt",
            how="outer",
        )
        df["vol"] = df["vol"].fillna(0)
        df["vol"] = df["vol"].apply(int)
        return df

    # }}}
    def __convertTimeframe(
        self, df: pd.DataFrame, timeframe: TimeFrame
    ):  # {{{
        converted = pd.DataFrame()
        step = timeframe.minutes()
        end = len(df.index)
        first = 0
        while first < end:
            last = first + step
            bars = df.iloc[first:last, :]
            bar = self.__mergeBar(bars)
            if bar is not None:
                converted = pd.concat([converted, bar])
            first = last
        converted = converted.reset_index()
        converted = converted.drop(["index"], axis="columns")
        return converted

    # }}}
    def __mergeBar(self, df: pd.DataFrame) -> Bar:  # {{{
        vol = df["vol"].sum()
        if vol == 0:
            return None
        df = df.reset_index()
        dt = df["dt"][0]
        opn = df["open"][df["open"].first_valid_index()]
        cls = df["close"][df["close"].last_valid_index()]
        hgh = df["high"].max()
        low = df["low"].min()
        bar = pd.DataFrame(
            {
                "dt": [dt],
                "open": [opn],
                "close": [cls],
                "low": [low],
                "high": [hgh],
                "vol": [vol],
            }
        )
        return bar


# }}}


if __name__ == "__main__":
    ...
    # start = now()
    # td = TinkoffDataFrame()
    # td.exportData("/home/alex/.DATA/MOEX/share/AFKS/", TimeFrame("1H"))
    # finish = now()
    # print("DataFrame version: ", finish - start)
    #
    # start = now()
    # td = TinkoffData()
    # td._exportDir("/home/alex/.DATA/MOEX/share/AFKS/Tinkoff/2018", TimeFrame("1H"))
    # td._exportDir("/home/alex/.DATA/MOEX/share/AFKS/Tinkoff/2019", TimeFrame("1H"))
    # td._exportDir("/home/alex/.DATA/MOEX/share/AFKS/Tinkoff/2020", TimeFrame("1H"))
    # td._exportDir("/home/alex/.DATA/MOEX/share/AFKS/Tinkoff/2021", TimeFrame("1H"))
    # td._exportDir("/home/alex/.DATA/MOEX/share/AFKS/Tinkoff/2022", TimeFrame("1H"))
    # td._exportDir("/home/alex/.DATA/MOEX/share/AFKS/Tinkoff/2023", TimeFrame("1H"))
    # finish = now()
    # print("Old version: ", finish - start)
