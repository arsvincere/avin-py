# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum
from datetime import UTC
from datetime import time as Time

from avin.utils import ExchangeNotFound


class Exchange(enum.Enum):
    """All exchanges enum."""

    MOEX = 1
    # SPB = 2

    @classmethod
    def from_str(cls, string: str) -> Exchange:
        """Get enum from str.

        Args:
            string: exchange name.

        Returns:
            Exchange Enum.

        Raises:
            ExchangeNotFound if exchange not exists.
        """
        if attr := getattr(cls, string.upper(), None):
            return attr

        raise ExchangeNotFound(
            f"Can't found exchange '{string}'. "
            f"Choice from {Exchange._member_names_}"
        )

    def morning(self) -> tuple[Time, Time]:
        match self:
            case Exchange.MOEX:
                return (Time(3, 59, tzinfo=UTC), Time(7, 0, tzinfo=UTC))
            case _:
                raise NotImplementedError()

    def day(self) -> tuple[Time, Time]:
        match self:
            case Exchange.MOEX:
                return (Time(7, 0, tzinfo=UTC), Time(15, 39, tzinfo=UTC))
            case _:
                raise NotImplementedError()

    def evening(self) -> tuple[Time, Time]:
        match self:
            case Exchange.MOEX:
                return (Time(16, 5, tzinfo=UTC), Time(20, 49, tzinfo=UTC))
            case _:
                raise NotImplementedError()


if __name__ == "__main__":
    ...
