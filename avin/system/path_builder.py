# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

from avin.domain.data.market_data import MarketData
from avin.domain.data.source import Source
from avin.domain.instrument.category import Category
from avin.domain.instrument.iid import Iid
from avin.system.conf import cfg
from avin.utils.dt import Date


class PathBuilder:
    ROOT: Path = cfg.root_dir

    CONNECT: Path = ROOT / "connect"
    DATA: Path = ROOT / "data"
    IID: Path = ROOT / "iid"
    LOG: Path = ROOT / "log"
    RES: Path = ROOT / "res"
    TMP: Path = ROOT / "tmp"

    @classmethod
    def iid_root(cls, iid: Iid) -> Path:
        return cls.DATA / iid.exchange / iid.category / iid.ticker

    @classmethod
    def iid_cache_file(
        cls,
        source: Source,
        category: Category,
    ) -> Path:
        return cls.IID / source / f"{category}.parquet"

    @classmethod
    def market_data_dir(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
    ) -> Path:
        return cls.iid_root(iid) / source / md

    @classmethod
    def market_data_file(
        cls,
        iid: Iid,
        source: Source,
        md: MarketData,
        date: Date,
    ) -> Path:
        d = cls.market_data_dir(iid, source, md)
        return d / str(date.year) / f"{date}.parquet"
