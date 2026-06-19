# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_source():
    s = Source.MOEX
    assert s.name == "MOEX"


def test_source_from_str():
    from_str = Source.from_str("MOEX")
    assert from_str == Source.MOEX

    from_str = Source.from_str("TINKOFF")
    assert from_str == Source.TINKOFF
