# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest

from avin.domain.common.price_range import PriceRange


def test_init():
    r = PriceRange(100.0, 120.0)

    assert r.start == 100.0
    assert r.finish == 120.0


def test_init_zero_start():
    with pytest.raises(ValueError):
        PriceRange(0.0, 100.0)


def test_init_zero_finish():
    with pytest.raises(ValueError):
        PriceRange(100.0, 0.0)


def test_str():
    r = PriceRange(100.0, 120.0)

    assert str(r) == "[100.0, 120.0]"


def test_repr():
    r = PriceRange(100.0, 120.0)

    assert repr(r) == "PriceRange(100.0, 120.0)"


def test_eq():
    a = PriceRange(100.0, 120.0)
    b = PriceRange(100.0, 120.0)

    assert a == b


def test_not_eq():
    a = PriceRange(100.0, 120.0)
    b = PriceRange(120.0, 100.0)

    assert a != b


def test_hash():
    a = PriceRange(100.0, 120.0)
    b = PriceRange(100.0, 120.0)

    assert hash(a) == hash(b)


def test_low_increase():
    r = PriceRange(100.0, 120.0)

    assert r.low == 100.0


def test_low_decrease():
    r = PriceRange(120.0, 100.0)

    assert r.low == 100.0


def test_high_increase():
    r = PriceRange(100.0, 120.0)

    assert r.high == 120.0


def test_high_decrease():
    r = PriceRange(120.0, 100.0)

    assert r.high == 120.0


def test_mid():
    r = PriceRange(100.0, 120.0)

    assert r.mid == 110.0


def test_abs():
    r = PriceRange(100.0, 120.0)

    assert r.abs == 20.0


def test_abs_decrease():
    r = PriceRange(120.0, 100.0)

    assert r.abs == 20.0


def test_abs_n():
    r = PriceRange(100.0, 120.0)

    assert r.abs_n == pytest.approx(20.0 / 120.0)


def test_abs_p():
    r = PriceRange(100.0, 120.0)

    assert r.abs_p == 16.67


def test_delta_positive():
    r = PriceRange(100.0, 120.0)

    assert r.delta == 20.0


def test_delta_negative():
    r = PriceRange(120.0, 100.0)

    assert r.delta == -20.0


def test_delta_n_positive():
    r = PriceRange(100.0, 120.0)

    assert r.delta_n == pytest.approx(0.2)


def test_delta_n_negative():
    r = PriceRange(120.0, 100.0)

    assert r.delta_n == pytest.approx(-20.0 / 120.0)


def test_delta_p_positive():
    r = PriceRange(100.0, 120.0)

    assert r.delta_p == 20.0


def test_delta_p_negative():
    r = PriceRange(120.0, 100.0)

    assert r.delta_p == -16.67


def test_contains_inside():
    r = PriceRange(100.0, 120.0)

    assert r.contains(110.0)


def test_contains_low_border():
    r = PriceRange(100.0, 120.0)

    assert r.contains(100.0)


def test_contains_high_border():
    r = PriceRange(100.0, 120.0)

    assert r.contains(120.0)


def test_contains_outside():
    r = PriceRange(100.0, 120.0)

    assert not r.contains(130.0)


def test_is_increase():
    r = PriceRange(100.0, 120.0)

    assert r.is_increase()


def test_is_decrease():
    r = PriceRange(120.0, 100.0)

    assert r.is_decrease()


def test_not_increase():
    r = PriceRange(120.0, 100.0)

    assert not r.is_increase()


def test_not_decrease():
    r = PriceRange(100.0, 120.0)

    assert not r.is_decrease()


def test_contract():
    r = PriceRange(100.0, 120.0)

    assert r.low <= r.mid <= r.high
