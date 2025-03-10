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
            tic.direction.short_name,
            tic.price,
            tic.lots,
            tic.amount(),
        ]

    # }}}

    def split(self, tf: TimeFrame) -> list[pd.DataFrame]:  # {{{
        """Return list[DataFrame] = parts by bar of TimeFrame"""

        # alias
        df = self.__df

        # check empty
        if df.empty:
            return list()

        all_parts = list()

        # first part
        begin = df.at[0, "dt"]
        end = next_dt(begin, tf)
        condition = (begin <= df["dt"]) & (df["dt"] < end)
        selected = df.loc[condition]
        all_parts.append(selected)

        # other parts
        next_day = next_dt(begin, TimeFrame("D"))
        while end < next_day:
            begin = end
            end = next_dt(begin, tf)
            condition = (begin <= df["dt"]) & (df["dt"] < end)
            selected = df.loc[condition]
            all_parts.append(selected)

        return all_parts

    # }}}
    def quant(self, tf: TimeFrame) -> pd.Series:  # {{{
        """Return Series of DataFrame like:

           price    buy   sell
        0  320.5  32050      0
        1  321.0      0  96300

        Возвращает pd.Series из датафреймов:
            - цена
            - сумма активных покупок
            - сумма активных продаж
        Ключи Series - dt кванта
        """

        quants = pd.Series()
        parts = self.split(tf)
        for part in parts:
            if part.empty:
                continue

            levels = list()
            buy_values = list()
            sell_values = list()

            prices = part.loc[~part["price"].duplicated()]["price"]
            for price in prices:
                selected = part.loc[part["price"] == price]
                buy = selected[selected["direction"] == "B"]["amount"].sum()
                sell = selected[selected["direction"] == "S"]["amount"].sum()

                levels.append(price)
                buy_values.append(buy)
                sell_values.append(sell)

            k = part.iloc[0]["dt"].replace(second=0)
            q = pd.DataFrame(
                {
                    "price": levels,
                    "buy": buy_values,
                    "sell": sell_values,
                }
            )
            quants[k] = q

        return quants

    # }}}
    def hist(self, tf: TimeFrame) -> pd.DataFrame:  # {{{
        """Return DataFrame like: # {{{

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
        """  # }}}

        dts = list()
        buys = list()
        sells = list()

        parts = self.split(tf)
        for part in parts:
            if part.empty:
                continue

            dt = part.iloc[0]["dt"]
            buy = part.loc[part["direction"] == "B"]["amount"].sum()
            sell = part.loc[part["direction"] == "S"]["amount"].sum()

            dts.append(dt.replace(second=0, microsecond=0))
            buys.append(buy)
            sells.append(sell)

        # create df histogram
        df_hist = pd.DataFrame(
            {
                "dt": dts,
                "buy": buys,
                "sell": sells,
            }
        )

        return df_hist


# }}}


if __name__ == "__main__":
    ...
