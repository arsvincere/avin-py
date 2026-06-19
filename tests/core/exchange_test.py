# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_exchange():
    moex = Exchange.MOEX
    assert moex.name == "MOEX"


def test_exchange_from_str():
    from_str = Exchange.from_str("MOEX")
    assert from_str == Exchange.MOEX
