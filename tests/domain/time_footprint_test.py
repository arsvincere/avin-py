# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import pytest

from avin.domain.common.direction import Direction
from avin.domain.common.timeframe import TimeFrame
from avin.domain.footprint.time_footprint import TimeFootprint
from avin.domain.raw.tick import Tick

# ============================================================================
# Helpers
# ============================================================================


def tick_s(
    seconds: int,
    price: float = 100.0,
) -> Tick:
    return Tick(
        ts=seconds * 1_000_000_000,
        direction=Direction.BUY,
        price=price,
        lots=1,
        quantity=1,
        value=price,
    )


# ============================================================================
# Init
# ============================================================================


def test_new_time_footprint():
    fp = TimeFootprint(TimeFrame.M1)

    assert fp.timeframe == TimeFrame.M1
    assert fp.is_empty
    assert len(fp) == 0


# ============================================================================
# One cluster
# ============================================================================


def test_first_tick_creates_cluster():
    fp = TimeFootprint(TimeFrame.M1)

    fp.add(tick_s(100))

    assert len(fp) == 1
    assert not fp.is_empty


def test_ticks_inside_same_minute_create_one_cluster():
    fp = TimeFootprint(TimeFrame.M1)

    fp.add(tick_s(100))
    fp.add(tick_s(110))
    fp.add(tick_s(119))

    assert len(fp) == 1

    cluster = fp[0]

    assert cluster.trades == 3
    assert cluster.vol == 3


# ============================================================================
# New cluster
# ============================================================================


def test_new_minute_creates_new_cluster():
    fp = TimeFootprint(TimeFrame.M1)

    fp.add(tick_s(100))
    fp.add(tick_s(110))

    fp.add(tick_s(160))

    assert len(fp) == 2


def test_multiple_minutes():
    fp = TimeFootprint(TimeFrame.M1)

    fp.add(tick_s(10))
    fp.add(tick_s(70))
    fp.add(tick_s(130))
    fp.add(tick_s(190))

    assert len(fp) == 4


# ============================================================================
# Last cluster
# ============================================================================


def test_last_cluster_is_updated():
    fp = TimeFootprint(TimeFrame.M1)

    fp.add(tick_s(10))
    first = fp.last_cluster

    fp.add(tick_s(70))
    second = fp.last_cluster

    assert first is not second


# ============================================================================
# Gaps
# ============================================================================


def test_gap_creates_only_one_new_cluster():
    fp = TimeFootprint(TimeFrame.M1)

    fp.add(tick_s(0))

    # jump 1 hour forward
    fp.add(tick_s(3600))

    assert len(fp) == 2


def test_gap_does_not_create_empty_clusters():
    fp = TimeFootprint(TimeFrame.M1)

    fp.add(tick_s(0))
    fp.add(tick_s(3600))

    assert len(fp) == 2


# ============================================================================
# OHLC
# ============================================================================


def test_cluster_ohlc_inside_same_frame():
    fp = TimeFootprint(TimeFrame.M1)

    fp.add(tick_s(10, price=100))
    fp.add(tick_s(20, price=105))
    fp.add(tick_s(30, price=95))
    fp.add(tick_s(40, price=102))

    cluster = fp[0]

    assert cluster.open == 100
    assert cluster.high == 105
    assert cluster.low == 95
    assert cluster.close == 102


# ============================================================================
# M5
# ============================================================================


def test_m5_same_cluster():
    fp = TimeFootprint(TimeFrame.M5)

    fp.add(tick_s(10))
    fp.add(tick_s(100))
    fp.add(tick_s(299))

    assert len(fp) == 1


def test_m5_new_cluster():
    fp = TimeFootprint(TimeFrame.M5)

    fp.add(tick_s(10))
    fp.add(tick_s(299))

    fp.add(tick_s(300))

    assert len(fp) == 2


# ============================================================================
# H1
# ============================================================================


def test_h1_same_cluster():
    fp = TimeFootprint(TimeFrame.H1)

    fp.add(tick_s(10))
    fp.add(tick_s(1000))
    fp.add(tick_s(3599))

    assert len(fp) == 1


def test_h1_new_cluster():
    fp = TimeFootprint(TimeFrame.H1)

    fp.add(tick_s(10))
    fp.add(tick_s(3600))

    assert len(fp) == 2


# ============================================================================
# Iteration
# ============================================================================


def test_iteration():
    fp = TimeFootprint(TimeFrame.M1)

    fp.add(tick_s(0))
    fp.add(tick_s(60))
    fp.add(tick_s(120))

    clusters = list(fp)

    assert len(clusters) == 3


# ============================================================================
# Ordering
# ============================================================================


def test_tick_with_older_timestamp_raises():
    fp = TimeFootprint(TimeFrame.M1)

    fp.add(tick_s(120))
    fp.add(tick_s(180))

    with pytest.raises(ValueError):
        fp.add(tick_s(60))
