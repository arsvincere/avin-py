# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import csv
from pathlib import Path
from time import perf_counter

import polars as pl

from avin.data.tic_storage import TickStorage
from avin.domain.market_data import MarketData
from avin.domain.source import Source
from avin.domain.tick import Tick
from avin.service.asset_factory import AssetFactory
from avin.service.footprint_builder import FootprintBuilder
from avin.utils.dt import DateTime, extract_range_dates, now_utc

RESULT_PATH = Path("bench/results/footprint_builder.csv")


def main() -> None:
    created_at = now_utc()
    source = Source.TINKOFF
    md = MarketData.TIC
    code = "MOEX_SHARE_SBER"
    begin = DateTime(2026, 1, 1)
    end = DateTime(2026, 2, 1)
    asset = AssetFactory.new(code)

    t0 = perf_counter()
    dfs = []
    for day in extract_range_dates(begin, end):
        df = TickStorage.load(asset.iid(), source, md, day)
        dfs.append(df)
    df = pl.concat(dfs)
    t1 = perf_counter()

    ticks = Tick.from_df(df)
    t2 = perf_counter()

    fp = FootprintBuilder.build_volume(ticks, 10_000)
    t3 = perf_counter()

    print()
    print("BENCH FOOTPRINT")
    print("-" * 40)
    print(f"rows:        {df.height}")
    print(f"ticks:       {len(ticks)}")
    print(f"clusters:    {len(fp)}")
    print()
    print(f"load df:     {t1 - t0:.3f} sec")
    print(f"df -> ticks: {t2 - t1:.3f} sec")
    print(f"build fp:    {t3 - t2:.3f} sec")
    print(f"total:       {t3 - t0:.3f} sec")

    result = {
        "created": created_at,
        "code": code,
        "begin": begin,
        "end": end,
        "rows": df.height,
        "ticks": len(ticks),
        "clusters": len(fp),
        "load df": f"{t1 - t0:.3f} sec",
        "df -> ticks": f"{t2 - t1:.3f} sec",
        "build fp": f"{t3 - t2:.3f} sec",
        "total": f"{t3 - t0:.3f} sec",
    }
    save_result(result)


def save_result(row: dict[str, object]) -> None:
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)

    exists = RESULT_PATH.exists()

    with RESULT_PATH.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))

        if not exists:
            writer.writeheader()

        writer.writerow(row)

    print("\nSaved: bench/results/footprint_builder.csv")


if __name__ == "__main__":
    main()
