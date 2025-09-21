# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from avin.core.tic import Tic


class Quant:
    def __init__(self, price: float):
        self.__price = price
        self.__vol_b = 0
        self.__vol_s = 0
        self.__val_b = 0.0
        self.__val_s = 0.0

    @property
    def price(self) -> float:
        return self.__price

    @property
    def vol_b(self) -> int:
        return self.__vol_b

    @property
    def vol_s(self) -> int:
        return self.__vol_s

    @property
    def val_b(self) -> float:
        return self.__val_b

    @property
    def val_s(self) -> float:
        return self.__val_s

    def add(self, tic: Tic) -> None:
        assert self.price == tic.price

        if tic.is_buy():
            self.__vol_b += tic.lots
            self.__val_b += tic.value
        else:
            self.__vol_s += tic.lots
            self.__val_s += tic.value

    def vol(self) -> int:
        return self.__vol_b + self.__vol_s

    def val(self) -> float:
        return self.__val_b + self.__val_s


if __name__ == "__main__":
    ...
