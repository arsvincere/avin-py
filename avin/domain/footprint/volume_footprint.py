# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from avin.domain.footprint.cluster import Cluster
from avin.domain.footprint.footprint import Footprint
from avin.domain.raw.tick import Tick


class VolumeFootprint(Footprint):
    def __init__(
        self,
        volume_per_cluster: int,
    ) -> None:
        if volume_per_cluster < 1:
            raise ValueError("volume_per_cluster must be > 0")

        super().__init__()

        self.volume_per_cluster = volume_per_cluster

    def add(self, tick: Tick) -> None:
        if self.is_empty or self.last_cluster.vol >= self.volume_per_cluster:
            self.clusters.append(Cluster())

        self.last_cluster.add(tick)
