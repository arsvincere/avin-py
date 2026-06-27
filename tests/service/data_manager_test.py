 # ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import polars as pl
import pytest

import avin.service.asset_factory as asset_factory_module
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


class FakeIidStorage:
    calls = 0

    @classmethod
    def load(cls, source, category):
        cls.calls += 1
        return shares_df()


def patch_iid_storage():
    original = asset_factory_module.IidStorage

    asset_factory_module.IidStorage = FakeIidStorage
    FakeIidStorage.calls = 0
    AssetFactory.new.cache_clear()
    asset_factory_module._cached_load_shares.cache_clear()

    return original


def restore_iid_storage(original) -> None:
    asset_factory_module.IidStorage = original
    AssetFactory.new.cache_clear()
    asset_factory_module._cached_load_shares.cache_clear()


# ────────────────────────────────────────────────────────────────────────────
# New
# ────────────────────────────────────────────────────────────────────────────


def test_new_returns_share():
    original = patch_iid_storage()

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
        restore_iid_storage(original)


def test_new_returns_correct_share():
    original = patch_iid_storage()

    try:
        asset = AssetFactory.new("MOEX_SHARE_GAZP")

        assert isinstance(asset, Share)
        assert asset.code == "MOEX_SHARE_GAZP"
        assert asset.ticker == "GAZP"
        assert asset.figi == "figi_gazp"
        assert asset.name == "Gazprom"

    finally:
        restore_iid_storage(original)


def test_new_missing_instrument_raises():
    original = patch_iid_storage()

    try:
        with pytest.raises(InstrumentNotFoundError):
            AssetFactory.new("MOEX_SHARE_LKOH")

    finally:
        restore_iid_storage(original)


def test_new_unsupported_category_raises():
    AssetFactory.new.cache_clear()

    with pytest.raises(NotImplementedError):
        AssetFactory.new("MOEX_FUTURE_SiZ5")

    AssetFactory.new.cache_clear()


# ────────────────────────────────────────────────────────────────────────────
# Cache
# ────────────────────────────────────────────────────────────────────────────


def test_new_is_cached():
    original = patch_iid_storage()

    try:
        first = AssetFactory.new("MOEX_SHARE_SBER")
        second = AssetFactory.new("MOEX_SHARE_SBER")

        assert first is second
        assert FakeIidStorage.calls == 1

    finally:
        restore_iid_storage(original)


def test_new_cache_is_separated_by_code():
    original = patch_iid_storage()

    try:
        sber = AssetFactory.new("MOEX_SHARE_SBER")
        gazp = AssetFactory.new("MOEX_SHARE_GAZP")

        assert sber is not gazp
        assert sber.ticker == "SBER"
        assert gazp.ticker == "GAZP"
        assert FakeIidStorage.calls == 1

    finally:
        restore_iid_storage(original)
