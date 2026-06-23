# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from datetime import UTC
from datetime import datetime as DateTime
from pathlib import Path

import polars as pl

from avin.core.iid import Iid
from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.utils import Cmd, dt_to_ts, log, ts_to_dt
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
        _validate_df(df)

        for year in _extract_years(df):
            year_df = _filter_by_year(df, year)

            if year_df.is_empty():
                continue

            path = _create_file_path(
                iid,
                source,
                md,
                year,
            )

            Cmd.write_pqt(year_df, path)

            log.info(f"Save bars: {path}")

    @classmethod
    def load(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
        year: int,
    ) -> pl.DataFrame:
        path = _create_file_path(
            iid,
            source,
            md,
            year,
        )

        if not path.exists():
            raise DataNotFound(f"{iid} {source} {md} {year}")

        return Cmd.read_pqt(path)

    @classmethod
    def load_last(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
    ) -> pl.DataFrame:
        dir_path = _create_dir_path(
            iid,
            source,
            md,
        )

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
    ):
        raise NotADirectoryError("TODO_ME")


def _validate_df(df: pl.DataFrame) -> None:
    if df.is_empty():
        raise ValueError("DataFrame is empty")

    if "ts" not in df.columns:
        raise ValueError("Column 'ts' not found")


def _extract_years(df: pl.DataFrame) -> range:
    first_year = ts_to_dt(df.item(0, "ts")).year
    last_year = ts_to_dt(df.item(-1, "ts")).year

    return range(first_year, last_year + 1)


def _filter_by_year(
    df: pl.DataFrame,
    year: int,
) -> pl.DataFrame:
    begin_ts = dt_to_ts(DateTime(year, 1, 1, tzinfo=UTC))

    end_ts = dt_to_ts(DateTime(year + 1, 1, 1, tzinfo=UTC))

    return df.filter(
        pl.col("ts") >= begin_ts,
        pl.col("ts") < end_ts,
    )


def _create_dir_path(
    iid: Iid,
    source: Source,
    md: MarketData,
) -> Path:
    return iid.path / source.name / md.name


def _create_file_path(
    iid: Iid,
    source: Source,
    md: MarketData,
    year: int,
) -> Path:
    return _create_dir_path(iid, source, md) / f"{year}.parquet"
