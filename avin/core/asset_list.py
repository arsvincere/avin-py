# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from avin.core.asset import Asset, Share
from avin.utils import CFG, AvinError, Cmd


class AssetList:
    """Users asset list.

    # ru
    Пользовательский список активов. Содержит имя и list активов.

    Списки хранятся в csv формате, в директории указанной в конфиге
    пользователя, в папке "asset".

    Используется в терминале. Или при создании тестов для стратегии,
    можно указать целый список активов.
    """

    def __init__(self, name: str, assets: list | None = None):
        self.__name = name
        self.__assets = assets if assets else list()

    def __iter__(self):
        return iter(self.__assets)

    def __len__(self) -> int:
        return len(self.__assets)

    def __getitem__(self, index: int) -> Asset:
        return self.__assets[index]

    @classmethod
    def load(cls, name: str) -> AssetList:
        """Load asset list.

        # ru
        Загружает пользовательский список активов по имени.
        """

        path = CFG.Dir.asset / f"{name}.csv"

        if not Cmd.is_exist(path):
            raise AvinError(f"Asset list '{name}' not found.")

        text = Cmd.read_text(path)
        assets = list()
        for csv_line in text:
            asset = Share.from_csv(csv_line)
            assets.append(asset)

        asset_list = AssetList(name, assets)

        return asset_list

    @property
    def name(self) -> str:
        """Return asset list name.

        # ru
        Возвращает имя списка.
        """

        return self.__name

    @property
    def assets(self) -> list[Asset]:
        """Return reference to list of assets.

        # ru
        Возвращает ссылку на list активов.
        """

        return self.__assets

    def is_empty(self) -> bool:
        """Check for asset list is empty.

        # ru
        Проверка если ли в списке активы.
        """

        return len(self.__assets) == 0

    def find_figi(self, figi: str) -> Share | None:
        """Find asset in asset list by figi.

        # ru
        Возвращает ссылку на актив с заданным figi.
        """

        for asset in self.__assets:
            if asset.figi() == figi:
                return asset

        return None


if __name__ == "__main__":
    ...
