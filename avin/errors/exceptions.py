# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

"""Custom exceptions used across the AVIN project."""

# =========================
# Base
# =========================


class AvinError(Exception):
    """Base exception for the AVIN project."""


class DomainError(AvinError):
    """Base exception for domain layer errors."""


# =========================
# Config
# =========================


class ConfigNotFoundError(AvinError):
    """Configuration file was not found."""


# =========================
# Data
# =========================


class DataNotFoundError(AvinError):
    """Requested market data was not found in storage."""


class InstrumentNotFoundError(AvinError):
    """Requested instrument was not found."""


class DataUnavailableError(DomainError):
    """Requested domain data is not currently available."""


# =========================
# Auth / Connect
# =========================


class InvalidTokenError(AvinError):
    """Authentication token is invalid."""
