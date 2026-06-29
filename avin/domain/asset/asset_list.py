# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from collections.abc import Iterable, Iterator

from avin.domain.asset.base_asset import BaseAsset
from avin.errors.exceptions import InstrumentNotFoundError


class AssetList:
    def __init__(
        self, name: str, assets: Iterable[BaseAsset] | None = None
    ) -> None:
        if not isinstance(name, str):
            raise TypeError(name)
        if not name:
            raise ValueError("AssetList name is required")

        self.name = name
        self._assets: dict[str, BaseAsset] = {}

        if assets is not None:
            for asset in assets:
                self.add(asset)

    def __len__(self) -> int:
        return len(self._assets)

    def __bool__(self) -> bool:
        return bool(self._assets)

    def __contains__(self, code: str) -> bool:
        if not isinstance(code, str):
            raise TypeError(code)

        return code in self._assets

    def __iter__(self) -> Iterator[BaseAsset]:
        return iter(self._assets.values())

    def __getitem__(self, code: str) -> BaseAsset:
        if not isinstance(code, str):
            raise TypeError(code)

        return self.asset(code)

    @property
    def is_empty(self) -> bool:
        return not self._assets

    @property
    def codes(self) -> list[str]:
        return list(self._assets.keys())

    @property
    def tickers(self) -> list[str]:
        return [asset.ticker for asset in self]

    def asset(self, code: str) -> BaseAsset:
        if not isinstance(code, str):
            raise TypeError(code)

        if code not in self._assets:
            raise InstrumentNotFoundError(code)

        return self._assets[code]

    def find(self, code: str) -> BaseAsset | None:
        if not isinstance(code, str):
            raise TypeError(code)

        return self._assets.get(code)

    def add(self, asset: BaseAsset) -> None:
        if not isinstance(asset, BaseAsset):
            raise TypeError(asset)

        if asset.code in self._assets:
            raise ValueError(f"Asset {asset.code} already exists")

        self._assets[asset.code] = asset

    def remove(self, code: str) -> BaseAsset:
        if not isinstance(code, str):
            raise TypeError(code)

        if code not in self._assets:
            raise InstrumentNotFoundError(code)

        return self._assets.pop(code)

    def clear(self) -> None:
        self._assets.clear()
