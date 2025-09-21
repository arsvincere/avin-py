# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from avin.core.bar import Bar
from avin.core.tic import Tic


class BarEvent:
    def __init__(self, figi: str, bar: Bar):
        self.figi = figi
        self.bar = bar

    def __str__(self):
        return f"BarEvent={self.figi} {self.bar}"


class TicEvent:
    def __init__(self, figi: str, tic: Tic):
        self.figi = figi
        self.tic = tic

    def __str__(self):
        return f"TicEvent={self.figi} {self.tic}"


if __name__ == "__main__":
    ...
