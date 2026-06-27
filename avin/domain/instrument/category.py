# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import enum


class Category(enum.StrEnum):
    """All categories enum."""

    CURRENCY = "CURRENCY"
    INDEX = "INDEX"
    SHARE = "SHARE"
    BOND = "BOND"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    ETF = "ETF"

    @classmethod
    def from_str(cls, value: str) -> Category:
        """Get enum from str."""
        if not isinstance(value, str):
            raise TypeError(value)

        s = value.upper()
        if s in cls.__members__:
            return cls[s]

        raise ValueError(
            f"Unknown category '{value}'. "
            f"Available: {', '.join(cls._member_names_)}"
        )
