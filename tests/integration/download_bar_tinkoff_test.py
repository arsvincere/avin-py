import pytest

from avin import *
from avin.data.tinkoff.bar_downloader import TinkoffBarDownloader


@pytest.mark.integration
def test_download_bar_tinkoff_year():
    code = "MOEX_SHARE_SBER"
    source = Source.TINKOFF
    md = MarketData.BAR_1M
    year = 2026

    DataManager.download(code, source, md, year)

    begin = DateTime(2026, 1, 1, tzinfo=UTC)
    end = DateTime(2026, 2, 1, tzinfo=UTC)

    df = DataManager.load(code, source, md, begin, end)

    assert not df.is_empty()


@pytest.mark.integration
def test_download_bar_tinkoff_day():
    code = "MOEX_SHARE_GAZP"
    source = Source.TINKOFF
    md = MarketData.BAR_1M
    day = Date(2026, 6, 1)
    begin = DateTime(2026, 6, 1, tzinfo=UTC)
    end = DateTime(2026, 6, 2, tzinfo=UTC)
    iid = IidStorage.find_code(code, source)

    downloader = TinkoffBarDownloader(iid, md)
    downloader.download_day(day)

    df = DataManager.load(code, source, md, begin, end)
    assert not df.is_empty()
