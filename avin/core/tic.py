# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from dataclasses import dataclass

from avin.core.direction import Direction


@dataclass
class Tic:
    ts: int
    direction: Direction
    lots: int
    price: float
    value: float

    def isBuy(self) -> bool:
        return self.direction == Direction.Buy

    def isSell(self) -> bool:
        return self.direction == Direction.Sell
