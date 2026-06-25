# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from dataclasses import dataclass

import polars as pl

from avin.core.direction import Direction
from avin.utils.conf import cfg
from avin.utils.dt import DateTime, ts_to_dt


@dataclass(frozen=True)
class Tic:
    ts: int
    direction: Direction
    price: float
    lots: int
    quantity: int
    value: float

    def __str__(self) -> str:
        s = (
            f"Tic: {self.dt_local} {self.direction} "
            f"{self.lots}x{self.quantity}x{self.price}={self.value}"
        )
        return s

    @property
    def dt(self) -> DateTime:
        return ts_to_dt(self.ts)

    @property
    def dt_local(self) -> DateTime:
        return self.dt.astimezone(cfg.local_timezone)

    def is_buy(self) -> bool:
        return self.direction == Direction.BUY

    def is_sell(self) -> bool:
        return self.direction == Direction.SELL

    def to_df(self) -> pl.DataFrame:
        data = {
            "datetime": [str(self.dt)],
            "direction": [self.direction.short_name],
            "price": [self.price],
            "lots": [self.lots],
            "quantity": [self.quantity],
            "value": [self.value],
            "ts": [self.ts],
        }

        df = pl.DataFrame(data)

        return df

    @classmethod
    def from_df(cls, df: pl.DataFrame) -> list[Tic]:
        tics = list()

        for row in df.iter_rows(named=True):
            t = Tic(
                row["ts"],
                Direction.from_str(row["direction"]),
                row["price"],
                row["lots"],
                row["quantity"],
                row["value"],
            )
            tics.append(t)

        return tics

    @classmethod
    def schema(cls) -> pl.Schema:
        return pl.Schema(
            {
                "datetime": pl.String,
                "direction": pl.String,
                "price": pl.Float64,
                "lots": pl.Int64,
                "quantity": pl.Int64,
                "value": pl.Float64,
                "ts": pl.Int64,
            }
        )
