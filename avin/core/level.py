# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from dataclasses import dataclass

from avin.core.tick import Tick


@dataclass(slots=True)
class Level:
    price: float

    vol_b: int = 0
    vol_s: int = 0

    val_b: float = 0.0
    val_s: float = 0.0

    trades_b: int = 0
    trades_s: int = 0

    @property
    def vol(self) -> int:
        return self.vol_b + self.vol_s

    @property
    def val(self) -> float:
        return self.val_b + self.val_s

    @property
    def trades(self) -> int:
        return self.trades_b + self.trades_s

    @property
    def delta_vol(self) -> int:
        return self.vol_b - self.vol_s

    @property
    def delta_val(self) -> float:
        return self.val_b - self.val_s

    @property
    def delta_trades(self) -> int:
        return self.trades_b - self.trades_s

    def add(self, tick: Tick) -> None:
        if self.price != tick.price:
            raise ValueError(
                f"tick price {tick.price} != level price {self.price}"
            )

        if tick.is_buy():
            self.vol_b += tick.lots
            self.val_b += tick.value
            self.trades_b += 1
        else:
            self.vol_s += tick.lots
            self.val_s += tick.value
            self.trades_s += 1
