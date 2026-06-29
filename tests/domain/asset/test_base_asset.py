# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest
from avin.domain.asset.base_asset import BaseAsset
from avin.domain.chart.bar import Bar
from avin.domain.chart.chart import Chart
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


def asset(
    ticker: str = "SBER",
    figi: str = "BBG004730N88",
    name: str = "Sber",
) -> BaseAsset:
    return BaseAsset(iid(ticker, figi, name))


def bar(ts: int = 1, close: float = 100.0) -> Bar:
    return Bar(
        ts=ts,
        open=close,
        high=close,
        low=close,
        close=close,
        vol=1,
    )


def chart(tf: TimeFrame = TimeFrame.M1) -> Chart:
    return Chart(
        iid=iid(),
        tf=tf,
        bars=[bar()],
    )


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
# Iid wrappers
# ============================================================================


def test_iid_wrappers() -> None:
    a = asset()

    assert a.iid == iid()
    assert a.code == "MOEX_SHARE_SBER"
    assert a.exchange == Exchange.MOEX
    assert a.category == Category.SHARE
    assert a.ticker == "SBER"
    assert a.figi == "BBG004730N88"
    assert a.name == "Sber"
    assert a.lot == 10
    assert a.step == 0.01


def test_str_returns_code() -> None:
    a = asset()

    assert str(a) == "MOEX_SHARE_SBER"


def test_hash_uses_figi() -> None:
    a = asset()

    assert hash(a) == hash("BBG004730N88")


def test_eq_same_figi() -> None:
    a1 = asset("SBER", "same_figi", "Sber")
    a2 = asset("GAZP", "same_figi", "Gazprom")

    assert a1 == a2


def test_eq_different_figi() -> None:
    a1 = asset("SBER", "figi_sber", "Sber")
    a2 = asset("GAZP", "figi_gazp", "Gazprom")

    assert a1 != a2


def test_eq_other_type() -> None:
    a = asset()

    assert a != "SBER"


# ============================================================================
# Chart
# ============================================================================


def test_new_asset_has_no_chart() -> None:
    a = asset()

    assert not a.has_chart(TimeFrame.M1)

    with pytest.raises(
        DataUnavailableError,
        match="Chart 1M is unavailable",
    ):
        a.chart(TimeFrame.M1)


def test_set_chart() -> None:
    a = asset()
    c = chart(TimeFrame.M1)

    a._set_chart(c)

    assert a.has_chart(TimeFrame.M1)
    assert a.chart(TimeFrame.M1) is c


def test_set_chart_uses_chart_timeframe() -> None:
    a = asset()
    c = chart(TimeFrame.M5)

    a._set_chart(c)

    assert not a.has_chart(TimeFrame.M1)
    assert a.has_chart(TimeFrame.M5)
    assert a.chart(TimeFrame.M5) is c


def test_different_chart_is_unavailable() -> None:
    a = asset()
    a._set_chart(chart(TimeFrame.M1))

    assert not a.has_chart(TimeFrame.M5)

    with pytest.raises(DataUnavailableError):
        a.chart(TimeFrame.M5)


# ============================================================================
# Ticks
# ============================================================================


def test_new_asset_has_no_ticks() -> None:
    a = asset()

    assert not a.has_ticks()

    with pytest.raises(
        DataUnavailableError,
        match="Tick data is unavailable",
    ):
        a.ticks()


def test_set_ticks() -> None:
    a = asset()
    ticks = [tick(1), tick(2)]

    a._set_ticks(ticks)

    assert a.has_ticks()
    assert a.ticks() is ticks


def test_set_empty_ticks_raises() -> None:
    a = asset()

    with pytest.raises(ValueError, match="Tick data is empty"):
        a._set_ticks([])


def test_set_ticks_replaces_previous_ticks() -> None:
    a = asset()

    old_ticks = [tick(1)]
    new_ticks = [tick(2), tick(3)]

    a._set_ticks(old_ticks)
    a._set_ticks(new_ticks)

    assert a.ticks() is new_ticks


# ============================================================================
# Time footprint
# ============================================================================


def test_new_asset_has_no_time_footprint() -> None:
    a = asset()

    assert not a.has_time_footprint(TimeFrame.M1)

    with pytest.raises(
        DataUnavailableError,
        match="Time footprint 1M is unavailable",
    ):
        a.time_footprint(TimeFrame.M1)


def test_set_time_footprint() -> None:
    a = asset()
    fp = TimeFootprint(TimeFrame.M1)

    a._set_time_footprint(TimeFrame.M1, fp)

    assert a.has_time_footprint(TimeFrame.M1)
    assert a.time_footprint(TimeFrame.M1) is fp


def test_different_time_footprint_is_unavailable() -> None:
    a = asset()
    a._set_time_footprint(TimeFrame.M1, TimeFootprint(TimeFrame.M1))

    assert not a.has_time_footprint(TimeFrame.M5)

    with pytest.raises(DataUnavailableError):
        a.time_footprint(TimeFrame.M5)


# ============================================================================
# Tick footprint
# ============================================================================


def test_new_asset_has_no_tick_footprint() -> None:
    a = asset()

    assert not a.has_tick_footprint(100)

    with pytest.raises(
        DataUnavailableError,
        match="Tick footprint 100 is unavailable",
    ):
        a.tick_footprint(100)


def test_set_tick_footprint() -> None:
    a = asset()
    fp = TickFootprint(100)

    a._set_tick_footprint(100, fp)

    assert a.has_tick_footprint(100)
    assert a.tick_footprint(100) is fp


def test_different_tick_footprint_is_unavailable() -> None:
    a = asset()
    a._set_tick_footprint(100, TickFootprint(100))

    assert not a.has_tick_footprint(200)

    with pytest.raises(DataUnavailableError):
        a.tick_footprint(200)


# ============================================================================
# Volume footprint
# ============================================================================


def test_new_asset_has_no_volume_footprint() -> None:
    a = asset()

    assert not a.has_volume_footprint(1000)

    with pytest.raises(
        DataUnavailableError,
        match="Volume footprint 1000 is unavailable",
    ):
        a.volume_footprint(1000)


def test_set_volume_footprint() -> None:
    a = asset()
    fp = VolumeFootprint(1000)

    a._set_volume_footprint(1000, fp)

    assert a.has_volume_footprint(1000)
    assert a.volume_footprint(1000) is fp


def test_different_volume_footprint_is_unavailable() -> None:
    a = asset()
    a._set_volume_footprint(1000, VolumeFootprint(1000))

    assert not a.has_volume_footprint(2000)

    with pytest.raises(DataUnavailableError):
        a.volume_footprint(2000)


# ============================================================================
# Value footprint
# ============================================================================


def test_new_asset_has_no_value_footprint() -> None:
    a = asset()

    assert not a.has_value_footprint(1_000_000)

    with pytest.raises(
        DataUnavailableError,
        match="Value footprint 1000000 is unavailable",
    ):
        a.value_footprint(1_000_000)


def test_set_value_footprint() -> None:
    a = asset()
    fp = ValueFootprint(1_000_000)

    a._set_value_footprint(1_000_000, fp)

    assert a.has_value_footprint(1_000_000)
    assert a.value_footprint(1_000_000) is fp


def test_different_value_footprint_is_unavailable() -> None:
    a = asset()
    a._set_value_footprint(1_000_000, ValueFootprint(1_000_000))

    assert not a.has_value_footprint(2_000_000)

    with pytest.raises(DataUnavailableError):
        a.value_footprint(2_000_000)


# ============================================================================
# Derived data invalidation
# ============================================================================


def test_set_ticks_clears_footprints() -> None:
    a = asset()

    a._set_time_footprint(TimeFrame.M1, TimeFootprint(TimeFrame.M1))
    a._set_tick_footprint(100, TickFootprint(100))
    a._set_volume_footprint(1000, VolumeFootprint(1000))
    a._set_value_footprint(1_000_000, ValueFootprint(1_000_000))

    assert a.has_time_footprint(TimeFrame.M1)
    assert a.has_tick_footprint(100)
    assert a.has_volume_footprint(1000)
    assert a.has_value_footprint(1_000_000)

    a._set_ticks([tick()])

    assert not a.has_time_footprint(TimeFrame.M1)
    assert not a.has_tick_footprint(100)
    assert not a.has_volume_footprint(1000)
    assert not a.has_value_footprint(1_000_000)


def test_set_ticks_does_not_clear_charts() -> None:
    a = asset()
    c = chart(TimeFrame.M1)

    a._set_chart(c)
    a._set_ticks([tick()])

    assert a.has_chart(TimeFrame.M1)
    assert a.chart(TimeFrame.M1) is c
