# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import pytest

from avin.domain.common.direction import Direction
from avin.domain.footprint.value_footprint import ValueFootprint
from avin.domain.raw.tick import Tick

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
    fp = ValueFootprint(1_000_000)

    assert fp.value_per_cluster == 1_000_000
    assert fp.is_empty
    assert len(fp) == 0


def test_init_invalid_value():
    with pytest.raises(ValueError):
        ValueFootprint(0)

    with pytest.raises(ValueError):
        ValueFootprint(-1)

    with pytest.raises(ValueError):
        ValueFootprint(-100.0)


# ============================================================================
# First cluster
# ============================================================================


def test_first_tick_creates_cluster():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=100, lots=2))

    assert len(fp) == 1
    assert fp[0].val == 200.0


def test_value_accumulates_inside_cluster():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=100, lots=2))
    fp.add(tick(2, price=200, lots=1))
    fp.add(tick(3, price=50, lots=4))

    assert len(fp) == 1

    cluster = fp[0]

    assert cluster.val == 600.0
    assert cluster.trades == 3


# ============================================================================
# Boundary
# ============================================================================


def test_cluster_stays_open_until_limit_reached():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=400, lots=1))
    fp.add(tick(2, price=300, lots=1))
    fp.add(tick(3, price=299, lots=1))

    assert len(fp) == 1
    assert fp[0].val == 999.0


def test_cluster_can_end_exactly_at_limit():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=400, lots=1))
    fp.add(tick(2, price=600, lots=1))

    assert len(fp) == 1
    assert fp[0].val == 1000.0


def test_next_tick_after_limit_creates_new_cluster():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=400, lots=1))
    fp.add(tick(2, price=600, lots=1))

    fp.add(tick(3, price=1, lots=1))

    assert len(fp) == 2

    assert fp[0].val == 1000.0
    assert fp[1].val == 1.0


# ============================================================================
# Overflow
# ============================================================================


def test_cluster_can_overflow_limit():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=900, lots=1))
    fp.add(tick(2, price=200, lots=1))

    assert len(fp) == 1
    assert fp[0].val == 1100.0


def test_new_cluster_created_after_overflow():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=900, lots=1))
    fp.add(tick(2, price=200, lots=1))

    fp.add(tick(3, price=50, lots=1))

    assert len(fp) == 2

    assert fp[0].val == 1100.0
    assert fp[1].val == 50.0


# ============================================================================
# Multiple clusters
# ============================================================================


def test_multiple_clusters():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=500, lots=1))
    fp.add(tick(2, price=500, lots=1))

    fp.add(tick(3, price=600, lots=1))
    fp.add(tick(4, price=400, lots=1))

    fp.add(tick(5, price=700, lots=1))

    assert len(fp) == 3

    assert fp[0].val == 1000.0
    assert fp[1].val == 1000.0
    assert fp[2].val == 700.0


# ============================================================================
# OHLC
# ============================================================================


def test_cluster_ohlc():
    fp = ValueFootprint(1_000_000)

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
# Volume
# ============================================================================


def test_cluster_volume():
    fp = ValueFootprint(1_000_000)

    fp.add(tick(1, lots=10))
    fp.add(tick(2, lots=20))
    fp.add(tick(3, lots=30))

    assert fp[0].vol == 60


# ============================================================================
# Iteration
# ============================================================================


def test_iteration():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=500))
    fp.add(tick(2, price=500))

    fp.add(tick(3, price=500))
    fp.add(tick(4, price=500))

    clusters = list(fp)

    assert len(clusters) == 2

    assert clusters[0].val == 1000.0
    assert clusters[1].val == 1000.0


# ============================================================================
# Last cluster
# ============================================================================


def test_last_cluster():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=500))
    first = fp.last_cluster

    fp.add(tick(2, price=500))
    assert fp.last_cluster is first

    fp.add(tick(3, price=1))
    assert fp.last_cluster is not first


# ============================================================================
# Large trade
# ============================================================================


def test_single_large_trade():
    fp = ValueFootprint(1000)

    fp.add(tick(1, price=10_000, lots=1))

    assert len(fp) == 1
    assert fp[0].val == 10_000.0

    fp.add(tick(2, price=1, lots=1))

    assert len(fp) == 2
    assert fp[1].val == 1.0


# ============================================================================
# Float threshold
# ============================================================================


def test_float_threshold():
    fp = ValueFootprint(1000.5)

    fp.add(tick(1, price=500))
    fp.add(tick(2, price=500))
    fp.add(tick(3, price=10))

    assert len(fp) == 1
    assert fp[0].val == 1010.0

    fp.add(tick(4, price=1))

    assert len(fp) == 2
