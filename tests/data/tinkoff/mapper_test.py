# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin.domain.instrument.category import Category
from avin.storage.tinkoff.mapper import (
    category_to_avin_category,
    exchange_to_avin_exchange,
)


def test_exchange_moex():
    assert exchange_to_avin_exchange("MOEX") == "MOEX"
    assert exchange_to_avin_exchange("MOEX_PLUS") == "MOEX"
    assert exchange_to_avin_exchange("MOEX_WEEKEND") == "MOEX"


def test_exchange_spb():
    assert exchange_to_avin_exchange("SPB") == "SPB"
    assert exchange_to_avin_exchange("SPB_RU_MORNING") == "SPB"


def test_exchange_forts():
    assert exchange_to_avin_exchange("FORTS") == "MOEX"
    assert exchange_to_avin_exchange("FORTS_EVENING") == "MOEX"


def test_exchange_fx():
    assert exchange_to_avin_exchange("FX") == "MOEX"


def test_exchange_case_insensitive():
    assert exchange_to_avin_exchange("moex_plus") == "MOEX"
    assert exchange_to_avin_exchange("spb_ru_morning") == "SPB"
    assert exchange_to_avin_exchange("forts_evening") == "MOEX"


def test_exchange_unknown():
    assert exchange_to_avin_exchange("UNKNOWN") == ""
    assert exchange_to_avin_exchange("LSE_MORNING") == ""
    assert exchange_to_avin_exchange("otc_ncc") == ""


def test_category_share():
    assert category_to_avin_category("shares") is Category.SHARE


def test_category_bond():
    assert category_to_avin_category("bonds") is Category.BOND


def test_category_future():
    assert category_to_avin_category("futures") is Category.FUTURE


def test_category_currency():
    assert category_to_avin_category("currencies") is Category.CURRENCY


def test_category_unknown():
    try:
        category_to_avin_category("crypto")
        assert False
    except KeyError:
        pass
