# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from datetime import datetime as DateTime

import polars as pl
from PyQt6 import QtCore

from avin.core.bar import Bar
from avin.core.iid import Iid
from avin.core.market_data import MarketData
from avin.core.ticker import Ticker
from avin.core.timeframe import TimeFrame
from avin.manager import Manager


class Chart(QtCore.QObject):
    """Aggregation of instrument id, timeframe and bars.

    # ru
    График - хранит идентификатора инструмента, таймфрейм и бары.
    """

    upd_bar = QtCore.pyqtSignal(Bar)
    new_bar = QtCore.pyqtSignal(Bar)

    def __init__(self, iid: Iid, tf: TimeFrame, bars: pl.DataFrame):
        QtCore.QObject.__init__(self)

        self.__iid = iid
        self.__tf = tf
        self.__bars = bars
        self.__now: Bar | None = None

    def __getitem__(self, n: int) -> Bar | None:
        """Get bar by number.

        # ru
        Возвращает ссылку на бар по номеру или None, если такой отсутствует.

        Поведение как Pine от TradingView.
        Бар с индексом 0 == текущий реалтайм бар, тоже что chart.now().
        Бар с индексом 1 == последний исторический бар.
        Бар с индексом 2 == предпоследний бар в графике.
        И так далее...
        """

        if n == 0:
            return self.__now

        if n <= len(self.__bars):
            row = self.__bars[-n]
            bar = Bar.from_df(row, self)
            return bar

        return None

    def __iter__(self):
        for dct in self.__bars.iter_rows(named=True):
            bar = Bar(data=dct, chart=self)
            yield bar

    def __len__(self) -> int:
        return len(self.__bars)

    @classmethod
    def empty(cls, iid: Iid, tf: TimeFrame) -> Chart:
        bars = pl.DataFrame(schema=Bar.schema())

        return Chart(iid, tf, bars)

    @classmethod
    def load(
        cls, iid: Iid, tf: TimeFrame, begin: DateTime, end: DateTime
    ) -> Chart:
        """Loading chart with bars from half-open interval [begin, end)
        market data must be available in 'CFG.Dir.data'.

        # ru
        Загружает график с барами в полузакрытом в интервале [begin, end).
        Данные должны быть доступны в папке указанной в конфиге пользователя.
        Рыночные данные можно загрузить воспользовавшись модулем avin_data.
        Так же есть консольная утилита avin-data см. репозитарий:
        https://github.com/arsvincere/avin.
        """

        market_data = MarketData.from_timeframe(tf)
        df_bars = Manager.load(iid, market_data, begin, end)

        chart = Chart(iid, tf, df_bars)

        return chart

    def iid(self) -> Iid:
        """Return chart instrument id.

        # ru
        Возвращает ссылку на идентификатор инструмента.
        """

        return self.__iid

    def ticker(self) -> Ticker:
        """Return ticker.

        # ru
        Возвращает ссылку на строку с тикером.
        """

        return self.__iid.ticker()

    def tf(self) -> TimeFrame:
        """Return chart timeframe.

        # ru
        Возвращает ссылку на таймфрейм.
        """

        return self.__tf

    def bars(self) -> pl.DataFrame:
        """Return bars of chart.

        # ru
        Возвращает cсылку на вектор исторических баров в графике.
        """

        return self.__bars

    def first(self) -> Bar | None:
        """Return fist historical bar of chart.

        # ru
        Возвращает ссылку на первый исторический бар или None,
        если график не содержит баров.
        """

        df = self.__bars.head(1)

        if df.is_empty():
            return None

        bar = Bar.from_df(df, self)

        return bar

    def last(self) -> Bar | None:
        """Return last historical bar of chart

        # ru
        Возвращает ссылку на последний исторический бар или None,
        если график не содержит баров.
        """

        df = self.__bars.tail(1)

        if df.is_empty():
            return None

        bar = Bar.from_df(df, self)

        return bar

    def now(self) -> Bar | None:
        """Return real-time bar of chart

        # ru
        Возвращает ссылку на текущий real-time бар или None,
        если график не содержит баров.
        """

        return self.__now

    def last_price(self) -> float | None:
        """Return last price

        # ru
        Возвращает цену последней сделки реал-тайм бара, если он есть,
        или последнего исторического бара, если реал-тайм бара нет.
        Если график не содержит баров, возвращает None.
        """

        if self.__now is not None:
            return self.__now.c

        if not self.__bars.is_empty():
            return self.__bars.item(-1, "close")

        return None

    def select(self, start: int, finish: int) -> pl.DataFrame:
        """Select bars in closed range [from, till].

        # ru
        Возвращает срез баров в закрытом интервале заданном
        начальным и конечным timestamp [from, till].
        """

        assert start <= finish

        df = self.__bars.filter(
            pl.col("ts_nanos") >= start,
            pl.col("ts_nanos") <= finish,
        )

        return df

    def add_bar(self, bar: Bar) -> None:
        """Add new bar

        Depending on datetime of 'new_bar' this function do:
         - only update real-time bar
         - add new historical bar and update real-time

        # ru
        Добавляет в график новый бар. В зависимости от даты и
        времени добавляемого бара функция:
        - обновит текущий реал-тайм бар новым баром;
        - сделает текущий реал-тайм бар историческим (last), а новый
          поставит текущим (now);
        """

        bar.set_chart(self)

        # если баров не было - в пустой график добавляем первый бар
        # или если время одинаковое - только обновить текущий бар
        if self.__now is None or self.__now.ts == bar.ts:
            self.__now = bar
            self.upd_bar.emit(self.now())
            return

        # время смены бара
        next_ts = self.__tf.next_ts(self.__now.ts)

        # если время пришедшего нового бара больше текущего последнего
        # и при этом меньше чем время смены бара, - джоинить этот бар
        if self.__now.ts < bar.ts < next_ts:
            self.__now = Bar.join(self.__now, bar)
            self.upd_bar.emit(bar)
            return

        # если время пришедшего нового бара больше текущего последнего
        # и больше времени смены бара, - новый текущий
        if bar.ts > self.__now.ts and bar.ts >= next_ts:
            self.__bars.extend(self.__now.df)
            self.__now = bar

            self.new_bar.emit(self.last())
            self.upd_bar.emit(self.now())
            return

        assert False, "Unreachable"

    def highest_high(self):
        return self.__bars["high"].max()

    def lowest_low(self):
        return self.__bars["low"].min()


if __name__ == "__main__":
    ...
