# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from pathlib import Path

import polars as pl

from avin.core.category import Category
from avin.core.source import Source
from avin.utils import Cmd, cfg, log


class IidCache:
    def __init__(
        self,
        source: Source,
        category: Category,
        iid_df: pl.DataFrame,
    ):
        assert isinstance(source, Source)
        assert isinstance(category, Category)
        assert isinstance(iid_df, pl.DataFrame)

        self.__source = source
        self.__category = category
        self.__iid_df = iid_df

    def source(self) -> Source:
        return self.__source

    def category(self) -> Category:
        return self.__category

    def df(self) -> pl.DataFrame:
        return self.__iid_df

    def path(self) -> str:
        file_path = _create_file_path(self.__source, self.__category)
        return file_path

    @classmethod
    def save(cls, cache: IidCache) -> None:
        assert isinstance(cache, IidCache)

        path = cache.path()
        df = cache.df()
        Cmd.write_pqt(df, Path(path))

        log.info(f"Cache save: {path}")

    @classmethod
    def load(cls, source: Source, category: Category) -> pl.DataFrame:
        path = _create_file_path(source, category)
        if path.exists():
            df = Cmd.read_pqt(Path(path))
            return df

        raise FileNotFoundError(path)


def _create_file_path(source: Source, category: Category) -> Path:
    cache_path = cfg.cache / source.name / f"{category.name}.parquet"

    return cache_path


if __name__ == "__main__":
    ...
