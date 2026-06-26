# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import pytest

from avin.domain.data.source import Source


def test_init():
    s = Source.MOEXALGO
    assert s.name == "MOEXALGO"


def test_source_str():
    assert str(Source.TINKOFF) == "TINKOFF"
    assert str(Source.MOEXALGO) == "MOEXALGO"


def test_source_from_str():
    assert Source.from_str("TINKOFF") is Source.TINKOFF
    assert Source.from_str("tinkoff") is Source.TINKOFF

    assert Source.from_str("MOEXALGO") is Source.MOEXALGO
    assert Source.from_str("moexalgo") is Source.MOEXALGO


def test_source_from_str_invalid_type():
    with pytest.raises(TypeError):
        Source.from_str(None)

    with pytest.raises(TypeError):
        Source.from_str(123)


def test_source_from_str_invalid_name():
    with pytest.raises(ValueError):
        Source.from_str("foo")
