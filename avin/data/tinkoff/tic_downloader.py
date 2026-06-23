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
from avin.data.tic_storage import TicStorage
from avin.data.tinkoff.schemas import TINKOFF_TIC_CSV_SCHEMA
from avin.utils import Cmd, Date, DateTime, TimeDelta, TimeZone, cfg, dt_to_ts


class TinkoffTicDownloader:
    SOURCE: Source = Source.TINKOFF

    def __init__(self, iid: Iid, md: MarketData, year: int) -> None:
        self.iid = iid
        self.md = md
        self.year = year

        self.tmp_dir = cfg.tmp / "tinkoff"
        self.archive_dir = self.tmp_dir / "download"
        self.extract_dir = self.tmp_dir / "extract"

    def download(self, cleanup: bool = True) -> None:
        self._prepare_workdir()

        try:
            self._download_year()
        finally:
            if cleanup:
                self._clear_workdir()

    def _prepare_workdir(self) -> None:
        if self.tmp_dir.exists():
            Cmd.delete_dir(self.tmp_dir)

        Cmd.make_dirs(self.archive_dir)
        Cmd.make_dirs(self.extract_dir)

    def _clear_workdir(self) -> None:
        Cmd.delete_dir(self.tmp_dir)

    def _download_year(self) -> None:
        start = Date(self.year, 1, 1)
        end = min(
            Date(self.year + 1, 1, 1),
            Date.today(),
        )

        day = start
        while day < end:
            df = self._download_day(day)
            if df is not None:
                TicStorage.save(self.iid, self.SOURCE, self.md, df)

            day += TimeDelta(days=1)

    def _download_day(self, day: Date) -> pl.DataFrame | None:
        time.sleep(1)  # rate limit protection

        archive_path = self._archive_path(day)
        extract_path = self._extract_path(day)

        ok = self._fetch_archive(day, archive_path)
        if not ok:
            return None

        self._extract_archive(archive_path, extract_path)

        df = self._read_day(extract_path)
        df = self._format_df(df)

        return df

    def _fetch_archive(self, day: Date, archive_path) -> bool:
        url = self._build_url(day)

        response = self._get_with_retry(url)

        # когда за сегодняшний день архива еще нет - 404
        if response.status_code == 404:
            return False

        # когда в этот день не было торгов тогда просто пустой ответ
        if not response.content:
            return False

        with open(archive_path, "wb") as f:
            f.write(response.content)

        if Cmd.size(archive_path) == 0:
            Cmd.delete(archive_path)
            return False

        return True

    def _get_with_retry(
        self, url: str, retries: int = 5
    ) -> requests.Response:
        last_exc = None

        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=30)

                if response.status_code == 404:
                    return response

                if response.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(
                        f"retryable {response.status_code}"
                    )

                response.raise_for_status()
                return response

            except (requests.RequestException, requests.HTTPError) as e:
                last_exc = e
                time.sleep((2**attempt) + random.uniform(0, 0.5))

        raise RuntimeError(f"failed request: {url}") from last_exc

    def _build_url(self, day: Date) -> str:
        return (
            "https://invest-public-api.tinkoff.ru/history-trades"
            f"/{day}"
            f"?instrumentId={self.iid.ticker}_TQBR"
        )

    def _extract_archive(self, archive_path, extract_path):
        Cmd.extract_gz(archive_path, extract_path)

    def _read_day(self, extract_path) -> pl.DataFrame:
        return pl.read_csv(
            extract_path,
            has_header=True,
            separator=",",
            schema=TINKOFF_TIC_CSV_SCHEMA,
        )

    def _format_df(self, df: pl.DataFrame) -> pl.DataFrame:
        # output df
        # ┌──────────┬───────────┬────────┬──────┬──────────┬────────┬───────┐
        # │ datetime ┆ direction ┆ price  ┆ lots ┆ quantity ┆ value  ┆ ts    │
        # │ str      ┆ str       ┆ f64    ┆ i64  ┆ i64      ┆ f64    ┆ i64   │
        # ╞══════════╪═══════════╪════════╪══════╪══════════╪════════╪═══════╡
        df = df.select(["datetime", "direction", "price", "lots"])

        df = df.with_columns(
            quantity=pl.col("lots") * self.iid.lot,
            value=pl.col("price") * pl.col("lots") * self.iid.lot,
            direction=pl.col("direction")
            .str.replace_all("BUY", "B")
            .str.replace_all("SELL", "S"),
        )

        df = df.with_columns(
            ts=pl.col("datetime").map_elements(
                lambda x: dt_to_ts(
                    DateTime.fromisoformat(x).replace(tzinfo=TimeZone.utc)
                ),
                return_dtype=pl.Int64,
            )
        )

        return df

    def _archive_path(self, day: Date):
        return self.archive_dir / f"{day}.csv.gz"

    def _extract_path(self, day: Date):
        return self.extract_dir / f"{day}.csv"
