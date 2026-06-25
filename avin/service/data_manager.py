# ============================================================================
# URL:          http://arsvincjre.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================


import polars as pl

from avin.data.bar_storage import BarStorage
from avin.data.iid_storage import IidStorage
from avin.data.tic_storage import TicStorage
from avin.data.tinkoff.source_tinkoff import SourceTinkoff
from avin.domain.instrument.category import Category
from avin.domain.instrument.iid import Iid
from avin.domain.market_data import MarketData
from avin.domain.source import Source
from avin.errors.exceptions import DataNotFound
from avin.utils.dt import Date, DateTime, TimeDelta, ts_to_dt


class DataManager:
    @classmethod
    def cache(
        cls,
        source: Source,
    ) -> None:
        if not isinstance(source, Source):
            raise TypeError(source)

        match source:
            case Source.TINKOFF:
                SourceTinkoff.cache()
            case _:
                raise NotImplementedError(source)

    @classmethod
    def download(
        cls,
        code: str,
        source: Source,
        md: MarketData,
        year: int,
    ) -> None:
        if not isinstance(code, str):
            raise TypeError(code)
        if not isinstance(source, Source):
            raise TypeError(source)
        if not isinstance(md, MarketData):
            raise TypeError(md)
        if not isinstance(year, int):
            raise TypeError(year)

        iid = IidStorage.find_code(code, source)

        source_impl = _get_source_impl(source)
        source_impl.download_year(iid, md, year)

    @classmethod
    def update(
        cls,
        code: str,
        source: Source,
        md: MarketData,
    ) -> None:
        if not isinstance(code, str):
            raise TypeError(code)
        if not isinstance(source, Source):
            raise TypeError(source)
        if not isinstance(md, MarketData):
            raise TypeError(md)

        iid = IidStorage.find_code(code, source)
        storage = _get_storage(md)
        source_impl = _get_source_impl(source)

        df = storage.load_last(iid, source, md)
        ts = df.item(-1, "ts")
        last_dt = ts_to_dt(ts).date()
        yesterday = Date.today() - TimeDelta(days=1)
        missing_days = (yesterday - last_dt).days

        if missing_days == 0:
            return
        elif missing_days == 1:
            source_impl.download_day(iid, md, yesterday)
        else:
            for year in range(
                last_dt.year,
                yesterday.year + 1,
            ):
                source_impl.download_year(iid, md, year)

    @classmethod
    def update_all(cls) -> None:
        for source in Source:
            for category in Category:
                try:
                    df = IidStorage.load(source, category)
                except DataNotFound:
                    continue

                for row in df.iter_rows(named=True):
                    iid = Iid(row)

                    # TODO: source_impl.available_market_data()
                    for md in SourceTinkoff.available_market_data():
                        cls.update(str(iid), source, md)

    @classmethod
    def load(
        cls,
        code: str,
        source: Source,
        md: MarketData,
        begin: DateTime,
        end: DateTime,
    ) -> pl.DataFrame:
        if not isinstance(code, str):
            raise TypeError(code)
        if not isinstance(source, Source):
            raise TypeError(source)
        if not isinstance(md, MarketData):
            raise TypeError(md)
        if not isinstance(begin, DateTime):
            raise TypeError(begin)
        if not isinstance(end, DateTime):
            raise TypeError(end)

        iid = IidStorage.find_code(code, source)

        storage = _get_storage(md)

        return storage.load_range(iid, source, md, begin, end)

    @classmethod
    def delete(
        cls,
        code: str,
        source: Source,
        md: MarketData,
    ):

        iid = IidStorage.find_code(code, source)

        storage = _get_storage(md)
        storage.delete(iid, source, md)


def _get_storage(md: MarketData):
    match md:
        case MarketData.TIC:
            return TicStorage
        case MarketData.BAR_1M:
            return BarStorage
        case _:
            raise ValueError(md)


def _get_source_impl(source: Source):
    match source:
        case Source.TINKOFF:
            return SourceTinkoff
        case _:
            raise NotImplementedError(source)
