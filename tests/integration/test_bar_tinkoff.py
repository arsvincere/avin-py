# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest
from avin.api.data import Data
from avin.domain.data.market_data import MarketData
from avin.domain.data.source import Source
from avin.errors.exceptions import DataNotFoundError
from avin.storage.iid_storage import IidStorage
from avin.storage.tinkoff.bar_downloader import TinkoffBarDownloader
from avin.utils.alias import UTC, Date, DateTime, Time, TimeDelta
from avin.utils.dt import (
    now_utc,
    ts_to_dt,
)


@pytest.mark.integration
def test_download_bar_tinkoff_year():
    code = "MOEX_SHARE_SBER"
    source = Source.TINKOFF
    md = MarketData.BAR_1M
    year = 2026

    Data.download(code, source, md, year)

    begin = DateTime(2026, 1, 1, tzinfo=UTC)
    end = DateTime(2026, 2, 1, tzinfo=UTC)

    df = Data.load(code, source, md, begin, end)

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
    df = Data.load(code, source, md, begin, end)

    assert not df.is_empty()


@pytest.mark.integration
def test_update_tinkoff_bar():
    code = "MOEX_SHARE_ABIO"
    source = Source.TINKOFF
    md = MarketData.BAR_1M

    Data.update(code, source, md)

    begin = DateTime.combine(
        Date.today() - TimeDelta(weeks=1), Time(0, 0), tzinfo=UTC
    )
    end = now_utc()
    df = Data.load(code, source, md, begin, end)
    last_dt = ts_to_dt(df.item(-1, "ts"))

    assert end - last_dt < TimeDelta(days=1)


@pytest.mark.integration
def test_delete_tinkoff_bar():
    code = "MOEX_SHARE_ABIO"
    source = Source.TINKOFF
    md = MarketData.BAR_1M

    Data.delete(code, source, md)

    begin = DateTime.min.replace(tzinfo=UTC)
    end = now_utc()
    with pytest.raises(DataNotFoundError):
        Data.load(
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

    Data.delete(code, source, md)
    Data.delete(code, source, md)
