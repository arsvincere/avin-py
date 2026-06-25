# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin.domain.footprint.level import Level
from avin.domain.tick import Tick


class Ladder:
    def __init__(self) -> None:
        self.levels: dict[float, Level] = {}

    def __len__(self) -> int:
        return len(self.levels)

    def __contains__(self, price: float) -> bool:
        return price in self.levels

    def __iter__(self):
        return iter(self.sorted_levels)

    @property
    def is_empty(self) -> bool:
        return not self.levels

    @property
    def high(self) -> float:
        self._check_not_empty()

        return max(self.levels)

    @property
    def low(self) -> float:
        self._check_not_empty()

        return min(self.levels)

    @property
    def sorted_prices(self) -> list[float]:
        return sorted(self.levels)

    @property
    def sorted_levels(self) -> list[Level]:
        return [self.levels[p] for p in sorted(self.levels)]

    def add(self, tick: Tick) -> None:
        level = self.levels.get(tick.price)

        if level is None:
            level = Level(price=tick.price)
            self.levels[tick.price] = level

        level.add(tick)

    def get(self, price: float) -> Level | None:
        return self.levels.get(price)

    def _check_not_empty(self) -> None:
        if self.is_empty:
            raise ValueError("ladder is empty")
