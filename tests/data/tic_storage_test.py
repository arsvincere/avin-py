from datetime import UTC
from datetime import datetime as DateTime
from pathlib import Path

import polars as pl
import pytest

from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.data.tic_storage import TicStorage
from avin.utils import dt_to_ts
from avin.utils.exceptions import DataNotFound


class FakeIid:
    def __init__(self, root: Path):
        self.path = root

    def __str__(self) -> str:
        return "MOEX_SHARE_SBER"


def _tic_df(datetimes: list[DateTime]) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "datetime": [dt.isoformat() for dt in datetimes],
            "direction": ["B" for _ in datetimes],
            "price": [float(i) for i in range(len(datetimes))],
            "lots": [1 for _ in datetimes],
            "quantity": [10 for _ in datetimes],
            "value": [float(i * 10) for i in range(len(datetimes))],
            "ts": [dt_to_ts(dt) for dt in datetimes],
        }
    )


def test_load_last(tmp_path):
    iid = FakeIid(tmp_path / "SBER")
    source = Source.TINKOFF
    md = MarketData.TIC

    TicStorage.save(
        iid,
        source,
        md,
        _tic_df([DateTime(2024, 1, 1, 10, 0, tzinfo=UTC)]),
    )
    TicStorage.save(
        iid,
        source,
        md,
        _tic_df([DateTime(2025, 1, 1, 10, 0, tzinfo=UTC)]),
    )

    df = TicStorage.load_last(iid, source, md)

    assert df["datetime"].to_list() == ["2025-01-01T10:00:00+00:00"]


def test_load_range_across_days(tmp_path):
    iid = FakeIid(tmp_path / "SBER")
    source = Source.TINKOFF
    md = MarketData.TIC

    TicStorage.save(
        iid,
        source,
        md,
        _tic_df(
            [
                DateTime(2025, 1, 1, 9, 59, tzinfo=UTC),
                DateTime(2025, 1, 1, 10, 0, tzinfo=UTC),
            ]
        ),
    )
    TicStorage.save(
        iid,
        source,
        md,
        _tic_df(
            [
                DateTime(2025, 1, 2, 10, 0, tzinfo=UTC),
                DateTime(2025, 1, 2, 10, 1, tzinfo=UTC),
            ]
        ),
    )

    df = TicStorage.load_range(
        iid,
        source,
        md,
        DateTime(2025, 1, 1, 10, 0, tzinfo=UTC),
        DateTime(2025, 1, 2, 10, 1, tzinfo=UTC),
    )

    assert df["datetime"].to_list() == [
        "2025-01-01T10:00:00+00:00",
        "2025-01-02T10:00:00+00:00",
    ]


def test_load_range_skips_missing_days(tmp_path):
    iid = FakeIid(tmp_path / "SBER")
    source = Source.TINKOFF
    md = MarketData.TIC

    TicStorage.save(
        iid,
        source,
        md,
        _tic_df([DateTime(2025, 1, 3, 10, 0, tzinfo=UTC)]),
    )

    df = TicStorage.load_range(
        iid,
        source,
        md,
        DateTime(2025, 1, 1, tzinfo=UTC),
        DateTime(2025, 1, 4, tzinfo=UTC),
    )

    assert df.height == 1


def test_load_range_empty_result_raises(tmp_path):
    iid = FakeIid(tmp_path / "SBER")

    with pytest.raises(DataNotFound):
        TicStorage.load_range(
            iid,
            Source.TINKOFF,
            MarketData.TIC,
            DateTime(2025, 1, 1, tzinfo=UTC),
            DateTime(2025, 1, 2, tzinfo=UTC),
        )


def test_load_range_invalid_range(tmp_path):
    iid = FakeIid(tmp_path / "SBER")

    with pytest.raises(ValueError):
        TicStorage.load_range(
            iid,
            Source.TINKOFF,
            MarketData.TIC,
            DateTime(2025, 1, 1, tzinfo=UTC),
            DateTime(2025, 1, 1, tzinfo=UTC),
        )
