# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import polars as pl
import pytest

from avin.core.category import Category
from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.data.tinkoff.source_tinkoff import SourceTinkoff


def test_available_market_data():
    result = SourceTinkoff.available_market_data()

    assert MarketData.BAR_1M in result
    assert MarketData.TIC in result
    assert len(result) == 2


def test_download_bar(monkeypatch):
    called = False

    class FakeDownloader:
        def __init__(self, iid, md, year):
            pass

        def download(self):
            nonlocal called
            called = True

    monkeypatch.setattr(
        "avin.data.tinkoff.source_tinkoff.TinkoffBarDownloader",
        FakeDownloader,
    )

    SourceTinkoff.download(
        iid=object(),
        md=MarketData.BAR_1M,
        year=2025,
    )

    assert called is True


def test_download_tic(monkeypatch):
    called = False

    class FakeDownloader:
        def __init__(self, iid, md, year):
            pass

        def download(self):
            nonlocal called
            called = True

    monkeypatch.setattr(
        "avin.data.tinkoff.source_tinkoff.TinkoffTicDownloader",
        FakeDownloader,
    )

    SourceTinkoff.download(
        iid=object(),
        md=MarketData.TIC,
        year=2025,
    )

    assert called is True


def test_download_unknown_market_data():
    with pytest.raises(ValueError):
        SourceTinkoff.download(
            iid=object(),
            md=None,
            year=2025,
        )


def test_cache_saves_dataframe(monkeypatch):
    saved = {}

    df = pl.DataFrame(
        {
            "ticker": ["SBER"],
        }
    )

    monkeypatch.setattr(
        SourceTinkoff,
        "_SourceTinkoff__get_favorite_shares",
        classmethod(lambda cls: ["dummy"]),
    )

    monkeypatch.setattr(
        SourceTinkoff,
        "_SourceTinkoff__get_shares_info",
        classmethod(lambda cls, shares: df),
    )

    def fake_save(source, category, dataframe):
        saved["source"] = source
        saved["category"] = category
        saved["df"] = dataframe

    monkeypatch.setattr(
        "avin.data.tinkoff.source_tinkoff.IidStorage.save",
        fake_save,
    )

    SourceTinkoff.cache()

    assert saved["source"] == Source.TINKOFF
    assert saved["category"] == Category.SHARE
    assert saved["df"].equals(df)
