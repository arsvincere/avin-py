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
from avin.system.data_manifest import DataManifest


def test_data_manifest_from_dict() -> None:
    manifest = DataManifest.from_dict(
        {
            "source": {
                "tinkoff": {
                    "market_data": ["BAR_1M", "TICK"],
                    "groups": [
                        {
                            "exchange": "MOEX",
                            "category": "SHARE",
                            "tickers": ["SBER", "gazp"],
                        },
                        {
                            "exchange": "MOEX",
                            "category": "FUTURE",
                            "tickers": ["USDRUBF"],
                        },
                    ],
                },
            },
        }
    )

    assert len(manifest.sources) == 1

    source = manifest.sources[0]
    assert source.source == Source.TINKOFF
    assert source.market_data == (MarketData.BAR_1M, MarketData.TICK)
    assert len(source.groups) == 2

    shares = source.groups[0]
    assert shares.exchange == "MOEX"
    assert shares.category == "SHARE"
    assert shares.tickers == ("SBER", "GAZP")
    assert shares.codes == ("MOEX_SHARE_SBER", "MOEX_SHARE_GAZP")
    assert shares.name == "MOEX_SHARE"

    futures = source.groups[1]
    assert futures.exchange == "MOEX"
    assert futures.category == "FUTURE"
    assert futures.tickers == ("USDRUBF",)
    assert futures.codes == ("MOEX_FUTURE_USDRUBF",)
    assert futures.name == "MOEX_FUTURE"


def test_data_manifest_load(tmp_path) -> None:
    path = tmp_path / "data.toml"
    path.write_text(
        """
[source.tinkoff]
market_data = ["BAR_1M", "TICK"]

[[source.tinkoff.groups]]
exchange = "MOEX"
category = "SHARE"
tickers = ["SBER", "GAZP"]
""",
        encoding="utf-8",
    )

    manifest = DataManifest.load(path)

    source = manifest.sources[0]
    group = source.groups[0]

    assert source.source == Source.TINKOFF
    assert source.market_data == (MarketData.BAR_1M, MarketData.TICK)
    assert group.codes == ("MOEX_SHARE_SBER", "MOEX_SHARE_GAZP")


def test_data_manifest_requires_source_section() -> None:
    with pytest.raises(ValueError, match="source"):
        DataManifest.from_dict({})


def test_data_manifest_requires_market_data() -> None:
    raw = {
        "source": {
            "tinkoff": {
                "groups": [
                    {
                        "exchange": "MOEX",
                        "category": "SHARE",
                        "tickers": ["SBER"],
                    },
                ],
            },
        },
    }

    with pytest.raises(ValueError, match="market_data"):
        DataManifest.from_dict(raw)


def test_data_manifest_requires_groups() -> None:
    raw = {
        "source": {
            "tinkoff": {
                "market_data": ["BAR_1M"],
            },
        },
    }

    with pytest.raises(ValueError, match="groups"):
        DataManifest.from_dict(raw)


def test_data_manifest_rejects_unknown_source() -> None:
    raw = {
        "source": {
            "unknown": {
                "market_data": ["BAR_1M"],
                "groups": [
                    {
                        "exchange": "MOEX",
                        "category": "SHARE",
                        "tickers": ["SBER"],
                    },
                ],
            },
        },
    }

    with pytest.raises(ValueError, match="Unknown source"):
        DataManifest.from_dict(raw)


def test_data_manifest_rejects_unknown_market_data() -> None:
    raw = {
        "source": {
            "tinkoff": {
                "market_data": ["UNKNOWN"],
                "groups": [
                    {
                        "exchange": "MOEX",
                        "category": "SHARE",
                        "tickers": ["SBER"],
                    },
                ],
            },
        },
    }

    with pytest.raises(ValueError, match="Invalid market data"):
        DataManifest.from_dict(raw)


def test_data_manifest_rejects_empty_tickers() -> None:
    raw = {
        "source": {
            "tinkoff": {
                "market_data": ["BAR_1M"],
                "groups": [
                    {
                        "exchange": "MOEX",
                        "category": "SHARE",
                        "tickers": [],
                    },
                ],
            },
        },
    }

    with pytest.raises(ValueError, match="tickers"):
        DataManifest.from_dict(raw)
