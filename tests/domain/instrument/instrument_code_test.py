# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest

from avin.domain.instrument.category import Category
from avin.domain.instrument.exchange import Exchange
from avin.domain.instrument.code import parse_code


def test_parse_code():
    exchange, category, ticker = parse_code("MOEX_SHARE_SBER")

    assert exchange is Exchange.MOEX
    assert category is Category.SHARE
    assert ticker == "SBER"


def test_parse_code_case_insensitive():
    exchange, category, ticker = parse_code("moEX_sHAre_sBEr")

    assert exchange is Exchange.MOEX
    assert category is Category.SHARE
    assert ticker == "SBER"


def test_parse_code_invalid_format():
    with pytest.raises(ValueError):
        parse_code("bugaga")


def test_parse_code_invalid_exchange():
    with pytest.raises(ValueError):
        parse_code("****_SHARE_SBER")


def test_parse_code_invalid_category():
    with pytest.raises(ValueError):
        parse_code("MOEX_####_SBER")
