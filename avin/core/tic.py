#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from typing import TypeVar

import pandas as pd

from avin.config import Usr
from avin.core.direction import Direction
from avin.core.timeframe import TimeFrame
from avin.data import Instrument
from avin.utils import DateTime, logger, next_dt

Asset = TypeVar("Asset")


class Tic:  # {{{
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
    def amount(self) -> int | None:  # {{{
        if self.__asset is None:
            return None

        amount = self.__price * self.__lots * self.__asset.lot
        return int(amount)

    # }}}
    def isBuy(self) -> bool:  # {{{
        return self.__direction == Direction.BUY

    # }}}
    def isSell(self) -> bool:  # {{{
        return self.__direction == Direction.SELL

    # }}}


# }}}
class Tics:  # {{{
    def __init__(  # {{{
        self,
        instrument: Instrument,
        tics: pd.DataFrame = None,
    ):
        self.__instrument = instrument

        if tics is None:
            self.__df = pd.DataFrame(
                columns=[
                    "dt",
                    "direction",
                    "price",
                    "lots",
                    "amount",
                ],
            )
        else:
            self.__df = tics

    # }}}

    @property  # instrument   # {{{
    def instrument(self) -> Instrument:
        return self.__instrument

    # }}}
    @property  # data_frame   # {{{
    def data_frame(self) -> pd.DataFrame:
        return self.__df

    # }}}

    def add(self, tic: Tic) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        tic.setAsset(self.__instrument)

        self.__df.loc[len(self.__df)] = [
            tic.dt,
            tic.direction,
            tic.price,
            tic.lots,
            tic.amount(),
        ]

    # }}}
    def level(self) -> pd.DataFrame:  # {{{
        """Return DataFrame like:

           price    buy   sell
        0  320.5  32050      0
        1  321.0      0  96300

        Возвращает датафрейм:
            - цена
            - сумма активных покупок
            - сумма активных продаж
        """

        df = self.__df
        levels = list()
        buy_values = list()
        sell_values = list()
        prices = df.loc[~df["price"].duplicated()]["price"]

        for price in prices:
            selected = df[df["price"] == price]
            buy = selected[selected["direction"] == Direction.BUY]
            buy_value = buy["amount"].sum()
            sell = selected[selected["direction"] == Direction.SELL]
            sell_value = sell["amount"].sum()

            levels.append(price)
            buy_values.append(buy_value)
            sell_values.append(sell_value)

        df_level = pd.DataFrame(
            {
                "price": levels,
                "buy": buy_values,
                "sell": sell_values,
            }
        )

        return df_level

    # }}}
    def graph(self, tf: TimeFrame) -> pd.DataFrame:  # {{{
        """Return DataFrame like:

                             dt          buy         sell
        0   2025-03-06 06:59:34    8421750.0    5790060.0
        1   2025-03-06 07:00:00  159324809.5  104707120.9
        2   2025-03-06 07:05:00   57389768.6  118869304.0
        3   2025-03-06 07:10:00    8474116.5   25889664.3
        4   2025-03-06 07:15:00   41633042.3   14208032.7

        Возвращает датафрейм:
            - dt начала бара
            - сумма активных покупок
            - сумма активных продаж
        """

        df = self.__df
        dts = list()
        buys = list()
        sells = list()

        begin = df.at[0, "dt"]
        end = next_dt(begin, tf)
        condition = (begin <= df["dt"]) & (df["dt"] < end)
        selected = df.loc[condition]
        while not selected.empty:
            buy = selected.loc[selected["direction"] == Direction.BUY]
            sell = selected.loc[selected["direction"] == Direction.SELL]
            buy_amount = buy["amount"].sum()
            sell_amount = sell["amount"].sum()

            dts.append(begin)
            buys.append(buy_amount)
            sells.append(sell_amount)

            begin = end
            end = next_dt(begin, tf)
            condition = (begin <= df["dt"]) & (df["dt"] < end)
            selected = df.loc[condition]

        df_graph = pd.DataFrame(
            {
                "dt": dts,
                "buy": buys,
                "sell": sells,
            }
        )

        return df_graph

    # }}}


# }}}


if __name__ == "__main__":
    ...
