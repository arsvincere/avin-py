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
    try:
        exchange, category, ticker = code.split(
            "_",
            maxsplit=2,
        )

        return (
            Exchange(exchange),
            Category(category),
            ticker,
        )

    except Exception as e:
        raise ValueError(f"Invalid instrument code: {code}") from e


# class InstrumentCode:
#     def __init__(self, code: str):
#         self.exchange
#         self.category
#         self.ticker
