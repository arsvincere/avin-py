# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppStarted:
    pass


@dataclass(frozen=True, slots=True)
class SelectIid:
    iid: str


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
    | SelectIid
    | SelectTimeframe
    | SelectCluster
    | SelectPrice
    | ClearSelection
)
