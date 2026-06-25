import pytest

from avin.data.iid_storage import IidStorage
from avin.data.tinkoff.tic_downloader import TinkoffTicDownloader
from avin.domain.market_data import MarketData
from avin.domain.source import Source
from avin.errors.exceptions import DataNotFound
from avin.service.data_manager import DataManager
from avin.utils.dt import (
    UTC,
    Date,
    DateTime,
    Time,
    TimeDelta,
    now_utc,
    ts_to_dt,
)


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
    code = "MOEX_SHARE_ABIO"
    source = Source.TINKOFF
    md = MarketData.TIC
    yesterday = Date.today() - TimeDelta(days=1)
    iid = IidStorage.find_code(code, source)

    downloader = TinkoffTicDownloader(iid, md)
    downloader.download_day(yesterday)

    begin = DateTime.combine(yesterday, Time(0, 0), tzinfo=UTC)
    end = now_utc()
    df = DataManager.load(code, source, md, begin, end)

    assert not df.is_empty()


@pytest.mark.integration
def test_update_tinkoff_tic():
    code = "MOEX_SHARE_ABIO"
    source = Source.TINKOFF
    md = MarketData.TIC

    DataManager.update(code, source, md)

    begin = DateTime.combine(
        Date.today() - TimeDelta(weeks=1), Time(0, 0), tzinfo=UTC
    )
    end = now_utc()
    df = DataManager.load(code, source, md, begin, end)
    last_dt = ts_to_dt(df.item(-1, "ts"))

    assert end - last_dt < TimeDelta(days=1)


@pytest.mark.integration
def test_delete_tinkoff_tic():
    code = "MOEX_SHARE_ABIO"
    source = Source.TINKOFF
    md = MarketData.TIC

    DataManager.delete(code, source, md)

    begin = DateTime.min.replace(tzinfo=UTC)
    end = now_utc()
    with pytest.raises(DataNotFound):
        DataManager.load(
            code,
            source,
            md,
            begin,
            end,
        )


@pytest.mark.integration
def test_delete_tinkoff_bar_idempotent():
    code = "MOEX_SHARE_ABIO"
    source = Source.TINKOFF
    md = MarketData.BAR_1M

    DataManager.delete(code, source, md)
    DataManager.delete(code, source, md)
