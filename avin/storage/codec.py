# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import polars as pl

from avin.domain.chart.bar import Bar
from avin.domain.common.direction import Direction
from avin.domain.raw.tick import Tick
from avin.storage.schema import Schema


class StorageCodec:
    @staticmethod
    def bars_from_df(df: pl.DataFrame) -> list[Bar]:
        bars: list[Bar] = []
        df = df.select(Schema.BAR.names())

        # First column is human-readable datetime for parquet viewers.
        for _, o, h, l, c, v, ts in df.iter_rows():  # noqa: E741
            bars.append(Bar(ts, o, h, l, c, v))

        return bars

    @staticmethod
    def bars_to_df(bars: list[Bar]) -> pl.DataFrame:
        data = {
            "datetime": [str(bar.dt) for bar in bars],
            "open": [bar.open for bar in bars],
            "high": [bar.high for bar in bars],
            "low": [bar.low for bar in bars],
            "close": [bar.close for bar in bars],
            "volume": [bar.vol for bar in bars],
            "ts": [bar.ts for bar in bars],
        }

        return pl.DataFrame(data, schema=Schema.BAR)

    @staticmethod
    def ticks_from_df(df: pl.DataFrame) -> list[Tick]:
        ticks: list[Tick] = []
        df = df.select(Schema.TICK.names())

        # First column is human-readable datetime for parquet viewers.
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

    @staticmethod
    def ticks_to_df(ticks: list[Tick]) -> pl.DataFrame:
        data = {
            "datetime": [str(tick.dt) for tick in ticks],
            "direction": [tick.direction.short_name for tick in ticks],
            "price": [tick.price for tick in ticks],
            "lots": [tick.lots for tick in ticks],
            "quantity": [tick.quantity for tick in ticks],
            "value": [tick.value for tick in ticks],
            "ts": [tick.ts for tick in ticks],
        }

        return pl.DataFrame(data, schema=Schema.TICK)
