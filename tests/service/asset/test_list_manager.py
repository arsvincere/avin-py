# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import polars as pl
import pytest

from avin.domain.asset.asset_list import AssetList
from avin.domain.data.source import Source
from avin.domain.instrument.category import Category
from avin.errors.exceptions import DataNotFoundError
from avin.service.asset import list_manager
from avin.service.asset.list_manager import AssetListManager
from avin.storage.iid_storage import IidStorage


def _iid_rows() -> list[dict[str, str]]:
    return [
        {
            "exchange": "MOEX",
            "category": "SHARE",
            "ticker": "SBER",
            "figi": "BBG004730N88",
            "name": "Sberbank",
            "lot": "10",
            "step": "0.01",
        },
        {
            "exchange": "MOEX",
            "category": "SHARE",
            "ticker": "GAZP",
            "figi": "BBG004730RP0",
            "name": "Gazprom",
            "lot": "10",
            "step": "0.01",
        },
    ]


def test_load_favorites_loads_tinkoff_shares(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[Source, Category]] = []

    def fake_load(source: Source, category: Category) -> pl.DataFrame:
        calls.append((source, category))
        return pl.DataFrame(_iid_rows())

    monkeypatch.setattr(IidStorage, "load", fake_load)

    assets = AssetListManager.load_favorites(Source.TINKOFF)

    assert assets.name == "favorites"
    assert assets.codes == ["MOEX_SHARE_SBER", "MOEX_SHARE_GAZP"]
    assert assets.tickers == ["SBER", "GAZP"]
    assert calls == [(Source.TINKOFF, Category.SHARE)]


def test_load_favorites_rejects_non_tinkoff_source() -> None:
    with pytest.raises(NotImplementedError, match="Favorites for AVIN"):
        AssetListManager.load_favorites(Source.AVIN)


def test_load_default_loads_favorites(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = AssetList("favorites")
    calls: list[Source] = []

    monkeypatch.setattr(
        list_manager.cfg,
        "default_asset_list_name",
        "favorites",
    )
    monkeypatch.setattr(list_manager.cfg, "default_source", Source.TINKOFF)

    def fake_load_favorites(source: Source) -> AssetList:
        calls.append(source)
        return expected

    monkeypatch.setattr(AssetListManager, "load_favorites", fake_load_favorites)

    assets = AssetListManager.load_default()

    assert assets is expected
    assert calls == [Source.TINKOFF]


def test_load_default_rejects_unknown_default_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(list_manager.cfg, "default_asset_list_name", "unknown")
    monkeypatch.setattr(list_manager.cfg, "default_source", Source.TINKOFF)

    with pytest.raises(NotImplementedError, match="unknown"):
        AssetListManager.load_default()


@pytest.mark.parametrize(
    "error",
    [
        KeyError("missing config"),
        NotImplementedError("unsupported list"),
        DataNotFoundError("missing data"),
    ],
)
def test_load_default_or_empty_returns_empty_list_on_known_errors(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
) -> None:
    def fake_load_default() -> AssetList:
        raise error

    monkeypatch.setattr(AssetListManager, "load_default", fake_load_default)

    assets = AssetListManager.load_default_or_empty()

    assert assets.name == AssetListManager.EMPTY_LIST_NAME
    assert assets.is_empty


def test_load_default_or_empty_returns_loaded_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = AssetList("favorites")

    def fake_load_default() -> AssetList:
        return expected

    monkeypatch.setattr(AssetListManager, "load_default", fake_load_default)

    assets = AssetListManager.load_default_or_empty()

    assert assets is expected
