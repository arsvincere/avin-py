# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_name():
    moex = Exchange.MOEX
    assert moex.name == "MOEX"


def test_from_str():
    assert Exchange.from_str("MOEX") == Exchange.MOEX
