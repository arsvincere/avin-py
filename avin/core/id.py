#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import time as timer


class Id:
    # {{{-- doc
    """Id - Identifier for trades, orders, operations.

    Note
    ----
    Don't use class constructor. Create new class object by call member
    newId()
    """  # }}}

    def __init__(self, id_value: str):  # {{{
        self.__val = id_value

    # }}}
    def __str__(self):  # {{{
        return f"{self.__val}"

    # }}}
    def __eq__(self, other: Id):  # {{{
        return self.__val == other.__val

    # }}}
    @classmethod  # newId# {{{
    def newId(cls) -> Id:
        val = str(timer.time())
        ID = Id(val)
        return ID

    # }}}

    @classmethod  # fromStr# {{{
    def fromStr(cls, id_value: str) -> Id:
        ID = Id(id_value)
        return ID

    # }}}


if __name__ == "__main__":
    ...
