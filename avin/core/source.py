# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum


class Source(enum.Enum):
    """Market data source."""

    MOEX = 1
    TINKOFF = 2

    @classmethod
    def from_str(cls, s: str) -> Source:
        """Get enum from str.

        Args:
            s: category name.

        Returns:
            Category Enum.

        Raises:
            InvalidSource if category not exists.
        """

        if attr := getattr(cls, s.upper(), None):
            return attr

        raise ValueError(
            f"Source '{s}' not found. Choice from {Source._member_names_}"
        )


if __name__ == "__main__":
    ...
