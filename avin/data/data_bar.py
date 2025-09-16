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
from avin.data.market_data import MarketData
from avin.utils import Cmd, DataNotFound, dt_to_ts, log, ts_to_dt


class DataBar:
    def __init__(self, iid: Iid, market_data: MarketData, df: pl.DataFrame):
        # check types
        assert isinstance(iid, Iid)
        assert isinstance(market_data, MarketData)
        assert isinstance(df, pl.DataFrame)

        # check data in df - must be only one year
        begin_year = ts_to_dt(df.item(0, "ts_nanos")).year
        end_year = ts_to_dt(df.item(-1, "ts_nanos")).year
        assert begin_year == end_year

        self.__iid = iid
        self.__market_data = market_data
        self.__df = df

    @classmethod
    def save(cls, data: DataBar) -> None:
        assert isinstance(data, DataBar)

        iid = data.iid
        market_data = data.market_data

        # NOTE:
        # после data.add(df) в датафрейме может быть данные за
        # два разных года. Например при обновление в первых
        # числах января. Перед сохранением нужно проверить состав
        # датафрейма и сохранить кусками по годам.
        year = ts_to_dt(data.__df.item(0, "ts_nanos")).year
        end = ts_to_dt(data.__df.item(-1, "ts_nanos")).year
        while year <= end:
            begin_ts = dt_to_ts(DateTime(year, 1, 1, tzinfo=UTC))
            end_ts = dt_to_ts(DateTime(year + 1, 1, 1, tzinfo=UTC))

            year_df = data.__df.filter(
                pl.col("ts_nanos") >= begin_ts,
                pl.col("ts_nanos") < end_ts,
            )

            path = _create_file_path(iid, market_data, year)
            Cmd.write_pqt(year_df, path)
            log.info(f"Save bars: {path}")

            year += 1

    @classmethod
    def load(
        cls,
        iid: Iid,
        md: MarketData,
        year: int,
    ) -> DataBar | None:
        path = Cmd.path(iid.path(), md.name, f"{year}.parquet")

        if not Cmd.is_exist(path):
            return None

        df = Cmd.read_pqt(path)
        data = DataBar(iid, md, df)

        return data

    @classmethod
    def load_last(cls, iid: Iid, market_data: MarketData) -> DataBar:
        dir_path = _create_dir_path(iid, market_data)

        if not Path(dir_path).exists():
            raise DataNotFound(f"{iid} {market_data} {dir_path}")

        files = sorted(Cmd.get_files(dir_path, full_path=True))
        if len(files) == 0:
            raise DataNotFound(f"{iid} {market_data} {dir_path}")

        last_file = files[-1]

        df = Cmd.read_pqt(Path(last_file))
        data = DataBar(iid, market_data, df)

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


def _create_dir_path(iid: Iid, market_data: MarketData) -> Path:
    dir_path = Cmd.path(
        iid.path(),
        market_data.name,
    )

    return dir_path


def _create_file_path(iid: Iid, market_data: MarketData, year: int) -> Path:
    dir_path = _create_dir_path(iid, market_data)
    file_path = Cmd.path(
        dir_path,
        f"{year}.parquet",
    )

    return Path(file_path)
