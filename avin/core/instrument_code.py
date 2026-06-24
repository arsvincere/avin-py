# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin.core.category import Category
from avin.core.exchange import Exchange


def parse_code(
    code: str,
) -> tuple[Exchange, Category, str]:
    parts = code.upper().split("_", maxsplit=2)
    if len(parts) != 3:
        raise ValueError(
            f"Invalid instrument code: '{code}'. "
            "Expected format: EXCHANGE_CATEGORY_TICKER"
        )

    try:
        return (
            Exchange(parts[0]),
            Category(parts[1]),
            parts[2],
        )

    except ValueError as e:
        raise ValueError(
            f"Invalid instrument code: '{code}'. "
            "Expected format: EXCHANGE_CATEGORY_TICKER"
        ) from e
