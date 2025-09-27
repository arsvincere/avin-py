# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from functools import cache
from pathlib import Path

import polars as pl

from avin.core.category import Category
from avin.data.source import Source
from avin.utils import CFG, Cmd, log


class IidCache:
    def __init__(self, source: Source, category: Category, df: pl.DataFrame):
        assert isinstance(source, Source)
        assert isinstance(category, Category)
        assert isinstance(df, pl.DataFrame)

        self.__source = source
        self.__category = category
        self.__iid_df = df

    @classmethod
    def save(cls, cache: IidCache) -> None:
        assert isinstance(cache, IidCache)

        path = cache.path()
        df = cache.df
        Cmd.write_pqt(df, Path(path))

        log.info(f"Cache save: {path}")

    @classmethod
    def load(cls, source: Source, category: Category) -> IidCache:
        path = _create_file_path(source, category)
        df = _cached_load_df(path)
        cache = IidCache(source, category, df)

        return cache

    @property
    def source(self) -> Source:
        return self.__source

    @property
    def category(self) -> Category:
        return self.__category

    @property
    def df(self) -> pl.DataFrame:
        return self.__iid_df

    def path(self) -> Path:
        file_path = _create_file_path(self.__source, self.__category)
        return file_path


def _create_file_path(source: Source, category: Category) -> Path:
    cache_path = Cmd.path(
        CFG.Dir.data,
        "cache",
        source.name,
        f"{category.name}.parquet",
    )

    return cache_path


@cache
def _cached_load_df(path: Path) -> pl.DataFrame:
    df = Cmd.read_pqt(path)

    return df


if __name__ == "__main__":
    ...
