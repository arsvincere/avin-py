# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta as TimeDelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from avin.utils.cmd import Cmd
from avin.utils.exceptions import ConfigNotFound

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

    raise ConfigNotFound(f"Config file not found. Tried: {candidates}")


# =========================
# Config model
# =========================


@dataclass(frozen=True)
class Configuration:
    _cfg: dict[str, Any]
    _base_path: Path = Path.home()

    # -------- paths --------

    @property
    def root(self) -> Path:
        return self._base_path / self._cfg["dir"]["root"]

    @property
    def data(self) -> Path:
        return self._base_path / self._cfg["dir"]["data"]

    @property
    def log(self) -> Path:
        return self.root / "log"

    @property
    def res(self) -> Path:
        return self.root / "res"

    @property
    def tmp(self) -> Path:
        return self.root / "tmp"

    @property
    def connect(self) -> Path:
        return self.root / "connect"

    @property
    def cache(self) -> Path:
        return self.data / "cache"

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

    # -------- helpers --------

    def get(self, *keys: str, default: Any | None = None) -> Any:
        """Safe nested access: cfg.get('trader','work_list')"""
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
