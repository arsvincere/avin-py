# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsTextItem

from avin.domain.asset.base_asset import BaseAsset
from avin.domain.common.timeframe import TimeFrame
from avin.domain.footprint.cluster import Cluster
from avin.domain.footprint.time_footprint import TimeFootprint
from avin.gui.app_state import AppState

# dev
DEV_FOOTPRINT_TIMEFRAME = TimeFrame.M1
DEV_MAX_CLUSTERS = 40

DEV_LEFT = 20
DEV_TOP = 20
DEV_PRICE_WIDTH = 80
DEV_CLUSTER_WIDTH = 90
DEV_ROW_HEIGHT = 22
DEV_HEADER_HEIGHT = 35


class CentralScene(QGraphicsScene):
    def __init__(self) -> None:
        super().__init__()

        self._font = QFont("monospace", 9)

        self.setSceneRect(0, 0, 1000, 700)

    def set_state(self, state: AppState) -> None:
        self.clear()

        if state.selected_asset_code is None:
            self._add_text("Select asset", 500, 50)
            return

        asset = state.asset_list.asset(state.selected_asset_code)

        if not asset.has_time_footprint(DEV_FOOTPRINT_TIMEFRAME):
            self._draw_asset_text(asset, state)
            return

        footprint = asset.time_footprint(DEV_FOOTPRINT_TIMEFRAME)

        if footprint.is_empty:
            self._add_text("Footprint is empty", 500, 50)
            return

        self._draw_time_footprint(asset, state, footprint)

    def _draw_time_footprint(
        self,
        asset: BaseAsset,
        state: AppState,
        footprint: TimeFootprint,
    ) -> None:
        clusters = self._visible_clusters(footprint)
        prices = self._prices(clusters)

        if not prices:
            self._add_text("Footprint has no prices", 500, 50)
            return

        scene_width = (
            DEV_LEFT
            + DEV_PRICE_WIDTH
            + len(clusters) * DEV_CLUSTER_WIDTH
            + DEV_LEFT
        )
        scene_height = (
            DEV_TOP
            + DEV_HEADER_HEIGHT
            + len(prices) * DEV_ROW_HEIGHT
            + DEV_TOP
        )

        self.setSceneRect(
            0,
            0,
            max(1000, scene_width),
            max(700, scene_height),
        )

        self._add_text(
            (
                f"{asset.code} | {asset.name} | {state.source} | "
                f"{DEV_FOOTPRINT_TIMEFRAME} | "
                f"last {len(clusters)} / {len(footprint)} clusters"
            ),
            DEV_LEFT,
            DEV_TOP,
        )

        self._draw_price_axis(prices)
        self._draw_clusters(footprint, clusters, prices)

    def _draw_price_axis(self, prices: list[float]) -> None:
        for row, price in enumerate(prices):
            y = self._price_y(row)
            self._add_text(self._price_text(price), DEV_LEFT, y)

    def _draw_clusters(
        self,
        footprint: TimeFootprint,
        clusters: list[Cluster],
        prices: list[float],
    ) -> None:
        first_cluster_index = len(footprint) - len(clusters)

        for local_index, cluster in enumerate(clusters):
            cluster_index = first_cluster_index + local_index
            x = self._cluster_x(local_index)

            self._add_text(str(cluster_index), x, DEV_TOP + 18)

            levels_by_price = {
                level.price: level for level in cluster.ladder.sorted_levels
            }

            for row, price in enumerate(prices):
                level = levels_by_price.get(price)

                if level is None:
                    continue

                text = f"{level.vol_s} | {level.vol_b}"
                self._add_text(text, x, self._price_y(row))

    def _draw_asset_text(self, asset: BaseAsset, state: AppState) -> None:
        self._add_text(self._asset_text(asset, state), 500, 50)

    def _asset_text(self, asset: BaseAsset, state: AppState) -> str:
        return "\n".join(
            [
                f"Selected asset: {asset.code}",
                f"Name: {asset.name}",
                f"Source: {state.source}",
                f"Ticks: {self._ticks_text(asset)}",
                (
                    f"TimeFootprint {DEV_FOOTPRINT_TIMEFRAME}: "
                    f"{self._time_footprint_text(asset)}"
                ),
                f"Message: {state.last_message}",
            ]
        )

    def _visible_clusters(self, footprint: TimeFootprint) -> list[Cluster]:
        clusters = list(footprint)
        return clusters[-DEV_MAX_CLUSTERS:]

    def _prices(self, clusters: list[Cluster]) -> list[float]:
        prices = {
            level.price
            for cluster in clusters
            for level in cluster.ladder.sorted_levels
        }

        return sorted(prices, reverse=True)

    def _cluster_x(self, cluster_index: int) -> int:
        return DEV_LEFT + DEV_PRICE_WIDTH + cluster_index * DEV_CLUSTER_WIDTH

    def _price_y(self, row: int) -> int:
        return DEV_TOP + DEV_HEADER_HEIGHT + row * DEV_ROW_HEIGHT

    def _price_text(self, price: float) -> str:
        return f"{price:g}"

    def _ticks_text(self, asset: BaseAsset) -> str:
        if not asset.has_ticks():
            return "No"

        return str(len(asset.ticks()))

    def _time_footprint_text(self, asset: BaseAsset) -> str:
        if not asset.has_time_footprint(DEV_FOOTPRINT_TIMEFRAME):
            return "No"

        footprint = asset.time_footprint(DEV_FOOTPRINT_TIMEFRAME)
        return f"{len(footprint)} clusters"

    def _add_text(self, text: str, x: float, y: float) -> QGraphicsTextItem:
        item = QGraphicsTextItem(text)
        item.setFont(self._font)
        item.setPos(x, y)

        self.addItem(item)

        return item
