# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import types
from pathlib import Path

import polars as pl
import pytest

from avin.core.market_data import MarketData
from avin.data.tinkoff.tic_downloader import TinkoffTicDownloader

# -------------------------
# FAKE DEPENDENCIES
# -------------------------


class FakeIid:
    def __init__(self):
        self.exchange = types.SimpleNamespace(name="MOEX")
        self.category = types.SimpleNamespace(name="STOCKS")
        self.ticker = "SBER"
        self.lot = 10
        self.path = Path("/tmp")


class FakeCmd:
    @staticmethod
    def delete_dir(_):
        pass

    @staticmethod
    def make_dirs(_):
        pass

    @staticmethod
    def make_dirs_for_file(_):
        pass

    @staticmethod
    def extract_gz(*args, **kwargs):
        pass

    @staticmethod
    def size(_):
        return 1

    @staticmethod
    def delete(_):
        pass


class FakeStorage:
    saved = []

    @staticmethod
    def save(iid, source, md, df):
        FakeStorage.saved.append(df)


# -------------------------
# FIXTURES
# -------------------------


@pytest.fixture
def downloader(monkeypatch):
    monkeypatch.setattr(
        "avin.data.tinkoff.tic_downloader.TicStorage",
        FakeStorage,
    )

    monkeypatch.setattr(
        "avin.data.tinkoff.tic_downloader.Cmd",
        FakeCmd,
    )

    FakeStorage.saved.clear()

    return TinkoffTicDownloader(
        FakeIid(),
        MarketData.TIC,
        2025,
    )


@pytest.fixture
def sample_df():
    return pl.DataFrame(
        {
            "datetime": ["2025-01-01T00:00:00"],
            "direction": ["BUY"],
            "price": [100.0],
            "lots": [2],
        }
    )


# -------------------------
# TESTS
# -------------------------


def test_build_url(downloader):
    url = downloader._build_url("2025-01-01")

    assert "history-trades" in url
    assert "instrumentId=SBER_TQBR" in url


def test_format_df(downloader, sample_df):
    df = downloader._format_df(sample_df)

    assert "ts" in df.columns
    assert "quantity" in df.columns
    assert "value" in df.columns

    assert df.height == 1
    assert df["direction"][0] == "B"


def test_fetch_archive_success(monkeypatch, downloader):
    class FakeResponse:
        def __init__(self):
            self.content = b"data"
            self.status_code = 200

        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda *a, **k: FakeResponse())

    result = downloader._fetch_archive(
        "2025-01-01",
        Path("/tmp/test.csv.gz"),
    )

    assert result is True


def test_fetch_archive_empty(monkeypatch, downloader):
    class FakeResponse:
        def __init__(self):
            self.content = b""
            self.status_code = 200

        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda *a, **k: FakeResponse())

    result = downloader._fetch_archive(
        "2025-01-01",
        Path("/tmp/test.csv.gz"),
    )

    assert result is False


def test_download_day(monkeypatch, downloader, sample_df):
    class FakeResponse:
        def __init__(self):
            self.content = b"zip"
            self.status_code = 200

        def raise_for_status(self):
            pass

    monkeypatch.setattr("requests.get", lambda *a, **k: FakeResponse())

    monkeypatch.setattr(downloader, "_extract_archive", lambda *a: None)
    monkeypatch.setattr(downloader, "_read_day", lambda *a: sample_df)
    monkeypatch.setattr(downloader, "_format_df", lambda df: df)

    df = downloader._download_day("2025-01-01")

    assert df is not None
    assert df.height == 1


def test_download_year(monkeypatch, downloader, sample_df):
    formatted = downloader._format_df(sample_df)

    monkeypatch.setattr(downloader, "_download_day", lambda day: formatted)

    downloader._download_year()

    assert len(FakeStorage.saved) > 0
