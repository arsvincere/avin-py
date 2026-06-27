# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest

from avin.domain.common.direction import Direction
from avin.domain.footprint.tick_footprint import TickFootprint
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
    fp = TickFootprint(100)

    assert fp.ticks_per_cluster == 100
    assert fp.is_empty
    assert len(fp) == 0


def test_init_invalid_size():
    with pytest.raises(ValueError):
        TickFootprint(0)

    with pytest.raises(ValueError):
        TickFootprint(-1)


# ============================================================================
# First cluster
# ============================================================================


def test_first_tick_creates_cluster():
    fp = TickFootprint(3)

    fp.add(tick(1))

    assert len(fp) == 1
    assert fp[0].trades == 1


def test_ticks_accumulate_inside_cluster():
    fp = TickFootprint(3)

    fp.add(tick(1))
    fp.add(tick(2))
    fp.add(tick(3))

    assert len(fp) == 1

    cluster = fp[0]

    assert cluster.trades == 3
    assert cluster.vol == 3
    assert cluster.val == 300.0


# ============================================================================
# Cluster rollover
# ============================================================================


def test_new_cluster_created_after_limit():
    fp = TickFootprint(3)

    fp.add(tick(1))
    fp.add(tick(2))
    fp.add(tick(3))

    assert len(fp) == 1

    fp.add(tick(4))

    assert len(fp) == 2
    assert fp[0].trades == 3
    assert fp[1].trades == 1


def test_multiple_clusters():
    fp = TickFootprint(2)

    fp.add(tick(1))
    fp.add(tick(2))

    fp.add(tick(3))
    fp.add(tick(4))

    fp.add(tick(5))

    assert len(fp) == 3

    assert fp[0].trades == 2
    assert fp[1].trades == 2
    assert fp[2].trades == 1


# ============================================================================
# Exact boundaries
# ============================================================================


def test_cluster_contains_exactly_limit_ticks():
    fp = TickFootprint(5)

    for i in range(5):
        fp.add(tick(i))

    assert len(fp) == 1
    assert fp[0].trades == 5


def test_next_tick_opens_new_cluster():
    fp = TickFootprint(5)

    for i in range(6):
        fp.add(tick(i))

    assert len(fp) == 2

    assert fp[0].trades == 5
    assert fp[1].trades == 1


# ============================================================================
# OHLC
# ============================================================================


def test_cluster_ohlc():
    fp = TickFootprint(10)

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
# Volume and value
# ============================================================================


def test_cluster_volume():
    fp = TickFootprint(10)

    fp.add(tick(1, lots=5))
    fp.add(tick(2, lots=10))
    fp.add(tick(3, lots=20))

    assert fp[0].vol == 35


def test_cluster_value():
    fp = TickFootprint(10)

    fp.add(tick(1, price=100, lots=2))
    fp.add(tick(2, price=200, lots=3))

    assert fp[0].val == 800.0


# ============================================================================
# Iteration
# ============================================================================


def test_iteration():
    fp = TickFootprint(2)

    fp.add(tick(1))
    fp.add(tick(2))
    fp.add(tick(3))
    fp.add(tick(4))
    fp.add(tick(5))

    clusters = list(fp)

    assert len(clusters) == 3

    assert clusters[0].trades == 2
    assert clusters[1].trades == 2
    assert clusters[2].trades == 1


# ============================================================================
# Last cluster
# ============================================================================


def test_last_cluster():
    fp = TickFootprint(2)

    fp.add(tick(1))
    first = fp.last_cluster

    fp.add(tick(2))
    assert fp.last_cluster is first

    fp.add(tick(3))
    assert fp.last_cluster is not first


# ============================================================================
# Ordering
# ============================================================================


def test_old_timestamp_is_allowed():
    fp = TickFootprint(2)

    fp.add(tick(100))
    fp.add(tick(50))

    assert len(fp) == 1
    assert fp[0].trades == 2
