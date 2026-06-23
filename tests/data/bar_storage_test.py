from datetime import UTC
from datetime import datetime as DateTime
from pathlib import Path

import polars as pl
import pytest

from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.data.bar_storage import BarStorage
from avin.utils import dt_to_ts
from avin.utils.exceptions import DataNotFound


class FakeIid:
    def __init__(self, root: Path):
        self.path = root

    def __str__(self) -> str:
        return "MOEX_SHARE_SBER"


def _bar_df(datetimes: list[DateTime]) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "datetime": [dt.isoformat() for dt in datetimes],
            "open": [float(i) for i in range(len(datetimes))],
            "high": [float(i) for i in range(len(datetimes))],
            "low": [float(i) for i in range(len(datetimes))],
            "close": [float(i) for i in range(len(datetimes))],
            "volume": [i for i in range(len(datetimes))],
            "ts": [dt_to_ts(dt) for dt in datetimes],
        }
    )


def test_load_range_across_years(tmp_path):
    iid = FakeIid(tmp_path / "SBER")
    source = Source.TINKOFF
    md = MarketData.BAR_1M

    BarStorage.save(
        iid,
        source,
        md,
        _bar_df(
            [
                DateTime(2024, 12, 31, 23, 58, tzinfo=UTC),
                DateTime(2024, 12, 31, 23, 59, tzinfo=UTC),
                DateTime(2025, 1, 1, 0, 0, tzinfo=UTC),
                DateTime(2025, 1, 1, 0, 1, tzinfo=UTC),
            ]
        ),
    )

    df = BarStorage.load_range(
        iid,
        source,
        md,
        DateTime(2024, 12, 31, 23, 59, tzinfo=UTC),
        DateTime(2025, 1, 1, 0, 1, tzinfo=UTC),
    )

    assert df["datetime"].to_list() == [
        "2024-12-31T23:59:00+00:00",
        "2025-01-01T00:00:00+00:00",
    ]


def test_load_range_end_boundary_does_not_require_next_year(tmp_path):
    iid = FakeIid(tmp_path / "SBER")
    source = Source.TINKOFF
    md = MarketData.BAR_1M

    BarStorage.save(
        iid,
        source,
        md,
        _bar_df([DateTime(2024, 12, 31, 23, 59, tzinfo=UTC)]),
    )

    df = BarStorage.load_range(
        iid,
        source,
        md,
        DateTime(2024, 12, 31, 23, 59, tzinfo=UTC),
        DateTime(2025, 1, 1, tzinfo=UTC),
    )

    assert df.height == 1


def test_load_range_empty_result_raises(tmp_path):
    iid = FakeIid(tmp_path / "SBER")
    source = Source.TINKOFF
    md = MarketData.BAR_1M

    BarStorage.save(
        iid,
        source,
        md,
        _bar_df([DateTime(2024, 1, 1, tzinfo=UTC)]),
    )

    with pytest.raises(DataNotFound):
        BarStorage.load_range(
            iid,
            source,
            md,
            DateTime(2024, 1, 2, tzinfo=UTC),
            DateTime(2024, 1, 3, tzinfo=UTC),
        )


def test_load_range_invalid_range(tmp_path):
    iid = FakeIid(tmp_path / "SBER")

    with pytest.raises(ValueError):
        BarStorage.load_range(
            iid,
            Source.TINKOFF,
            MarketData.BAR_1M,
            DateTime(2024, 1, 1, tzinfo=UTC),
            DateTime(2024, 1, 1, tzinfo=UTC),
        )
