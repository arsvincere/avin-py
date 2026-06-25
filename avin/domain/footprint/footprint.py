# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from collections.abc import Iterator

from avin.domain.footprint.cluster import Cluster
from avin.domain.tick import Tick


class Footprint:
    clusters: list[Cluster]

    def __init__(self) -> None:
        self.clusters: list[Cluster] = []

    def __len__(self) -> int:
        return len(self.clusters)

    def __iter__(self) -> Iterator[Cluster]:
        return iter(self.clusters)

    def __getitem__(self, index: int) -> Cluster:
        return self.clusters[index]

    @property
    def is_empty(self) -> bool:
        return not self.clusters

    @property
    def last_cluster(self) -> Cluster:
        if not self.clusters:
            raise ValueError("footprint is empty")

        return self.clusters[-1]

    def add(self, tick: Tick) -> None:
        raise NotImplementedError()
