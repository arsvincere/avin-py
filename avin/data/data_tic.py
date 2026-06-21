# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from datetime import date as Date
from pathlib import Path

import polars as pl

from avin.core.iid import Iid
from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.utils import Cmd, log, ts_to_dt
from avin.utils.exceptions import DataNotFound


class DataTic:
    @classmethod
    def save(
        cls, iid: Iid, source: Source, md: MarketData, df: pl.DataFrame
    ) -> None:
        assert isinstance(iid, Iid)
        assert isinstance(md, MarketData)
        assert isinstance(df, pl.DataFrame)
        assert md == MarketData.TIC

        date = ts_to_dt(df.item(0, "ts_nanos")).date()

        path = cls.__create_file_path(iid, source, md, date)
        Cmd.write_pqt(df, path)

        log.info(f"Save tics: {path}")

    @classmethod
    def load(
        cls, iid: Iid, source: Source, md: MarketData, date: Date
    ) -> pl.DataFrame:
        assert isinstance(iid, Iid)
        assert isinstance(md, MarketData)
        assert isinstance(date, Date)

        path = cls.__create_file_path(iid, source, md, date)
        if Cmd.is_exist(path):
            df = Cmd.read_pqt(path)
            return df

        raise DataNotFound(f"{iid} {source} {md} {date}")

    @classmethod
    def __create_file_path(
        cls, iid: Iid, source: Source, md: MarketData, date: Date
    ) -> Path:
        file_path = (
            iid.path()
            / source.name
            / md.name
            / f"{date.year}"
            / f"{date}.parquet"
        )

        return file_path
