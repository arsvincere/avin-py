# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import pytest

from avin.core.category import Category
from avin.core.exchange import Exchange
from avin.core.instrument_code import parse_code


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
