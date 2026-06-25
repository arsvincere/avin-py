# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from avin.core.cluster import Cluster
from avin.core.footprint import Footprint
from avin.core.tick import Tick
from avin.core.timeframe import TimeFrame


class TimeFootprint(Footprint):
    def __init__(
        self,
        timeframe: TimeFrame,
    ) -> None:
        super().__init__()

        self.timeframe = timeframe
        self._last_frame_ts: int | None = None

    def add(self, tick: Tick) -> None:
        if not self.is_empty and tick.ts < self.last_cluster.ts_last:
            raise ValueError(
                f"tick ts {tick.ts} < last ts {self.last_cluster.ts_last}"
            )

        frame_ts = self.timeframe.begin_frame_ts(tick.ts)

        if frame_ts != self._last_frame_ts:
            self.clusters.append(Cluster())
            self._last_frame_ts = frame_ts

        self.last_cluster.add(tick)
