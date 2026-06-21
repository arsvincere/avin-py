# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

from avin import *


def test_iid():
    info = {
        "exchange": "MOEX",
        "category": "SHARE",
        "ticker": "SBER",
        "figi": "BBG004730N88",
        "name": "Сбер Банк",
        "lot": "10",
        "step": "0.01",
        "uid": "e6123145-9665-43e0-8413-cd61b8aa9b13",
    }

    iid = Iid(info)
    assert str(iid) == "MOEX_SHARE_SBER"
    assert iid.exchange() == Exchange.MOEX
    assert iid.category() == Category.SHARE
    assert iid.ticker() == "SBER"
    assert iid.figi() == "BBG004730N88"
    assert iid.name() == "Сбер Банк"
    assert iid.lot() == 10
    assert iid.step() == 0.01
    assert iid.info()["uid"] == "e6123145-9665-43e0-8413-cd61b8aa9b13"
    assert iid.path() == Path("/home/alex/trading/data/MOEX/SHARE/SBER")
