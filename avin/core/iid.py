# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

import polars as pl

from avin.core.category import Category
from avin.core.exchange import Exchange
from avin.utils.cmd import Cmd
from avin.utils.conf import cfg


class Iid:
    """Instrument id"""

    def __init__(self, info: dict[str, str]):
        assert info["exchange"] is not None
        assert info["category"] is not None
        assert info["ticker"] is not None
        assert info["figi"] is not None
        assert info["name"] is not None
        assert info["lot"] is not None
        assert info["step"] is not None

        self.__info = info

    def __str__(self):
        s = f"{self.exchange().name}_{self.category().name}_{self.ticker()}"
        return s

    def __hash__(self):
        return hash(self.figi())

    def __eq__(self, other: object):
        assert isinstance(other, Iid)
        return self.figi() == other.figi()

    def info(self) -> dict[str, str]:
        return self.__info

    def exchange(self) -> Exchange:
        return Exchange.from_str(self.__info["exchange"])

    def category(self) -> Category:
        return Category.from_str(self.__info["category"])

    def ticker(self) -> str:
        return self.__info["ticker"]

    def figi(self) -> str:
        return self.__info["figi"]

    def name(self) -> str:
        return self.__info["name"]

    def lot(self) -> int:
        return int(self.__info["lot"])

    def step(self) -> float:
        return float(self.__info["step"])

    def path(self) -> Path:
        path = (
            cfg.data
            / self.exchange().name
            / self.category().name
            / self.ticker()
        )
        return path

    def print(self) -> str:
        return Cmd.to_json_str(self.__info, indent=4)

    @classmethod
    def from_df(cls, df: pl.DataFrame) -> Iid:
        assert len(df) == 1

        dct = df.row(0, named=True)

        return Iid(dct)
