# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin.domain.common.timeframe import TimeFrame
from avin.domain.footprint import (
    TickFootprint,
    TimeFootprint,
    ValueFootprint,
    VolumeFootprint,
)
from avin.domain.raw.tick import Tick


class FootprintBuilder:
    @classmethod
    def build_time(cls, ticks: list[Tick], tf: TimeFrame) -> TimeFootprint:
        fp = TimeFootprint(tf)
        for tick in ticks:
            fp.add(tick)
        return fp

    @classmethod
    def build_tick(
        cls, ticks: list[Tick], tick_per_cluster: int
    ) -> TickFootprint:
        fp = TickFootprint(tick_per_cluster)
        for tick in ticks:
            fp.add(tick)
        return fp

    @classmethod
    def build_volume(
        cls, ticks: list[Tick], volume_per_cluster: int
    ) -> VolumeFootprint:
        fp = VolumeFootprint(volume_per_cluster)
        for tick in ticks:
            fp.add(tick)
        return fp

    @classmethod
    def build_value(
        cls, ticks: list[Tick], value_per_cluster: float
    ) -> ValueFootprint:
        fp = ValueFootprint(value_per_cluster)
        for tick in ticks:
            fp.add(tick)
        return fp
