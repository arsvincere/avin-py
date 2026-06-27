# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from functools import cache

import polars as pl

from avin.domain.data.source import Source
from avin.domain.instrument.category import Category
from avin.domain.instrument.iid import Iid
from avin.domain.instrument.code import parse_code
from avin.errors.exceptions import DataNotFoundError, InstrumentNotFoundError
from avin.system.logger import log
from avin.system.path_builder import PathBuilder
from avin.utils.cmd import Cmd


class IidStorage:
    @classmethod
    @cache
    def find_code(cls, code: str, source: Source) -> Iid:
        exchange, category, ticker = parse_code(code)

        iid_cache = cls.load(source, category)

        row = iid_cache.filter(
            (pl.col("exchange") == exchange)
            # & (pl.col("category") == category) # cache и так той категории
            & (pl.col("ticker") == ticker)
        )

        if row.height != 1:
            raise InstrumentNotFoundError(f"Code='{code}' in {source}")

        return Iid.from_df(row)

    @classmethod
    @cache
    def find_figi(cls, figi: str, source: Source) -> Iid:
        for category in Category:
            try:
                iid_cache = cls.load(source, category)
            except DataNotFoundError:
                continue

            row = iid_cache.filter(pl.col("figi") == figi)

            if row.height == 1:
                return Iid.from_df(row)

        raise InstrumentNotFoundError(f"FIGI='{figi}' in {source}")

    @classmethod
    def save(
        cls,
        source: Source,
        category: Category,
        df: pl.DataFrame,
    ) -> None:
        if df.is_empty():
            raise ValueError("DataFrame is empty")

        path = PathBuilder.iid_cache_file(source, category)

        Cmd.write_pqt(df, path)

        log.info(f"Save iid cache: {path}")

    @classmethod
    @cache
    def load(
        cls,
        source: Source,
        category: Category,
    ) -> pl.DataFrame:

        path = PathBuilder.iid_cache_file(source, category)

        if not path.is_file():
            raise DataNotFoundError(f"{source} {category} ({path})")

        return Cmd.read_pqt(path)

    @classmethod
    def delete(cls, source: Source, category: Category) -> None:
        path = PathBuilder.iid_cache_file(source, category)

        if Cmd.is_file(path):
            Cmd.delete(path)
