#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum


class Term(enum.Enum):  # {{{
    T1 = 1
    T2 = 2
    T3 = 3
    T4 = 4
    T5 = 5

    def __str__(self):
        return self.name


# }}}


if __name__ == "__main__":
    ...
