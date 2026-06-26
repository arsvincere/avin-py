# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin.domain.footprint import (
    TickFootprint,
    TimeFootprint,
    ValueFootprint,
    VolumeFootprint,
)
from avin.domain.tick import Tick
from avin.domain.timeframe import TimeFrame


class FootprintBuilder:
    @classmethod
    def build_time(cls, ticks: list[Tick], tf: TimeFrame) -> TimeFootprint:
        fp = TimeFootprint(tf)
        for tick in ticks:
            fp.add(tick)
        return fp

    @classmethod
    def build_tick(cls, ticks: list[Tick], step: int) -> TickFootprint:
        fp = TickFootprint(step)
        for tick in ticks:
            fp.add(tick)
        return fp

    @classmethod
    def build_volume(cls, ticks: list[Tick], step: int) -> VolumeFootprint:
        fp = VolumeFootprint(step)
        for tick in ticks:
            fp.add(tick)
        return fp

    @classmethod
    def build_value(cls, ticks: list[Tick], step: float) -> ValueFootprint:
        fp = ValueFootprint(step)
        for tick in ticks:
            fp.add(tick)
        return fp
