# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import polars as pl

from avin import *

IID = Manager.find("moex_share_sber")


# data for testing chart.add_bar(...)
def bars_data_list() -> list:
    data = [
        (1735887540000000000, 280.0, 280.0, 280.0, 280.0, 158150),
        (1735887600000000000, 279.99, 280.0, 279.55, 279.7, 476620),
        (1735887660000000000, 279.64, 279.9, 279.2, 279.85, 643880),
        (1735887720000000000, 279.85, 280.41, 279.74, 280.1, 584470),
        (1735887780000000000, 280.17, 280.2, 279.87, 279.9, 369760),
        (1735887840000000000, 279.9, 279.95, 279.54, 279.54, 338140),
        (1735887900000000000, 279.54, 279.56, 279.0, 279.44, 767470),
        (1735887960000000000, 279.43, 279.44, 278.58, 278.91, 520310),
        (1735888020000000000, 278.99, 279.38, 278.71, 279.07, 281490),
        (1735888080000000000, 279.07, 279.07, 278.11, 278.31, 304020),
        (1735888140000000000, 278.34, 278.91, 278.15, 278.4, 416040),
        (1735888200000000000, 278.53, 278.89, 278.14, 278.62, 233030),
        (1735888260000000000, 278.62, 278.93, 278.58, 278.93, 164140),
        (1735888320000000000, 278.91, 279.21, 278.85, 278.86, 208890),
        (1735888380000000000, 278.86, 278.88, 278.51, 278.73, 153850),
    ]

    return data


# tests ----------------------------------------------------------------------


def test_chart():
    bars = pl.DataFrame(
        {
            "ts_nanos": [1, 2, 3, 4, 5],
            "open": [11.0, 22.0, 33.0, 44.0, 55.0],
            "high": [11.0, 22.0, 33.0, 44.0, 55.0],
            "low": [11.0, 22.0, 33.0, 44.0, 55.0],
            "close": [11.0, 22.0, 33.0, 44.0, 55.0],
            "volume": [111, 222, 333, 444, 555],
        }
    )
    tf = TimeFrame.DAY
    chart = Chart(IID, tf, bars)

    assert chart.iid() == IID
    assert chart.ticker() == Ticker("SBER")
    assert chart.tf() == tf
    # assert chart.bars() == BARS  # хз, дф одинаковые но TypeError..
    assert chart.first() == Bar(bars[0])
    assert chart.last() == Bar(bars[-1])
    assert chart.now() is None
    assert chart.last_price() == 55.0


def test_chart_load():
    tf = TimeFrame.M1
    begin = str_to_utc("2025-07-01 00:00")
    end = str_to_utc("2025-08-01 00:00")

    chart = Chart.load(IID, tf, begin, end)

    assert chart.first().dt() == str_to_utc("2025-07-01 06:59")
    assert chart.last().dt() == str_to_utc("2025-07-31 23:49")


def test_chart_select_d():
    tf = TimeFrame.DAY
    begin = str_to_utc("2024-12-20")
    end = str_to_utc("2025-01-01")
    chart = Chart.load(IID, tf, begin, end)

    start = str_to_utc("2024-12-23")
    start = dt_to_ts(start)
    finish = str_to_utc("2024-12-25")
    finish = dt_to_ts(finish)

    selected = chart.select(start, finish)
    assert len(selected) == 3


def test_chart_select_h1():
    tf = TimeFrame.H1
    begin = str_to_utc("2023-08-01")
    end = str_to_utc("2025-08-02")
    chart = Chart.load(IID, tf, begin, end)

    # выборка с 12:30 до 15:30
    # должно войти 3 бара 13:00 14:00 15:00
    start = str_to_utc("2023-08-01 12:30")
    finish = str_to_utc("2023-08-01 15:30")

    start = dt_to_ts(start)
    finish = dt_to_ts(finish)

    selected = chart.select(start, finish)
    assert len(selected) == 3


def test_chart_add_10m():
    tf = TimeFrame.M10
    chart = Chart.empty(IID, tf)

    bars_data = bars_data_list()
    for i in bars_data:
        bar = Bar.from_ohlcv(i[0], i[1], i[2], i[3], i[4], i[5])
        chart.add_bar(bar)

    assert len(chart.bars()) == 2

    assert chart.first() == Bar.from_ohlcv(
        1735887540000000000, 280.0, 280.0, 280.0, 280.0, 158150
    )
    assert chart[2] == Bar.from_ohlcv(
        1735887540000000000, 280.0, 280.0, 280.0, 280.0, 158150
    )
    assert chart[1] == Bar.from_ohlcv(
        1735887600000000000, 279.99, 280.41, 278.11, 278.4, 4702200
    )
    assert chart[0] == Bar.from_ohlcv(
        1735888200000000000, 278.53, 279.21, 278.14, 278.73, 759910
    )


def test_chart_add_1h():
    tf = TimeFrame.H1
    chart = Chart.empty(IID, tf)

    bars_data = bars_data_list()
    for i in bars_data:
        bar = Bar.from_ohlcv(i[0], i[1], i[2], i[3], i[4], i[5])
        chart.add_bar(bar)

    assert len(chart.bars()) == 1

    assert chart[1] == Bar.from_ohlcv(
        1735887540000000000, 280.0, 280.0, 280.0, 280.0, 158150
    )
    assert chart[0] == Bar.from_ohlcv(
        1735887600000000000, 279.99, 280.41, 278.11, 278.73, 5462110
    )


def test_chart_add_d():
    tf = TimeFrame.DAY
    chart = Chart.empty(IID, tf)

    bars_data = bars_data_list()
    for i in bars_data:
        bar = Bar.from_ohlcv(i[0], i[1], i[2], i[3], i[4], i[5])
        chart.add_bar(bar)

    assert len(chart.bars()) == 0

    assert chart[0] == Bar.from_ohlcv(
        1735887540000000000, 280.0, 280.41, 278.11, 278.73, 5620260
    )
