# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from functools import cache

import polars as pl

from avin.domain.asset.future import Future
from avin.domain.asset.share import Share
from avin.domain.data.source import Source
from avin.domain.instrument.category import Category
from avin.domain.instrument.exchange import Exchange
from avin.domain.instrument.iid import Iid
from avin.domain.instrument.instrument_code import parse_code
from avin.errors.exceptions import InstrumentNotFoundError
from avin.storage.iid_storage import IidStorage


class AssetFactory:
    @classmethod
    @cache
    def new(cls, code: str) -> Share | Future:
        e, c, t = parse_code(code)
        if e is not Exchange.MOEX:
            raise NotImplementedError("TODO")
        if c is not Category.SHARE:
            raise NotImplementedError("TODO")

        shares = _cached_load_shares()

        row = shares.filter(pl.col("ticker") == t)

        if row.is_empty():
            raise InstrumentNotFoundError(f"{t} ({code})")

        iid = Iid.from_df(row)
        share = Share(iid)

        return share


@cache
def _cached_load_shares() -> pl.DataFrame:
    return IidStorage.load(Source.TINKOFF, Category.SHARE)
