# ============================================================================
# URL:          http://arsvincjre.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import polars as pl
import t_tech.invest as ti

from avin.core.category import Category
from avin.core.iid import Iid
from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.data.iid_storage import IidStorage
from avin.data.tinkoff.auth import TinkoffAuth
from avin.data.tinkoff.bar_downloader import TinkoffBarDownloader
from avin.data.tinkoff.mapper import extract_info
from avin.data.tinkoff.schemas import IID_SCHEMA
from avin.data.tinkoff.tic_downloader import TinkoffTicDownloader
from avin.utils import Date, log


class SourceTinkoff:
    SOURCE: Source = Source.TINKOFF
    TARGET: str = ti.constants.INVEST_GRPC_API

    @classmethod
    def available_market_data(cls) -> list[MarketData]:
        return [MarketData.BAR_1M, MarketData.TIC]

    @classmethod
    def cache(cls) -> None:
        log.info("Caching instruments info from Tinkoff")

        # favorite list with short info (ti.FavoriteInstrument)
        f_shares = cls.__get_favorite_shares()
        # df with full info about shares
        df_shares_info = cls.__get_shares_info(f_shares)

        IidStorage.save(cls.SOURCE, Category.SHARE, df_shares_info)

    @classmethod
    def download_year(cls, iid: Iid, md: MarketData, year: int) -> None:
        match md:
            case MarketData.BAR_1M:
                TinkoffBarDownloader(iid, md).download_year(year)
            case MarketData.TIC:
                TinkoffTicDownloader(iid, md).download_year(year)
            case _:
                raise ValueError(f"Tinkoff not provide: {md}")

    @classmethod
    def download_day(cls, iid: Iid, md: MarketData, day: Date) -> None:
        match md:
            case MarketData.BAR_1M:
                TinkoffBarDownloader(iid, md).download_day(day)
            case MarketData.TIC:
                TinkoffTicDownloader(iid, md).download_day(day)
            case _:
                raise ValueError(f"Tinkoff not provide: {md}")

    @classmethod
    def __get_favorite_shares(cls) -> list[ti.FavoriteInstrument]:
        shares = list()
        token = TinkoffAuth.token()

        with ti.Client(token) as client:
            # get favorite instruments & select shares
            response = client.instruments.get_favorites()
            for i in response.favorite_instruments:
                if i.instrument_type == "share":
                    shares.append(i)

        return shares

    @classmethod
    def __get_shares_info(
        cls,
        shares: list[ti.FavoriteInstrument],
    ) -> pl.DataFrame:
        token = TinkoffAuth.token()
        rows = list()

        with ti.Client(token) as client:
            for i in shares:
                response = client.instruments.share_by(
                    id_type=ti.InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                    id=i.figi,
                )
                info = extract_info(response.instrument)
                rows.append(info)

        return pl.DataFrame(rows, schema=IID_SCHEMA)


if __name__ == "__main__":
    ...
