# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================


import polars as pl
import pytest

from avin.domain.instrument.category import Category
from avin.domain.instrument.exchange import Exchange
from avin.domain.instrument.iid import Iid


@pytest.fixture
def raw_info():
    return {
        "exchange": "MOEX",
        "category": "SHARE",
        "ticker": "SBER",
        "figi": "BBG004730N88",
        "name": "Сбер Банк",
        "lot": "10",
        "step": "0.01",
        "uid": "e6123145-9665-43e0-8413-cd61b8aa9b13",
    }


def test_init(raw_info):
    iid = Iid(raw_info)

    assert iid.exchange == Exchange.MOEX
    assert iid.category == Category.SHARE
    assert iid.ticker == "SBER"
    assert iid.figi == "BBG004730N88"
    assert iid.name == "Сбер Банк"
    assert iid.lot == 10
    assert iid.step == 0.01
    assert (
        iid.dump_raw_info()["uid"] == "e6123145-9665-43e0-8413-cd61b8aa9b13"
    )


def test_str(raw_info):
    iid = Iid(raw_info)

    assert str(iid) == "MOEX_SHARE_SBER"


def test_eq(raw_info):
    iid1 = Iid(raw_info)

    iid2 = Iid(raw_info.copy())

    assert iid1 == iid2


def test_not_eq(raw_info):
    raw2 = raw_info.copy()
    raw2["figi"] = "OTHER"

    iid1 = Iid(raw_info)
    iid2 = Iid(raw2)

    assert iid1 != iid2


def test_hash(raw_info):
    iid1 = Iid(raw_info)
    iid2 = Iid(raw_info.copy())

    assert hash(iid1) == hash(iid2)


@pytest.mark.parametrize(
    "key",
    [
        "exchange",
        "category",
        "ticker",
        "figi",
        "name",
        "lot",
        "step",
    ],
)
def test_missing_field(raw_info, key):
    raw = raw_info.copy()
    del raw[key]

    with pytest.raises(ValueError):
        Iid(raw)


@pytest.mark.parametrize(
    "key",
    [
        "exchange",
        "category",
        "ticker",
        "figi",
        "name",
        "lot",
        "step",
    ],
)
def test_empty_field(raw_info, key):
    raw = raw_info.copy()
    raw[key] = ""

    with pytest.raises(ValueError):
        Iid(raw)


def test_dump_raw_info_copy(raw_info):
    iid = Iid(raw_info)

    dumped = iid.dump_raw_info()

    dumped["ticker"] = "GAZP"

    assert iid.ticker == "SBER"


def test_from_df(raw_info):
    df = pl.DataFrame([raw_info])

    iid = Iid.from_df(df)

    assert iid.ticker == "SBER"


def test_from_df_invalid_rows(raw_info):
    df = pl.DataFrame([raw_info, raw_info])

    with pytest.raises(ValueError):
        Iid.from_df(df)
