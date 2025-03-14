#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from abc import ABC

import polars as pl

from avin.config import Usr
from avin.core.asset import Asset
from avin.extra.size import Size
from avin.utils import Cmd, logger


class Analytic(ABC):
    @classmethod  # save  # {{{
    def save(
        cls, asset: Asset, analyse_name: str, data_frame: pl.DataFrame
    ) -> None:
        logger.debug(f"{cls.__name__}.save()")

        file_path = cls.__getFilePath(asset, analyse_name)
        dir_path = Cmd.dirPath(file_path)
        Cmd.makeDirs(Cmd.dirPath(file_path))

        data_frame.write_parquet(file_path)

    # }}}
    @classmethod  # load  # {{{
    def load(cls, asset: Asset, analyse_name: str) -> pl.DataFrame | None:
        logger.debug(f"{cls.__name__}.load()")

        file_path = cls.__getFilePath(asset, analyse_name)
        if not Cmd.isExist(file_path):
            logger.error(f"Analyse file not found: {file_path}")
            return None

        df = pl.read_parquet(file_path)

        return df

    # }}}

    @classmethod  # _classifySizes  # {{{
    def _classifySizes(cls, values: pl.Series) -> pl.DataFrame:
        assert isinstance(values, pl.Series)
        assert len(values) > 100

        cdf = cls.__createCDF(values)
        sizes_df = cls.__createSizesDataFrame(cdf)
        return sizes_df

    # }}}
    @classmethod  # _identifySize  # {{{
    def _identifySize(cls, value, sizes: pl.DataFrame) -> Size:
        # try find size
        result = sizes.filter(
            (value >= pl.col("begin")),
            (value < pl.col("end")),
        )

        # ok - return size
        if len(result) == 1:
            size = Size.fromStr(result.item(0, "size"))
            return size

        # else - BLACKSWAN
        if value < sizes.item(0, "begin"):
            return Size.BLACKSWAN_SMALL
        if value > sizes.item(-1, "begin"):
            return Size.BLACKSWAN_BIG

        assert False, "WTF?"

    # }}}

    @classmethod  # __getFilePath  # {{{
    def __getFilePath(cls, asset: Asset, analyse_name: str):
        logger.debug(f"{cls.__name__}.__getFilePath()")

        path_parts = str(asset).split() + analyse_name.split()
        file_path = Cmd.path(Usr.ANALYSE, *path_parts)
        file_path += ".parquet"

        return file_path

    # }}}
    @classmethod  # __createCDF  # {{{
    def __createCDF(cls, values: pl.Series) -> pl.DataFrame:
        """
        PF - probability function
        CDF - cummulative distribution function
        см.вики "функция вероятности"    (само распределение)
        см.вики "функция распределения"  (а это от 0 до 1 короче...)
        """
        assert isinstance(values, pl.Series)

        # probability function - PF
        values = values.alias("value").sort()
        df = values.value_counts(name="probability", normalize=True)

        # cumulative distribution function - CDF
        df = df.with_columns(pl.col("probability").cum_sum().alias("cdf"))

        # PDF in percent  *100
        df = df.with_columns((pl.col("cdf") * 100).alias("cdf_percent"))

        return df

    # }}}
    @classmethod  # __createSizesDataFrame  #{{{
    def __createSizesDataFrame(cls, cdf: pl.DataFrame) -> pl.DataFrame:
        value_type = type(cdf.item(0, "value"))
        sizes_df = pl.DataFrame(
            schema=[
                ("size", pl.String),
                ("begin", value_type),
                ("end", value_type),
            ]
        )

        cdf = cdf.with_row_index()
        begin = cdf.item(0, "value")
        for size in Size:
            if size in (
                Size.BLACKSWAN_SMALL,  # не существующие еще черные лебеди
                Size.BLACKSWAN_BIG,  # не существующие еще черные лебеди
            ):
                continue

            f = cdf.filter(pl.col("cdf_percent") <= size.value.max)
            if f.is_empty():
                end = begin
            else:
                end = f.item(-1, "value")

            row = pl.DataFrame(
                {"size": str(size), "begin": begin, "end": end}
            )
            sizes_df.extend(row)
            begin = end

        return sizes_df

    # }}}

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


if __name__ == "__main__":
    ...
