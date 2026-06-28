# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest

from avin.domain.chart.bar import Bar
from avin.domain.chart.bar_kind import BarKind
from avin.domain.common.price_range import PriceRange


def test_bar_contains_price_inside_range() -> None:
    bar = Bar(ts=1, open=10.0, high=12.0, low=9.0, close=11.0, vol=100)

    assert 9.0 in bar
    assert 10.5 in bar
    assert 12.0 in bar


def test_bar_does_not_contain_price_outside_range() -> None:
    bar = Bar(ts=1, open=10.0, high=12.0, low=9.0, close=11.0, vol=100)

    assert 8.9 not in bar
    assert 12.1 not in bar


def test_bar_detects_bull_kind() -> None:
    bar = Bar(ts=1, open=10.0, high=12.0, low=9.0, close=11.0, vol=100)

    assert bar.kind is BarKind.BULL
    assert bar.is_bull()
    assert not bar.is_bear()
    assert not bar.is_doji()


def test_bar_detects_bear_kind() -> None:
    bar = Bar(ts=1, open=11.0, high=12.0, low=9.0, close=10.0, vol=100)

    assert bar.kind is BarKind.BEAR
    assert bar.is_bear()
    assert not bar.is_bull()
    assert not bar.is_doji()


def test_bar_detects_doji_kind() -> None:
    bar = Bar(ts=1, open=10.0, high=12.0, low=9.0, close=10.0, vol=100)

    assert bar.kind is BarKind.DOJI
    assert bar.is_doji()
    assert not bar.is_bull()
    assert not bar.is_bear()


def test_bar_price_ranges_for_bull_bar() -> None:
    bar = Bar(ts=1, open=10.0, high=12.0, low=9.0, close=11.0, vol=100)

    assert bar.full() == PriceRange(9.0, 12.0)
    assert bar.body() == PriceRange(10.0, 11.0)
    assert bar.lower() == PriceRange(9.0, 10.0)
    assert bar.upper() == PriceRange(11.0, 12.0)


def test_bar_price_ranges_for_bear_bar() -> None:
    bar = Bar(ts=1, open=11.0, high=12.0, low=9.0, close=10.0, vol=100)

    assert bar.full() == PriceRange(9.0, 12.0)
    assert bar.body() == PriceRange(10.0, 11.0)
    assert bar.lower() == PriceRange(9.0, 10.0)
    assert bar.upper() == PriceRange(11.0, 12.0)


def test_bar_join_returns_combined_bar() -> None:
    b1 = Bar(ts=1, open=10.0, high=12.0, low=9.0, close=11.0, vol=100)
    b2 = Bar(ts=2, open=11.0, high=13.0, low=8.0, close=10.5, vol=200)

    bar = Bar.join(b1, b2)

    assert bar == Bar(
        ts=1,
        open=10.0,
        high=13.0,
        low=8.0,
        close=10.5,
        vol=300,
    )


def test_bar_rejects_low_greater_than_high() -> None:
    with pytest.raises(ValueError, match="Bar low > high"):
        Bar(ts=1, open=10.0, high=9.0, low=12.0, close=11.0, vol=100)


def test_bar_rejects_open_outside_range() -> None:
    with pytest.raises(ValueError, match="Bar open is outside range"):
        Bar(ts=1, open=13.0, high=12.0, low=9.0, close=11.0, vol=100)


def test_bar_rejects_close_outside_range() -> None:
    with pytest.raises(ValueError, match="Bar close is outside range"):
        Bar(ts=1, open=10.0, high=12.0, low=9.0, close=13.0, vol=100)


def test_bar_rejects_negative_volume() -> None:
    with pytest.raises(ValueError, match="Bar volume is negative"):
        Bar(ts=1, open=10.0, high=12.0, low=9.0, close=11.0, vol=-1)
