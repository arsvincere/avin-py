# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import enum


class WeekDays(enum.Enum):
    Mon = 0
    Tue = 1
    Wed = 2
    Thu = 3
    Fri = 4
    Sat = 5
    Sun = 6

    @staticmethod
    def isWorkday(day_number: int):
        return day_number < 5

    @staticmethod
    def isHoliday(day_number: int):
        return day_number in (5, 6)
