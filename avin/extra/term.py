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
    STERM = 1
    MTERM = 2
    LTERM = 3

    def __str__(self):
        return self.name[0:2]


# }}}


if __name__ == "__main__":
    ...
