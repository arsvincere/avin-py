import types

import polars as pl
import pytest

from avin.data.tinkoff.bar_downloader import TinkoffBarDownloader

# -------------------------
# Fakes (стабильные, простые)
# -------------------------


class FakeIid:
    def __init__(self):
        self.exchange = types.SimpleNamespace(name="MOEX")
        self.category = types.SimpleNamespace(name="STOCKS")
        self.ticker = "SBER"

    def dump_raw_info(self):
        return {"uid": "test-uid"}


class FakeMD:
    def __str__(self):
        return "1m"


# -------------------------
# Fixtures
# -------------------------


@pytest.fixture
def downloader():
    return TinkoffBarDownloader(FakeIid(), FakeMD(), 2025)


@pytest.fixture
def sample_df():
    return pl.DataFrame(
        {
            "datetime": [
                "2025-01-01T00:00:00+00:00",
                "2025-01-01T00:01:00+00:00",
            ],
            "open": [1.0, 2.0],
            "high": [1.1, 2.1],
            "low": [0.9, 1.9],
            "close": [1.05, 2.05],
            "volume": [10, 20],
        }
    )


# -------------------------
# 1. URL test (pure logic)
# -------------------------


def test_build_url(downloader):
    url = downloader._build_url()

    assert "instrumentId=test-uid" in url
    assert "year=2025" in url


# -------------------------
# 2. format function (PURE → самый важный тест)
# -------------------------


def test_format_tinkoff_df(downloader, sample_df):
    out = downloader._format_tinkoff_df(sample_df)

    assert "ts" in out.columns
    assert out.height == 2

    # проверка структуры
    assert set(out.columns) == {
        "datetime",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "ts",
    }

    # ts должен быть int
    assert out["ts"].dtype in (pl.Int64,)


# -------------------------
# 3. read_csv concat (без файлов, через mock Polars)
# -------------------------


def test_read_csv_concat(monkeypatch, downloader, sample_df):

    def fake_get_files(*args, **kwargs):
        return ["a.csv", "b.csv"]

    def fake_read_csv(*args, **kwargs):
        return sample_df

    monkeypatch.setattr(
        "avin.data.tinkoff.bar_downloader.Cmd.get_files",
        fake_get_files,
    )
    monkeypatch.setattr(
        "avin.data.tinkoff.bar_downloader.pl.read_csv",
        fake_read_csv,
    )

    df = downloader._read_tinkoff_csv_files()

    # 2 файла × 2 строки
    assert df.height == 4


# -------------------------
# 4. download flow (smoke test, без zip/FS)
# -------------------------


def test_download_flow(monkeypatch, downloader, sample_df):
    monkeypatch.setattr(
        "avin.data.tinkoff.bar_downloader.TinkoffBarDownloader._prepare_workdir",
        lambda self: None,
    )
    monkeypatch.setattr(
        "avin.data.tinkoff.bar_downloader.TinkoffBarDownloader._download_archive",
        lambda self: None,
    )

    # bypass zip + FS completely
    monkeypatch.setattr(
        "avin.data.tinkoff.bar_downloader.TinkoffBarDownloader._extract_archive",
        lambda self: None,
    )

    monkeypatch.setattr(
        "avin.data.tinkoff.bar_downloader.Cmd.get_files",
        lambda *a, **k: ["a.csv", "b.csv"],
    )

    monkeypatch.setattr(
        "avin.data.tinkoff.bar_downloader.pl.read_csv",
        lambda *a, **k: sample_df,
    )

    saved = {}

    class FakeStorage:
        @staticmethod
        def save(iid, source, md, df):
            saved["df"] = df

    monkeypatch.setattr(
        "avin.data.tinkoff.bar_downloader.BarStorage",
        FakeStorage,
    )

    downloader.download(cleanup=False)

    assert "df" in saved
    assert saved["df"].height == 4
