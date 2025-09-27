# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_increase_range():
    r = Range(100, 120)

    assert r.start == 100
    assert r.finish == 120

    assert r.min() == 100.0
    assert r.max() == 120.0
    assert r.mid() == 110.0

    # contains
    assert 101 in r
    assert 99 not in r
    assert 131 not in r

    # part
    half = r[50:100]
    assert str(half) == "Range[110.0, 120.0]"


def test_decrease_range():
    r = Range(120, 100)

    assert r.start == 120
    assert r.finish == 100

    assert r.min() == 100.0
    assert r.max() == 120.0
    assert r.mid() == 110.0

    assert 101 in r
    assert 99 not in r
    assert 131 not in r

    half = r[50:100]
    assert str(half) == "Range[110.0, 120.0]"


def test_abs():
    r = Range(1000, 1100)
    assert r.abs() == 100.0
    assert r.abs_n() == 0.1
    assert r.abs_p() == 10.0

    r = Range(1100, 1000)
    assert r.abs() == 100.0
    assert r.abs_n() == 0.09090909090909091
    assert r.abs_p() == 9.09


def test_delta():
    r = Range(1000, 1100)
    assert r.delta() == 100.0
    assert r.delta_n() == 0.1
    assert r.delta_p() == 10.0

    r = Range(1100, 1000)
    assert r.delta() == -100.0
    assert r.delta_n() == -0.09090909090909091
    assert r.delta_p() == -9.09
