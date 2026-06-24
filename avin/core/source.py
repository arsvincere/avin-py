# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum


class Source(enum.StrEnum):
    """Market data source."""

    TINKOFF = "TINKOFF"
    MOEXALGO = "MOEXALGO"

    @classmethod
    def from_str(cls, string: str) -> Source:
        """Get enum from str."""
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
