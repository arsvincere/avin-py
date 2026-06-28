# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import polars as pl
import pytest
from avin.domain.asset.share import Share
from avin.domain.common.direction import Direction
from avin.domain.common.timeframe import TimeFrame
from avin.domain.data.market_data import MarketData
from avin.domain.data.source import Source
from avin.domain.instrument.iid import Iid
from avin.domain.raw.tick import Tick
from avin.service.asset.loader import AssetLoader
from avin.storage.codec import StorageCodec
from avin.storage.data_manager import DataManager
from avin.utils.dt import DateTime


def _share() -> Share:
    return Share(
        Iid(
            {
                "exchange": "MOEX",
                "category": "SHARE",
                "ticker": "SBER",
                "figi": "BBG004730N88",
                "name": "Sberbank",
                "lot": "10",
                "step": "0.01",
            }
        )
    )


def test_load_ticks_loads_tick_data_into_asset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    asset = _share()
    begin = DateTime(2026, 6, 1)
    end = DateTime(2026, 6, 2)
    df = pl.DataFrame({"tick": [1, 2]})
    ticks = [
        Tick(
            ts=1,
            direction=Direction.BUY,
            price=100.0,
            lots=10,
            quantity=100,
            value=1000.0,
        ),
        Tick(
            ts=2,
            direction=Direction.SELL,
            price=101.0,
            lots=20,
            quantity=200,
            value=2020.0,
        ),
    ]

    load_calls: list[tuple[str, Source, MarketData, DateTime, DateTime]] = []
    codec_calls: list[pl.DataFrame] = []

    def fake_load(
        code: str,
        source: Source,
        market_data: MarketData,
        begin_: DateTime,
        end_: DateTime,
    ) -> pl.DataFrame:
        load_calls.append((code, source, market_data, begin_, end_))
        return df

    def fake_ticks_from_df(df_: pl.DataFrame) -> list[Tick]:
        codec_calls.append(df_)
        return ticks

    monkeypatch.setattr(DataManager, "load", fake_load)
    monkeypatch.setattr(StorageCodec, "ticks_from_df", fake_ticks_from_df)

    AssetLoader.load_ticks(asset, Source.TINKOFF, begin, end)

    assert load_calls == [
        (
            "MOEX_SHARE_SBER",
            Source.TINKOFF,
            MarketData.TICK,
            begin,
            end,
        )
    ]
    assert codec_calls == [df]
    assert asset.ticks() == ticks


def test_load_ticks_replaces_existing_ticks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    asset = _share()
    begin = DateTime(2026, 6, 1)
    end = DateTime(2026, 6, 2)
    df = pl.DataFrame({"tick": [1]})
    old_ticks = [
        Tick(
            ts=1,
            direction=Direction.BUY,
            price=100.0,
            lots=10,
            quantity=100,
            value=1000.0,
        )
    ]
    new_ticks = [
        Tick(
            ts=2,
            direction=Direction.SELL,
            price=101.0,
            lots=20,
            quantity=200,
            value=2020.0,
        )
    ]

    asset._set_ticks(old_ticks)

    def fake_load(
        code: str,
        source: Source,
        market_data: MarketData,
        begin_: DateTime,
        end_: DateTime,
    ) -> pl.DataFrame:
        return df

    def fake_ticks_from_df(df_: pl.DataFrame) -> list[Tick]:
        return new_ticks

    monkeypatch.setattr(DataManager, "load", fake_load)
    monkeypatch.setattr(StorageCodec, "ticks_from_df", fake_ticks_from_df)

    AssetLoader.load_ticks(asset, Source.TINKOFF, begin, end)

    assert asset.ticks() == new_ticks


def test_load_bars_is_not_implemented() -> None:
    asset = _share()
    begin = DateTime(2026, 6, 1)
    end = DateTime(2026, 6, 2)

    with pytest.raises(NotImplementedError, match="TODO"):
        AssetLoader.load_bars(
            asset,
            Source.TINKOFF,
            TimeFrame.M1,
            begin,
            end,
        )


def test_load_order_book_is_not_implemented() -> None:
    asset = _share()
    begin = DateTime(2026, 6, 1)
    end = DateTime(2026, 6, 2)

    with pytest.raises(NotImplementedError, match="TODO"):
        AssetLoader.load_order_book(
            asset,
            Source.TINKOFF,
            begin,
            end,
        )
