# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from functools import cache

import polars as pl

from avin.asset.future import Future
from avin.asset.share import Share
from avin.core.category import Category
from avin.core.iid import Iid
from avin.core.source import Source
from avin.data.iid_storage import IidStorage
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
