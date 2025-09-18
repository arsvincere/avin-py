# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum

from avin.utils import InvalidDirection


class Direction(enum.Enum):
    """Order and transaction direction.

    # ru
    Направление сделки, перечисление, используется в ордерах, тиках...
    """

    BUY = 1
    SELL = -1

    @classmethod
    def from_str(cls, s: str) -> Direction:
        """Get enum from str.

        Args:
            string: direction name.

        Returns:
            Direction Enum.

        Raises:
            InvalidDirection if name not exists.
        """

        directions = {
            "B": Direction.BUY,
            "BUY": Direction.BUY,
            "S": Direction.SELL,
            "SELL": Direction.SELL,
        }

        if value := directions.get(s):
            return value

        raise InvalidDirection(
            f"Invalid name. Choice from {Direction._member_names_}"
        )

    def short_name(self) -> str:
        """Direction short name.

        # ru
        Короткое имя, для BUY="b", для SELL="s".

        Используется в датафреймах с тиковыми данными, в столбце "direction"
        """
        match self:
            case Direction.BUY:
                return "B"
            case Direction.SELL:
                return "S"


if __name__ == "__main__":
    ...
