# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import enum

from avin.utils import InvalidMarketData


class MarketData(enum.Enum):
    """List for selecting the market data type.

    # ru
    Перечисление для выбора типа данных.
    """

    BAR_1M = enum.auto()
    BAR_10M = enum.auto()
    BAR_1H = enum.auto()
    BAR_D = enum.auto()
    BAR_W = enum.auto()
    BAR_M = enum.auto()
    TIC = enum.auto()
    TRADE_STATS = enum.auto()
    ORDER_STATS = enum.auto()
    OB_STATS = enum.auto()

    @classmethod
    def from_str(cls, string: str) -> MarketData:
        """Get enum from str.

        Args:
            string: market data name.

        Returns:
            MarketData Enum.

        Raises:
            InvalidMarketData if market data not exists.
        """
        if attr := getattr(cls, string.upper(), None):
            return attr

        raise InvalidMarketData(
            f"Invalid name. Choice from {MarketData._member_names_}"
        )


if __name__ == "__main__":
    ...
