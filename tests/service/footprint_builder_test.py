# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from avin.domain.common.direction import Direction
from avin.domain.common.timeframe import TimeFrame
from avin.domain.footprint import (
    TickFootprint,
    TimeFootprint,
    ValueFootprint,
    VolumeFootprint,
)
from avin.domain.raw.tick import Tick
from avin.service.footprint_builder import FootprintBuilder

# ============================================================================
# Helpers
# ============================================================================


def tick(
    ts: int,
    price: float = 100.0,
    lots: int = 1,
) -> Tick:
    return Tick(
        ts=ts,
        direction=Direction.BUY,
        price=price,
        lots=lots,
        quantity=lots,
        value=price * lots,
    )


def tick_s(
    seconds: int,
    price: float = 100.0,
    lots: int = 1,
) -> Tick:
    return tick(
        ts=seconds * 1_000_000_000,
        price=price,
        lots=lots,
    )


# ============================================================================
# Empty
# ============================================================================


def test_build_empty_tick_footprint():
    fp = FootprintBuilder.build_tick([], 100)

    assert isinstance(fp, TickFootprint)
    assert fp.ticks_per_cluster == 100
    assert fp.is_empty
    assert len(fp) == 0


def test_build_empty_time_footprint():
    fp = FootprintBuilder.build_time([], TimeFrame.M1)

    assert isinstance(fp, TimeFootprint)
    assert fp.timeframe == TimeFrame.M1
    assert fp.is_empty
    assert len(fp) == 0


def test_build_empty_volume_footprint():
    fp = FootprintBuilder.build_volume([], 1000)

    assert isinstance(fp, VolumeFootprint)
    assert fp.volume_per_cluster == 1000
    assert fp.is_empty
    assert len(fp) == 0


def test_build_empty_value_footprint():
    fp = FootprintBuilder.build_value([], 1_000_000)

    assert isinstance(fp, ValueFootprint)
    assert fp.value_per_cluster == 1_000_000
    assert fp.is_empty
    assert len(fp) == 0


# ============================================================================
# Build tick footprint
# ============================================================================


def test_build_tick_footprint():
    ticks = [
        tick(1),
        tick(2),
        tick(3),
        tick(4),
        tick(5),
    ]

    fp = FootprintBuilder.build_tick(ticks, 2)

    assert isinstance(fp, TickFootprint)
    assert fp.ticks_per_cluster == 2
    assert len(fp) == 3

    assert fp[0].trades == 2
    assert fp[1].trades == 2
    assert fp[2].trades == 1


# ============================================================================
# Build time footprint
# ============================================================================


def test_build_time_footprint():
    ticks = [
        tick_s(10),
        tick_s(20),
        tick_s(70),
        tick_s(80),
        tick_s(130),
    ]

    fp = FootprintBuilder.build_time(ticks, TimeFrame.M1)

    assert isinstance(fp, TimeFootprint)
    assert fp.timeframe == TimeFrame.M1
    assert len(fp) == 3

    assert fp[0].trades == 2
    assert fp[1].trades == 2
    assert fp[2].trades == 1


# ============================================================================
# Build volume footprint
# ============================================================================


def test_build_volume_footprint():
    ticks = [
        tick(1, lots=40),
        tick(2, lots=60),
        tick(3, lots=30),
        tick(4, lots=70),
        tick(5, lots=10),
    ]

    fp = FootprintBuilder.build_volume(ticks, 100)

    assert isinstance(fp, VolumeFootprint)
    assert fp.volume_per_cluster == 100
    assert len(fp) == 3

    assert fp[0].vol == 100
    assert fp[1].vol == 100
    assert fp[2].vol == 10


# ============================================================================
# Build value footprint
# ============================================================================


def test_build_value_footprint():
    ticks = [
        tick(1, price=400, lots=1),
        tick(2, price=600, lots=1),
        tick(3, price=300, lots=1),
        tick(4, price=700, lots=1),
        tick(5, price=100, lots=1),
    ]

    fp = FootprintBuilder.build_value(ticks, 1000)

    assert isinstance(fp, ValueFootprint)
    assert fp.value_per_cluster == 1000
    assert len(fp) == 3

    assert fp[0].val == 1000.0
    assert fp[1].val == 1000.0
    assert fp[2].val == 100.0
