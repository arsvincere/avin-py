# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from avin.domain.data.market_data import MarketData
from avin.domain.data.source import Source
from avin.domain.instrument.iid import Iid
from avin.storage.iid_storage import IidStorage
from avin.system.data_manifest import DataManifest, DataManifestSource


@dataclass(frozen=True, slots=True)
class DataSyncTask:
    iid: Iid
    source: Source
    market_data: MarketData
    group: str
    years: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class DataSyncPlan:
    tasks: tuple[DataSyncTask, ...]

    @classmethod
    def from_manifest(
        cls,
        manifest: DataManifest,
        current_year: int | None = None,
    ) -> DataSyncPlan:
        if current_year is None:
            current_year = _current_year()

        tasks: list[DataSyncTask] = []

        for manifest_source in manifest.sources:
            tasks.extend(_build_source_tasks(manifest_source, current_year))

        return cls(tasks=tuple(tasks))

    @property
    def is_empty(self) -> bool:
        return not self.tasks


def _current_year() -> int:
    return date.today().year


def _build_source_tasks(
    manifest_source: DataManifestSource,
    current_year: int,
) -> list[DataSyncTask]:
    years = _build_years(current_year, manifest_source.history_years)
    tasks: list[DataSyncTask] = []

    for group in manifest_source.groups:
        tasks.extend(
            _build_group_tasks(
                source=manifest_source.source,
                market_data=manifest_source.market_data,
                group=group.name,
                codes=group.codes,
                years=years,
            )
        )

    return tasks


def _build_group_tasks(
    source: Source,
    market_data: tuple[MarketData, ...],
    group: str,
    codes: tuple[str, ...],
    years: tuple[int, ...],
) -> list[DataSyncTask]:
    tasks: list[DataSyncTask] = []

    for code in codes:
        iid = IidStorage.find_code(code, source)

        for md in market_data:
            tasks.append(
                DataSyncTask(
                    iid=iid,
                    source=source,
                    market_data=md,
                    group=group,
                    years=years,
                )
            )

    return tasks


def _build_years(
    current_year: int,
    history_years: int,
) -> tuple[int, ...]:
    if history_years < 1:
        raise ValueError("history_years must be positive")

    return tuple(range(current_year, current_year - history_years, -1))
