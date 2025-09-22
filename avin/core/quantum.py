# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import polars as pl

from avin.core.quant import Quant


class Quantum:
    def __init__(self, tics: pl.DataFrame):
        prices = tics["price"].unique()

        self.__quants = list()
        for price in prices:
            df = tics.filter(pl.col("price") == price)
            q = Quant.from_df(df)
            self.__quants.append(q)

    @property
    def quants(self) -> list[Quant]:
        return self.__quants

    def poc(self) -> Quant:
        max = self.__quants[0]

        for q in self.__quants:
            if q.vol > max.vol:
                max = q

        return max


if __name__ == "__main__":
    ...
