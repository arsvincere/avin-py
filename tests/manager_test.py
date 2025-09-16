# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

from avin import *


def test_cache():
    Manager.cache(Source.MOEX)
    Manager.cache(Source.TINKOFF)


def test_find():
    iid = Manager.find("MOEX_SHARE_SBER")

    assert iid.exchange() == Exchange.MOEX
    assert iid.category() == Category.SHARE
    assert iid.ticker() == Ticker("SBER")
    assert iid.name() == "Сбербанк"
    assert iid.lot() == 1
    assert iid.step() == 0.01
    assert iid.path() == Path("/home/alex/avin/usr/data/MOEX/SHARE/SBER")


def test_download():
    source = Source.MOEX
    iid = Manager.find("moex_share_sber")
    market_data = MarketData.BAR_D
    year = 2024

    Manager.download(source, iid, market_data, year=year)
