# ============================================================================
# URL:          http://arsvincjre.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================


import polars as pl

from avin.core.category import Category
from avin.core.iid import Iid
from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.data.bar_storage import BarStorage
from avin.data.iid_storage import IidStorage
from avin.data.tic_storage import TicStorage
from avin.data.tinkoff.source_tinkoff import SourceTinkoff
from avin.utils import DateTime, ts_to_dt
from avin.utils.exceptions import DataNotFound


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
        source_impl.download(iid, md, year)

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

        df = storage.load_last(iid, source, md)
        ts = df.item(-1, "ts")
        dt = ts_to_dt(ts)
        year = dt.year

        source_impl = _get_source_impl(source)
        source_impl.download(iid, md, year)

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


def _get_storage(md: MarketData):
    match md:
        case MarketData.TIC:
            return TicStorage
        case (
            MarketData.BAR_1M,
            MarketData.BAR_5M,
            MarketData.BAR_10M,
            MarketData.BAR_1H,
            MarketData.BAR_DAY,
            MarketData.BAR_WEEK,
            MarketData.BAR_MONTH,
        ):
            return BarStorage
        case _:
            raise NotImplementedError(md)


def _get_source_impl(source: Source):
    match source:
        case Source.TINKOFF:
            return SourceTinkoff
        case _:
            raise NotImplementedError(source)
