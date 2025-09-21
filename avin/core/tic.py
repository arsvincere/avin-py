# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from datetime import datetime as DateTime

import polars as pl

from avin.core.direction import Direction
from avin.utils import ts_to_dt, utc_to_local


class Tic:
    def __init__(self, data: pl.DataFrame):
        assert len(data) == 1

        self.__data = data

    def __str__(self):
        s = (
            f"Tic: {self.dt_local()} "
            f"{self.direction.name} {self.lots}x{self.price}={self.value}"
        )

        return s

    def __eq__(self, other):
        return (
            self.ts == other.ts
            and self.direction == other.direction
            and self.lots == other.lots
            and self.price == other.price
            and self.value == other.value
        )

    @classmethod
    def new(
        cls,
        ts: int,
        direction: Direction,
        lots: int,
        price: float,
        value: float,
        session: int | None = None,
        tradeno: int | None = None,
    ):
        df = pl.DataFrame(
            {
                "ts_nanos": ts,
                "direction": direction.short_name(),
                "lots": lots,
                "price": price,
                "value": value,
                "session": session,
                "tradeno": session,
            }
        )

        return Tic(df)

    @classmethod
    def schema(self) -> dict:
        """Polars dataframe schema for tic"""

        tic_schema = {
            "ts_nanos": pl.Int64,
            "direction": pl.String,
            "lots": pl.Int64,
            "price": pl.Float64,
            "value": pl.Float64,
            "session": pl.Int8,
            "tradeno": pl.Int64,
        }

        return tic_schema

    @property
    def df(self) -> pl.DataFrame:
        """Tic data as dataframe"""

        return self.__data

    @property
    def ts(self) -> int:
        """Tic timestamp"""

        return self.__data.item(0, "ts_nanos")

    @property
    def direction(self) -> Direction:
        """Tic direction"""

        short_name = self.__data.item(0, "direction")
        direction = Direction.from_str(short_name)

        return direction

    @property
    def lots(self) -> int:
        """Tic lots"""

        return self.__data.item(0, "lots")

    @property
    def price(self) -> float:
        """Tic price"""

        return self.__data.item(0, "price")

    @property
    def value(self) -> float:
        """Tic value"""

        return self.__data.item(0, "value")

    def dt(self) -> DateTime:
        """Return DateTime UTC of tic.

        # ru
        Возвращает DateTime UTC тика.
        """

        return ts_to_dt(self.ts)

    def dt_local(self) -> str:
        """Return local date time of tic as str.

        # ru
        Возвращает локальную (наивную) дату и время тика как строку.
        Форматирование строки и оффсет задается в конфиге.
        """
        dt = ts_to_dt(self.ts)

        return utc_to_local(dt)

    def is_buy(self) -> bool:
        return self.direction == Direction.BUY

    def is_sell(self) -> bool:
        return self.direction == Direction.SELL


if __name__ == "__main__":
    ...
