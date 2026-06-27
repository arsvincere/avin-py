# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import enum


class Direction(enum.Enum):
    BUY = 1
    SELL = -1

    def __str__(self) -> str:
        return self.name

    @property
    def short_name(self) -> str:
        return "B" if self is Direction.BUY else "S"

    @classmethod
    def from_str(cls, string: str) -> Direction:
        if not isinstance(string, str):
            raise TypeError(string)

        match string.upper():
            case "BUY" | "B":
                return cls.BUY
            case "SELL" | "S":
                return cls.SELL
            case _:
                raise ValueError(
                    f"Unknown direction '{string}'. "
                    f"Available: BUY, SELL, B, S"
                )
