# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from avin.domain.footprint.cluster import Cluster
from avin.domain.footprint.footprint import Footprint
from avin.domain.raw.tick import Tick


class TickFootprint(Footprint):
    def __init__(
        self,
        ticks_per_cluster: int,
    ) -> None:
        if ticks_per_cluster < 1:
            raise ValueError("...")

        super().__init__()

        self.ticks_per_cluster = ticks_per_cluster

    def add(self, tick: Tick) -> None:
        if (
            self.is_empty
            or self.last_cluster.trades >= self.ticks_per_cluster
        ):
            self.clusters.append(Cluster())

        self.last_cluster.add(tick)
