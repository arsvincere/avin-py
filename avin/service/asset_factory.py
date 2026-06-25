# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from functools import cache

import polars as pl

from avin.data.iid_storage import IidStorage
from avin.domain.asset.future import Future
from avin.domain.asset.share import Share
from avin.domain.instrument.category import Category
from avin.domain.instrument.iid import Iid
from avin.domain.source import Source
from avin.errors.exceptions import InstrumentNotFound


class AssetFactory:
    @classmethod
    @cache
    def new(cls, code: str) -> Share | Future:
        e, c, t = code.split("_")
        assert e == "MOEX"
        assert c == "SHARE"

        shares = _cached_load_shares()

        row = shares.filter(pl.col("ticker") == t)

        if row.is_empty():
            raise InstrumentNotFound(f"{t} ({code})")

        iid = Iid.from_df(row)
        share = Share(iid)

        return share


@cache
def _cached_load_shares() -> pl.DataFrame:
    return IidStorage.load(Source.TINKOFF, Category.SHARE)
