#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

from datetime import datetime
from typing import Optional

from avin.config import Usr
from avin.core.direction import Direction
from avin.core.id import Id
from avin.data import Instrument
from avin.keeper import Keeper
from avin.utils import logger


class Operation:
    def __init__(  # {{{
        self,
        account_name: str,
        dt: datetime,
        direction: Direction,
        instrument: Instrument,
        lots: int,
        quantity: int,
        price: float,
        amount: float,
        commission: Optional[float],
        operation_id: Optional[Id] = None,
        order_id: Optional[Id] = None,
        trade_id: Optional[Id] = None,
        meta: Optional[str] = None,
    ):
        logger.debug("Operation.__init__()")

        self.account_name = account_name
        self.dt = dt
        self.direction = direction
        self.instrument = instrument
        self.price = price
        self.lots = lots
        self.quantity = quantity
        self.amount = amount
        self.commission = commission
        self.operation_id = operation_id
        self.order_id = order_id
        self.trade_id = trade_id
        self.meta = meta

    # }}}
    def __str__(self):  # {{{
        usr_dt = self.dt + Usr.TIME_DIF
        str_dt = usr_dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"{str_dt} {self.direction.name} {self.instrument.ticker} "
            f"{self.quantity} * {self.price} = {self.amount} "
            f"+ {self.commission}"
        )
        return string

    # }}}
    def pretty(self) -> str:  # {{{
        logger.debug(f"{self.__class__.__name__}.pretty()")

        text = f"""Operation:
    id:             {self.operation_id}
    account:        {self.account_name}
    dt:             {Usr.localTime(self.dt)}
    direction:      {self.direction.name}
    instrument:     {self.instrument}
    lots:           {self.lots}
    quantity:       {self.quantity}
    price:          {self.price}
    amount:         {self.amount}
    commission:     {self.commission}
    order_id:       {self.order_id}
    trade_it:       {self.trade_id}
    meta:           {self.meta}
"""
        return text

    # }}}

    async def setParentTrade(self, trade):  # {{{
        logger.debug(f"Operation.setParentTrade({trade})")
        self.trade_id = trade.trade_id
        await Operation.update(self)

    # }}}
    @classmethod  # fromRecord  # {{{
    async def fromRecord(cls, record: asyncpg.Record) -> Operation:
        logger.debug(f"Operation.fromRecord({record})")

        instrument = await Instrument.fromFigi(record["figi"])

        op = Operation(
            account_name=record["account"],
            dt=record["dt"],
            direction=Direction.fromStr(record["direction"]),
            instrument=instrument,
            lots=record["lots"],
            quantity=record["quantity"],
            price=record["price"],
            amount=record["amount"],
            commission=record["commission"],
            operation_id=Id.fromStr(record["operation_id"]),
            order_id=Id.fromStr(record["order_id"]),
            trade_id=Id.fromStr(record["trade_id"]),
            meta=record["meta"],
        )
        return op

    # }}}
    @classmethod  # save  # {{{
    async def save(cls, operation: Operation) -> None:
        logger.debug(f"Operation.save({operation})")
        await Keeper.add(operation)

    # }}}
    @classmethod  # load  # {{{
    async def load(cls, operation_id: Id) -> Operation:
        logger.debug(f"Operation.load({operation_id})")
        op = await Keeper.get(cls, operation_id=operation_id)
        return op

    # }}}
    @classmethod  # delete  # {{{
    async def delete(cls, operation: Operation) -> None:
        logger.debug(f"Operation.delete({operation})")
        await Keeper.delete(operation)

    # }}}
    @classmethod  # update  # {{{
    async def update(cls, operation: Operation) -> None:
        logger.debug(f"Operation.update({operation})")
        await Keeper.update(operation)

    # }}}


if __name__ == "__main__":
    ...
