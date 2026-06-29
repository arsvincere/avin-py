# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from avin.domain.asset.base_asset import BaseAsset
from avin.domain.instrument.category import Category
from avin.domain.instrument.iid import Iid


class Share(BaseAsset):
    def __init__(self, iid: Iid) -> None:
        if iid.category != Category.SHARE:
            raise ValueError(f"Expected SHARE category, got {iid.category}")

        super().__init__(iid)
