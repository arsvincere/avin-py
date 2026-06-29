# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from avin.domain.asset.future import Future
from avin.domain.asset.share import Share
from avin.domain.data.source import Source
from avin.domain.instrument.category import Category
from avin.domain.instrument.iid import Iid
from avin.storage.iid_storage import IidStorage


class Asset:
    """
    Public typed asset factory.

    Asset creates concrete domain assets by instrument code or Iid.
    It does not load market data.

    # ru
    Публичная типизированная фабрика активов.

    Asset создаёт конкретные доменные активы по коду инструмента или Iid.
    Она не загружает market data.
    """

    @staticmethod
    def share(
        value: str | Iid,
        source: Source = Source.TINKOFF,
    ) -> Share:
        iid = _iid(value, source)
        _ensure_category(iid, Category.SHARE)

        return Share(iid)

    @staticmethod
    def future(
        value: str | Iid,
        source: Source = Source.TINKOFF,
    ) -> Future:
        iid = _iid(value, source)
        _ensure_category(iid, Category.FUTURE)

        return Future(iid)


def _iid(
    value: str | Iid,
    source: Source,
) -> Iid:
    if isinstance(value, Iid):
        return value

    return IidStorage.find_code(value, source)


def _ensure_category(
    iid: Iid,
    expected: Category,
) -> None:
    if iid.category is not expected:
        raise ValueError(
            f"Expected {expected} asset, got {iid.category}: {iid.code}"
        )
