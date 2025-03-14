#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import enum

from avin.core import Range

__all__ = (
    "Size",
    "SimpleSize",
)


class Size(enum.Enum):
    BLACKSWAN_SMALL = Range(-100500, 0)
    GREATEST_SMALL = Range(0, 1)
    ANOMAL_SMALL = Range(1, 3)
    EXTRA_SMALL = Range(3, 5)
    VERY_SMALL = Range(5, 10)
    SMALLEST = Range(10, 20)
    SMALLER = Range(20, 30)
    SMALL = Range(30, 40)
    M = Range(40, 60)
    BIG = Range(60, 70)
    BIGGER = Range(70, 80)
    BIGGEST = Range(80, 90)
    VERY_BIG = Range(90, 95)
    EXTRA_BIG = Range(95, 97)
    ANOMAL_BIG = Range(97, 99)
    GREATEST_BIG = Range(99, 100)
    BLACKSWAN_BIG = Range(100, 100500)

    def __str__(self):  # {{{
        return self.name

    # }}}
    def __lt__(self, other):  # operator <  # {{{
        assert isinstance(other, Size)
        return self.value.max < other.value.max

    # }}}
    def __le__(self, other):  # operator <=  # {{{
        assert isinstance(other, Size)
        return self.value.max <= other.value.max

    # }}}
    def __gt__(self, other):  # operator >  # {{{
        assert isinstance(other, Size)
        return self.value.max > other.value.max

    # }}}
    def __ge__(self, other):  # operator >=  # {{{
        assert isinstance(other, Size)
        return self.value.max >= other.value.max

    # }}}

    def simple(self) -> SimpleSize:  # {{{
        for ssize in SimpleSize:
            if self == ssize:
                return ssize

        assert False, "WTF???"
        return None

    # }}}

    @classmethod  # fromStr  # {{{
    def fromStr(cls, string_size: str):
        sizes = {
            "BLACKSWAN_SMALL": Size.BLACKSWAN_SMALL,
            "GREATEST_SMALL": Size.GREATEST_SMALL,
            "ANOMAL_SMALL": Size.ANOMAL_SMALL,
            "EXTRA_SMALL": Size.EXTRA_SMALL,
            "VERY_SMALL": Size.VERY_SMALL,
            "SMALLEST": Size.SMALLEST,
            "SMALLER": Size.SMALLER,
            "SMALL": Size.SMALL,
            "M": Size.M,
            "BIG": Size.BIG,
            "BIGGER": Size.BIGGER,
            "BIGGEST": Size.BIGGEST,
            "VERY_BIG": Size.VERY_BIG,
            "EXTRA_BIG": Size.EXTRA_BIG,
            "ANOMAL_BIG": Size.ANOMAL_BIG,
            "GREATEST_BIG": Size.GREATEST_BIG,
            "BLACKSWAN_BIG": Size.BLACKSWAN_BIG,
        }
        return sizes[string_size]

    # }}}


class SimpleSize(enum.Enum):
    XXS = Range(-100500, 0)
    XS = Range(0, 10)
    S = Range(10, 30)
    M = Range(30, 70)
    L = Range(70, 90)
    XL = Range(90, 100)
    XXL = Range(100, 100500)

    def __str__(self):  # {{{
        return self.name

    # }}}
    def __eq__(self, other):  # operator ==  # {{{
        if isinstance(other, SimpleSize):
            return self.value == other.value
        elif isinstance(other, str):
            other = SimpleSize.fromStr(other)
            return self.value == other.value

        assert isinstance(other, Size)
        match self:
            case SimpleSize.XXS:
                equal = (Size.BLACKSWAN_SMALL.value,)
            case SimpleSize.XS:
                equal = (
                    Size.GREATEST_SMALL.value,
                    Size.ANOMAL_SMALL.value,
                    Size.EXTRA_SMALL.value,
                    Size.VERY_SMALL.value,
                )
            case SimpleSize.S:
                equal = (
                    Size.SMALLEST.value,
                    Size.SMALLER.value,
                )
            case SimpleSize.M:
                equal = (
                    Size.SMALL.value,
                    Size.M.value,
                    Size.BIG.value,
                )
            case SimpleSize.L:
                equal = (
                    Size.BIGGER.value,
                    Size.BIGGEST.value,
                )
            case SimpleSize.XL:
                equal = (
                    Size.VERY_BIG.value,
                    Size.EXTRA_BIG.value,
                    Size.ANOMAL_BIG.value,
                    Size.GREATEST_BIG.value,
                )
            case SimpleSize.XXL:
                equal = (Size.BLACKSWAN_BIG.value,)

        return other.value in equal

    # }}}
    def __hash__(self):  # {{{
        return hash(self.value)

    # }}}
    def __lt__(self, other):  # operator <  # {{{
        if isinstance(other, str):
            other = SimpleSize.fromStr(other)

        assert isinstance(other, (SimpleSize))
        return self.value < other.value

    # }}}
    def __le__(self, other):  # operator <=  # {{{
        if isinstance(other, str):
            other = SimpleSize.fromStr(other)

        assert isinstance(other, (SimpleSize))
        return self.value <= other.value

    # }}}
    def __gt__(self, other):  # operator >  # {{{
        if isinstance(other, str):
            other = SimpleSize.fromStr(other)

        assert isinstance(other, (SimpleSize))
        return self.value > other.value

    # }}}
    def __ge__(self, other):  # operator >=  # {{{
        if isinstance(other, str):
            other = SimpleSize.fromStr(other)

        assert isinstance(other, (SimpleSize))
        return self.value >= other.value

    # }}}

    @classmethod  # fromStr  # {{{
    def fromStr(cls, string_size: str):
        sizes = {
            "XXS": SimpleSize.XXS,
            "XS": SimpleSize.XS,
            "S": SimpleSize.S,
            "M": SimpleSize.M,
            "L": SimpleSize.L,
            "XL": SimpleSize.XL,
            "XXL": SimpleSize.XXL,
        }
        return sizes[string_size]

    # }}}


if __name__ == "__main__":
    ...
