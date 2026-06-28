# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass

from avin.domain.common.direction import Direction
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
