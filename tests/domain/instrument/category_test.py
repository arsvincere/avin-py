# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest
from avin.domain.instrument.category import Category


def test_name():
    c = Category.SHARE
    assert c.name == "SHARE"


def test_str():
    assert str(Category.SHARE) == "SHARE"


def test_from_str_upper():
    assert Category.from_str("SHARE") == Category.SHARE


def test_from_str_lower():
    assert Category.from_str("share") == Category.SHARE


def test_from_str_mixed():
    assert Category.from_str("ShArE") == Category.SHARE


def test_from_str_invalid():
    with pytest.raises(ValueError):
        Category.from_str("bitcoin")


def test_from_str_type_error():
    with pytest.raises(TypeError):
        Category.from_str(123)


def test_category_from_str_all():
    assert Category.from_str("CURRENCY") == Category.CURRENCY
    assert Category.from_str("INDEX") == Category.INDEX
    assert Category.from_str("SHARE") == Category.SHARE
    assert Category.from_str("BOND") == Category.BOND
    assert Category.from_str("FUTURE") == Category.FUTURE
    assert Category.from_str("OPTION") == Category.OPTION
    assert Category.from_str("ETF") == Category.ETF
