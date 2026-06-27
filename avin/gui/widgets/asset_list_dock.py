# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QTreeWidget, QTreeWidgetItem

from avin.gui.app_controller import AppController
from avin.gui.messages import SelectAsset
from avin.gui.app_state import AppState


class AssetListDock(QDockWidget):
    def __init__(self, controller: AppController) -> None:
        super().__init__("Assets")

        self.setObjectName("asset_list_dock")
        self._controller = controller

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.itemClicked.connect(self._on_item_clicked)

        self.setWidget(self._tree)

    def set_state(self, state: AppState) -> None:
        self._tree.clear()

        current_item: QTreeWidgetItem | None = None

        for asset in state.assets:
            item = QTreeWidgetItem([asset.ticker])
            item.setData(0, Qt.ItemDataRole.UserRole, asset.code)

            self._tree.addTopLevelItem(item)

            if asset.code == state.current_asset_code:
                current_item = item

        if current_item is not None:
            self._tree.setCurrentItem(current_item)

    def _on_item_clicked(self, item: QTreeWidgetItem) -> None:
        code = item.data(0, Qt.ItemDataRole.UserRole)

        if not isinstance(code, str):
            raise TypeError(code)

        self._controller.handle(SelectAsset(code))
