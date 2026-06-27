# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────


"""Closed interval [from, till].

# ru
Закрытый диапазон [from, till] - используется для представления
ценового диапазона, и определяет несколько утилитарных методов:
проверка на вхождение, выразить диапазон в процентах и тп.

Диапазон может быть:
1. Возрастающий - конечное значение больше начального.
2. Убывающий - конечное значение меньше начального.
"""


class PriceRange:
    def __init__(self, start: float, finish: float):
        if start == 0.0:
            raise ValueError("start must not be zero")

        if finish == 0.0:
            raise ValueError("finish must not be zero")

        self.__start = start
        self.__finish = finish

    def __str__(self) -> str:
        return f"[{self.start}, {self.finish}]"

    def __repr__(self) -> str:
        return f"PriceRange({self.start}, {self.finish})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PriceRange):
            return NotImplemented

        return self.start == other.start and self.finish == other.finish

    def __hash__(self) -> int:
        return hash((self.start, self.finish))

    @property
    def start(self) -> float:
        return self.__start

    @property
    def finish(self) -> float:
        return self.__finish

    @property
    def low(self) -> float:
        """Return low of range.

        # ru
        Возвращает минимум диапазона.
        """
        if self.start < self.finish:
            return self.start
        else:
            return self.finish

    @property
    def high(self) -> float:
        """Return high of range.

        # ru
        Возвращает максимум диапазона.
        """

        if self.start > self.finish:
            return self.start
        else:
            return self.finish

    @property
    def mid(self) -> float:
        """
        Returns the middle of the range.

        # ru
        Возвращает середину диапазона.
        """

        mn = self.low
        mx = self.high
        half = (mx - mn) / 2.0

        return mn + half

    @property
    def abs(self) -> float:
        """Abs of range.

        # ru
        Модуль диапазона.
        """

        return self.high - self.low

    @property
    def abs_n(self) -> float:
        """Normalized abs of range.

        # ru
        Нормализованный модуль диапазона.
        """
        mn = self.low
        mx = self.high

        return (mx - mn) / mx

    @property
    def abs_p(self) -> float:
        """Abs of range in percent.

        # ru
        Модуль диапазона в процентах, округляется до 2-х знаков.
        """

        mn = self.low
        mx = self.high

        value = (mx - mn) / mx * 100.0

        return round(value, 2)

    @property
    def delta(self) -> float:
        """Delta of range (signed).

        # ru
        Дельта диапазона (знаковая).
        """

        return self.finish - self.start

    @property
    def delta_n(self) -> float:
        """Normalized delta of range (signed).

        # ru
        Нормализованная дельта диапазона (знаковая) - показывает коэффициент
        изменения конечной цены относительно начальной.
        """

        return (self.finish - self.start) / self.start

    @property
    def delta_p(self) -> float:
        """Delta of range in percent.

        # ru
        Дельта диапазона (знаковая) в процентах - показывает процент
        изменения конечной цены относительно начальной. Округляется до
        2-х знаков.
        """

        value = (self.finish - self.start) / self.start * 100.0

        return round(value, 2)

    def contains(self, value: float) -> bool:
        """Check for value in range.

        # ru
        Проверка на вхождения в диапазон.
        """
        return self.low <= value and value <= self.high

    def is_increase(self) -> bool:
        """Is range increase.

        # ru
        Если диапазон возврастающий - true.
        """
        return self.delta > 0.0

    def is_decrease(self) -> bool:
        """Is range decrease.

        # ru
        Если диапазон убывающий - true.
        """

        return self.delta < 0.0
