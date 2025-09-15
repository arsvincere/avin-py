# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations


class Ticker:
    def __init__(self, string: str):
        self.__ticker = string.upper()

    def __str__(self):
        return self.__ticker

    def __eq__(self, other):
        return self.__ticker == other.__ticker

    @property
    def name(self) -> str:
        return self.__ticker
