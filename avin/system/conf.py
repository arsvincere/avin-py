# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta as TimeDelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from avin.domain.data.source import Source
from avin.errors.exceptions import ConfigNotFoundError
from avin.utils.cmd import Cmd

# =========================
# Core Config Loader
# =========================

CONFIG_FILENAME = "config.toml"


def _search_config_file() -> Path:
    """Search config in priority order."""

    candidates = [
        Path.cwd() / CONFIG_FILENAME,
        Path.home() / ".config" / "avin" / CONFIG_FILENAME,
        Path(__file__).parents[2] / "res" / CONFIG_FILENAME,
    ]

    for path in candidates:
        if path.exists():
            return path

    raise ConfigNotFoundError(f"Config file not found. Tried: {candidates}")


# =========================
# Config model
# =========================


@dataclass(frozen=True)
class Configuration:
    _cfg: dict[str, Any]
    _base_path: Path = Path.home()

    # -------- paths --------

    @property
    def root_dir(self) -> Path:
        return self._base_path / self._cfg["dir"]["root"]

    # -------- secrets (paths) --------

    @property
    def tinkoff_token_path(self) -> Path:
        return self._base_path / self._cfg["connect"]["tinkoff_token"]

    @property
    def moex_account_path(self) -> Path:
        return self._base_path / self._cfg["connect"]["moex_account"]

    @property
    def moex_token_path(self) -> Path:
        return self._base_path / self._cfg["connect"]["moex_token"]

    # -------- log --------

    @property
    def log_history_days(self) -> int:
        return int(self._cfg["log"]["history"])

    @property
    def log_debug(self) -> bool:
        return bool(self._cfg["log"]["debug"])

    @property
    def log_info(self) -> bool:
        return bool(self._cfg["log"]["info"])

    # -------- user --------

    @property
    def local_timezone(self) -> ZoneInfo:
        return ZoneInfo(self._cfg["usr"]["timezone"])

    @property
    def offset(self) -> TimeDelta:
        return TimeDelta(hours=int(self._cfg["usr"]["offset"]))

    @property
    def dt_fmt(self) -> str:
        return self._cfg["usr"]["dt_fmt"]

    # -------- default --------

    @property
    def default_asset_list_name(self) -> str:
        return self._cfg["default"]["asset_list"]

    @property
    def default_source(self) -> Source:
        return Source(self._cfg["default"]["source"])

    @property
    def default_bars_count(self) -> int:
        return int(self._cfg["default"]["bars_count"])

    # -------- helpers --------

    def get(self, *keys: str, default: Any | None = None) -> Any:
        """Safe nested access"""
        cur: Any = self._cfg
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur


# =========================
# Public API
# =========================


def load_config() -> Configuration:
    path = _search_config_file()
    dct = Cmd.read_toml(path)
    return Configuration(dct)


cfg = load_config()
