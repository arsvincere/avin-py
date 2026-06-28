# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest
from avin.domain.chart.bar_kind import BarKind


def test_bar_kind_values() -> None:
    assert BarKind.BULL == 1
    assert BarKind.DOJI == 0
    assert BarKind.BEAR == -1


def test_bar_kind_str() -> None:
    assert str(BarKind.BULL) == "BULL"
    assert str(BarKind.DOJI) == "DOJI"
    assert str(BarKind.BEAR) == "BEAR"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("BULL", BarKind.BULL),
        ("DOJI", BarKind.DOJI),
        ("BEAR", BarKind.BEAR),
        ("bull", BarKind.BULL),
        ("doji", BarKind.DOJI),
        ("bear", BarKind.BEAR),
    ],
)
def test_bar_kind_from_str(value: str, expected: BarKind) -> None:
    assert BarKind.from_str(value) is expected


def test_bar_kind_from_str_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        BarKind.from_str(1)  # type: ignore[arg-type]


def test_bar_kind_from_str_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="Unknown bar kind 'HAMMER'"):
        BarKind.from_str("HAMMER")
