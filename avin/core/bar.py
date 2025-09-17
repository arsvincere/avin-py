# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum
from datetime import datetime as DateTime

import polars as pl

from avin.core.range import Range
from avin.utils import ts_to_dt, utc_to_local


class Bar:
    """Like cundle, but more shortly name.

    # ru
    Бар - суть таже что и свеча, но слово короче.

    Обертка над polars.DataFrame с удобным доступом к значениям.
    """

    class Kind(enum.Enum):
        """Bar types enum.

        # ru
        Перечисление типов бара.
        Бычий, медвежий или доджи (когда open == close).
        """

        BULL = 1
        DODJI = 0
        BEAR = -1

    def __init__(self, df: pl.DataFrame):
        assert len(df) == 1

        self.__data = df

    def __str__(self):
        s = (
            f"Bar: dt={self.dt_local()} "
            f"o={self.o} h={self.h} l={self.l} c={self.c} v={self.v}"
        )

        return s

    def __contains__(self, price: float):
        """Check for price in bar.

        # ru
        Проверка на вхождение цены в диапазон бара.
        """
        return self.l <= price <= self.h

    def __eq__(self, other):
        return (
            self.ts == other.ts
            and self.o == other.o
            and self.h == other.h
            and self.l == other.l
            and self.c == other.c
            and self.v == other.v
        )

    @classmethod
    def from_ohlcv(
        cls,
        ts: int,
        open: float,
        high: float,
        low: float,
        close: float,
        vol: int,
        value: int | None = None,
    ) -> Bar:
        """Create Bar from OHLCV.

        # ru
        Создает датафрейм из OHLCV значений и оборачивает его в Bar.
        Возвращает Bar.

        ## Пример датафрейма внутри
        ```text
        ┌───────────┬────────┬────────┬────────┬────────┬───────────┬────────┐
        │ ts_nanos  ┆ open   ┆ high   ┆ low    ┆ close  ┆ volume    ┆ value  │
        │ ---       ┆ ---    ┆ ---    ┆ ---    ┆ ---    ┆ ---       ┆ ---    │
        │ i64       ┆ f64    ┆ f64    ┆ f64    ┆ f64    ┆ i64       ┆ f64    │
        ╞═══════════╪════════╪════════╪════════╪════════╪═══════════╪════════╡
        │ 173585... ┆ 280.0  ┆ 280.41 ┆ 271.8  ┆ 272.25 ┆ 43086870  ┆ ...    │
        """

        df = pl.DataFrame(
            {
                "ts_nanos": ts,
                "open": open,
                "high": high,
                "low": low,
                "close": close,
                "volume": vol,
                "value": value,
            }
        )

        return Bar(df)

    @classmethod
    def join(cls, b1: Bar, b2: Bar) -> Bar:
        """Join bar_1 and bar_2, used when converting timeframes.

        # ru
        Объединяет бары. Используется для преобразования таймфреймов.
        """

        ts = b1.ts
        open = b1.o
        high = max(b1.h, b2.h)
        low = min(b1.l, b2.l)
        close = b2.c
        vol = b1.v + b2.v

        df = pl.DataFrame(
            {
                "ts_nanos": ts,
                "open": open,
                "high": high,
                "low": low,
                "close": close,
                "volume": vol,
                "value": None,
            }
        )

        return Bar(df)

    @classmethod
    def schema(cls) -> dict:
        """Polars dataframe schema for bars"""

        bar_schema = {
            "ts_nanos": pl.Int64,
            "open": pl.Float64,
            "high": pl.Float64,
            "low": pl.Float64,
            "close": pl.Float64,
            "volume": pl.Int64,
            "value": pl.Float64,
        }

        return bar_schema

    @property
    def df(self) -> pl.DataFrame:
        return self.__data

    @property
    def ts(self) -> int:
        """Bar timestamp"""
        return self.__data.item(0, "ts_nanos")

    @property
    def o(self) -> float:
        """Bar open"""
        return self.__data.item(0, "open")

    @property
    def h(self) -> float:
        """Bar high"""
        return self.__data.item(0, "high")

    @property
    def l(self) -> float:
        """Bar low"""
        return self.__data.item(0, "low")

    @property
    def c(self) -> float:
        """Bar close"""
        return self.__data.item(0, "close")

    @property
    def v(self) -> int:
        """Bar volume"""
        return self.__data.item(0, "volume")

    def dt(self) -> DateTime:
        """Return DateTime UTC of bar.

        # ru
        Возвращает DateTime UTC бара.
        """

        return ts_to_dt(self.ts)

    def dt_local(self) -> str:
        """Return local date time of bar as str.

        # ru
        Возвращает локальную (наивную) дату и время бара как строку.
        Форматирование строки и оффсет задается в конфиге.
        """
        dt = ts_to_dt(self.ts)

        return utc_to_local(dt)

    def kind(self) -> Bar.Kind:
        """Return kind of bar, enum.

        # ru
        Возвращает тип бара, перечисление 'Bar.Kind': бычий, медвежий, доджи.
        """
        if self.is_bear():
            return Bar.Kind.BEAR
        elif self.is_bull():
            return Bar.Kind.BULL
        else:
            return Bar.Kind.DODJI

    def is_bear(self) -> bool:
        """Check for bar is bear.

        # ru
        Если бар медвежий -> true, иначе -> false
        """
        return self.o > self.c

    def is_bull(self) -> bool:
        """Check for bar is bull.

        # ru
        Если бар бычий -> true, иначе -> false
        """
        return self.o < self.c

    def is_dodji(self) -> bool:
        """Check for bar is dodji.

        # ru
        Если бар доджи -> true, иначе -> false
        """
        return self.o == self.c

    def full(self) -> Range:
        """Full range of bar [bar.l, bar.h]

        # ru
        Возвращает полный диапазон бара [bar.l, bar.h]
        """

        return Range(self.l, self.h)

    def body(self) -> Range:
        """Body range of bar [bar.o, bar.c]

        # ru
        Возвращает диапазон тела бара [bar.o, bar.c]
        """

        return Range(self.o, self.c)

    def lower(self) -> Range:
        """Lower shadow range of bar.

        # ru
        Возвращает диапазон нижней тени бара.
        """

        if self.is_bull():
            return Range(self.l, self.o)
        else:
            return Range(self.l, self.c)

    def upper(self) -> Range:
        """Upper shadow range of bar.

        # ru
        Возвращает диапазон верхней тени бара.
        """

        if self.is_bull():
            return Range(self.c, self.h)
        else:
            return Range(self.o, self.h)


if __name__ == "__main__":
    ...
