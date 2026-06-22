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
        if not isinstance(string, str):
            raise TypeError(string)

        s = string.upper()
        if s in cls.__members__:
            return cls[s]

        raise ValueError(
            f"Unknown exchange '{string}'. "
            f"Available: {', '.join(cls._member_names_)}"
        )
