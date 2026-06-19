# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import enum


class Exchange(enum.Enum):
    """All exchanges enum."""

    MOEX = 1

    @classmethod
    def from_str(cls, string: str) -> Exchange:
        """Get enum from str.

        Args:
            string: category name.

        Returns:
            Category Enum.

        Raises:
            ExchangeNotFound if category not exists.
        """

        if attr := getattr(cls, string.upper(), None):
            return attr

        raise ValueError(
            f"Exchangw not found. Choice from {Exchange._member_names_}"
        )
