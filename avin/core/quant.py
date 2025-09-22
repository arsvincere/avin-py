# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import polars as pl

from avin.core.tic import Tic


class Quant:
    def __init__(
        self, price: float, vol_b: int, vol_s: int, val_b: float, val_s: float
    ):
        self.__price = price

        self.__vol_b = vol_b
        self.__vol_s = vol_s
        self.__vol = vol_b + vol_s

        self.__val_b = val_b
        self.__val_s = val_s
        self.__val = val_b + val_s

    @classmethod
    def new(cls, price: float) -> Quant:
        q = Quant(price, 0, 0, 0.0, 0.00)

        return q

    @classmethod
    def from_df(cls, tics: pl.DataFrame) -> Quant:
        price = tics.item(0, "price")
        q = Quant.new(price)

        buy = tics.filter(pl.col("direction") == "B")
        sell = tics.filter(pl.col("direction") == "S")

        q.__vol_b = buy["lots"].sum()  # type: ignore
        q.__vol_s = sell["lots"].sum()  # type: ignore
        q.__vol = q.__vol_b + q.__vol_s

        q.__val_b = buy["value"].sum()
        q.__val_s = sell["value"].sum()
        q.__val = q.__val_b + q.__val_s

        return q

    @property
    def price(self) -> float:
        return self.__price

    @property
    def vol_b(self) -> int:
        return self.__vol_b

    @property
    def vol_s(self) -> int:
        return self.__vol_s

    @property
    def vol(self) -> int:
        return self.__vol

    @property
    def val_b(self) -> float:
        return self.__val_b

    @property
    def val_s(self) -> float:
        return self.__val_s

    @property
    def val(self) -> float:
        return self.__val

    def add(self, tic: Tic) -> None:
        assert self.price == tic.price

        if tic.is_buy():
            self.__vol_b += tic.lots
            self.__val_b += tic.value
        else:
            self.__vol_s += tic.lots
            self.__val_s += tic.value

        self.__vol += tic.lots
        self.__val += tic.value


if __name__ == "__main__":
    ...
