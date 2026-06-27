# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import enum


class Exchange(enum.StrEnum):
    """All exchanges enum."""

    MOEX = "MOEX"

    @classmethod
    def from_str(cls, value: str) -> Exchange:
        """Get enum from str."""

        if not isinstance(value, str):
            raise TypeError(value)

        s = value.upper()
        if s in cls.__members__:
            return cls[s]

        raise ValueError(
            f"Unknown exchange '{value}'. "
            f"Available: {', '.join(cls._member_names_)}"
        )
