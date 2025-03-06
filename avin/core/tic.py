#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from typing import TypeVar

from avin.config import Usr
from avin.core.direction import Direction
from avin.utils import DateTime

Asset = TypeVar("Asset")


class Tic:
    def __init__(  # {{{
        self,
        dt: DateTime,
        direction: Direction,
        price: float,
        lots: int,
        asset: Optional[Asset] = None,
    ):
        self.__dt = dt
        self.__direction = direction
        self.__price = price
        self.__lots = lots
        self.__asset = asset

    # }}}
    def __str__(self):  # {{{
        usr_dt = self.dt + Usr.TIME_DIF
        str_dt = usr_dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"Tic={str_dt} {self.__asset} "
            f"{self.__direction.name} {self.__price} {self.__lots}"
        )

        return string

    # }}}

    @property  # dt  # {{{
    def dt(self) -> DateTime:
        return self.__dt

    # }}}
    @property  # direction  # {{{
    def direction(self) -> Direction:
        return self.__direction

    # }}}
    @property  # price  # {{{
    def price(self) -> float:
        return self.__price

    # }}}
    @property  # lots  # {{{
    def lots(self) -> int:
        return self.__lots

    # }}}
    @property  # asset  # {{{
    def asset(self) -> Asset:
        return self.__asset

    # }}}

    def setAsset(self, asset: Asset) -> None:  # {{{
        self.__asset = asset

    # }}}
    def amount(self) -> float | None:  # {{{
        if self.__asset is None:
            return None

        amount = self.__price * self.__lots * self.__asset.lot
        return amount

    # }}}


if __name__ == "__main__":
    ...
