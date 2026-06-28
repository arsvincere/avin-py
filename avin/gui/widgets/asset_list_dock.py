# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem

from avin.gui.app_controller import AppController
from avin.gui.app_state import AppState
from avin.gui.messages import SelectAsset


class AssetListDock(QDockWidget):
    def __init__(self, controller: AppController) -> None:
        super().__init__("Asset list")

        self._controller = controller

        self._create_widget()
        self._configure()
        self._connect()

    def _create_widget(self) -> None:
        self.setObjectName("asset_list_dock")

        self._tree = QTreeWidget()
        self.setWidget(self._tree)

    def _configure(self) -> None:
        self._tree.setHeaderHidden(True)
        self._tree.setSortingEnabled(True)

    def _connect(self) -> None:
        self._tree.itemClicked.connect(self._on_item_clicked)

    def set_state(self, state: AppState) -> None:
        self._tree.clear()

        current_item: QTreeWidgetItem | None = None

        for asset in state.asset_list:
            item = QTreeWidgetItem([asset.ticker])
            item.setData(0, Qt.ItemDataRole.UserRole, asset.code)

            self._tree.addTopLevelItem(item)

            if asset.code == state.selected_asset_code:
                current_item = item

        self._tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        if current_item is not None:
            self._tree.setCurrentItem(current_item)

    def _on_item_clicked(self, item: QTreeWidgetItem) -> None:
        code = item.data(0, Qt.ItemDataRole.UserRole)

        if not isinstance(code, str):
            raise TypeError(code)

        self._controller.handle(SelectAsset(code))
