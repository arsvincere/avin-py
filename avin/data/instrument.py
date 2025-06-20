#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum
import json

from avin.config import Usr
from avin.data.data_source import DataSource
from avin.data.exchange import Exchange
from avin.keeper import Keeper
from avin.utils import Cmd, logger


class Instrument:
    """Base class for all assets.

    Contains information about market instrument, like: ticker, figi, name..
    """

    class Type(enum.Enum):  # {{{
        UNDEFINE = 0
        CASH = 1
        INDEX = 2
        SHARE = 3
        BOND = 4
        FUTURE = 5
        OPTION = 6
        CURRENCY = 7
        ETF = 8

        @classmethod  # fromStr# {{{
        def fromStr(cls, string: str) -> Instrument.Type:
            types = {
                "CASH": Instrument.Type.CASH,
                "INDEX": Instrument.Type.INDEX,
                "SHARE": Instrument.Type.SHARE,
                "BOND": Instrument.Type.BOND,
                "FUTURE": Instrument.Type.FUTURE,
                "OPTION": Instrument.Type.OPTION,
                "CURRENCY": Instrument.Type.CURRENCY,
                "ETF": Instrument.Type.ETF,
            }
            return types[string]

        # }}}
        # TODO: dead code?
        # @classmethod  # fromRecord# {{{
        # def fromRecord(cls, record: asyncpg.Record) -> Instrument.Type:
        #     string_name = record["instrument_type"]
        #     itype = cls.fromStr(string_name)
        #     return itype
        #
        # # }}}

    # }}}

    def __init__(self, info: dict):  # {{{
        assert info["exchange"] is not None
        assert info["type"] is not None
        assert info["ticker"] is not None
        assert info["figi"] is not None
        assert info["name"] is not None
        assert info["lot"] is not None
        assert info["min_price_step"] is not None

        self.__info = info

    # }}}
    def __str__(self):  # {{{
        s = f"{self.exchange.name} {self.type.name} {self.ticker}"
        return s

    # }}}
    def __hash__(self):  # {{{
        return hash(self.figi)

    # }}}
    def __eq__(self, other: Instrument) -> bool:  # {{{
        assert isinstance(other, Instrument)
        return self.figi == other.figi

    # }}}

    @property  # info  # {{{
    def info(self):
        return self.__info

    # }}}
    @property  # exchange  # {{{
    def exchange(self):
        exchange = Exchange.fromStr(self.__info["exchange"])
        return exchange

    # }}}
    @property  # type  # {{{
    def type(self):
        t = Instrument.Type.fromStr(self.__info["type"])
        return t

    # }}}
    @property  # ticker  # {{{
    def ticker(self):
        return self.__info["ticker"]

    # }}}
    @property  # figi  # {{{
    def figi(self):
        return self.__info["figi"]

    # }}}
    @property  # name  # {{{
    def name(self):
        return self.__info["name"]

    # }}}
    @property  # lot  # {{{
    def lot(self):
        return int(self.__info["lot"])

    # }}}
    @property  # min_price_step  # {{{
    def min_price_step(self):
        return float(self.info["min_price_step"])

    # }}}
    @property  # path  # {{{
    def path(self) -> str:
        path = Cmd.path(
            Usr.DATA,
            self.exchange.name,
            self.type.name,
            self.ticker,
        )
        return path

    # }}}

    def pretty(self) -> str:  # {{{
        logger.debug(f"{self.__class__.__name__}.pretty()")

        s = json.dumps(self.__info, indent=4, ensure_ascii=False)
        return s

    # }}}

    @classmethod  # fromStr # {{{
    async def fromStr(cls, string: str) -> Instrument:
        logger.debug(f"{cls.__name__}.fromStr()")

        # string is like "MOEX SHARE SBER"
        exchange, itype, ticker = string.split(" ")

        # convert types
        exchange = Exchange.fromStr(exchange)
        itype = Instrument.Type.fromStr(itype)

        # request and return instrument
        instrument = await cls.fromTicker(exchange, itype, ticker)
        return instrument

    # }}}
    @classmethod  # fromRecord  # {{{
    def fromRecord(cls, record: asyncpg.Record) -> Instrument:
        logger.debug(f"{cls.__name__}.fromRecord()")

        # NOTE: asyncpg.Record работает идентично словарю,
        # а название столбцов в БД совпадает с тем что в этом словаре класс
        # будет искать.
        instrument = cls(record)

        return instrument

    # }}}
    @classmethod  # fromFigi  # {{{
    async def fromFigi(cls, figi: str) -> Instrument:
        logger.debug(f"{cls.__name__}.fromFigi()")

        if not cls.__checkArgs(figi=figi):
            assert False

        instr_list = await Keeper.get(cls, figi=figi)
        assert len(instr_list) == 1
        instrument = instr_list[0]

        return instrument

    # }}}
    @classmethod  # fromTicker  # {{{
    async def fromTicker(
        cls, exchange: Exchange, itype: Instrument.Type, ticker: str
    ) -> Instrument:
        logger.debug(f"{cls.__name__}.fromTicker()")

        if not cls.__checkArgs(exchange=exchange, itype=itype, ticker=ticker):
            assert False

        instr_list = await Keeper.get(
            cls,
            exchange=exchange,
            itype=itype,
            ticker=ticker,
        )

        assert len(instr_list) == 1
        instrument = instr_list[0]
        return instrument

    # }}}
    @classmethod  # fromUid  # {{{
    async def fromUid(cls, uid: str) -> Instrument:
        logger.debug(f"{cls.__name__}.fromUid()")

        if not cls.__checkArgs(uid=uid):
            return None

        info_list = await Keeper.info(DataSource.TINKOFF, itype=None, uid=uid)
        assert len(info_list) == 1
        info = info_list[0]

        instrument = cls(info)
        return instrument

    # }}}
    @classmethod  # __checkArgs  # {{{
    def __checkArgs(
        cls,
        itype=None,
        exchange=None,
        ticker=None,
        figi=None,
        name=None,
        uid=None,
    ):
        logger.debug(f"{cls.__name__}.__checkArgs()")

        if itype:
            assert isinstance(itype, Instrument.Type)
        if exchange:
            assert hasattr(exchange, "name")
        if ticker:
            assert isinstance(ticker, str)
        if figi:
            assert isinstance(figi, str)
        if name:
            assert isinstance(name, str)
        if uid:
            assert isinstance(uid, str)

        return True

    # }}}


if __name__ == "__main__":
    ...
