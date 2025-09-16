# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin import *


def test_from_str():
    assert Category.from_str("CURRENCY") == Category.CURRENCY
    assert Category.from_str("INDEX") == Category.INDEX
    assert Category.from_str("SHARE") == Category.SHARE
    assert Category.from_str("BOND") == Category.BOND
    assert Category.from_str("FUTURE") == Category.FUTURE
    assert Category.from_str("OPTION") == Category.OPTION
    assert Category.from_str("ETF") == Category.ETF
