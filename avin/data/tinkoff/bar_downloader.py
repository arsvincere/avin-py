# ============================================================================
# URL:          http://arsvincjre.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import random
import time

import polars as pl
import requests

from avin.core.iid import Iid
from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.data.bar_storage import BarStorage
from avin.data.tinkoff.schemas import TINKOFF_BAR_CSV_SCHEMA
from avin.utils import Cmd, DateTime, cfg, dt_to_ts


class TinkoffBarDownloader:
    SOURCE: Source = Source.TINKOFF

    def __init__(self, iid: Iid, md: MarketData, year: int):
        self.iid = iid
        self.md = md
        self.year = year

        self.tmp_dir = cfg.tmp / "tinkoff"

        e = self.iid.exchange.name
        c = self.iid.category.name
        t = self.iid.ticker
        prefix = f"{e}-{c}-{t}-{self.md}"

        archive_name = f"{prefix}-{self.year}.zip"
        self.archive_path = self.tmp_dir / "download" / archive_name

        extract_dir_name = f"{prefix}-{self.year}"
        self.extract_path = self.tmp_dir / "extract" / extract_dir_name

    def download(self, cleanup: bool = True) -> None:
        self._prepare_workdir()

        try:
            self._download_archive()
            self._extract_archive()

            tinkoff_df = self._read_tinkoff_csv_files()
            df = self._format_tinkoff_df(tinkoff_df)

            BarStorage.save(self.iid, self.SOURCE, self.md, df)

        finally:
            if cleanup:
                Cmd.delete_dir(self.tmp_dir)

    def _prepare_workdir(self):
        if self.tmp_dir.exists():
            Cmd.delete_dir(self.tmp_dir)

        Cmd.make_dirs(self.tmp_dir / "download")
        Cmd.make_dirs(self.tmp_dir / "extract")

    def _build_url(self) -> str:
        uid = self.iid.dump_raw_info()["uid"]

        return (
            f"https://invest-public-api.tinkoff.ru/history-data"
            f"?instrumentId={uid}"
            f"&year={self.year}"
        )

    def _download_archive(self):
        url = self._build_url()

        response = self._get_with_retry(url)
        if not response.content:
            raise ValueError(
                f"Market data for {self.iid}-{self.year} unavailable"
            )

        with open(self.archive_path, "wb") as f:
            f.write(response.content)

    def _get_with_retry(
        self, url: str, retries: int = 5
    ) -> requests.Response:
        last_exc = None

        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=30)

                # retryable HTTP codes
                if response.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(
                        f"retryable status {response.status_code}"
                    )

                response.raise_for_status()
                return response

            except (requests.RequestException, requests.HTTPError) as e:
                last_exc = e

                sleep_time = (2**attempt) + random.uniform(0, 0.5)
                time.sleep(sleep_time)

        raise RuntimeError(f"failed to fetch {url}") from last_exc

    def _extract_archive(self):
        Cmd.extract_zip(self.archive_path, self.extract_path)

    def _read_tinkoff_csv_files(self) -> pl.DataFrame:
        files = sorted(Cmd.get_files(self.extract_path, full_path=True))
        if not files:
            raise FileNotFoundError("No CSV files found")

        df = pl.concat(
            pl.read_csv(
                file,
                has_header=False,
                separator=";",
                schema=TINKOFF_BAR_CSV_SCHEMA,
            )
            for file in files
        )

        return df

    @staticmethod
    def _format_tinkoff_df(tinkoff_df: pl.DataFrame) -> pl.DataFrame:
        """Convert Tinkoff CSV schema to AVIN bar schema.

        Input:
            uid, datetime, open, close, high, low, volume, x
            str  str       f64   f64    f64   f64  f64     null

        Output:
            datetime, open, high, low, close, volume, ts
            str       f64   f64   f64  f64    i64     i64
        """

        # 1. extract base columns (drop uid/x early)
        df = tinkoff_df.select(
            ["datetime", "open", "high", "low", "close", "volume"]
        )

        # 2. deterministic timestamp conversion (no Polars parser surprises)
        df = df.with_columns(
            pl.col("datetime")
            .map_elements(
                lambda x: dt_to_ts(DateTime.fromisoformat(x)),
                return_dtype=pl.Int64,
            )
            .alias("ts")
        )

        return df
