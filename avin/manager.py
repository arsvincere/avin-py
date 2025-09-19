#!/usr/bin/env  python3
# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from datetime import UTC
from datetime import datetime as Date
from datetime import datetime as DateTime
from pathlib import Path

import polars as pl

from avin.core.bar import Bar
from avin.core.category import Category
from avin.core.exchange import Exchange
from avin.core.iid import Iid
from avin.core.market_data import MarketData
from avin.core.tic import Tic
from avin.core.ticker import Ticker
from avin.data.data_bar import DataBar
from avin.data.data_tic import DataTic
from avin.data.source import Source
from avin.data.source_moex import SourceMoex
from avin.data.source_tinkoff import SourceTinkoff
from avin.utils import (
    CFG,
    ONE_DAY,
    Cmd,
    DataNotFound,
    filter_dt,
    log,
    now,
    ts_to_dt,
)


class Manager:
    @classmethod
    def cache(cls, source: Source) -> None:
        """Make cache of instruments info"""

        log.info("Manager cache")
        match source:
            case Source.MOEX:
                SourceMoex.cache_instruments_info()
            case Source.TINKOFF:
                SourceTinkoff.cache_instruments_info()
            case _:
                log.error("Not implemented")
                exit(1)

    @classmethod
    def find(cls, s: str) -> Iid:
        """Find instrument id"""

        e, c, t = s.upper().split("_")
        exchange = Exchange.from_str(e)
        category = Category.from_str(c)
        ticker = Ticker.from_str(t)

        assert exchange == Exchange.MOEX

        match category:
            case Category.INDEX:
                iid = SourceMoex.find(exchange, category, ticker)
            case Category.SHARE:
                iid = SourceTinkoff.find(exchange, category, ticker)
            case _:
                raise NotImplementedError()

        return iid

    @classmethod
    def download(
        cls,
        source: Source,
        iid: Iid,
        market_data: MarketData,
        *,
        year: int | None = None,
    ) -> None:
        assert isinstance(source, Source)
        assert isinstance(iid, Iid)
        assert isinstance(market_data, MarketData)
        log.info(f"Download {iid.ticker()} {market_data.name}")

        match market_data:
            case MarketData.TIC:
                _download_tics(source, iid, market_data)
            case _:  # bars
                _download_bars(source, iid, market_data, year)

    @classmethod
    def update(
        cls,
        source: Source,
        iid: Iid,
        market_data: MarketData,
    ) -> None:
        assert isinstance(source, Source)
        assert isinstance(iid, Iid)
        assert isinstance(market_data, MarketData)
        assert source == Source.MOEX
        log.info(f"Update {iid.ticker()} {market_data.name}")

        match market_data:
            case MarketData.TIC:
                _update_tics(source, iid, market_data)
            case MarketData.TRADE_STATS:
                log.error(f"Not implemented: {market_data}")
            case MarketData.ORDER_STATS:
                log.error(f"Not implemented: {market_data}")
            case MarketData.OB_STATS:
                log.error(f"Not implemented: {market_data}")
            case _:  # bars
                _update_bars(source, iid, market_data)

    @classmethod
    def update_all(
        cls,
    ) -> None:
        log.info("Update all market data")

        # check data dir
        data_dir = CFG.Dir.data
        if not Cmd.is_exist(data_dir):
            log.error(f"Data dir not found: {data_dir}")
            exit(1)

        # for each exchange & for each category
        for e in Exchange:
            for c in Category:
                instrument_path = Cmd.path(data_dir, e.name, c.name)
                if not Cmd.is_exist(Path(instrument_path)):
                    continue

                # dir name == ticker
                dir_names = sorted(Cmd.get_dirs(instrument_path))
                for ticker in dir_names:
                    iid = cls.find(f"{e.name}_{c.name}_{ticker}")
                    assert iid is not None

                    # for each market data if exist
                    for md in MarketData:
                        path = Cmd.path(instrument_path, ticker, md.name)
                        if not Cmd.is_exist(Path(path)):
                            continue

                        cls.update(Source.MOEX, iid, md)

    @classmethod
    def load(
        cls, iid: Iid, market_data: MarketData, begin: DateTime, end: DateTime
    ) -> pl.DataFrame:
        match market_data:
            case MarketData.BAR_1M:
                return _load_bars(iid, market_data, begin, end)
            case MarketData.BAR_10M:
                return _load_bars(iid, market_data, begin, end)
            case MarketData.BAR_1H:
                return _load_bars(iid, market_data, begin, end)
            case MarketData.BAR_D:
                return _load_bars(iid, market_data, begin, end)
            case MarketData.BAR_W:
                return _load_bars(iid, market_data, begin, end)
            case MarketData.BAR_M:
                return _load_bars(iid, market_data, begin, end)
            case MarketData.TIC:
                return _load_tics(iid, begin, end)
            case MarketData.TRADE_STATS:
                raise NotImplementedError()
            case MarketData.ORDER_STATS:
                raise NotImplementedError()
            case MarketData.OB_STATS:
                raise NotImplementedError()

        raise NotImplementedError()


def _download_bars(source: Source, iid: Iid, md: MarketData, year):
    if year is None:
        _download_bars_all(source, iid, md)
    else:
        _download_bars_year(source, iid, md, year)


def _download_bars_all(source: Source, iid: Iid, md: MarketData):
    year = 1997
    end = now().year
    while year <= end:
        _download_bars_year(source, iid, md, year)
        year += 1


def _download_bars_year(source: Source, iid: Iid, md: MarketData, year: int):
    assert source == Source.MOEX

    b = DateTime(year, 1, 1, tzinfo=UTC)
    e = DateTime(year + 1, 1, 1, tzinfo=UTC)

    df = SourceMoex.get_market_data(iid, md, begin=b, end=e)
    if df.is_empty():
        log.info(f"{year} no data")
        return

    file = DataBar(iid, md, df)
    DataBar.save(file)


def _download_tics(source: Source, iid: Iid, md: MarketData) -> None:
    assert source == Source.MOEX
    assert md == MarketData.TIC

    df = SourceMoex.get_market_data(iid, md)
    if df.is_empty():
        log.info(f"{Date.today()} no data")
        return

    file = DataTic(iid, md, df)
    DataTic.save(file)


def _update_bars(source: Source, iid: Iid, md: MarketData) -> None:
    # load last
    last_data = DataBar.load_last(iid, md)

    # get last datetime
    ts = last_data.df.item(-1, "ts_nanos")
    dt = ts_to_dt(ts)

    # request [last, now()]
    df = SourceMoex.get_market_data(iid, md, begin=dt, end=now())
    df = df[1:]  # remove first duplicate item

    if df.is_empty():
        log.info("no new bars")
    else:
        log.info(f"receved {len(df)} bars")
        last_data.add(df)
        DataBar.save(last_data)


def _update_tics(source: Source, iid: Iid, md: MarketData) -> None:
    # check today tics
    last_data = DataTic.load(iid, md, now().date())
    if last_data is None:
        Manager.download(source, iid, md)
        return

    # get last tradeno
    n = last_data.df.item(-1, "tradeno")

    # request from trade n
    df = SourceMoex.get_market_data(iid, md, tradeno=n)
    df = df[1:]  # remove first duplicate item

    if df.is_empty():
        log.info("no new tics")
    else:
        log.info(f"receved {len(df)} tics")
        last_data.add(df)
        DataTic.save(last_data)


def _load_bars(
    iid: Iid, md: MarketData, b: DateTime, e: DateTime
) -> pl.DataFrame:
    # create empty df
    df = pl.DataFrame(schema=Bar.schema())

    # load data by years
    year = b.year
    end_year = e.year
    while year <= end_year:
        data = DataBar.load(iid, md, year)
        if data is not None:
            df.extend(data.df)

        year += 1

    # filter & check empty
    df = filter_dt(b, e, df)
    if df.is_empty():
        raise DataNotFound(f"{iid} {md}")

    return df


def _load_tics(iid: Iid, b: DateTime, e: DateTime) -> pl.DataFrame:
    # create empty df
    df = pl.DataFrame(schema=Tic.schema())

    # load data by days
    day = b.date()
    end = e.date()
    while day <= end:
        data = DataTic.load(iid, MarketData.TIC, day)
        if data is not None:
            df.extend(data.df)

        day += ONE_DAY

    # filter & check empty
    df = filter_dt(b, e, df)
    if df.is_empty():
        raise DataNotFound(f"{iid} {MarketData.TIC}")

    return df


if __name__ == "__main__":
    ...
