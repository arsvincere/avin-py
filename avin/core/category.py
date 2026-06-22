# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum


class Category(enum.Enum):
    """All categories enum."""

    CURRENCY = 1
    INDEX = 2
    SHARE = 3
    BOND = 4
    FUTURE = 5
    OPTION = 6
    ETF = 7

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, string: str) -> Category:
        """Get enum from str.

        Args:
            string: category name.

        Returns:
            Category Enum.

        Raises:
            ValueError: if category does not exist.
        """

        if attr := getattr(cls, string.upper(), None):
            return attr

        raise ValueError(
            f"Unknown category '{string}'. "
            f"Available: {', '.join(cls._member_names_)}"
        )
