# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_ticker():
    t1 = Ticker("sber")
    t2 = Ticker("SBER")

    assert t1.name == "SBER"
    assert str(t1) == "SBER"
    assert t1 == t2
