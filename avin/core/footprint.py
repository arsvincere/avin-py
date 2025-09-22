# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import polars as pl

from avin.core.cluster import Cluster
from avin.core.iid import Iid
from avin.core.tic import Tic
from avin.core.timeframe import TimeFrame


class Footprint:
    def __init__(self, iid: Iid, tf: TimeFrame, clusters: list[Cluster]):
        self.__iid = iid
        self.__tf = tf
        self.__clusters = clusters
        self.__now = None

    @classmethod
    def from_tics(cls, tics: pl.DataFrame) -> Footprint:
        raise NotImplementedError()

    def add_tic(self, tic: Tic) -> None:
        raise NotImplementedError()


if __name__ == "__main__":
    ...
