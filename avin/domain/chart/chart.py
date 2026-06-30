# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from bisect import bisect_left, bisect_right
from collections.abc import Iterator

from avin.domain.chart.bar import Bar
from avin.domain.common.timeframe import TimeFrame
from avin.domain.instrument import Iid


class Chart:
    """
    Mutable candlestick chart for one instrument and one timeframe.

    Chart stores bars ordered by timestamp. The last bar in the list is
    the current bar. In realtime it may be unfinished. In backtest/analyse
    it is still treated as current because trading code observes bars
    through the same interface.

    Invariants:
    - bars are ordered by increasing ts;
    - bars have unique ts;
    - every Bar.ts is the beginning timestamp of its timeframe frame;
    - first == chart[0] when chart is not empty;
    - current == chart[-1] when chart is not empty;
    - last == chart[-2] when chart has at least 2 bars.

    Constructor accepts trusted bars. Historical validation belongs to
    storage/service, not to Chart.

    Chart does not know about Asset, Source, Storage, DataFrame, Broker, GUI.

    -- ru
    Мутабельный свечной график одного инструмента и одного таймфрейма.

    Chart хранит бары, упорядоченные по timestamp. Последний бар в списке —
    current. В realtime он может быть незавершенным. В backtest/analyse он
    всё равно рассматривается как current, потому что торговый код работает
    через единый интерфейс.

    Инварианты:
    - бары упорядочены по возрастанию ts;
    - бары имеют уникальный ts;
    - каждый Bar.ts — timestamp начала frame своего таймфрейма;
    - first == chart[0], если chart не пустой;
    - current == chart[-1], если chart не пустой;
    - last == chart[-2], если в chart есть минимум 2 бара.

    Конструктор принимает trusted bars. Проверка исторических данных —
    ответственность storage/service, а не Chart.

    Chart не знает про Asset, Source, Storage, DataFrame, Broker и GUI.
    """

    def __init__(self, iid: Iid, tf: TimeFrame, bars: list[Bar]) -> None:
        self._iid = iid
        self._tf = tf
        self._bars = bars

    def __len__(self) -> int:
        return len(self._bars)

    def __iter__(self) -> Iterator[Bar]:
        return iter(self._bars)

    def __getitem__(self, index: int | slice) -> Bar | list[Bar]:
        if not isinstance(index, int | slice):
            raise TypeError(
                f"Chart index must be int or slice, "
                f"got {type(index).__name__}"
            )

        return self._bars[index]

    def __str__(self) -> str:
        return f"Chart {self.ticker} {self.tf}"

    @property
    def iid(self) -> Iid:
        return self._iid

    @property
    def ticker(self) -> str:
        return self._iid.ticker

    @property
    def tf(self) -> TimeFrame:
        return self._tf

    @property
    def bars(self) -> list[Bar]:
        """
        Returns internal bars list for fast domain/GUI/analyse access.

        The last bar is current and may be unfinished in realtime.
        Do not mutate the list directly; it may break Chart invariants.
        Use Chart methods to change chart state.

        -- ru
        Возвращает внутренний список баров для быстрого доступа
        из domain/gui/analyse кода.

        Последний бар — current, в realtime он может быть незавершенным.
        Не мутировать список напрямую: это может сломать инварианты Chart.
        Для изменения состояния Chart использовать методы Chart.
        """
        return self._bars

    @property
    def first(self) -> Bar | None:
        """First bar in chart."""
        if not self._bars:
            return None

        return self._bars[0]

    @property
    def last(self) -> Bar | None:
        """Previous bar before current."""
        if len(self._bars) < 2:
            return None

        return self._bars[-2]

    @property
    def current(self) -> Bar | None:
        """Last bar in chart, may be unfinished in realtime."""
        if not self._bars:
            return None

        return self._bars[-1]

    @property
    def last_price(self) -> float | None:
        current = self.current
        if current is None:
            return None

        return current.close

    @property
    def is_empty(self) -> bool:
        return not self._bars

    def select(self, from_ts: int, till_ts: int) -> list[Bar]:
        """
        Select bars in closed interval [from_ts, till_ts].

        Returns a new list slice.

        -- ru
        Возвращает бары в закрытом интервале [from_ts, till_ts].

        Возвращает новый list-срез.
        """
        if from_ts > till_ts:
            raise ValueError("Chart select from_ts > till_ts")

        left = bisect_left(self._bars, from_ts, key=lambda b: b.ts)
        right = bisect_right(self._bars, till_ts, key=lambda b: b.ts)

        return self._bars[left:right]

    def upsert(self, bar: Bar) -> None:
        """
        Insert or replace bar by timestamp.

        -- ru
        Вставляет бар в график или заменяет существующий бар
        с таким же timestamp.
        """

        # 1. График пустой — добавляем первый бар.
        if not self._bars:
            self._bars.append(bar)
            return

        # 2. Бар новее последнего — добавляем в конец.
        if bar.ts > self._bars[-1].ts:
            self._bars.append(bar)
            return

        # 3. Ищем позицию бара по timestamp.
        index = bisect_left(self._bars, bar.ts, key=lambda b: b.ts)

        # 4. Бар с таким timestamp уже есть — заменяем.
        if index < len(self._bars) and self._bars[index].ts == bar.ts:
            self._bars[index] = bar
            return

        # 5. Бара с таким timestamp нет — вставляем в правильное место.
        self._bars.insert(index, bar)
