#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum


class Term(enum.Enum):
    T1 = 0
    T2 = 1
    T3 = 2
    T4 = 3
    T5 = 4

    def __str__(self):  # {{{
        return self.name

    # }}}
    def __lt__(self, other):  # operator <  # {{{
        assert isinstance(other, Term)
        return self.value < other.value

    # }}}
    def __gt__(self, other):  # operator >  # {{{
        assert isinstance(other, Term)
        return self.value > other.value

    # }}}

    @classmethod  # fromStr  # {{{
    def fromStr(cls, string: str):
        types = {
            "T1": Term.T1,
            "T2": Term.T2,
            "T3": Term.T3,
            "T4": Term.T4,
            "T5": Term.T5,
        }
        return types[string]

    # }}}


if __name__ == "__main__":
    ...
