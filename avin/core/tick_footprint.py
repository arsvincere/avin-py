# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin.core.cluster import Cluster
from avin.core.footprint import Footprint
from avin.core.tick import Tick


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
