# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin.core.ladder import Ladder
from avin.core.tick import Tick


class Cluster:
    ladder: Ladder

    ts_first: int
    ts_last: int

    open: float
    high: float
    low: float
    close: float

    vol: int
    val: float
    trades: int

    def __init__(self) -> None:
        self.ladder = Ladder()

        self.ts_first = 0
        self.ts_last = 0

        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0

        self.vol = 0
        self.val = 0.0
        self.trades = 0

    @property
    def is_empty(self) -> bool:
        return self.trades == 0

    def add(self, tick: Tick) -> None:
        if self.is_empty:
            self.ts_first = tick.ts
            self.ts_last = tick.ts

            self.open = tick.price
            self.high = tick.price
            self.low = tick.price
            self.close = tick.price

        else:
            self.ts_last = tick.ts

            self.high = max(self.high, tick.price)
            self.low = min(self.low, tick.price)
            self.close = tick.price

        self.vol += tick.lots
        self.val += tick.value
        self.trades += 1

        self.ladder.add(tick)
