# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from avin.domain.asset.base_asset import BaseAsset
from avin.domain.common.timeframe import TimeFrame
from avin.domain.data.market_data import MarketData
from avin.domain.data.source import Source
from avin.storage.codec import StorageCodec
from avin.storage.data_manager import DataManager
from avin.utils.dt import DateTime


class AssetLoader:
    @staticmethod
    def load_ticks(
        asset: BaseAsset,
        source: Source,
        begin: DateTime,
        end: DateTime,
    ) -> None:
        df = DataManager.load(
            asset.code,
            source,
            MarketData.TICK,
            begin,
            end,
        )
        ticks = StorageCodec.ticks_from_df(df)
        asset._set_ticks(ticks)

    @staticmethod
    def load_bars(
        asset: BaseAsset,
        source: Source,
        tf: TimeFrame,
        begin: DateTime,
        end: DateTime,
    ) -> None:
        raise NotImplementedError("TODO")

    @staticmethod
    def load_order_book(
        asset: BaseAsset,
        source: Source,
        begin: DateTime,
        end: DateTime,
    ) -> None:
        raise NotImplementedError("TODO")
