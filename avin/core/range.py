# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations


class Range:
    """Closed interval [from, till].

    # ru
    Закрытый диапазон [from, till] - используется для представления
    ценового диапазона, и определяет несколько утилитарных методов:
    проверка на вхождение, выразить диапазон в процентах и тп.

    Диапазон может быть:
    1. Возрастающий - конечное значение больше начального.
    2. Убывающий - конечное значение меньше начального.
    """

    def __init__(self, start: float, finish: float):
        self.__start = start
        self.__finish = finish

    def __str__(self):
        return f"Range[{self.__start}, {self.__finish}]"

    def __getitem__(self, slice_) -> Range:
        """Return part of range.

        # ru
        Возвращает часть диапазона.

        [0:10] - от 0 до 10% исходного диапазона
        [40:60] - от 40% до 60% исходного диапазона

        Example:
            bar.body()[0:5] - нижние 5% тела бара
            bar.upper()[90:100] - верхние 10% верхней тени бара
        """

        assert isinstance(slice_, slice)
        assert slice_.step is None
        assert slice_.start >= 0
        assert slice_.stop <= 100
        assert slice_.start <= slice_.stop

        if slice_.start == 0:
            start = self.min()
        else:
            tmp = (self.max() - self.min()) * slice_.start / 100.0
            start = self.min() + tmp

        if slice_.stop == 0:
            stop = self.max()
        else:
            tmp = (self.max() - self.min()) * slice_.stop / 100.0
            stop = self.min() + tmp

        return Range(start, stop)

    def __contains__(self, price: float) -> bool:
        """Check for value in range.

        # ru
        Проверка на вхождения в диапазон.
        """

        return self.min() <= price <= self.max()

    def __eq__(self, other) -> bool:
        return self.start == other.start and self.finish == other.finish

    @property
    def start(self):
        """Return start of range.

        # ru
        Возвращает начало диапазона.
        """
        return self.__start

    @property
    def finish(self):
        """Return finish of range.

        # ru
        Возвращает конец диапазона.
        """
        return self.__finish

    def min(self):
        """Return min of range.

        # ru
        Возвращает минимум диапазона.
        """

        if self.__start < self.__finish:
            return self.__start
        else:
            return self.__finish

    def max(self):
        """Return max of range.

        # ru
        Возвращает максимум диапазона.
        """
        if self.__start > self.__finish:
            return self.__start
        else:
            return self.__finish

    def mid(self):
        """Return middle of range.

        # ru
        Возвращает середину диапазона.
        """
        return (self.__start + self.__finish) / 2.0

    def abs(self) -> float:
        """Abs of range.

        # ru
        Модуль диапазона.
        """

        return self.max() - self.min()

    def abs_n(self) -> float:
        """Normalized abs of range.

        # ru
        Нормализованный модуль диапазона.
        """

        value = self.abs() / self.start

        return round(value, 2)

    def abs_p(self) -> float:
        """
        Abs of range in percent.

        # ru
        Модуль диапазона в процентах.
        """

        value = self.abs_n() * 100.0

        return round(value, 2)

    def delta(self) -> float:
        """Delta of range (signed).

        # ru
        Дельта диапазона (знаковая).
        """

        return self.__finish - self.__start

    def delta_n(self) -> float:
        """Normalized delta of range (signed).

        # ru
        Нормализованная дельта диапазона (знаковая) - показывает коэффициент
        изменения конечной цены относительно начальной.
        """

        value = self.delta() / self.__start

        return round(value, 2)

    def delta_p(self) -> float:
        """Delta of range in percent

        # ru
        Дельта диапазона (знаковая) в процентах - показывает процент
        изменения конечной цены относительно начальной.
        """
        value = self.delta_n() * 100.0

        return round(value, 2)


if __name__ == "__main__":
    ...
