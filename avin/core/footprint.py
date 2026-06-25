# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin.core.cluster import Cluster
from avin.core.tick import Tick


class Footprint:
    clusters: list[Cluster]

    def __init__(self) -> None:
        self.clusters: list[Cluster] = []

    def __len__(self) -> int:
        raise NotImplementedError("TODO")

    def __iter__(self):
        raise NotImplementedError("TODO")

    def __getitem__(self, index: int) -> Cluster:
        raise NotImplementedError("TODO")

    @property
    def last_cluster(self) -> Cluster:
        raise NotImplementedError("TODO")

    @property
    def high(self) -> float:
        raise NotImplementedError("TODO")

    @property
    def low(self) -> float:
        raise NotImplementedError("TODO")

    @property
    def vol(self) -> int:
        raise NotImplementedError("TODO")

    @property
    def val(self) -> int:
        raise NotImplementedError("TODO")

    def add(self, tick: Tick) -> None:
        raise NotImplementedError("TODO")
