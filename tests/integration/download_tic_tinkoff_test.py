import pytest

from avin import *
from avin.data.tinkoff.tic_downloader import TinkoffTicDownloader


@pytest.mark.integration
def test_download_tic_tinkoff_day():
    sber = AssetFactory.new("MOEX_SHARE_SBER")
    iid = sber.iid()
    md = MarketData.TIC
    year = Date.today().year
    day = Date(2026, 6, 22)

    downloader = TinkoffTicDownloader(iid, md, year)

    downloader._prepare_workdir()

    try:
        df = downloader._download_day(day)

        assert df is not None
        assert not df.is_empty()
    finally:
        downloader._clear_workdir()


@pytest.mark.slow
def test_download_tic_tinkoff_year():
    sber = AssetFactory.new("MOEX_SHARE_SBER")
    iid = sber.iid()
    md = MarketData.TIC
    year = Date.today().year

    TinkoffTicDownloader(iid, md, year).download()
