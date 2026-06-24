# ============================================================================
# URL:          http://arsvincjre.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import polars as pl

from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.utils import DateTime


class DataManager:
    @classmethod
    def cache(
        cls,
        source: Source,
    ) -> None: ...

    @classmethod
    def download(
        cls,
        code: str,
        source: Source,
        md: MarketData,
        year: int,
    ) -> None: ...

    @classmethod
    def update(
        cls,
        code: str,
        source: Source,
        md: MarketData,
    ) -> None: ...

    @classmethod
    def update_all(cls) -> None: ...

    @classmethod
    def load(
        cls,
        code: str,
        source: Source,
        md: MarketData,
        begin: DateTime,
        end: DateTime,
    ) -> pl.DataFrame: ...
