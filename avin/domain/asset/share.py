# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================


from avin.domain.asset.asset import Asset
from avin.domain.instrument.category import Category
from avin.domain.instrument.iid import Iid


class Share(Asset):
    def __init__(self, iid: Iid) -> None:
        if iid.category != Category.SHARE:
            raise ValueError(iid)

        super().__init__(iid)
