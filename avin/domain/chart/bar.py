# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass


@dataclass
class Bar(frozen=True):
    ts: int
    open: float
    high: float
    low: float
    close: float
    vol: int
