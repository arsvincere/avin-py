import pytest

from avin import *
from avin.data.tinkoff.tic_downloader import TinkoffTicDownloader


@pytest.mark.slow
def test_download_tic_tinkoff_year():
    code = "MOEX_SHARE_SBER"
    source = Source.TINKOFF
    md = MarketData.TIC
    year = 2026

    DataManager.download(code, source, md, year)

    begin = DateTime(2026, 1, 1, tzinfo=UTC)
    end = DateTime(2026, 1, 5, tzinfo=UTC)
    df = DataManager.load(code, source, md, begin, end)

    assert not df.is_empty()


@pytest.mark.integration
def test_download_tic_tinkoff_day():
    code = "MOEX_SHARE_GAZP"
    source = Source.TINKOFF
    md = MarketData.TIC
    day = Date(2026, 6, 1)
    begin = DateTime(2026, 6, 1, tzinfo=UTC)
    end = DateTime(2026, 6, 2, tzinfo=UTC)
    iid = IidStorage.find_code(code, source)

    downloader = TinkoffTicDownloader(iid, md)

    downloader.download_day(day)

    df = DataManager.load(code, source, md, begin, end)
    assert not df.is_empty()


@pytest.mark.integration
def test_update_tinkoff_tic():
    code = "MOEX_SHARE_GAZP"
    source = Source.TINKOFF
    md = MarketData.TIC

    DataManager.update(code, source, md)
