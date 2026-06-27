# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from avin.domain.asset.asset import Asset
from avin.domain.common.timeframe import TimeFrame
from avin.domain.data.market_data import MarketData
from avin.domain.data.source import Source
from avin.domain.raw.tick import Tick
from avin.service.data_service import DataService
from avin.service.footprint_builder import FootprintBuilder
from avin.utils.dt import DateTime


class AssetDataService:
    @staticmethod
    def load_ticks(
        asset: Asset,
        source: Source,
        begin: DateTime,
        end: DateTime,
    ) -> None:
        df = DataService.load(
            asset.code,
            source,
            MarketData.TICK,
            begin,
            end,
        )
        ticks = Tick.from_df(df)
        asset._set_ticks(ticks)

    @staticmethod
    def build_time_footprint(
        asset: Asset,
        tf: TimeFrame,
    ) -> None:
        fp = FootprintBuilder.build_time(asset.ticks(), tf)
        asset._set_time_footprint(tf, fp)

    @staticmethod
    def build_tick_footprint(
        asset: Asset,
        ticks_per_cluster: int,
    ) -> None:
        fp = FootprintBuilder.build_tick(asset.ticks(), ticks_per_cluster)
        asset._set_tick_footprint(ticks_per_cluster, fp)

    @staticmethod
    def build_volume_footprint(
        asset: Asset,
        volume_per_cluster: int,
    ) -> None:
        fp = FootprintBuilder.build_volume(asset.ticks(), volume_per_cluster)
        asset._set_volume_footprint(volume_per_cluster, fp)

    @staticmethod
    def build_value_footprint(
        asset: Asset,
        value_per_cluster: float,
    ) -> None:
        fp = FootprintBuilder.build_value(asset.ticks(), value_per_cluster)
        asset._set_value_footprint(value_per_cluster, fp)
