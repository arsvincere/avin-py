# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest
from avin.domain.asset.asset import Asset
from avin.domain.asset.share import Share
from avin.domain.common.direction import Direction
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

# ============================================================================
# Helpers
# ============================================================================


def iid(
    ticker: str = "SBER",
    figi: str = "BBG004730N88",
    name: str = "Sber",
) -> Iid:
    return Iid(
        {
            "exchange": "MOEX",
            "category": "SHARE",
            "ticker": ticker,
            "figi": figi,
            "name": name,
            "lot": "10",
            "step": "0.01",
        }
    )


def share(
    ticker: str = "SBER",
    figi: str = "BBG004730N88",
    name: str = "Sber",
) -> Share:
    return Share(iid(ticker, figi, name))


def tick(
    ts: int = 1,
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
# Abstract
# ============================================================================


def test_asset_cannot_be_created_directly():
    with pytest.raises(TypeError):
        Asset(iid())  # type: ignore[abstract]


# ============================================================================
# Iid wrappers
# ============================================================================


def test_iid_wrappers():
    asset = share()

    assert asset.iid == iid()
    assert asset.code == "MOEX_SHARE_SBER"
    assert asset.exchange == Exchange.MOEX
    assert asset.category == Category.SHARE
    assert asset.ticker == "SBER"
    assert asset.figi == "BBG004730N88"
    assert asset.name == "Sber"
    assert asset.lot == 10
    assert asset.step == 0.01


def test_str_returns_code():
    asset = share()

    assert str(asset) == "MOEX_SHARE_SBER"


def test_hash_uses_figi():
    asset = share()

    assert hash(asset) == hash("BBG004730N88")


def test_eq_same_figi():
    a1 = share("SBER", "same_figi", "Sber")
    a2 = share("GAZP", "same_figi", "Gazprom")

    assert a1 == a2


def test_eq_different_figi():
    a1 = share("SBER", "figi_sber", "Sber")
    a2 = share("GAZP", "figi_gazp", "Gazprom")

    assert a1 != a2


def test_eq_other_type():
    asset = share()

    assert asset != "SBER"


# ============================================================================
# Ticks
# ============================================================================


def test_new_asset_has_no_ticks():
    asset = share()

    assert not asset.has_ticks()

    with pytest.raises(
        DataUnavailableError, match="Tick data is unavailable"
    ):
        asset.ticks()


def test_set_ticks():
    asset = share()
    ticks = [tick(1), tick(2)]

    asset._set_ticks(ticks)

    assert asset.has_ticks()
    assert asset.ticks() is ticks


def test_set_empty_ticks_raises():
    asset = share()

    with pytest.raises(ValueError, match="Tick data is empty"):
        asset._set_ticks([])


# ============================================================================
# Time footprint
# ============================================================================


def test_new_asset_has_no_time_footprint():
    asset = share()

    assert not asset.has_time_footprint(TimeFrame.M1)

    with pytest.raises(
        DataUnavailableError,
        match="Time footprint 1M is unavailable",
    ):
        asset.time_footprint(TimeFrame.M1)


def test_set_time_footprint():
    asset = share()
    fp = TimeFootprint(TimeFrame.M1)

    asset._set_time_footprint(TimeFrame.M1, fp)

    assert asset.has_time_footprint(TimeFrame.M1)
    assert asset.time_footprint(TimeFrame.M1) is fp


def test_different_time_footprint_is_unavailable():
    asset = share()
    asset._set_time_footprint(TimeFrame.M1, TimeFootprint(TimeFrame.M1))

    assert not asset.has_time_footprint(TimeFrame.M5)

    with pytest.raises(DataUnavailableError):
        asset.time_footprint(TimeFrame.M5)


# ============================================================================
# Tick footprint
# ============================================================================


def test_new_asset_has_no_tick_footprint():
    asset = share()

    assert not asset.has_tick_footprint(100)

    with pytest.raises(
        DataUnavailableError,
        match="Tick footprint 100 is unavailable",
    ):
        asset.tick_footprint(100)


def test_set_tick_footprint():
    asset = share()
    fp = TickFootprint(100)

    asset._set_tick_footprint(100, fp)

    assert asset.has_tick_footprint(100)
    assert asset.tick_footprint(100) is fp


def test_different_tick_footprint_is_unavailable():
    asset = share()
    asset._set_tick_footprint(100, TickFootprint(100))

    assert not asset.has_tick_footprint(200)

    with pytest.raises(DataUnavailableError):
        asset.tick_footprint(200)


# ============================================================================
# Volume footprint
# ============================================================================


def test_new_asset_has_no_volume_footprint():
    asset = share()

    assert not asset.has_volume_footprint(1000)

    with pytest.raises(
        DataUnavailableError,
        match="Volume footprint 1000 is unavailable",
    ):
        asset.volume_footprint(1000)


def test_set_volume_footprint():
    asset = share()
    fp = VolumeFootprint(1000)

    asset._set_volume_footprint(1000, fp)

    assert asset.has_volume_footprint(1000)
    assert asset.volume_footprint(1000) is fp


def test_different_volume_footprint_is_unavailable():
    asset = share()
    asset._set_volume_footprint(1000, VolumeFootprint(1000))

    assert not asset.has_volume_footprint(2000)

    with pytest.raises(DataUnavailableError):
        asset.volume_footprint(2000)


# ============================================================================
# Value footprint
# ============================================================================


def test_new_asset_has_no_value_footprint():
    asset = share()

    assert not asset.has_value_footprint(1_000_000)

    with pytest.raises(
        DataUnavailableError,
        match="Value footprint 1000000 is unavailable",
    ):
        asset.value_footprint(1_000_000)


def test_set_value_footprint():
    asset = share()
    fp = ValueFootprint(1_000_000)

    asset._set_value_footprint(1_000_000, fp)

    assert asset.has_value_footprint(1_000_000)
    assert asset.value_footprint(1_000_000) is fp


def test_different_value_footprint_is_unavailable():
    asset = share()
    asset._set_value_footprint(1_000_000, ValueFootprint(1_000_000))

    assert not asset.has_value_footprint(2_000_000)

    with pytest.raises(DataUnavailableError):
        asset.value_footprint(2_000_000)


# ============================================================================
# Derived data invalidation
# ============================================================================


def test_set_ticks_clears_footprints():
    asset = share()

    asset._set_time_footprint(TimeFrame.M1, TimeFootprint(TimeFrame.M1))
    asset._set_tick_footprint(100, TickFootprint(100))
    asset._set_volume_footprint(1000, VolumeFootprint(1000))
    asset._set_value_footprint(1_000_000, ValueFootprint(1_000_000))

    assert asset.has_time_footprint(TimeFrame.M1)
    assert asset.has_tick_footprint(100)
    assert asset.has_volume_footprint(1000)
    assert asset.has_value_footprint(1_000_000)

    asset._set_ticks([tick()])

    assert not asset.has_time_footprint(TimeFrame.M1)
    assert not asset.has_tick_footprint(100)
    assert not asset.has_volume_footprint(1000)
    assert not asset.has_value_footprint(1_000_000)


def test_set_ticks_replaces_previous_ticks():
    asset = share()

    old_ticks = [tick(1)]
    new_ticks = [tick(2), tick(3)]

    asset._set_ticks(old_ticks)
    asset._set_ticks(new_ticks)

    assert asset.ticks() is new_ticks
