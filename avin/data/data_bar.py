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


class DataBar:
    @classmethod
    def save(
        cls, iid: Iid, source: Source, md: MarketData, df: pl.DataFrame
    ) -> None:
        assert isinstance(iid, Iid)
        assert isinstance(source, Source)
        assert isinstance(md, MarketData)
        assert isinstance(df, pl.DataFrame)

        b = ts_to_dt(df.item(0, "ts_nanos")).year
        e = ts_to_dt(df.item(-1, "ts_nanos")).year
        assert b == e

        # NOTE:
        # после data.add(df) в датафрейме может быть данные за
        # два разных года. Например при обновление в первых
        # числах января. Перед сохранением нужно проверить состав
        # датафрейма и сохранить кусками по годам.
        year = ts_to_dt(df.item(0, "ts_nanos")).year
        end = ts_to_dt(df.item(-1, "ts_nanos")).year
        while year <= end:
            begin_ts = dt_to_ts(DateTime(year, 1, 1, tzinfo=UTC))
            end_ts = dt_to_ts(DateTime(year + 1, 1, 1, tzinfo=UTC))

            year_df = df.filter(
                pl.col("ts_nanos") >= begin_ts,
                pl.col("ts_nanos") < end_ts,
            )

            path = cls.__create_file_path(iid, source, md, year)
            Cmd.write_pqt(year_df, path)
            log.info(f"Save bars: {path}")

            year += 1

    @classmethod
    def load(
        cls, iid: Iid, source: Source, md: MarketData, year: int
    ) -> pl.DataFrame:
        path = cls.__create_file_path(iid, source, md, year)
        if path.exists():
            df = Cmd.read_pqt(path)
            return df

        raise DataNotFound(f"{iid} {source} {md} {year}")

    @classmethod
    def load_last(
        cls, iid: Iid, source: Source, md: MarketData
    ) -> pl.DataFrame:
        dir_path = cls.__create_dir_path(iid, source, md)

        if not Path(dir_path).exists():
            raise DataNotFound(f"{iid} {source} {md} ({dir_path})")

        files = sorted(Cmd.get_files(dir_path, full_path=True))
        if len(files) == 0:
            raise DataNotFound(f"{iid} {source} {md} ({dir_path})")

        last_file = files[-1]

        df = Cmd.read_pqt(Path(last_file))

        return df

    @classmethod
    def __create_dir_path(
        cls, iid: Iid, source: Source, md: MarketData
    ) -> Path:
        dir_path = iid.path() / md.name

        return dir_path

    @classmethod
    def __create_file_path(
        cls, iid: Iid, source: Source, md: MarketData, year: int
    ) -> Path:
        dir_path = cls.__create_dir_path(iid, source, md)
        file_path = dir_path / f"{year}.parquet"

        return file_path
