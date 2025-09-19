# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from datetime import UTC
from datetime import datetime as DateTime
from pathlib import Path

import pytest

from avin import *

pytestmark = pytest.mark.skip()


def test_cache():
    Manager.cache(Source.MOEX)
    Manager.cache(Source.TINKOFF)


def test_find():
    iid = Manager.find("MOEX_SHARE_SBER")

    assert iid.exchange() == Exchange.MOEX
    assert iid.category() == Category.SHARE
    assert iid.ticker() == Ticker("SBER")
    assert iid.name() == "Сбер Банк"
    assert iid.lot() == 1
    assert iid.step() == 0.01
    assert iid.path() == Path("/home/alex/avin/usr/data/MOEX/SHARE/SBER")


def test_download():
    source = Source.MOEX
    iid = Manager.find("moex_share_sber")
    market_data = MarketData.BAR_D
    year = 2024

    Manager.download(source, iid, market_data, year=year)


def test_update():
    source = Source.MOEX
    iid = Manager.find("moex_share_sber")
    market_data = MarketData.BAR_D

    Manager.update(source, iid, market_data)


def test_load_1m():
    iid = Manager.find("moex_share_sber")
    market_data = MarketData.BAR_1M
    begin = str_to_utc("2023-08-01 10:00")
    end = str_to_utc("2023-08-01 11:00")

    df = Manager.load(iid, market_data, begin, end)

    begin_ts = df.item(0, "ts_nanos")
    end_ts = df.item(-1, "ts_nanos")
    assert begin == ts_to_dt(begin_ts)
    assert end - ONE_MINUTE == ts_to_dt(end_ts)


def test_load_10m():
    iid = Manager.find("moex_share_sber")
    market_data = MarketData.BAR_10M
    begin = str_to_utc("2023-08-01 10:00")
    end = str_to_utc("2023-08-01 11:00")

    df = Manager.load(iid, market_data, begin, end)

    begin_ts = df.item(0, "ts_nanos")
    end_ts = df.item(-1, "ts_nanos")
    assert begin == ts_to_dt(begin_ts)
    assert end - TEN_MINUTE == ts_to_dt(end_ts)


def test_load_1h():
    iid = Manager.find("moex_share_sber")
    market_data = MarketData.BAR_1H
    begin = str_to_utc("2023-08-01 10:00")
    end = str_to_utc("2023-08-01 13:00")

    df = Manager.load(iid, market_data, begin, end)

    begin_ts = df.item(0, "ts_nanos")
    end_ts = df.item(-1, "ts_nanos")
    assert begin == ts_to_dt(begin_ts)
    assert end - ONE_HOUR == ts_to_dt(end_ts)


def test_load_d():
    iid = Manager.find("moex_share_sber")
    market_data = MarketData.BAR_D
    begin = str_to_utc("2023-08-01 00:00")
    end = str_to_utc("2023-09-01 00:00")

    df = Manager.load(iid, market_data, begin, end)

    begin_ts = df.item(0, "ts_nanos")
    end_ts = df.item(-1, "ts_nanos")

    assert begin == ts_to_dt(begin_ts)
    assert end - ONE_DAY == ts_to_dt(end_ts)


def test_load_w():
    iid = Manager.find("moex_share_sber")
    market_data = MarketData.BAR_W
    begin = str_to_utc("2024-01-01 00:00")
    end = str_to_utc("2025-01-01 00:00")

    df = Manager.load(iid, market_data, begin, end)

    begin_ts = df.item(0, "ts_nanos")
    end_ts = df.item(-1, "ts_nanos")

    assert ts_to_dt(begin_ts) == DateTime(2023, 12, 31, 21, 0, 0, tzinfo=UTC)
    assert ts_to_dt(end_ts) == DateTime(2024, 12, 29, 21, 0, 0, tzinfo=UTC)


def test_load_m():
    iid = Manager.find("moex_share_sber")
    market_data = MarketData.BAR_M
    begin = str_to_utc("2024-01-01 00:00")
    end = str_to_utc("2025-01-01 00:00")

    df = Manager.load(iid, market_data, begin, end)

    begin_ts = df.item(0, "ts_nanos")
    end_ts = df.item(-1, "ts_nanos")

    assert ts_to_dt(begin_ts) == DateTime(2023, 12, 31, 21, 0, 0, tzinfo=UTC)
    assert ts_to_dt(end_ts) == DateTime(2024, 11, 30, 21, 0, 0, tzinfo=UTC)
