#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from abc import ABC, abstractmethod


class Indicator(ABC):
    name = "AbstractIndicator"

    @abstractmethod
    def __init__(self): ...

    def __str__(self):
        return f"Indicator={self.name}"


if __name__ == "__main__":
    ...
