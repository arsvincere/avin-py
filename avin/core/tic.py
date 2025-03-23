#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from typing import TypeVar

import polars as pl

from avin.config import Usr
from avin.core.direction import Direction
from avin.core.timeframe import TimeFrame
from avin.utils import UTC, DateTime, logger, next_dt

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
        asset: Asset,
        tics: pl.DataFrame = None,
    ):
        self.__asset = asset
        self.__schema = {
            "dt": pl.datatypes.Datetime("us", UTC),
            "direction": str,
            "price": float,
            "lots": int,
            "amount": float,
        }

        if tics is None:
            self.__df = pl.DataFrame(schema=self.__schema)
        else:
            self.__df = tics

    # }}}

    @property  # asset   # {{{
    def asset(self) -> Asset:
        return self.__asset

    # }}}
    @property  # data_frame   # {{{
    def data_frame(self) -> pl.DataFrame:
        return self.__df

    # }}}

    def add(self, tic: Tic) -> None:  # {{{
        logger.debug(f"{self.__class__.__name__}.add()")

        tic.setAsset(self.__asset)

        self.__df.loc[len(self.__df)] = [
            tic.dt,
            tic.direction.short_name,
            tic.price,
            tic.lots,
            tic.amount(),
        ]

    # }}}

    def split(self, tf: TimeFrame) -> list[pl.DataFrame]:  # {{{
        """Return list[DataFrame] = parts by bar of TimeFrame"""

        # alias
        df = self.__df

        # check empty
        if df.is_empty():
            return list()

        all_parts = list()
        last_tic_dt = df.item(-1, "dt")
        end = df.item(0, "dt")
        while end < last_tic_dt:
            begin = end
            end = next_dt(end, tf)
            condition = (begin <= pl.col("dt")) & (pl.col("dt") < end)
            selected = df.filter(condition)
            all_parts.append(selected)

        return all_parts

    # }}}
    def hist(self, tf: TimeFrame) -> pl.DataFrame:  # {{{
        """Return DataFrame like: # {{{
        ┌─────────────────────────┬────────────┬────────────┐
        │ dt                      ┆ buy        ┆ sell       │
        │ ---                     ┆ ---        ┆ ---        │
        │ datetime[μs, UTC]       ┆ f64        ┆ f64        │
        ╞═════════════════════════╪════════════╪════════════╡
        │ 2025-03-22 03:59:00 UTC ┆ 1.079989e7 ┆ 1.612385e7 │
        │ 2025-03-22 04:00:00 UTC ┆ 1.3550e8   ┆ 7.4541e7   │
        │ 2025-03-22 04:05:00 UTC ┆ 4.9212e7   ┆ 2.0465e7   │
        │ 2025-03-22 04:10:00 UTC ┆ 1.1269e7   ┆ 3.8757e7   │
        │ 2025-03-22 04:15:00 UTC ┆ 2.3632e7   ┆ 2.0811e7   │
        │ …                       ┆ …          ┆ …          │

        Возвращает датафрейм:
            - dt начала бара (в первом не совпадает с началом периода ТФ)
              а равен dt первого тика
            - сумма активных покупок
            - сумма активных продаж
        """  # }}}

        dts = list()
        buys = list()
        sells = list()

        parts = self.split(tf)
        for part in parts:
            if part.is_empty():
                continue

            dt = part.item(0, "dt")
            buy = part.filter(direction="B")["amount"].sum()
            sell = part.filter(direction="S")["amount"].sum()

            dts.append(dt.replace(second=0, microsecond=0))
            buys.append(buy)
            sells.append(sell)

        # create df histogram
        df_hist = pl.DataFrame(
            {
                "dt": dts,
                "buy": buys,
                "sell": sells,
            }
        )

        return df_hist

    # }}}
    def quant(self, tf: TimeFrame) -> dict[DateTime, pl.DataFrame]:  # {{{
        """Return dict of DataFrame like:

        ┌────────┬────────────┬─────────────┐
        │ price  ┆ buy        ┆ sell        │
        │ ---    ┆ ---        ┆ ---         │
        │ f64    ┆ f64        ┆ f64         │
        ╞════════╪════════════╪═════════════╡
        │ 166.8  ┆ 0.0        ┆ 9.5548044e7 │
        │ 166.81 ┆ 8829253.3  ┆ 6.8592e6    │
        │ 166.82 ┆ 5.321558e6 ┆ 6.9230e6    │
        │ 166.83 ┆ 7270451.4  ┆ 7519028.1   │
        │ 166.84 ┆ 4.9785e6   ┆ 2.4842e6    │
        │ …      ┆ …          ┆ …           │

        Возвращает dict из датафреймов:
            - цена
            - сумма активных покупок
            - сумма активных продаж
        Ключи dict - dt кванта
        """

        quants = dict()
        parts = self.split(tf)
        for part in parts:
            if part.is_empty():
                continue

            price_values = list()
            buy_values = list()
            sell_values = list()
            unique_prices = part["price"].unique()
            for price in unique_prices:
                selected = part.filter(price=price)
                buy = selected.filter(direction="B")["amount"].sum()
                sell = selected.filter(direction="S")["amount"].sum()

                price_values.append(price)
                buy_values.append(buy)
                sell_values.append(sell)

            dt = part.item(0, "dt").replace(second=0)
            quant = pl.DataFrame(
                {
                    "price": price_values,
                    "buy": buy_values,
                    "sell": sell_values,
                }
            )
            quants[dt] = quant

        return quants

    # }}}


if __name__ == "__main__":
    ...
