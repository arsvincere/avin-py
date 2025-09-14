#!/usr/bin/env python3
# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from datetime import UTC
from datetime import datetime as DateTime

from avin import *


def test_from_ohlcv():
    bar = Bar.from_ohlcv(100500, 100.0, 102.0, 99.5, 101.0, 500)

    assert bar.ts == 100500
    assert bar.o == 100.0
    assert bar.h == 102.0
    assert bar.l == 99.5
    assert bar.c == 101.0
    assert bar.v == 500


def test_bar_str():
    bar = Bar.from_ohlcv(100500, 100.0, 102.0, 99.5, 101.0, 500)

    expected = (
        "Bar: dt=1970-01-01 03:00:00 o=100.0 h=102.0 l=99.5 c=101.0 v=500"
    )

    assert str(bar) == expected


def test_contains():
    bar = Bar.from_ohlcv(100500, 100.0, 102.0, 99.5, 101.0, 500)

    assert 100.5 in bar
    assert 99 not in bar
    assert 102.1 not in bar


def test_join():
    b1 = Bar.from_ohlcv(100500, 100.0, 102.0, 99.0, 101.0, 500)
    b2 = Bar.from_ohlcv(100600, 101.1, 103.3, 101.0, 102.5, 600)

    bar = Bar.join(b1, b2)

    assert bar.ts == 100500
    assert bar.o == 100.0
    assert bar.h == 103.3
    assert bar.l == 99.0
    assert bar.c == 102.5
    assert bar.v == 1100


def test_dt():
    b1 = Bar.from_ohlcv(0, 100.0, 102.0, 99.0, 101.0, 500)
    dt = DateTime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)

    assert b1.dt() == dt


def test_dt_local():
    dt = DateTime(2025, 9, 14, 15, 50, 14, tzinfo=UTC)
    ts = dt_to_ts(dt)
    bar = Bar.from_ohlcv(ts, 100.0, 102.0, 99.0, 101.0, 500)

    assert bar.dt_local() == "2025-09-14 18:50:14"


def test_kind():
    bar = Bar.from_ohlcv(0, 100.0, 102.0, 99.0, 101.0, 500)

    assert bar.kind() == Bar.Kind.BULL
    assert bar.kind() != Bar.Kind.BEAR
    assert bar.kind() != Bar.Kind.DODJI


def test_bear_bull_dodji():
    bar = Bar.from_ohlcv(0, 100.0, 102.0, 99.0, 101.0, 500)

    assert bar.is_bull()
    assert not bar.is_bear()
    assert not bar.is_dodji()


def test_full():
    bar = Bar.from_ohlcv(0, 100.0, 102.0, 99.0, 101.0, 500)

    assert bar.full() == Range(99.0, 102.0)


def test_body():
    bar = Bar.from_ohlcv(0, 100.0, 102.0, 99.0, 101.0, 500)

    assert bar.body() == Range(100.0, 101.0)


def test_upper():
    bar = Bar.from_ohlcv(0, 100.0, 102.0, 99.0, 101.0, 500)

    assert bar.upper() == Range(101.0, 102.0)


def test_lower():
    bar = Bar.from_ohlcv(0, 100.0, 102.0, 99.0, 101.0, 500)

    assert bar.lower() == Range(99.0, 100.0)
