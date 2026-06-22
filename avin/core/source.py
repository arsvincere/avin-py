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

    TINKOFF = 1
    MOEXALGO = 2

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, string: str) -> Source:
        """Get enum from str.

        Args:
            string: source name.

        Returns:
            Category Enum.

        Raises:
            InvalidSource if category not exists.
        """
        if not isinstance(string, str):
            raise TypeError(string)

        s = string.upper()
        if s in cls.__members__:
            return cls[s]

        raise ValueError(
            f"Unknown source '{string}'. "
            f"Available: {', '.join(cls.__members__)}"
        )


if __name__ == "__main__":
    ...
