# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from avin.domain.asset.asset_list import AssetList
from avin.domain.asset.share import Share
from avin.domain.data.source import Source
from avin.domain.instrument.category import Category
from avin.domain.instrument.iid import Iid
from avin.storage.iid_storage import IidStorage
from avin.system.conf import cfg


class AssetListService:
    @classmethod
    def load_default(cls) -> AssetList:
        asset_list_name = cfg.default_asset_list_name
        source = cfg.default_source

        match asset_list_name:
            case "favorites":
                return cls.load_favorites(source)
            case _:
                raise NotImplementedError(asset_list_name)

    @classmethod
    def load_favorites(cls, source: Source) -> AssetList:
        if source is not Source.TINKOFF:
            raise NotImplementedError(f"Favorites for {source}")

        df = IidStorage.load(source, Category.SHARE)

        assets = AssetList()

        for row in df.iter_rows(named=True):
            iid = Iid(row)
            assets.add(Share(iid))

        return assets
