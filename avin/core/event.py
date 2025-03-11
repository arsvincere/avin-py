#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""doc"""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod

from avin.core.order import Order
from avin.core.tic import Tic
from avin.core.timeframe import TimeFrame
from avin.core.transaction import Transaction


class Event(ABC):  # {{{
    class Type(enum.Enum):  # {{{
        UNDEFINE = 0
        BAR = 1
        TIC = 2
        TRANSACTION = 3

    # }}}

    @abstractmethod
    def __init__(self): ...


# }}}
class BarEvent(Event):  # {{{
    def __init__(self, figi: str, timeframe: TimeFrame, bar: Bar):  # {{{
        self.figi = figi
        self.timeframe = timeframe
        self.bar = bar
        self.type = Event.Type.BAR

    # }}}
    def __str__(self):  # {{{
        s = f"BarEvent={self.figi}, {self.timeframe}, {self.bar}"
        return s

    # }}}


# }}}
class TicEvent(Event):  # {{{
    def __init__(self, figi: str, tic: Tic):  # {{{
        self.figi = figi
        self.tic = tic
        self.type = Event.Type.TIC

    # }}}
    def __str__(self):  # {{{
        s = f"TickEvent={self.figi}, {self.tic}"
        return s

    # }}}


# }}}
class TransactionEvent(Event):  # {{{
    def __init__(  # {{{
        self,
        account_name: str,
        figi: str,
        direction: Order.Direction,
        order_broker_id: str,
        transaction: Transaction,
    ):
        self.account = account_name
        self.figi = figi
        self.direction = direction
        self.order_broker_id = order_broker_id
        self.transaction = transaction
        self.type = Event.Type.TRANSACTION

    # }}}
    def __str__(self):  # {{{
        string = f"TransactionEvent={self.transaction}"
        return string

    # }}}


# }}}


if __name__ == "__main__":
    ...
