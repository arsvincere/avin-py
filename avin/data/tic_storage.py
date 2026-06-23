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
from avin.utils import Cmd, Date, DateTime, log, ts_to_dt
from avin.utils.exceptions import DataNotFound


class TicStorage:
    @classmethod
    def save(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
        df: pl.DataFrame,
    ) -> None:
        if md is not MarketData.TIC:
            raise ValueError(f"TicStorage supports only {MarketData.TIC}")

        date = _validate_df(df)

        path = _create_file_path(
            iid,
            source,
            md,
            date,
        )

        Cmd.write_pqt(df, path)

        log.info(f"Save tics: {path}")

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
    def load_last(cls, iid: Iid, source: Source, md: MarketData):
        raise NotImplementedError("TODO ME")

    @classmethod
    def load_range(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
        begin: DateTime,
        end: DateTime,
    ):
        raise NotImplementedError("TODO ME")


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


def _create_file_path(
    iid: Iid,
    source: Source,
    md: MarketData,
    date: Date,
) -> Path:
    return (
        iid.path / source.name / md.name / str(date.year) / f"{date}.parquet"
    )
