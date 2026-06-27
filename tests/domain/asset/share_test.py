# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest
from avin.domain.asset.asset import Asset
from avin.domain.asset.share import Share
from avin.domain.instrument.category import Category
from avin.domain.instrument.exchange import Exchange
from avin.domain.instrument.iid import Iid

# ============================================================================
# Helpers
# ============================================================================


def iid(
    category: str = "SHARE",
    ticker: str = "SBER",
    figi: str = "BBG004730N88",
    name: str = "Sber",
) -> Iid:
    return Iid(
        {
            "exchange": "MOEX",
            "category": category,
            "ticker": ticker,
            "figi": figi,
            "name": name,
            "lot": "10",
            "step": "0.01",
        }
    )


# ============================================================================
# Init
# ============================================================================


def test_share_is_asset():
    share = Share(iid())

    assert isinstance(share, Asset)


def test_share_accepts_share_iid():
    share = Share(iid())

    assert share.category == Category.SHARE
    assert share.code == "MOEX_SHARE_SBER"
    assert share.ticker == "SBER"
    assert share.figi == "BBG004730N88"
    assert share.name == "Sber"
    assert share.exchange == Exchange.MOEX
    assert share.lot == 10
    assert share.step == 0.01


def test_share_rejects_non_share_iid():
    with pytest.raises(ValueError, match="Expected SHARE category"):
        Share(iid(category="FUTURE"))


# ============================================================================
# String / identity
# ============================================================================


def test_str_returns_code():
    share = Share(iid())

    assert str(share) == "MOEX_SHARE_SBER"


def test_hash_uses_figi():
    share = Share(iid())

    assert hash(share) == hash("BBG004730N88")


def test_eq_same_figi():
    sber = Share(iid(ticker="SBER", figi="same_figi", name="Sber"))
    gazp = Share(iid(ticker="GAZP", figi="same_figi", name="Gazprom"))

    assert sber == gazp


def test_eq_different_figi():
    sber = Share(iid(ticker="SBER", figi="figi_sber", name="Sber"))
    gazp = Share(iid(ticker="GAZP", figi="figi_gazp", name="Gazprom"))

    assert sber != gazp


def test_eq_other_type():
    share = Share(iid())

    assert share != "SBER"
