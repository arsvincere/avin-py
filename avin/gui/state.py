# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppState:
    current_iid: str | None = None
    source: str | None = None
    timeframe: str | None = None

    ticks_loaded: int = 0
    footprint_clusters: int = 0

    selected_cluster: int | None = None
    selected_price: float | None = None

    last_message: str = "AppStarted"
