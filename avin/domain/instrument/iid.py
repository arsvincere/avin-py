# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import polars as pl

from avin.domain.instrument.category import Category
from avin.domain.instrument.exchange import Exchange
from avin.utils.cmd import Cmd


class Iid:
    """Instrument id"""

    def __init__(self, raw_info: dict[str, str]):
        required = (
            "exchange",
            "category",
            "ticker",
            "figi",
            "name",
            "lot",
            "step",
        )
        for key in required:
            if key not in raw_info:
                raise ValueError(f"{key} missing")

            if not isinstance(raw_info[key], str) or raw_info[key] == "":
                raise ValueError(f"{key} invalid")

        self.__raw_info = raw_info.copy()

    def __str__(self) -> str:
        return self.code

    def __hash__(self) -> int:
        return hash(self.figi)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Iid):
            return NotImplemented

        return self.figi == other.figi

    @property
    def code(self) -> str:
        return f"{self.exchange.name}_{self.category.name}_{self.ticker}"

    @property
    def exchange(self) -> Exchange:
        return Exchange.from_str(self.__raw_info["exchange"])

    @property
    def category(self) -> Category:
        return Category.from_str(self.__raw_info["category"])

    @property
    def ticker(self) -> str:
        return self.__raw_info["ticker"]

    @property
    def figi(self) -> str:
        return self.__raw_info["figi"]

    @property
    def name(self) -> str:
        return self.__raw_info["name"]

    @property
    def lot(self) -> int:
        return int(self.__raw_info["lot"])

    @property
    def step(self) -> float:
        return float(self.__raw_info["step"])

    def to_json_str(self) -> str:
        return Cmd.to_json_str(self.__raw_info, indent=4)

    def dump_raw_info(self) -> dict[str, str]:
        return self.__raw_info.copy()

    @classmethod
    def from_df(cls, df: pl.DataFrame) -> Iid:
        if df.height != 1:
            raise ValueError("Iid DataFrame must contain exactly 1 row")

        dct = df.row(0, named=True)

        return Iid(dct)
