# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────


from avin.domain.chart.chart import Chart
from avin.domain.common.timeframe import TimeFrame
from avin.domain.footprint.tick_footprint import TickFootprint
from avin.domain.footprint.time_footprint import TimeFootprint
from avin.domain.footprint.value_footprint import ValueFootprint
from avin.domain.footprint.volume_footprint import VolumeFootprint
from avin.domain.instrument.category import Category
from avin.domain.instrument.exchange import Exchange
from avin.domain.instrument.iid import Iid
from avin.domain.raw.tick import Tick
from avin.errors import DataUnavailableError


class BaseAsset:
    """
    Base domain asset.
    Share, Future, Bond, Option and other asset types inherit from it.

    BaseAsset stores instrument identity and loaded market data.
    It does not load, build, download or save data by itself. Services are
    responsible for loading/building data and putting it into the asset.

    -- ru
    Базовый доменный актив.
    От него наследуются Share, Future, Bond, Option...

    BaseAsset хранит идентификатор инструмента и загруженную market data.
    Он сам не загружает, не строит, не скачивает и не сохраняет данные.
    Сервисы отвечают за загрузку/построение данных и кладут их в актив.
    """

    def __init__(self, iid: Iid) -> None:
        self._iid = iid
        self._charts: dict[TimeFrame, Chart] = {}
        self._ticks: list[Tick] = []
        self._time_footprints: dict[TimeFrame, TimeFootprint] = {}
        self._tick_footprints: dict[int, TickFootprint] = {}
        self._volume_footprints: dict[int, VolumeFootprint] = {}
        self._value_footprints: dict[float, ValueFootprint] = {}

    def __str__(self) -> str:
        return self.code

    def __hash__(self) -> int:
        return hash(self.figi)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseAsset):
            return NotImplemented

        return self.figi == other.figi

    @property
    def iid(self) -> Iid:
        return self._iid

    @property
    def code(self) -> str:
        return self._iid.code

    @property
    def exchange(self) -> Exchange:
        return self._iid.exchange

    @property
    def category(self) -> Category:
        return self._iid.category

    @property
    def ticker(self) -> str:
        return self._iid.ticker

    @property
    def figi(self) -> str:
        return self._iid.figi

    @property
    def name(self) -> str:
        return self._iid.name

    @property
    def lot(self) -> int:
        return self._iid.lot

    @property
    def step(self) -> float:
        return self._iid.step

    def chart(self, tf: TimeFrame) -> Chart:
        if tf not in self._charts:
            raise DataUnavailableError(f"Chart {tf} is unavailable")

        return self._charts[tf]

    def ticks(self) -> list[Tick]:
        if not self._ticks:
            raise DataUnavailableError("Tick data is unavailable")

        return self._ticks

    def time_footprint(self, tf: TimeFrame) -> TimeFootprint:
        if tf not in self._time_footprints:
            raise DataUnavailableError(f"Time footprint {tf} is unavailable")

        return self._time_footprints[tf]

    def tick_footprint(self, ticks_per_cluster: int) -> TickFootprint:
        if ticks_per_cluster not in self._tick_footprints:
            raise DataUnavailableError(
                f"Tick footprint {ticks_per_cluster} is unavailable"
            )

        return self._tick_footprints[ticks_per_cluster]

    def volume_footprint(self, volume_per_cluster: int) -> VolumeFootprint:
        if volume_per_cluster not in self._volume_footprints:
            raise DataUnavailableError(
                f"Volume footprint {volume_per_cluster} is unavailable"
            )

        return self._volume_footprints[volume_per_cluster]

    def value_footprint(self, value_per_cluster: float) -> ValueFootprint:
        if value_per_cluster not in self._value_footprints:
            raise DataUnavailableError(
                f"Value footprint {value_per_cluster} is unavailable"
            )

        return self._value_footprints[value_per_cluster]

    def has_chart(self, tf: TimeFrame) -> bool:
        return tf in self._charts

    def has_ticks(self) -> bool:
        return bool(self._ticks)

    def has_time_footprint(self, tf: TimeFrame) -> bool:
        return tf in self._time_footprints

    def has_tick_footprint(self, ticks_per_cluster: int) -> bool:
        return ticks_per_cluster in self._tick_footprints

    def has_volume_footprint(self, volume_per_cluster: int) -> bool:
        return volume_per_cluster in self._volume_footprints

    def has_value_footprint(self, value_per_cluster: float) -> bool:
        return value_per_cluster in self._value_footprints

    def _set_chart(self, chart: Chart) -> None:
        self._charts[chart.tf] = chart

    def _set_ticks(self, ticks: list[Tick]) -> None:
        if not ticks:
            raise ValueError("Tick data is empty")

        self._ticks = ticks

        self._time_footprints.clear()
        self._tick_footprints.clear()
        self._volume_footprints.clear()
        self._value_footprints.clear()

    def _set_time_footprint(
        self,
        tf: TimeFrame,
        fp: TimeFootprint,
    ) -> None:
        self._time_footprints[tf] = fp

    def _set_tick_footprint(
        self,
        ticks_per_cluster: int,
        fp: TickFootprint,
    ) -> None:
        self._tick_footprints[ticks_per_cluster] = fp

    def _set_volume_footprint(
        self,
        volume_per_cluster: int,
        fp: VolumeFootprint,
    ) -> None:
        self._volume_footprints[volume_per_cluster] = fp

    def _set_value_footprint(
        self,
        value_per_cluster: float,
        fp: ValueFootprint,
    ) -> None:
        self._value_footprints[value_per_cluster] = fp
