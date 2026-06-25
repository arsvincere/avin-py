# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import pytest

from avin.core.direction import Direction
from avin.core.tick import Tick
from avin.core.volume_footprint import VolumeFootprint

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


# ============================================================================
# Init
# ============================================================================


def test_init():
    fp = VolumeFootprint(100)

    assert fp.volume_per_cluster == 100
    assert fp.is_empty
    assert len(fp) == 0


def test_init_invalid_volume():
    with pytest.raises(ValueError):
        VolumeFootprint(0)

    with pytest.raises(ValueError):
        VolumeFootprint(-1)


# ============================================================================
# First cluster
# ============================================================================


def test_first_tick_creates_cluster():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=10))

    assert len(fp) == 1
    assert fp[0].vol == 10


def test_volume_accumulates_inside_cluster():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=10))
    fp.add(tick(2, lots=20))
    fp.add(tick(3, lots=30))

    assert len(fp) == 1

    cluster = fp[0]

    assert cluster.vol == 60
    assert cluster.trades == 3


# ============================================================================
# Boundary
# ============================================================================


def test_cluster_stays_open_until_limit_reached():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=30))
    fp.add(tick(2, lots=30))
    fp.add(tick(3, lots=39))

    assert len(fp) == 1
    assert fp[0].vol == 99


def test_cluster_can_end_exactly_at_limit():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=40))
    fp.add(tick(2, lots=60))

    assert len(fp) == 1
    assert fp[0].vol == 100


def test_next_tick_after_limit_creates_new_cluster():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=40))
    fp.add(tick(2, lots=60))

    fp.add(tick(3, lots=1))

    assert len(fp) == 2

    assert fp[0].vol == 100
    assert fp[1].vol == 1


# ============================================================================
# Overflow
# ============================================================================


def test_cluster_can_overflow_limit():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=90))
    fp.add(tick(2, lots=20))

    assert len(fp) == 1
    assert fp[0].vol == 110


def test_new_cluster_created_after_overflow():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=90))
    fp.add(tick(2, lots=20))

    fp.add(tick(3, lots=5))

    assert len(fp) == 2

    assert fp[0].vol == 110
    assert fp[1].vol == 5


# ============================================================================
# Multiple clusters
# ============================================================================


def test_multiple_clusters():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=50))
    fp.add(tick(2, lots=50))

    fp.add(tick(3, lots=60))
    fp.add(tick(4, lots=40))

    fp.add(tick(5, lots=70))

    assert len(fp) == 3

    assert fp[0].vol == 100
    assert fp[1].vol == 100
    assert fp[2].vol == 70


# ============================================================================
# OHLC
# ============================================================================


def test_cluster_ohlc():
    fp = VolumeFootprint(1000)

    fp.add(tick(1, price=100))
    fp.add(tick(2, price=110))
    fp.add(tick(3, price=90))
    fp.add(tick(4, price=105))

    cluster = fp[0]

    assert cluster.open == 100
    assert cluster.high == 110
    assert cluster.low == 90
    assert cluster.close == 105


# ============================================================================
# Value
# ============================================================================


def test_cluster_value():
    fp = VolumeFootprint(1000)

    fp.add(tick(1, price=100, lots=2))
    fp.add(tick(2, price=200, lots=3))

    assert fp[0].val == 800.0


# ============================================================================
# Iteration
# ============================================================================


def test_iteration():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=50))
    fp.add(tick(2, lots=50))

    fp.add(tick(3, lots=50))
    fp.add(tick(4, lots=50))

    clusters = list(fp)

    assert len(clusters) == 2

    assert clusters[0].vol == 100
    assert clusters[1].vol == 100


# ============================================================================
# Last cluster
# ============================================================================


def test_last_cluster():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=50))
    first = fp.last_cluster

    fp.add(tick(2, lots=50))
    assert fp.last_cluster is first

    fp.add(tick(3, lots=1))
    assert fp.last_cluster is not first


# ============================================================================
# Large tick
# ============================================================================


def test_single_large_tick():
    fp = VolumeFootprint(100)

    fp.add(tick(1, lots=1000))

    assert len(fp) == 1
    assert fp[0].vol == 1000

    fp.add(tick(2, lots=1))

    assert len(fp) == 2
    assert fp[1].vol == 1
