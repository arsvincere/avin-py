# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest
from avin.domain.asset.share import Share
from avin.domain.common.direction import Direction
from avin.domain.common.timeframe import TimeFrame
from avin.domain.instrument.iid import Iid
from avin.domain.raw.tick import Tick
from avin.errors import DataUnavailableError
from avin.service.asset.ensurer import AssetEnsurer

# ============================================================================
# Helpers
# ============================================================================


NS = 1_000_000_000


def share() -> Share:
    return Share(
        Iid(
            {
                "exchange": "MOEX",
                "category": "SHARE",
                "ticker": "SBER",
                "figi": "BBG004730N88",
                "name": "Sber",
                "lot": "10",
                "step": "0.01",
            }
        )
    )


def tick(
    seconds: int,
    price: float = 100.0,
    lots: int = 1,
) -> Tick:
    return Tick(
        ts=seconds * NS,
        direction=Direction.BUY,
        price=price,
        lots=lots,
        quantity=lots,
        value=price * lots,
    )


# ============================================================================
# Time footprint
# ============================================================================


def test_build_time_footprint():
    asset = share()
    asset._set_ticks(
        [
            tick(0),
            tick(10),
            tick(60),
        ]
    )

    AssetEnsurer._build_time_footprint(asset, TimeFrame.M1)

    assert asset.has_time_footprint(TimeFrame.M1)

    fp = asset.time_footprint(TimeFrame.M1)

    assert len(fp) == 2
    assert fp[0].trades == 2
    assert fp[1].trades == 1


def test_build_time_footprint_without_ticks_raises():
    asset = share()

    with pytest.raises(DataUnavailableError):
        AssetEnsurer._build_time_footprint(asset, TimeFrame.M1)


# ============================================================================
# Tick footprint
# ============================================================================


def test_build_tick_footprint():
    asset = share()
    asset._set_ticks(
        [
            tick(1),
            tick(2),
            tick(3),
            tick(4),
            tick(5),
        ]
    )

    AssetEnsurer._build_tick_footprint(asset, 2)

    assert asset.has_tick_footprint(2)

    fp = asset.tick_footprint(2)

    assert len(fp) == 3
    assert fp[0].trades == 2
    assert fp[1].trades == 2
    assert fp[2].trades == 1


def test_build_tick_footprint_without_ticks_raises():
    asset = share()

    with pytest.raises(DataUnavailableError):
        AssetEnsurer._build_tick_footprint(asset, 2)


# ============================================================================
# Volume footprint
# ============================================================================


def test_build_volume_footprint():
    asset = share()
    asset._set_ticks(
        [
            tick(1, lots=50),
            tick(2, lots=50),
            tick(3, lots=25),
        ]
    )

    AssetEnsurer._build_volume_footprint(asset, 100)

    assert asset.has_volume_footprint(100)

    fp = asset.volume_footprint(100)

    assert len(fp) == 2
    assert fp[0].vol == 100
    assert fp[1].vol == 25


def test_build_volume_footprint_without_ticks_raises():
    asset = share()

    with pytest.raises(DataUnavailableError):
        AssetEnsurer._build_volume_footprint(asset, 100)


# ============================================================================
# Value footprint
# ============================================================================


def test_build_value_footprint():
    asset = share()
    asset._set_ticks(
        [
            tick(1, price=500, lots=1),
            tick(2, price=500, lots=1),
            tick(3, price=250, lots=1),
        ]
    )

    AssetEnsurer._build_value_footprint(asset, 1000)

    assert asset.has_value_footprint(1000)

    fp = asset.value_footprint(1000)

    assert len(fp) == 2
    assert fp[0].val == 1000.0
    assert fp[1].val == 250.0


def test_build_value_footprint_without_ticks_raises():
    asset = share()

    with pytest.raises(DataUnavailableError):
        AssetEnsurer._build_value_footprint(asset, 1000)
