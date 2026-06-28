# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass

from avin.domain.asset.asset_list import AssetList


@dataclass(slots=True)
class AppState:
    asset_list: AssetList
    current_asset_code: str | None = None

    source: str | None = None
    timeframe: str | None = None

    ticks_loaded: int = 0
    footprint_clusters: int = 0

    selected_cluster: int | None = None
    selected_price: float | None = None

    last_message: str = "AppStarted"
