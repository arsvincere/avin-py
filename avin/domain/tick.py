# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from dataclasses import dataclass

import polars as pl

from avin.domain.direction import Direction
from avin.utils.dt import DateTime, ts_to_dt


@dataclass(frozen=True, slots=True)
class Tick:
    ts: int
    direction: Direction
    price: float
    lots: int
    quantity: int
    value: float

    def __str__(self) -> str:
        s = (
            f"Tick: {self.dt} {self.direction} "
            f"{self.lots}x{self.quantity}x{self.price}={self.value}"
        )
        return s

    @property
    def dt(self) -> DateTime:
        return ts_to_dt(self.ts)

    def is_buy(self) -> bool:
        return self.direction == Direction.BUY

    def is_sell(self) -> bool:
        return self.direction == Direction.SELL

    # def to_df(self) -> pl.DataFrame:
    #     data = {
    #         "datetime": [str(self.dt)],
    #         "direction": [self.direction.short_name],
    #         "price": [self.price],
    #         "lots": [self.lots],
    #         "quantity": [self.quantity],
    #         "value": [self.value],
    #         "ts": [self.ts],
    #     }
    #
    #     df = pl.DataFrame(data)
    #
    #     return df

    @classmethod
    def from_df(cls, df: pl.DataFrame) -> list[Tick]:
        ticks: list[Tick] = []

        for _, direction, price, lots, quantity, value, ts in df.iter_rows():
            ticks.append(
                Tick(
                    ts,
                    Direction.from_str(direction),
                    price,
                    lots,
                    quantity,
                    value,
                )
            )

        return ticks

    # @classmethod
    # def schema(cls) -> pl.Schema:
    #     return pl.Schema(
    #         {
    #             "datetime": pl.String,
    #             "direction": pl.String,
    #             "price": pl.Float64,
    #             "lots": pl.Int64,
    #             "quantity": pl.Int64,
    #             "value": pl.Float64,
    #             "ts": pl.Int64,
    #         }
    #     )
