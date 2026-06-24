# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from pathlib import Path

import polars as pl

from avin.core.iid import Iid
from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.utils import Cmd, Date, DateTime, TimeDelta, dt_to_ts, log, ts_to_dt
from avin.utils.exceptions import DataNotFound


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

        path = _create_file_path(
            iid,
            source,
            md,
            date,
        )

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
        path = _create_file_path(
            iid,
            source,
            md,
            date,
        )

        if not path.is_file():
            raise DataNotFound(f"{iid} {source} {md} {date}")

        return Cmd.read_pqt(path)

    @classmethod
    def load_last(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
    ) -> pl.DataFrame:
        dir_path = _create_dir_path(iid, source, md)
        if not dir_path.exists():
            raise DataNotFound(f"{iid} {source} {md} ({dir_path})")

        files = sorted(
            Cmd.get_files(
                dir_path,
                full_path=True,
            )
        )

        if not files:
            raise DataNotFound(f"{iid} {source} {md} ({dir_path})")

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
            except DataNotFound:
                continue

            dfs.append(df)

        if not dfs:
            raise DataNotFound(f"{iid} {source} {md} {begin} - {end}")

        df = pl.concat(dfs)
        df = df.filter(
            pl.col("ts") >= begin_ts,
            pl.col("ts") < end_ts,
        ).sort("ts")
        # TODO: а нужен ли здесь сорт? даты идутт последовательно...
        # concat же не нарушает порядок????

        if df.is_empty():
            raise DataNotFound(f"{iid} {source} {md} {begin} - {end}")

        return df

    @classmethod
    def delete(cls, iid: Iid, source: Source, md: MarketData) -> None:
        dir_path = _create_dir_path(iid, source, md)

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
        raise ValueError("TicStorage accepts data only for a single day")

    return first_date


def _extract_range_dates(begin: DateTime, end: DateTime) -> list[Date]:
    last_date = (end - TimeDelta(microseconds=1)).date()

    dates = list()
    current = begin.date()
    while current <= last_date:
        dates.append(current)
        current += TimeDelta(days=1)

    return dates


def _create_dir_path(
    iid: Iid,
    source: Source,
    md: MarketData,
) -> Path:
    return iid.path / source / md


def _create_file_path(
    iid: Iid,
    source: Source,
    md: MarketData,
    date: Date,
) -> Path:
    return (
        _create_dir_path(iid, source, md) / str(date.year) / f"{date}.parquet"
    )
