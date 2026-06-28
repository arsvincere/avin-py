# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest
from avin.domain.asset.asset_list import AssetList
from avin.domain.asset.share import Share
from avin.domain.instrument.iid import Iid
from avin.errors import InstrumentNotFoundError

# ============================================================================
# Helpers
# ============================================================================


def share(
    ticker: str = "SBER",
    figi: str = "BBG004730N88",
    name: str = "Sber",
) -> Share:
    return Share(
        Iid(
            {
                "exchange": "MOEX",
                "category": "SHARE",
                "ticker": ticker,
                "figi": figi,
                "name": name,
                "lot": "10",
                "step": "0.01",
            }
        )
    )


# ============================================================================
# Init
# ============================================================================


def test_new_asset_list_is_empty():
    assets = AssetList("test")

    assert len(assets) == 0
    assert not assets
    assert assets.is_empty
    assert assets.codes == []
    assert assets.tickers == []


def test_init_with_assets():
    sber = share("SBER", "figi_sber", "Sber")
    gazp = share("GAZP", "figi_gazp", "Gazprom")

    assets = AssetList("test", [sber, gazp])

    assert len(assets) == 2
    assert bool(assets)
    assert not assets.is_empty


# ============================================================================
# Add
# ============================================================================


def test_add_asset():
    assets = AssetList("test")
    sber = share("SBER", "figi_sber", "Sber")

    assets.add(sber)

    assert len(assets) == 1
    assert "MOEX_SHARE_SBER" in assets
    assert assets.asset("MOEX_SHARE_SBER") is sber


def test_add_duplicate_asset_raises():
    assets = AssetList("test")
    sber = share("SBER", "figi_sber", "Sber")

    assets.add(sber)

    with pytest.raises(
        ValueError, match="Asset MOEX_SHARE_SBER already exists"
    ):
        assets.add(sber)


def test_add_invalid_type_raises():
    assets = AssetList("test")

    with pytest.raises(TypeError):
        assets.add("SBER")  # type: ignore[arg-type]


# ============================================================================
# Contains
# ============================================================================


def test_contains():
    assets = AssetList("test")
    assets.add(share("SBER", "figi_sber", "Sber"))

    assert "MOEX_SHARE_SBER" in assets
    assert "MOEX_SHARE_GAZP" not in assets


def test_contains_invalid_type_raises():
    assets = AssetList("test")

    with pytest.raises(TypeError):
        _ = 123 in assets  # type: ignore[operator]


# ============================================================================
# Iteration
# ============================================================================


def test_iter():
    sber = share("SBER", "figi_sber", "Sber")
    gazp = share("GAZP", "figi_gazp", "Gazprom")

    assets = AssetList("test", [sber, gazp])

    assert list(assets) == [sber, gazp]


# ============================================================================
# Codes / tickers
# ============================================================================


def test_codes():
    assets = AssetList(
        "test",
        [
            share("SBER", "figi_sber", "Sber"),
            share("GAZP", "figi_gazp", "Gazprom"),
        ],
    )

    assert assets.codes == ["MOEX_SHARE_SBER", "MOEX_SHARE_GAZP"]


def test_tickers():
    assets = AssetList(
        "test",
        [
            share("SBER", "figi_sber", "Sber"),
            share("GAZP", "figi_gazp", "Gazprom"),
        ],
    )

    assert assets.tickers == ["SBER", "GAZP"]


# ============================================================================
# Strict access
# ============================================================================


def test_asset():
    sber = share("SBER", "figi_sber", "Sber")
    assets = AssetList("test", [sber])

    assert assets.asset("MOEX_SHARE_SBER") is sber


def test_asset_missing_raises():
    assets = AssetList("test")

    with pytest.raises(InstrumentNotFoundError):
        assets.asset("MOEX_SHARE_SBER")


def test_asset_invalid_type_raises():
    assets = AssetList("test")

    with pytest.raises(TypeError):
        assets.asset(123)  # type: ignore[arg-type]


# ============================================================================
# Find
# ============================================================================


def test_find_existing_asset():
    sber = share("SBER", "figi_sber", "Sber")
    assets = AssetList("test", [sber])

    assert assets.find("MOEX_SHARE_SBER") is sber


def test_find_missing_asset_returns_none():
    assets = AssetList("test")

    assert assets.find("MOEX_SHARE_SBER") is None


def test_find_invalid_type_raises():
    assets = AssetList("test")

    with pytest.raises(TypeError):
        assets.find(123)  # type: ignore[arg-type]


# ============================================================================
# Get item
# ============================================================================


def test_getitem():
    sber = share("SBER", "figi_sber", "Sber")
    assets = AssetList("test", [sber])

    assert assets["MOEX_SHARE_SBER"] is sber


def test_getitem_missing_raises():
    assets = AssetList("test")

    with pytest.raises(InstrumentNotFoundError):
        _ = assets["MOEX_SHARE_SBER"]


def test_getitem_invalid_type_raises():
    assets = AssetList("test")

    with pytest.raises(TypeError):
        _ = assets[123]  # type: ignore[index]


# ============================================================================
# Remove
# ============================================================================


def test_remove():
    sber = share("SBER", "figi_sber", "Sber")
    assets = AssetList("test", [sber])

    removed = assets.remove("MOEX_SHARE_SBER")

    assert removed is sber
    assert len(assets) == 0
    assert assets.is_empty


def test_remove_missing_raises():
    assets = AssetList("test")

    with pytest.raises(InstrumentNotFoundError):
        assets.remove("MOEX_SHARE_SBER")


def test_remove_invalid_type_raises():
    assets = AssetList("test")

    with pytest.raises(TypeError):
        assets.remove(123)  # type: ignore[arg-type]


# ============================================================================
# Clear
# ============================================================================


def test_clear():
    assets = AssetList(
        "test",
        [
            share("SBER", "figi_sber", "Sber"),
            share("GAZP", "figi_gazp", "Gazprom"),
        ],
    )

    assets.clear()

    assert len(assets) == 0
    assert not assets
    assert assets.is_empty
    assert assets.codes == []
    assert assets.tickers == []


# ============================================================================
# Name
# ============================================================================


def test_asset_list_has_name():
    assets = AssetList("favorites")

    assert assets.name == "favorites"


def test_init_empty_name_raises():
    with pytest.raises(ValueError, match="AssetList name is required"):
        AssetList("")
