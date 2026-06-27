# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from pathlib import Path

import polars as pl

from avin.domain.data.market_data import MarketData
from avin.domain.data.source import Source
from avin.domain.instrument.iid import Iid
from avin.errors.exceptions import DataNotFoundError
from avin.system.logger import log
from avin.system.path_builder import PathBuilder
from avin.utils.cmd import Cmd
from avin.utils.dt import Date, DateTime, TimeDelta, dt_to_ts, ts_to_dt

# TODO:
# BarStorage and TickStorage are nearly identical.
# Consider merge into DataStorage after raw/derived architecture stabilizes.


class BarStorage:
    @classmethod
    def save(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
        df: pl.DataFrame,
    ) -> None:
        if md is not MarketData.BAR_1M:
            raise ValueError(f"BarStorage supports only {MarketData.BAR_1M}")

        date = _validate_df(df)

        path = PathBuilder.market_data_file(iid, source, md, date)

        Cmd.write_pqt(df, path)

        log.info(f"Save bars: {path}")

    @classmethod
    def load(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
        date: Date,
    ) -> pl.DataFrame:
        path = PathBuilder.market_data_file(iid, source, md, date)

        if not path.is_file():
            raise DataNotFoundError(f"{iid} {source} {md} {date}")

        return Cmd.read_pqt(path)

    @classmethod
    def load_last(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
    ) -> pl.DataFrame:
        dir_path = PathBuilder.market_data_dir(iid, source, md)
        if not dir_path.exists():
            raise DataNotFoundError(f"{iid} {source} {md} ({dir_path})")

        year_dirs = sorted(
            Cmd.get_dirs(
                dir_path,
                full_path=True,
            )
        )
        if not year_dirs:
            raise DataNotFoundError(f"{iid} {source} {md} ({dir_path})")

        last_year_dir = Path(year_dirs[-1])
        files = Cmd.get_files(last_year_dir, full_path=True)
        if not files:
            raise DataNotFoundError(f"{iid} {source} {md} ({dir_path})")

        return Cmd.read_pqt(Path(files[-1]))

    @classmethod
    def load_range(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
        begin: DateTime,
        end: DateTime,
    ) -> pl.DataFrame:
        if begin >= end:
            raise ValueError("begin must be less than end")

        begin_ts = dt_to_ts(begin)
        end_ts = dt_to_ts(end)

        dfs = list()
        for date in _extract_range_dates(begin, end):
            try:
                df = cls.load(iid, source, md, date)
            except DataNotFoundError:
                continue

            dfs.append(df)

        if not dfs:
            raise DataNotFoundError(f"{iid} {source} {md} {begin} - {end}")

        df = pl.concat(dfs)
        df = df.filter(
            pl.col("ts") >= begin_ts,
            pl.col("ts") < end_ts,
        ).sort("ts")
        # TODO: а нужен ли здесь сорт? даты идутт последовательно...
        # concat же не нарушает порядок????

        if df.is_empty():
            raise DataNotFoundError(f"{iid} {source} {md} {begin} - {end}")

        return df

    @classmethod
    def delete(cls, iid: Iid, source: Source, md: MarketData) -> None:
        dir_path = PathBuilder.market_data_dir(iid, source, md)

        if Cmd.is_dir(dir_path):
            Cmd.delete_dir(dir_path)


def _validate_df(df: pl.DataFrame) -> Date:
    """
    Validate tic dataframe and return its trading date.
    """

    if df.is_empty():
        raise ValueError("DataFrame is empty")

    if "ts" not in df.columns:
        raise ValueError("Column 'ts' not found")

    first_date = ts_to_dt(df.item(0, "ts")).date()
    last_date = ts_to_dt(df.item(-1, "ts")).date()
    if first_date != last_date:
        raise ValueError("BarStorage accepts data only for a single day")

    return first_date


def _extract_range_dates(begin: DateTime, end: DateTime) -> list[Date]:
    last_date = (end - TimeDelta(microseconds=1)).date()

    dates = list()
    current = begin.date()
    while current <= last_date:
        dates.append(current)
        current += TimeDelta(days=1)

    return dates
