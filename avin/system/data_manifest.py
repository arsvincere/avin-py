# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from avin.domain.data.market_data import MarketData
from avin.domain.data.source import Source
from avin.domain.instrument.category import Category
from avin.domain.instrument.exchange import Exchange
from avin.utils.cmd import Cmd


@dataclass(frozen=True, slots=True)
class DataManifestSourceGroup:
    exchange: str
    category: str
    tickers: tuple[str, ...]
    codes: tuple[str, ...]

    @property
    def name(self) -> str:
        return f"{self.exchange}_{self.category}"


@dataclass(frozen=True, slots=True)
class DataManifestSource:
    source: Source
    market_data: tuple[MarketData, ...]
    history_years: int
    groups: tuple[DataManifestSourceGroup, ...]


@dataclass(frozen=True, slots=True)
class DataManifest:
    sources: tuple[DataManifestSource, ...]

    @classmethod
    def load(cls, path: Path) -> DataManifest:
        raw = Cmd.read_toml(path)

        return cls.from_dict(raw)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> DataManifest:
        source_root = _get_dict(raw, "source")

        sources: list[DataManifestSource] = []

        for source_name, source_raw in source_root.items():
            source_path = f"source.{source_name}"
            source_data = _as_dict(source_raw, source_path)
            source = Source.from_str(source_name)

            market_data = _parse_market_data(
                source_data,
                f"{source_path}.market_data",
            )
            history_years = _parse_history_years(
                source_data,
                f"{source_path}.history_years",
            )
            groups = _parse_groups(
                source_data,
                f"{source_path}.groups",
            )

            sources.append(
                DataManifestSource(
                    source=source,
                    market_data=market_data,
                    history_years=history_years,
                    groups=groups,
                )
            )

        if not sources:
            raise ValueError("Data manifest has no sources")

        return cls(sources=tuple(sources))


def _parse_market_data(
    raw: dict[str, Any],
    path: str,
) -> tuple[MarketData, ...]:
    values = _get_list(raw, "market_data", path)
    result: list[MarketData] = []

    for value in values:
        if not isinstance(value, str):
            raise TypeError(f"{path} item must be str: {value!r}")

        result.append(MarketData.from_str(value))

    if not result:
        raise ValueError(f"{path} must not be empty")

    return tuple(result)


def _parse_history_years(
    raw: dict[str, Any],
    path: str,
) -> int:
    value = _get_int(raw, "history_years", path)

    if value < 1:
        raise ValueError(f"{path} must be positive")

    return value


def _parse_groups(
    raw: dict[str, Any],
    path: str,
) -> tuple[DataManifestSourceGroup, ...]:
    values = _get_list(raw, "groups", path)
    groups: list[DataManifestSourceGroup] = []

    for index, value in enumerate(values):
        group_path = f"{path}[{index}]"
        group_raw = _as_dict(value, group_path)

        groups.append(_parse_group(group_raw, group_path))

    if not groups:
        raise ValueError(f"{path} must not be empty")

    return tuple(groups)


def _parse_group(
    raw: dict[str, Any],
    path: str,
) -> DataManifestSourceGroup:
    exchange = Exchange.from_str(_get_str(raw, "exchange", path))
    category = Category.from_str(_get_str(raw, "category", path))
    tickers = _parse_tickers(raw, f"{path}.tickers")
    codes = _build_codes(exchange, category, tickers)

    return DataManifestSourceGroup(
        exchange=exchange.value,
        category=category.value,
        tickers=tickers,
        codes=codes,
    )


def _parse_tickers(
    raw: dict[str, Any],
    path: str,
) -> tuple[str, ...]:
    values = _get_list(raw, "tickers", path)
    tickers: list[str] = []

    for value in values:
        if not isinstance(value, str):
            raise TypeError(f"{path} item must be str: {value!r}")

        ticker = value.upper()
        if not ticker:
            raise ValueError(f"{path} item must not be empty")

        tickers.append(ticker)

    if not tickers:
        raise ValueError(f"{path} must not be empty")

    return tuple(tickers)


def _build_codes(
    exchange: Exchange,
    category: Category,
    tickers: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(
        f"{exchange.value}_{category.value}_{ticker}" for ticker in tickers
    )


def _get_dict(
    raw: dict[str, Any],
    key: str,
) -> dict[str, Any]:
    if key not in raw:
        raise ValueError(f"Data manifest has no '{key}' section")

    return _as_dict(raw[key], key)


def _get_list(
    raw: dict[str, Any],
    key: str,
    path: str,
) -> list[Any]:
    if key not in raw:
        raise ValueError(f"{path} is required")

    value = raw[key]

    if not isinstance(value, list):
        raise TypeError(f"{path} must be list")

    return value


def _get_str(
    raw: dict[str, Any],
    key: str,
    path: str,
) -> str:
    field_path = f"{path}.{key}"

    if key not in raw:
        raise ValueError(f"{field_path} is required")

    value = raw[key]

    if not isinstance(value, str):
        raise TypeError(f"{field_path} must be str")

    if not value:
        raise ValueError(f"{field_path} must not be empty")

    return value


def _get_int(
    raw: dict[str, Any],
    key: str,
    path: str,
) -> int:
    if key not in raw:
        raise ValueError(f"{path} is required")

    value = raw[key]

    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{path} must be int")

    return value


def _as_dict(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeError(f"{path} must be table")

    return value
