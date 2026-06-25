# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================


from avin.domain.asset.asset import Asset
from avin.domain.instrument.category import Category
from avin.domain.instrument.exchange import Exchange
from avin.domain.instrument.iid import Iid


class Share(Asset):
    def __init__(self, iid: Iid):
        assert iid.category == Category.SHARE

        self.__iid = iid

    def __str__(self):
        s = f"{self.exchange().name}_{self.category().name}_{self.ticker()}"
        return s

    def __hash__(self):
        return hash(self.figi())

    def __eq__(self, other: object):
        assert isinstance(other, Iid)
        return self.figi == other.figi

    def iid(self) -> Iid:
        return self.__iid

    def exchange(self) -> Exchange:
        return self.__iid.exchange

    def category(self) -> Category:
        return self.__iid.category

    def ticker(self) -> str:
        return self.__iid.ticker

    def figi(self) -> str:
        return self.__iid.figi

    def name(self) -> str:
        return self.__iid.name

    def lot(self) -> int:
        return self.__iid.lot

    def step(self) -> float:
        return self.__iid.step
