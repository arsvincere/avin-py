# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from avin.domain.asset.asset import Asset
from avin.domain.common.timeframe import TimeFrame
from avin.domain.data.source import Source
from avin.service.asset.loader import AssetLoader
from avin.service.footprint.builder import FootprintBuilder
from avin.utils.dt import DateTime


class AssetEnsurer:
    @staticmethod
    def ensure_time_footprint(
        asset: Asset,
        source: Source,
        begin: DateTime,
        end: DateTime,
        tf: TimeFrame,
    ) -> None:
        if asset.has_time_footprint(tf):
            return

        if not asset.has_ticks():
            AssetLoader.load_ticks(asset, source, begin, end)

        AssetEnsurer._build_time_footprint(asset, tf)

    @staticmethod
    def ensure_tick_footprint(
        asset: Asset,
        source: Source,
        begin: DateTime,
        end: DateTime,
        ticks_per_cluster: int,
    ) -> None:
        if asset.has_tick_footprint(ticks_per_cluster):
            return

        if not asset.has_ticks():
            AssetLoader.load_ticks(asset, source, begin, end)

        AssetEnsurer._build_tick_footprint(asset, ticks_per_cluster)

    @staticmethod
    def ensure_volume_footprint(
        asset: Asset,
        source: Source,
        begin: DateTime,
        end: DateTime,
        volume_per_cluster: int,
    ) -> None:
        if asset.has_volume_footprint(volume_per_cluster):
            return

        if not asset.has_ticks():
            AssetLoader.load_ticks(asset, source, begin, end)

        AssetEnsurer._build_volume_footprint(asset, volume_per_cluster)

    @staticmethod
    def ensure_value_footprint(
        asset: Asset,
        source: Source,
        begin: DateTime,
        end: DateTime,
        value_per_cluster: float,
    ) -> None:
        if asset.has_value_footprint(value_per_cluster):
            return

        if not asset.has_ticks():
            AssetLoader.load_ticks(asset, source, begin, end)

        AssetEnsurer._build_value_footprint(asset, value_per_cluster)

    @staticmethod
    def _build_time_footprint(
        asset: Asset,
        tf: TimeFrame,
    ) -> None:
        fp = FootprintBuilder.build_time(asset.ticks(), tf)
        asset._set_time_footprint(tf, fp)

    @staticmethod
    def _build_tick_footprint(
        asset: Asset,
        ticks_per_cluster: int,
    ) -> None:
        fp = FootprintBuilder.build_tick(asset.ticks(), ticks_per_cluster)
        asset._set_tick_footprint(ticks_per_cluster, fp)

    @staticmethod
    def _build_volume_footprint(
        asset: Asset,
        volume_per_cluster: int,
    ) -> None:
        fp = FootprintBuilder.build_volume(asset.ticks(), volume_per_cluster)
        asset._set_volume_footprint(volume_per_cluster, fp)

    @staticmethod
    def _build_value_footprint(
        asset: Asset,
        value_per_cluster: float,
    ) -> None:
        fp = FootprintBuilder.build_value(asset.ticks(), value_per_cluster)
        asset._set_value_footprint(value_per_cluster, fp)
