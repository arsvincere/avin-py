# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

"""Custom exceptions for Avin system."""


# =========================
# Base
# =========================


class AvinError(Exception):
    """Base exception for Avin project."""


# =========================
# Config
# =========================


class ConfigNotFound(AvinError): ...


# =========================
# Data
# =========================


class DataNotFound(AvinError): ...


class InstrumentNotFound(AvinError): ...


# =========================
# Auth / Connect
# =========================


class InvalidToken(AvinError): ...
