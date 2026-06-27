# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest

from avin.domain.instrument.exchange import Exchange


def test_init():
    moex = Exchange.MOEX
    assert moex.name == "MOEX"


def test_from_str_upper():
    assert Exchange.from_str("MOEX") == Exchange.MOEX


def test_from_str_lower():
    assert Exchange.from_str("moex") == Exchange.MOEX


def test_from_str_mixed():
    assert Exchange.from_str("mOeX") == Exchange.MOEX


def test_str():
    assert str(Exchange.MOEX) == "MOEX"


def test_invalid():
    with pytest.raises(ValueError):
        Exchange.from_str("NYSE")
