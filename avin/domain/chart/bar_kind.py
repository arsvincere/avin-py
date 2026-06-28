# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import enum


class BarKind(enum.IntEnum):
    BULL = 1
    DOJI = 0
    BEAR = -1

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, value: str) -> BarKind:
        if not isinstance(value, str):
            raise TypeError(value)

        match value.upper():
            case "BULL":
                return cls.BULL
            case "DOJI":
                return cls.DOJI
            case "BEAR":
                return cls.BEAR
            case _:
                raise ValueError(
                    f"Unknown bar kind '{value}'. Available: BULL, BEAR, DOJI"
                )
