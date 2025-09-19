# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

"""Custom exceptions."""


class AvinError(Exception):
    """Any error"""


class ConfigNotFound(Exception):
    """Config not found exception."""


class SourceNotFound(Exception):
    """Source not found exception."""


class ExchangeNotFound(Exception):
    """Exchange not found exception."""


class CategoryNotFound(Exception):
    """Category not found exception."""


class TickerNotFound(Exception):
    """Ticker not found exception."""


class InvalidMarketData(Exception):
    """Invalid market data name exception."""


class DataNotFound(Exception):
    """Data not found exception."""


class InvalidDirection(Exception):
    """Invalid direction name exception."""
