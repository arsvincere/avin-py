#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import polars as pl

from avin.const import ONE_DAY
from avin.core.bar import Bar
from avin.core.event import BarEvent, Event
from avin.core.timeframe import TimeFrame
from avin.data import Data
from avin.utils import (
    UTC,
    DateTime,
    Signal,
    logger,
)

# class Chart:
#     DEFAULT_BARS_COUNT = 5000
#     MAX_BARS_COUNT = None  # used in tester
#
#     def __init__(  # {{{
#         self,
#         instrument: Instrument,
#         timeframe: TimeFrame,
#         bars: list[Bar],
#     ):
#         logger.debug(f"{self.__class__.__name__}.__init__()")
#
#         check = self.__checkArgs(
#             instrument=instrument,
#             timeframe=timeframe,
#             bars=bars,
#         )
#         if not check:
#             return
#
#         self.__instrument = instrument
#         self.__timeframe = timeframe
#
#         for i in bars:
#             i.setChart(self)
#
#         if len(bars) > 0:
#             self.__now = bars.pop(-1)
#         else:
#             self.__now = _VoidBar(DateTime(1, 1, 1, tzinfo=UTC))
#         self.__bars = bars
#         self.__head = len(self.__bars)  # index of HEAD bar
#
#         # signals
#         self.new_historical_bar = Signal(Chart, Bar)
#         self.upd_realtime_bar = Signal(Chart, Bar)
#
#     # }}}
#     def __getitem__(self, index: int):  # {{{
#         """Доступ к барам графика по индексу
#         ----------------------------------------------------------------------
#         [0, 1, 2, 3] (real_time_bar)  - так данные лежат физически
#          4  3  2  1        0          - так через getitem [i]
#         По умолчанию head == len(bars) == 4, тогда:
#         chart[0]   - перехватываем и возвращаем реал тайм бар,
#         chart[1] == bars[4 - 1] == bars[3] указывает на вчерашний бар
#         chart[2] == bars[4 - 2] == bars[2] указывает на позавчера
#         chart[3] == bars[4 - 3] == bars[1] ...
#         chart[4] == bars[4 - 4] == bars[0] самый старый исторический
#         сhart[5] == 4 - 5 < 0 перехватываем и возвращаем None
#         ----------------------------------------------------------------------
#         Если head установить == 0, тогда:
#         chart[0]     перехватываем и возвращаем реал тайм бар,
#         chart[1] == 0 - 1 < 0 перехватываем и возвращаем None
#         """
#         logger.debug(f"{self.__class__.__name__}.__getitem__()")
#
#         if index == 0:
#             return self.__now  # возвращаем реал тайм бар
#
#         index = self.__head - index
#         if index < 0:
#             return None
#         if index >= len(self.__bars):
#             return None
#
#         return self.__bars[index]
#
#     # }}}
#     def __iter__(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.__iter__()")
#         return iter(self.__bars)
#
#     # }}}
#     def __len__(self):  # {{{
#         return len(self.__bars)
#
#     # }}}
#
#     @property  # instrument  # {{{
#     def instrument(self):
#         return self.__instrument
#
#     # }}}
#     @property  # timeframe# {{{
#     def timeframe(self):
#         return self.__timeframe
#
#     # }}}
#     @property  # first# {{{
#     def first(self):
#         """Возвращает самый старый исторический бар в графике"""
#         return self.__bars[0]
#
#     # }}}
#     @property  # last# {{{
#     def last(self):
#         """
#         Возвращает самый новый исторический бар (относительно head!!!)
#         """
#         index = self.__head - 1
#         if 0 < index < len(self.__bars):
#             return self.__bars[index]
#         else:
#             return None
#
#     # }}}
#     @property  # now# {{{
#     def now(self):
#         """Возвращает реал тайм бар, тоже что chart[0]"""
#         return self.__now
#
#     @now.setter
#     def now(self, new_bar: Bar):
#         """Изменяет реал-тайм бар без генерации сигнала chart.updated"""
#         self.__now = new_bar
#
#     # }}}
#
#     def receive(self, e: BarEvent) -> None:  # {{{
#         logger.debug(f"{self.__class__.__name__}.receive()")
#         assert e.type == Event.Type.BAR
#
#         new_bar = e.bar
#         new_bar.setChart(self)
#
#         # only update now bar
#         if self.__now.dt == new_bar.dt:
#             self.__now = new_bar
#             self.upd_realtime_bar.emit(self, new_bar)
#             return
#
#         # new historical bar and update now bar
#         if self.__now.dt < new_bar.dt:
#             self.__bars.append(self.__now)
#             self.__now = new_bar
#
#             # trunc bars list if needed
#             if (
#                 Chart.MAX_BARS_COUNT is not None
#                 and len(self.__bars) > Chart.MAX_BARS_COUNT
#             ):
#                 mid = Chart.MAX_BARS_COUNT // 2
#                 self.__bars = self.__bars[mid:]
#
#             # update head position
#             self.__head = len(self.__bars)
#
#             # emit signals
#             self.new_historical_bar.emit(self, self.__bars[-1])
#             self.upd_realtime_bar.emit(self, self.__now)
#             return
#
#         logger.critical(f"{e}")
#         assert False, "WTF???"
#
#     # }}}
#
#     def getIndex(self, bar: Bar) -> int:  # {{{
#         logger.debug(f"{self.__class__.__name__}.getIndex()")
#
#         bars = self.getBars()  # not ignored self.__head
#         index = binary_search(bars, bar.dt, lambda x: x.dt)
#
#         assert index is not None
#         return index
#
#     # }}}
#     def getBars(  # {{{
#         self, begin: Optional[Bar] = None, end: Optional[Bar] = None
#     ) -> list[Bar]:
#         logger.debug(f"{self.__class__.__name__}.getBars()")
#
#         begin_index = 0 if begin is None else self.getIndex(begin)
#         end_index = self.__head if end is None else self.getIndex(end) + 1
#
#         return self.__bars[begin_index:end_index]
#
#     # }}}
#     def getTodayBars(self) -> list[Bar]:  # {{{
#         logger.debug(f"{self.__class__.__name__}.getTodayBars()")
#
#         if self.__now is None:
#             return list()
#
#         today = self.__now.dt.date()
#         i = self.__head
#         while i - 1 > 0 and self.__bars[i - 1].dt.date() == today:
#             i -= 1
#
#         return self.__bars[i : self.__head]
#
#     # }}}
#     def getBarsOfYear(self, dt: DateTime) -> list[Bar]:  # {{{
#         """Return list[Bar] with year the same, as year of argument 'dt'"""
#
#         logger.debug(f"{self.__class__.__name__}.getBarsOfYear()")
#
#         year = dt.year
#         i = bisect.bisect_left(self.__bars, year, key=lambda x: x.dt.year)
#         j = bisect.bisect_right(self.__bars, year, key=lambda x: x.dt.year)
#
#         return self.__bars[i:j]
#
#     # }}}
#     def getBarsOfMonth(self, dt: DateTime) -> list[Bar]:  # {{{
#         """Return list[Bar] with month the same, as month of argument 'dt'"""
#
#         logger.debug(f"{self.__class__.__name__}.getBarsOfWeek()")
#
#         if self.__timeframe >= TimeFrame("M"):
#             return []
#
#         year_bars = self.getBarsOfYear(dt)
#         month = dt.month
#         i = bisect.bisect_left(year_bars, month, key=lambda x: x.dt.month)
#         j = bisect.bisect_right(year_bars, month, key=lambda x: x.dt.month)
#
#         return year_bars[i:j]
#
#     # }}}
#     def getBarsOfWeek(self, dt: DateTime) -> list[Bar]:  # {{{
#         """Return list[Bar] with week the same, as week of argument 'dt'"""
#
#         logger.debug(f"{self.__class__.__name__}.getBarsOfWeek()")
#
#         if self.__timeframe >= TimeFrame("W"):
#             return []
#
#         year_bars = self.getBarsOfYear(dt)
#         week = dt.isocalendar()[1]
#         i = bisect.bisect_left(
#             year_bars, week, key=lambda x: x.dt.isocalendar()[1]
#         )
#         j = bisect.bisect_right(
#             year_bars, week, key=lambda x: x.dt.isocalendar()[1]
#         )
#
#         return year_bars[i:j]
#
#     # }}}
#     def getBarsOfDay(self, dt: DateTime) -> list[Bar]:  # {{{
#         """Return list[Bar] with day the same, as day of argument 'dt'"""
#
#         logger.debug(f"{self.__class__.__name__}.getBarsOfDate()")
#
#         if self.__timeframe >= TimeFrame("D"):
#             return []
#
#         day = dt.date()
#         i = bisect.bisect_left(self.__bars, day, key=lambda x: x.dt.date())
#         j = bisect.bisect_right(self.__bars, day, key=lambda x: x.dt.date())
#
#         return self.__bars[i:j]
#
#     # }}}
#     def getBarsOfHour(self, dt: DateTime) -> list[Bar]:  # {{{
#         """Return list[Bar] with hour the same, as hour of argument 'dt'"""
#
#         logger.debug(f"{self.__class__.__name__}.getBarsOfHour()")
#
#         if self.__timeframe >= TimeFrame("1H"):
#             return []
#
#         bars_of_day = self.getBarsOfDay(dt)
#         hour = dt.hour
#         i = bisect.bisect_left(bars_of_day, hour, key=lambda x: x.dt.hour)
#         j = bisect.bisect_right(bars_of_day, hour, key=lambda x: x.dt.hour)
#
#         return bars_of_day[i:j]
#
#     # }}}
#
#     def highestHigh(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.highestHigh()")
#
#         # using method getBars() instead of self.__bars
#         # because its return only [0, head] bars
#         bars = self.getBars()
#
#         bar = max(bars, key=lambda x: x.high)
#         return bar.high
#
#     # }}}
#     def lowestLow(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.lowestLow()")
#
#         # using method getBars() instead of self.__bars
#         # because its return only [0, head] bars
#         bars = self.getBars()
#         bar = min(bars, key=lambda x: x.low)
#         return bar.low
#
#     # }}}
#
#     def lastPrice(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.todayOpen()")
#
#         return self.__now.close
#
#     # }}}
#     def todayOpen(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.todayOpen()")
#
#         bars = self.getTodayBars()
#         if not bars:
#             return None
#
#         return bars[0].open
#
#     # }}}
#     def todayHigh(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.todayHigh()")
#
#         bars = self.getTodayBars()
#         if not bars:
#             return None
#
#         bar = max(bars, key=lambda x: x.high)
#         return bar.high
#
#     # }}}
#     def todayLow(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.todayLow()")
#
#         bars = self.getTodayBars()
#         if not bars:
#             return None
#
#         bar = min(bars, key=lambda x: x.low)
#         return bar.low
#
#     # }}}
#     def yesterdayOpen(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.yesterdayOpen()")
#
#         yesterday = self.__now.dt - ONE_DAY
#         bars = self.getBarsOfDay(yesterday)
#         if not bars:
#             return None
#
#         return bars[0].open
#
#     # }}}
#     def yesterdayHigh(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.yesterdayHigh()")
#
#         yesterday = self.__now.dt - ONE_DAY
#         bars = self.getBarsOfDay(yesterday)
#         if not bars:
#             return None
#
#         bar = max(bars, key=lambda x: x.high)
#         return bar.high
#
#     # }}}
#     def yesterdayLow(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.yesterdayLow()")
#
#         yesterday = self.__now.dt - ONE_DAY
#         bars = self.getBarsOfDay(yesterday)
#         if not bars:
#             return None
#
#         bar = min(bars, key=lambda x: x.low)
#         return bar.low
#
#     # }}}
#     def yesterdayClose(self):  # {{{
#         logger.debug(f"{self.__class__.__name__}.yesterdayClose()")
#
#         yesterday = self.__now.dt - ONE_DAY
#         bars = self.getBarsOfDay(yesterday)
#         if not bars:
#             return None
#
#         return bars[-1].close
#
#     # }}}
#
#     # def setHeadIndex(self, index) -> bool:  # {{{
#     #     logger.debug(f"{self.__class__.__name__}.setHeadIndex()")
#     #     assert isinstance(index, int)
#     #
#     #     if index < 0:
#     #         return False
#     #     if index > len(self.__bars):
#     #         return False
#     #
#     #     self.__head = index
#     #     self.__now = self.__bars[self.__head]
#     #     return True
#     #
#     # # }}}
#     # def getHeadIndex(self) -> int:  # {{{
#     #     logger.debug(f"{self.__class__.__name__}.getHeadIndex()")
#     #     return self.__head
#     #
#     # # }}}
#     # def setHeadDatetime(self, dt: DateTime) -> bool:  # {{{
#     #     logger.debug(f"{self.__class__.__name__}.setHeadDatetime()")
#     #     assert isinstance(dt, DateTime)
#     #
#     #     index = find_left(self.__bars, dt, lambda x: x.dt)
#     #     if index is not None:
#     #         self.__head = index
#     #         self.__now = self.__bars[index]
#     #         return True
#     #     else:
#     #         assert False
#     #
#     # # }}}
#     # def resetHead(self) -> None:  # {{{
#     #     logger.debug(f"{self.__class__.__name__}.resetHead()")
#     #     self.__head = len(self.__bars)
#     #     self.__now = None
#     #
#     # # }}}
#     # def nextHead(self) -> Bar | None:  # {{{
#     #     logger.debug(f"{self.__class__.__name__}.nextHead()")
#     #     if self.__head < len(self.__bars) - 1:
#     #         self.__head += 1
#     #         self.__now = self.__bars[self.__head]
#     #         return self.__now
#     #     else:
#     #         return None
#     #
#     # # }}}
#     # def prevHead(self) -> Bar | None:  # {{{
#     #     logger.debug(f"{self.__class__.__name__}.prevHead()")
#     #
#     #     if self.__head > 0:
#     #         self.__head -= 1
#     #         self.__now = self.__bars[self.__head]
#     #         return self.__now
#     #     else:
#     #         return None
#     #
#     # # }}}
#
#     @classmethod  # load  # {{{
#     async def load(
#         cls,
#         instrument: Instrument,
#         timeframe: TimeFrame,
#         begin: DateTime,
#         end: DateTime,
#     ) -> Chart:
#         logger.debug(f"{cls.__name__}.load()")
#
#         # check args, may be raise TypeError, ValueError
#         cls.__checkArgs(
#             instrument=instrument,
#             timeframe=timeframe,
#             begin=begin,
#             end=end,
#         )
#
#         # request bars
#         records = await Data.request(
#             instrument=instrument,
#             data_type=timeframe.toDataType(),
#             begin=begin,
#             end=end,
#         )
#
#         # create bars
#         bars = list()
#         for record in records:
#             bar = Bar.fromRecord(record)
#             bars.append(bar)
#
#         # create and return chart
#         chart = Chart(instrument, timeframe, bars)
#         return chart
#
#     # }}}
#
#     @classmethod  # __checkArgs  # {{{
#     def __checkArgs(
#         cls,
#         instrument=None,
#         timeframe=None,
#         bars=None,
#         begin=None,
#         end=None,
#     ):
#         logger.debug(f"{cls.__name__}.__checkArgs()")
#
#         if instrument is not None:
#             cls.__checkID(instrument)
#
#         if timeframe is not None:
#             cls.__checkTimeFrame(timeframe)
#
#         if bars is not None:
#             cls.__checkBars(bars)
#
#         if begin is not None:
#             cls.__checkBegin(begin)
#
#         if end is not None:
#             cls.__checkEnd(end)
#
#         return True
#
#     # }}}
#     @classmethod  # __checkAsset  # {{{
#     def __checkID(cls, instrument):
#         logger.debug(f"{cls.__name__}.__checkID()")
#
#         if not isinstance(instrument, Instrument):
#             logger.critical(f"Invalid instrument={instrument}")
#             raise TypeError(instrument)
#
#     # }}}
#     @classmethod  # __checkTimeFrame  # {{{
#     def __checkTimeFrame(cls, timeframe):
#         logger.debug(f"{cls.__name__}.__checkTimeFrame()")
#
#         if not isinstance(timeframe, TimeFrame):
#             logger.critical(f"Invalid timeframe={timeframe}")
#             raise TypeError(timeframe)
#
#     # }}}
#     @classmethod  # __checkBars  # {{{
#     def __checkBars(cls, bars):
#         logger.debug(f"{cls.__name__}.__checkBars()")
#
#         if not isinstance(bars, list):
#             logger.critical(f"Invalid bars={bars}")
#             raise TypeError(bars)
#
#         # if len(bars) == 0:
#         #     logger.critical("Impossible create chart from 0 bars")
#         #     raise ValueError(bars)
#         #
#         # bar = bars[0]
#         # if not isinstance(bar, Bar):
#         #     logger.critical(f"Invalid bar={bar}")
#         #     raise TypeError(bar)
#
#     # }}}
#     @classmethod  # __checkBegin  # {{{
#     def __checkBegin(cls, begin: DateTime):
#         logger.debug(f"{cls.__name__}.__checkBegin()")
#
#         if not isinstance(begin, DateTime):
#             logger.critical(f"Invalid begin={begin}")
#             raise TypeError(begin)
#
#         if begin.tzinfo != UTC:
#             logger.critical("Invalid begin timezone='{begin.tzinfo}")
#             raise ValueError(begin)
#
#     # }}}
#     @classmethod  # __checkEnd  # {{{
#     def __checkEnd(cls, end: DateTime):
#         logger.debug(f"{cls.__name__}.__checkEnd()")
#
#         if not isinstance(end, DateTime):
#             logger.critical(f"Invalid end={end}")
#             raise TypeError(end)
#
#         if end.tzinfo != UTC:
#             logger.critical("Invalid end timezone='{end.tzinfo}")
#             raise ValueError(end)
#
#     # }}}


class Chart:
    DEFAULT_BARS_COUNT = 5000
    MAX_BARS_COUNT = None  # used in tester

    def __init__(  # {{{
        self,
        asset: Asset,
        timeframe: TimeFrame,
        data: pl.DataFrame,
    ):
        assert isinstance(asset.figi, str)
        assert isinstance(timeframe, TimeFrame)
        assert isinstance(data, pl.DataFrame)

        self.__asset = asset
        self.__timeframe = timeframe
        self.__data = data
        self.__now = None

        # signals
        self.new_bar = Signal(Chart, Bar)
        self.upd_bar = Signal(Chart, Bar)

    # }}}
    def __getitem__(self, index: int):  # {{{
        """Доступ к барам графика по индексу
        ----------------------------------------------------------------------
        [0, 1, 2, 3] (now_bar)  - так данные лежат физически
         4  3  2  1      0      - так через getitem [i]

        chart[0]                - возвращаем реал тайм бар self.__now
        chart[1] == data[-1]    - указывает на вчерашний бар
        chart[2] == data[-2]    - указывает на позавчера
        chart[3] == data[-3]    - ...
        chart[4] == data[-4]    - самый старый исторический
        сhart[5] (>len(data)    - возвращаем None
        ----------------------------------------------------------------------
        Если head установить == 0, тогда:
        chart[0]     перехватываем и возвращаем реал тайм бар,
        chart[1] == 0 - 1 < 0 перехватываем и возвращаем None
        """

        if index == 0:
            return self.__now  # возвращаем реал тайм бар

        if index <= len(self.__data):
            dct = self.__data[-index]
            bar = Bar(dct, self)
            return bar

        if index > len(self.__data):
            return None

        if index < 0:
            return None

    # }}}
    def __iter__(self) -> Iterable:  # {{{
        for dct in self.__data.iter_rows(named=True):
            bar = Bar(data=dct, chart=self)
            yield bar

    # }}}
    def __len__(self) -> int:  # {{{
        """Return count of historical bars"""

        return len(self.__data)

    # }}}
    def __str__(self) -> str:  # {{{
        s = f"Chart={self.__asset}-{self.__timeframe}"
        return s

    # }}}

    @property  # asset  # {{{
    def asset(self) -> Asset:
        return self.__asset

    # }}}
    @property  # timeframe  # {{{
    def timeframe(self) -> TimeFrame:
        return self.__timeframe

    # }}}
    @property  # first  # {{{
    def first(self) -> Bar | None:
        """Возвращает самый старый исторический бар в графике"""

        if len(self.__data) != 0:
            dct = self.__data[0].to_dicts()[0]
            bar = Bar(dct, self)
            return bar

        return None

    # }}}
    @property  # last  # {{{
    def last(self) -> Bar | None:
        """Возвращает самый новый исторический бар в графике"""

        if len(self.__data) != 0:
            dct = self.__data[-1].to_dicts()[0]
            bar = Bar(dct, self)
            return bar

        return None

    # }}}
    @property  # now  # {{{
    def now(self) -> Bar | None:
        """Возвращает реал тайм бар, тоже что chart[0]"""
        return self.__now

    @now.setter
    def now(self, upd_bar: Bar):
        """Изменяет реал-тайм бар без генерации сигнала chart.upd_bar"""
        self.__now = upd_bar

    # }}}
    @property  # last_price  # {{{
    def last_price(self) -> float | None:
        """Возвращает последюю цену"""
        if self.__now is not None:
            return self.__now.close

        return None

    @now.setter
    def now(self, upd_bar: Bar):
        """Изменяет реал-тайм бар без генерации сигнала chart.upd_bar"""
        self.__now = upd_bar

    # }}}
    @property  # data_frame  # {{{
    def data_frame(self) -> pl.DataFrame:
        return self.__data

    # }}}
    @property  # data_frame_with_now  # {{{
    def data_frame(self) -> pl.DataFrame:
        return self.__data

    # }}}

    def highestHigh(self):  # {{{
        return self.__data["high"].max()

    # }}}
    def lowestLow(self):  # {{{
        return self.__data["low"].min()

    # }}}

    def select(self, b: DateTime, e: DateTime) -> pl.DataFrame:  # {{{
        selected = self.__data.filter(
            (b <= pl.col("dt")) & (pl.col("dt") < e)
        )

        return selected

    # }}}
    def selectTodayBars(self) -> pl.DataFrame:  # {{{
        """Return df bars with dt.date() == chart.now.dt.date()"""

        if self.__now is None:
            return pl.DataFrame()

        b = self.__now.dt.replace(hour=0, minute=0, second=0, microsecond=0)
        e = b + ONE_DAY

        return self.select(b, e)

    # }}}
    def selectBarsOfYear(self, dt: DateTime) -> pl.DataFrame:  # {{{
        """Return df with year the same, as year of argument 'dt'"""

        b = DateTime(dt.year, 1, 1, tzinfo=UTC)
        e = DateTime(dt.year + 1, 1, 1, tzinfo=UTC)

        return self.select(b, e)

    # }}}
    def selectBarsOfMonth(self, dt: DateTime) -> pl.DataFrame:  # {{{
        """Return df with month the same, as month of argument 'dt'"""

        if self.__timeframe >= TimeFrame("M"):
            return pl.DataFrame()

        b = DateTime(dt.year, dt.month, 1, tzinfo=UTC)
        e = next_month(b)

        return self.select(b, e)

    # }}}
    def selectBarsOfWeek(self, dt: DateTime) -> pl.DataFrame:  # {{{
        """Return df with week the same, as week of argument 'dt'"""

        if self.__timeframe >= TimeFrame("W"):
            return pl.DataFrame()

        # TODO: тут можно сделать функции типа
        # get_week_begin(dt)
        # get_week_end(dt)
        # в утилитах, и от этого плясать
        assert False, "TODO_ME"

    # }}}
    def selectBarsOfDay(self, dt: DateTime) -> list[Bar]:  # {{{
        """Return df with day the same, as day of argument 'dt'"""

        if self.__timeframe >= TimeFrame("D"):
            return pl.DataFrame()

        b = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        e = b + ONE_DAY

        return self.select(b, e)

    # }}}
    def selectBarsOfHour(self, dt: DateTime) -> list[Bar]:  # {{{
        """Return df with hour the same, as hour of argument 'dt'"""

        if self.__timeframe >= TimeFrame("1H"):
            return pl.DataFrame()

        b = dt.replace(minute=0, second=0, microsecond=0)
        e = b + ONE_HOUR

        return self.select(b, e)

    # }}}

    def todayOpen(self):  # {{{
        bars = self.selectTodayBars()
        if bars.is_empty():
            return None

        return bars.item(0, "open")

    # }}}
    def todayHigh(self):  # {{{
        bars = self.selectTodayBars()
        if bars.is_empty():
            return None

        return bars["high"].max()

    # }}}
    def todayLow(self):  # {{{
        bars = self.selectTodayBars()
        if bars.is_empty():
            return None

        return bars["low"].min()

    # }}}
    def yesterdayOpen(self):  # {{{
        yesterday = self.__now.dt - ONE_DAY

        bars = self.selectBarsOfDay(yesterday)
        if bars.is_empty():
            return None

        return bars.item(0, "open")

    # }}}
    def yesterdayHigh(self):  # {{{
        yesterday = self.__now.dt - ONE_DAY

        bars = self.selectBarsOfDay(yesterday)
        if bars.is_empty():
            return None

        return bars["high"].max()

    # }}}
    def yesterdayLow(self):  # {{{
        yesterday = self.__now.dt - ONE_DAY

        bars = self.selectBarsOfDay(yesterday)
        if bars.is_empty():
            return None

        return bars["low"].min()

    # }}}
    def yesterdayClose(self):  # {{{
        yesterday = self.__now.dt - ONE_DAY

        bars = self.selectBarsOfDay(yesterday)
        if bars.is_empty():
            return None

        return bars.item(-1, "close")

    # }}}

    def receive(self, e: BarEvent) -> None:  # {{{
        assert e.type == Event.Type.BAR
        assert e.figi == self.__asset.figi

        new_bar = e.bar

        # 1. first real-time bar, in chart only historical bars
        if self.__now is None:
            self.__now = new_bar

            self.upd_bar.emit(self, new_bar)
            return

        # 2. only update now bar
        if self.__now.dt == new_bar.dt:
            self.__now = new_bar

            self.upd_bar.emit(self, new_bar)
            return

        # 3. new historical bar and update now bar
        if self.__now.dt < new_bar.dt:
            df = pl.DataFrame(self.__now.data)
            self.__data.extend(df)
            self.__now = new_bar

            # emit signals
            self.new_bar.emit(self, self.last)
            self.upd_bar.emit(self, self.now)
            return

        logger.critical(f"{e}")
        assert False, "WTF???"

    # }}}

    @classmethod  # load  # {{{
    async def load(
        cls,
        asset: Asset,
        timeframe: TimeFrame,
        begin: DateTime,
        end: DateTime,
    ) -> Chart:
        logger.debug(f"{cls.__name__}.load()")
        assert isinstance(asset.figi, str)
        assert isinstance(timeframe, TimeFrame)
        assert isinstance(begin, DateTime)
        assert isinstance(end, DateTime)
        assert begin.tzinfo == UTC
        assert end.tzinfo == UTC
        assert begin < end

        # request bars
        records = await Data.request(
            instrument=asset,
            data_type=timeframe.toDataType(),
            begin=begin,
            end=end,
        )
        df = pl.DataFrame([dict(r) for r in records])

        # create and return chart
        chart = Chart(asset, timeframe, df)
        return chart

    # }}}


if __name__ == "__main__":
    ...
