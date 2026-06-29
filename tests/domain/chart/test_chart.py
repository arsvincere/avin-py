# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from types import SimpleNamespace
from typing import cast

import pytest
from avin.domain.chart.bar import Bar
from avin.domain.chart.chart import Chart
from avin.domain.common.timeframe import TimeFrame
from avin.domain.instrument import Iid


def make_iid(ticker: str = "SBER") -> Iid:
    return cast(Iid, SimpleNamespace(ticker=ticker))


def make_tf(value: str = "M1") -> TimeFrame:
    return cast(TimeFrame, value)


def make_bar(ts: int, close: float | None = None, vol: int = 1) -> Bar:
    price = float(ts) if close is None else close

    return Bar(
        ts=ts,
        open=price,
        high=price,
        low=price,
        close=price,
        vol=vol,
    )


def make_chart(bars: list[Bar] | None = None) -> Chart:
    return Chart(
        iid=make_iid(),
        tf=make_tf(),
        bars=[] if bars is None else bars,
    )


def test_empty_chart() -> None:
    chart = make_chart()

    assert chart.is_empty is True
    assert len(chart) == 0
    assert list(chart) == []
    assert chart.first is None
    assert chart.last is None
    assert chart.current is None
    assert chart.last_price is None


def test_chart_accessors() -> None:
    iid = make_iid("GAZP")
    tf = make_tf("M5")
    bars = [make_bar(10), make_bar(20)]

    chart = Chart(iid=iid, tf=tf, bars=bars)

    assert chart.iid is iid
    assert chart.ticker == "GAZP"
    assert chart.tf is tf
    assert chart.bars is bars
    assert str(chart) == "Chart GAZP M5"


def test_len_iter_getitem_and_slice() -> None:
    bars = [make_bar(10), make_bar(20), make_bar(30)]
    chart = make_chart(bars)

    assert len(chart) == 3
    assert list(chart) == bars
    assert chart[0] is bars[0]
    assert chart[-1] is bars[-1]
    assert chart[1:] == bars[1:]


def test_getitem_rejects_invalid_index_type() -> None:
    chart = make_chart([make_bar(10)])

    with pytest.raises(TypeError, match="Chart index must be int or slice"):
        chart["bad"]  # type: ignore[index]


def test_first_last_current_for_single_bar() -> None:
    bar = make_bar(10)
    chart = make_chart([bar])

    assert chart.first is bar
    assert chart.last is None
    assert chart.current is bar
    assert chart.last_price == bar.close


def test_first_last_current_for_multiple_bars() -> None:
    first = make_bar(10)
    last = make_bar(20)
    current = make_bar(30, close=123.0)

    chart = make_chart([first, last, current])

    assert chart.first is first
    assert chart.last is last
    assert chart.current is current
    assert chart.last_price == 123.0


def test_select_returns_bars_in_closed_interval() -> None:
    bars = [
        make_bar(10),
        make_bar(20),
        make_bar(30),
        make_bar(40),
        make_bar(50),
    ]
    chart = make_chart(bars)

    assert chart.select(20, 40) == [bars[1], bars[2], bars[3]]
    assert chart.select(30, 30) == [bars[2]]


def test_select_returns_partial_intersection() -> None:
    bars = [
        make_bar(10),
        make_bar(20),
        make_bar(30),
    ]
    chart = make_chart(bars)

    assert chart.select(0, 15) == [bars[0]]
    assert chart.select(25, 100) == [bars[2]]


def test_select_returns_empty_list_when_no_intersection() -> None:
    chart = make_chart([make_bar(10), make_bar(20), make_bar(30)])

    assert chart.select(0, 5) == []
    assert chart.select(35, 100) == []
    assert chart.select(11, 19) == []


def test_select_rejects_invalid_interval() -> None:
    chart = make_chart([make_bar(10)])

    with pytest.raises(ValueError, match="Chart select from_ts > till_ts"):
        chart.select(20, 10)


def test_upsert_appends_first_bar_to_empty_chart() -> None:
    chart = make_chart()
    bar = make_bar(10)

    chart.upsert(bar)

    assert chart.bars == [bar]
    assert chart.current is bar


def test_upsert_appends_newer_bar_to_end() -> None:
    first = make_bar(10)
    second = make_bar(20)
    chart = make_chart([first])

    chart.upsert(second)

    assert chart.bars == [first, second]
    assert chart.last is first
    assert chart.current is second


def test_upsert_replaces_existing_current_bar() -> None:
    old = make_bar(10, close=10.0)
    new = make_bar(10, close=11.0)
    chart = make_chart([old])

    chart.upsert(new)

    assert chart.bars == [new]
    assert chart.current is new
    assert chart.last_price == 11.0


def test_upsert_replaces_existing_historical_bar() -> None:
    old_10 = make_bar(10, close=10.0)
    bar_20 = make_bar(20, close=20.0)
    final_10 = make_bar(10, close=11.0)
    chart = make_chart([old_10, bar_20])

    chart.upsert(final_10)

    assert chart.bars == [final_10, bar_20]
    assert chart.last is final_10
    assert chart.current is bar_20


def test_upsert_inserts_missing_bar_in_correct_position() -> None:
    bar_10 = make_bar(10)
    bar_30 = make_bar(30)
    bar_20 = make_bar(20)
    chart = make_chart([bar_10, bar_30])

    chart.upsert(bar_20)

    assert chart.bars == [bar_10, bar_20, bar_30]


def test_upsert_inserts_older_bar_before_first() -> None:
    bar_10 = make_bar(10)
    bar_20 = make_bar(20)
    bar_5 = make_bar(5)
    chart = make_chart([bar_10, bar_20])

    chart.upsert(bar_5)

    assert chart.bars == [bar_5, bar_10, bar_20]
