# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from dataclasses import dataclass

from avin.domain.asset.asset_list import AssetList
from avin.domain.data.source import Source


@dataclass(slots=True)
class AppState:
    asset_list: AssetList
    source: Source

    selected_asset_code: str | None = None
    last_message: str = "AppStarted"
