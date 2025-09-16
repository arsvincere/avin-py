#!/usr/bin/env  python3
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
from avin.utils import Cmd, log, ts_to_dt


class DataTic:
    def __init__(self, iid: Iid, market_data: MarketData, df: pl.DataFrame):
        assert isinstance(iid, Iid)
        assert isinstance(market_data, MarketData)
        assert isinstance(df, pl.DataFrame)

        self.__iid = iid
        self.__market_data = market_data
        self.__df = df

    @classmethod
    def save(cls, data: DataTic) -> None:
        assert isinstance(data, DataTic)

        iid = data.iid
        market_data = data.market_data
        df = data.df
        date = ts_to_dt(df.item(0, "ts_nanos")).date()

        path = _create_file_path(iid, market_data, date)
        Cmd.write_pqt(df, path)

        log.info(f"Save tics: {path}")

    @classmethod
    def load(
        cls, iid: Iid, market_data: MarketData, date: Date
    ) -> DataTic | None:
        assert isinstance(iid, Iid)
        assert isinstance(market_data, MarketData)
        assert isinstance(date, Date)

        path = _create_file_path(iid, market_data, date)
        if not Cmd.is_exist(path):
            return None

        df = Cmd.read_pqt(path)
        data = DataTic(iid, market_data, df)

        return data

    @property
    def iid(self) -> Iid:
        return self.__iid

    @property
    def market_data(self) -> MarketData:
        return self.__market_data

    @property
    def df(self) -> pl.DataFrame:
        return self.__df

    def add(self, df: pl.DataFrame) -> None:
        self.__df.extend(df)


def _create_file_path(iid: Iid, market_data: MarketData, date: Date) -> Path:
    file_path = Cmd.path(
        iid.path(),
        market_data.name,
        f"{date.year}",
        f"{date}.parquet",
    )

    return Path(file_path)
