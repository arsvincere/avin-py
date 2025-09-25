# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_terminal():
    t = Terminal()

    assert t.asset_list.name == "xxx"
    assert t.current_asset.ticker() == Ticker("AFKS")
