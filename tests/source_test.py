# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_source():
    src = Source.TINKOFF
    assert src.name == "TINKOFF"

    src = Source.MOEX
    assert src.name == "MOEX"

    from_str = Source.from_str("MOEX")
    assert from_str == Source.MOEX

    from_str = Source.from_str("TINKOFF")
    assert from_str == Source.TINKOFF
