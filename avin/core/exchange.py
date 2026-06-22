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

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, string: str) -> Exchange:
        """Get enum from str.

        Args:
            string: category name.

        Returns:
            Category Enum.

        Raises:
            ValueError if category not exists.
        """

        if attr := getattr(cls, string.upper(), None):
            return attr

        raise ValueError(
            f"Unknown exchange '{string}'. "
            f"Available: {', '.join(cls._member_names_)}"
        )
