# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

from avin import *


def test_from_str():
    info = {
        "exchange": "MOEX",
        "category": "SHARE",
        "ticker": "SBER",
        "figi": "BBG004730N88",
        "name": "Сбер Банк",
        "lot": "1",
        "step": "0.01",
    }
    iid = Iid(info)

    assert iid.info == info
    assert iid.exchange() == Exchange.MOEX
    assert iid.category() == Category.SHARE
    assert iid.ticker() == Ticker("SBER")
    assert iid.name() == "Сбер Банк"
    assert iid.lot() == 1
    assert iid.step() == 0.01
    assert iid.path() == Path("/home/alex/avin/usr/data/MOEX/SHARE/SBER")
