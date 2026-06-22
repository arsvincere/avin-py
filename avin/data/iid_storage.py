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
from avin.utils.exceptions import DataNotFound


class IidStorage:
    @classmethod
    def save(
        cls,
        source: Source,
        category: Category,
        df: pl.DataFrame,
    ) -> None:
        if df.is_empty():
            raise ValueError("DataFrame is empty")

        path = _create_file_path(
            source,
            category,
        )

        Cmd.write_pqt(df, path)

        log.info(f"Save iid cache: {path}")

    @classmethod
    def load(
        cls,
        source: Source,
        category: Category,
    ) -> pl.DataFrame:
        path = _create_file_path(
            source,
            category,
        )

        if not path.is_file():
            raise DataNotFound(f"{source} {category} ({path})")

        return Cmd.read_pqt(path)


def _create_file_path(
    source: Source,
    category: Category,
) -> Path:
    return cfg.cache / source.name / f"{category.name}.parquet"
