# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin.domain.footprint.cluster import Cluster
from avin.domain.footprint.footprint import Footprint
from avin.domain.tick import Tick


class ValueFootprint(Footprint):
    def __init__(
        self,
        value_per_cluster: float,
    ) -> None:
        if value_per_cluster <= 0:
            raise ValueError("value_per_cluster must be > 0")

        super().__init__()

        self.value_per_cluster = value_per_cluster

    def add(self, tick: Tick) -> None:
        if self.is_empty or self.last_cluster.val >= self.value_per_cluster:
            self.clusters.append(Cluster())

        self.last_cluster.add(tick)
