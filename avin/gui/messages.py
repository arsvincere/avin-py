# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppStarted:
    pass


@dataclass(frozen=True, slots=True)
class SelectAsset:
    code: str


@dataclass(frozen=True, slots=True)
class SelectTimeframe:
    timeframe: str


@dataclass(frozen=True, slots=True)
class SelectCluster:
    cluster_index: int


@dataclass(frozen=True, slots=True)
class SelectPrice:
    price: float


@dataclass(frozen=True, slots=True)
class ClearSelection:
    pass


type Message = (
    AppStarted
    | SelectAsset
    | SelectTimeframe
    | SelectCluster
    | SelectPrice
    | ClearSelection
)
