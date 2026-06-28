# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass

from avin.domain.chart.bar_kind import BarKind
from avin.domain.common import PriceRange
from avin.utils.alias import DateTime
from avin.utils.dt import ts_to_dt


@dataclass(frozen=True, slots=True)
class Bar:
    ts: int
    open: float
    high: float
    low: float
    close: float
    vol: int

    def __post_init__(self) -> None:
        if self.low > self.high:
            raise ValueError("Bar low > high")

        if not self.low <= self.open <= self.high:
            raise ValueError("Bar open is outside range")

        if not self.low <= self.close <= self.high:
            raise ValueError("Bar close is outside range")

        if self.vol < 0:
            raise ValueError("Bar volume is negative")

    def __str__(self) -> str:
        return (
            f"Bar: {self.dt} "
            f"{self.open} {self.high} {self.low} {self.close} {self.vol}"
        )

    def __contains__(self, price: float) -> bool:
        return self.low <= price <= self.high

    @property
    def dt(self) -> DateTime:
        return ts_to_dt(self.ts)

    @property
    def kind(self) -> BarKind:
        if self.is_bull():
            return BarKind.BULL
        elif self.is_bear():
            return BarKind.BEAR
        else:
            return BarKind.DOJI

    def is_bull(self) -> bool:
        return self.open < self.close

    def is_bear(self) -> bool:
        return self.open > self.close

    def is_doji(self) -> bool:
        return self.open == self.close

    def full(self) -> PriceRange:
        return PriceRange(self.low, self.high)

    def body(self) -> PriceRange:
        return PriceRange(
            min(self.open, self.close), max(self.open, self.close)
        )

    def lower(self) -> PriceRange:
        return PriceRange(self.low, min(self.open, self.close))

    def upper(self) -> PriceRange:
        return PriceRange(max(self.open, self.close), self.high)

    @classmethod
    def join(cls, b1: Bar, b2: Bar) -> Bar:
        return cls(
            ts=b1.ts,
            open=b1.open,
            high=max(b1.high, b2.high),
            low=min(b1.low, b2.low),
            close=b2.close,
            vol=b1.vol + b2.vol,
        )
