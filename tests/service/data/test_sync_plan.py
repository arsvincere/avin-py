# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import pytest
from avin.domain.data.market_data import MarketData
from avin.domain.data.source import Source
from avin.domain.instrument.iid import Iid
from avin.service.data.sync_plan import DataSyncPlan
from avin.storage.iid_storage import IidStorage
from avin.system.data_manifest import (
    DataManifest,
    DataManifestSource,
    DataManifestSourceGroup,
)


def test_data_sync_plan_from_manifest(monkeypatch) -> None:
    calls: list[tuple[str, Source]] = []

    def fake_find_code(cls, code: str, source: Source) -> Iid:
        calls.append((code, source))
        exchange, category, ticker = code.split("_", maxsplit=2)

        return Iid(
            {
                "exchange": exchange,
                "category": category,
                "ticker": ticker,
                "figi": f"FIGI_{ticker}",
                "name": ticker,
                "lot": "1",
                "step": "0.01",
            }
        )

    monkeypatch.setattr(
        IidStorage,
        "find_code",
        classmethod(fake_find_code),
    )

    manifest = DataManifest(
        sources=(
            DataManifestSource(
                source=Source.TINKOFF,
                market_data=(MarketData.BAR_1M, MarketData.TICK),
                history_years=5,
                groups=(
                    DataManifestSourceGroup(
                        exchange="MOEX",
                        category="SHARE",
                        tickers=("SBER", "GAZP"),
                        codes=("MOEX_SHARE_SBER", "MOEX_SHARE_GAZP"),
                    ),
                    DataManifestSourceGroup(
                        exchange="MOEX",
                        category="FUTURE",
                        tickers=("SI",),
                        codes=("MOEX_FUTURE_SI",),
                    ),
                ),
            ),
        ),
    )

    plan = DataSyncPlan.from_manifest(manifest, current_year=2026)

    assert not plan.is_empty
    assert len(plan.tasks) == 6

    assert calls == [
        ("MOEX_SHARE_SBER", Source.TINKOFF),
        ("MOEX_SHARE_GAZP", Source.TINKOFF),
        ("MOEX_FUTURE_SI", Source.TINKOFF),
    ]

    actual = [
        (
            task.iid.code,
            task.source,
            task.market_data,
            task.group,
            task.years,
        )
        for task in plan.tasks
    ]

    expected_years = (2026, 2025, 2024, 2023, 2022)

    assert actual == [
        (
            "MOEX_SHARE_SBER",
            Source.TINKOFF,
            MarketData.BAR_1M,
            "MOEX_SHARE",
            expected_years,
        ),
        (
            "MOEX_SHARE_SBER",
            Source.TINKOFF,
            MarketData.TICK,
            "MOEX_SHARE",
            expected_years,
        ),
        (
            "MOEX_SHARE_GAZP",
            Source.TINKOFF,
            MarketData.BAR_1M,
            "MOEX_SHARE",
            expected_years,
        ),
        (
            "MOEX_SHARE_GAZP",
            Source.TINKOFF,
            MarketData.TICK,
            "MOEX_SHARE",
            expected_years,
        ),
        (
            "MOEX_FUTURE_SI",
            Source.TINKOFF,
            MarketData.BAR_1M,
            "MOEX_FUTURE",
            expected_years,
        ),
        (
            "MOEX_FUTURE_SI",
            Source.TINKOFF,
            MarketData.TICK,
            "MOEX_FUTURE",
            expected_years,
        ),
    ]


def test_data_sync_plan_empty_manifest() -> None:
    manifest = DataManifest(sources=())

    plan = DataSyncPlan.from_manifest(manifest, current_year=2026)

    assert plan.is_empty
    assert plan.tasks == ()


def test_data_sync_plan_rejects_invalid_history_years() -> None:
    manifest = DataManifest(
        sources=(
            DataManifestSource(
                source=Source.TINKOFF,
                market_data=(MarketData.BAR_1M,),
                history_years=0,
                groups=(
                    DataManifestSourceGroup(
                        exchange="MOEX",
                        category="SHARE",
                        tickers=("SBER",),
                        codes=("MOEX_SHARE_SBER",),
                    ),
                ),
            ),
        ),
    )

    with pytest.raises(ValueError, match="history_years"):
        DataSyncPlan.from_manifest(manifest, current_year=2026)
