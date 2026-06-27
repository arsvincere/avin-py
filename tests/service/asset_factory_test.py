# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import avin.service.asset_factory as asset_factory_module
import polars as pl
import pytest
from avin.domain.asset.share import Share
from avin.domain.instrument.category import Category
from avin.domain.instrument.exchange import Exchange
from avin.errors import InstrumentNotFoundError
from avin.service.asset_factory import AssetFactory

# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────


def shares_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "exchange": ["MOEX", "MOEX"],
            "category": ["SHARE", "SHARE"],
            "ticker": ["SBER", "GAZP"],
            "figi": ["figi_sber", "figi_gazp"],
            "name": ["Sber", "Gazprom"],
            "lot": ["10", "10"],
            "step": ["0.01", "0.01"],
        }
    )


def set_cached_load_shares(df: pl.DataFrame):
    original = asset_factory_module._cached_load_shares

    def fake_cached_load_shares() -> pl.DataFrame:
        return df

    asset_factory_module._cached_load_shares = fake_cached_load_shares
    AssetFactory.new.cache_clear()

    return original


def restore_cached_load_shares(original) -> None:
    asset_factory_module._cached_load_shares = original
    AssetFactory.new.cache_clear()


# ────────────────────────────────────────────────────────────────────────────
# New
# ────────────────────────────────────────────────────────────────────────────


def test_new_returns_share():
    original = set_cached_load_shares(shares_df())

    try:
        asset = AssetFactory.new("MOEX_SHARE_SBER")

        assert isinstance(asset, Share)
        assert asset.code == "MOEX_SHARE_SBER"
        assert asset.exchange == Exchange.MOEX
        assert asset.category == Category.SHARE
        assert asset.ticker == "SBER"
        assert asset.figi == "figi_sber"
        assert asset.name == "Sber"
        assert asset.lot == 10
        assert asset.step == 0.01

    finally:
        restore_cached_load_shares(original)


def test_new_returns_correct_share():
    original = set_cached_load_shares(shares_df())

    try:
        asset = AssetFactory.new("MOEX_SHARE_GAZP")

        assert isinstance(asset, Share)
        assert asset.code == "MOEX_SHARE_GAZP"
        assert asset.ticker == "GAZP"
        assert asset.figi == "figi_gazp"
        assert asset.name == "Gazprom"

    finally:
        restore_cached_load_shares(original)


def test_new_missing_instrument_raises():
    original = set_cached_load_shares(shares_df())

    try:
        with pytest.raises(InstrumentNotFoundError):
            AssetFactory.new("MOEX_SHARE_LKOH")

    finally:
        restore_cached_load_shares(original)


def test_new_unsupported_category_raises():
    AssetFactory.new.cache_clear()

    with pytest.raises(NotImplementedError):
        AssetFactory.new("MOEX_FUTURE_SiZ5")

    AssetFactory.new.cache_clear()


# ────────────────────────────────────────────────────────────────────────────
# Cache
# ────────────────────────────────────────────────────────────────────────────


def test_new_is_cached():
    calls = 0
    df = shares_df()
    original = asset_factory_module._cached_load_shares

    def fake_cached_load_shares() -> pl.DataFrame:
        nonlocal calls
        calls += 1
        return df

    asset_factory_module._cached_load_shares = fake_cached_load_shares
    AssetFactory.new.cache_clear()

    try:
        first = AssetFactory.new("MOEX_SHARE_SBER")
        second = AssetFactory.new("MOEX_SHARE_SBER")

        assert first is second
        assert calls == 1

    finally:
        restore_cached_load_shares(original)


def test_new_cache_is_separated_by_code():
    original = set_cached_load_shares(shares_df())

    try:
        sber = AssetFactory.new("MOEX_SHARE_SBER")
        gazp = AssetFactory.new("MOEX_SHARE_GAZP")

        assert sber is not gazp
        assert sber.ticker == "SBER"
        assert gazp.ticker == "GAZP"

    finally:
        restore_cached_load_shares(original)
