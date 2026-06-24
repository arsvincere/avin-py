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
    code = "MOEX_SHARE_ABIO"
    source = Source.TINKOFF
    md = MarketData.BAR_1M
    day = Date.today() - TimeDelta(weeks=1)
    iid = IidStorage.find_code(code, source)

    downloader = TinkoffBarDownloader(iid, md)
    downloader.download_day(day)

    begin = DateTime.combine(day, Time(0, 0), tzinfo=UTC)
    end = now_utc()
    df = DataManager.load(code, source, md, begin, end)

    assert not df.is_empty()


@pytest.mark.integration
def test_update_tinkoff_bar():
    code = "MOEX_SHARE_ABIO"
    source = Source.TINKOFF
    md = MarketData.BAR_1M

    DataManager.update(code, source, md)

    begin = DateTime.combine(
        Date.today() - TimeDelta(weeks=1), Time(0, 0), tzinfo=UTC
    )
    end = now_utc()
    df = DataManager.load(code, source, md, begin, end)
    last_dt = ts_to_dt(df.item(-1, "ts"))

    assert end - last_dt < TimeDelta(days=1)


@pytest.mark.integration
def test_delete_tinkoff_bar():
    code = "MOEX_SHARE_ABIO"
    source = Source.TINKOFF
    md = MarketData.BAR_1M

    DataManager.delete(code, source, md)
