# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import pytest
from avin.api.asset import Asset
from avin.domain.asset.future import Future
from avin.domain.asset.share import Share
from avin.domain.data.source import Source
from avin.domain.instrument.category import Category
from avin.domain.instrument.iid import Iid
from avin.storage.iid_storage import IidStorage

# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────


def iid(
    category: Category,
    ticker: str,
    figi: str,
    name: str,
) -> Iid:
    return Iid(
        {
            "exchange": "MOEX",
            "category": category.name,
            "ticker": ticker,
            "figi": figi,
            "name": name,
            "lot": "10",
            "step": "0.01",
        }
    )


def share_iid() -> Iid:
    return iid(
        category=Category.SHARE,
        ticker="SBER",
        figi="figi_sber",
        name="Sber",
    )


def future_iid() -> Iid:
    return iid(
        category=Category.FUTURE,
        ticker="SiZ5",
        figi="figi_siz5",
        name="Si future",
    )


# ────────────────────────────────────────────────────────────────────────────
# Share
# ────────────────────────────────────────────────────────────────────────────


def test_share_from_code_returns_share(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, Source]] = []

    def fake_find_code(code: str, source: Source) -> Iid:
        calls.append((code, source))
        return share_iid()

    monkeypatch.setattr(IidStorage, "find_code", fake_find_code)

    asset = Asset.share("MOEX_SHARE_SBER")

    assert isinstance(asset, Share)
    assert asset.code == "MOEX_SHARE_SBER"
    assert asset.ticker == "SBER"
    assert asset.figi == "figi_sber"
    assert asset.name == "Sber"
    assert calls == [("MOEX_SHARE_SBER", Source.TINKOFF)]


def test_share_from_code_uses_custom_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, Source]] = []

    def fake_find_code(code: str, source: Source) -> Iid:
        calls.append((code, source))
        return share_iid()

    monkeypatch.setattr(IidStorage, "find_code", fake_find_code)

    Asset.share("MOEX_SHARE_SBER", Source.MOEXALGO)

    assert calls == [("MOEX_SHARE_SBER", Source.MOEXALGO)]


def test_share_from_iid_returns_share(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_find_code(code: str, source: Source) -> Iid:
        pytest.fail("IidStorage.find_code should not be called for Iid input")

    monkeypatch.setattr(IidStorage, "find_code", fake_find_code)

    source_iid = share_iid()

    asset = Asset.share(source_iid)

    assert isinstance(asset, Share)
    assert asset.iid is source_iid
    assert asset.code == "MOEX_SHARE_SBER"


def test_share_rejects_future_iid() -> None:
    with pytest.raises(
        ValueError,
        match="Expected SHARE asset, got FUTURE: MOEX_FUTURE_SiZ5",
    ):
        Asset.share(future_iid())


def test_share_rejects_future_code(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_find_code(code: str, source: Source) -> Iid:
        return future_iid()

    monkeypatch.setattr(IidStorage, "find_code", fake_find_code)

    with pytest.raises(
        ValueError,
        match="Expected SHARE asset, got FUTURE: MOEX_FUTURE_SiZ5",
    ):
        Asset.share("MOEX_FUTURE_SiZ5")


# ────────────────────────────────────────────────────────────────────────────
# Future
# ────────────────────────────────────────────────────────────────────────────


def test_future_from_code_returns_future(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, Source]] = []

    def fake_find_code(code: str, source: Source) -> Iid:
        calls.append((code, source))
        return future_iid()

    monkeypatch.setattr(IidStorage, "find_code", fake_find_code)

    asset = Asset.future("MOEX_FUTURE_SiZ5")

    assert isinstance(asset, Future)
    assert asset.code == "MOEX_FUTURE_SiZ5"
    assert asset.ticker == "SiZ5"
    assert asset.figi == "figi_siz5"
    assert asset.name == "Si future"
    assert calls == [("MOEX_FUTURE_SiZ5", Source.TINKOFF)]


def test_future_from_code_uses_custom_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, Source]] = []

    def fake_find_code(code: str, source: Source) -> Iid:
        calls.append((code, source))
        return future_iid()

    monkeypatch.setattr(IidStorage, "find_code", fake_find_code)

    Asset.future("MOEX_FUTURE_SiZ5", Source.MOEXALGO)

    assert calls == [("MOEX_FUTURE_SiZ5", Source.MOEXALGO)]


def test_future_from_iid_returns_future(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_find_code(code: str, source: Source) -> Iid:
        pytest.fail("IidStorage.find_code should not be called for Iid input")

    monkeypatch.setattr(IidStorage, "find_code", fake_find_code)

    source_iid = future_iid()

    asset = Asset.future(source_iid)

    assert isinstance(asset, Future)
    assert asset.iid is source_iid
    assert asset.code == "MOEX_FUTURE_SiZ5"


def test_future_rejects_share_iid() -> None:
    with pytest.raises(
        ValueError,
        match="Expected FUTURE asset, got SHARE: MOEX_SHARE_SBER",
    ):
        Asset.future(share_iid())


def test_future_rejects_share_code(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_find_code(code: str, source: Source) -> Iid:
        return share_iid()

    monkeypatch.setattr(IidStorage, "find_code", fake_find_code)

    with pytest.raises(
        ValueError,
        match="Expected FUTURE asset, got SHARE: MOEX_SHARE_SBER",
    ):
        Asset.future("MOEX_SHARE_SBER")
