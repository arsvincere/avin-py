# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

import polars as pl

from avin import *


def test_quantum():
    path = Path(
        "/home/alex/avin/usr/data/MOEX/SHARE/AFKS/TIC/2025/2025-09-16.parquet"
    )
    tics = Cmd.read_pqt(path)
    tics = tics.tail(10)
    tf = TimeFrame.M1

    # ┌─────────────────────┬───────────┬──────┬────────┬──────────┬─────┐
    # │ ts_nanos            ┆ direction ┆ lots ┆ price  ┆ value    ┆ ... │
    # │ ---                 ┆ ---       ┆ ---  ┆ ---    ┆ ---      ┆ --- │
    # │ i64                 ┆ str       ┆ i64  ┆ f64    ┆ f64      ┆ ... │
    # ╞═════════════════════╪═══════════╪══════╪════════╪══════════╪═════╡
    # │ 1758054666000000000 ┆ S         ┆ 10   ┆ 14.956 ┆ 14956.0  ┆ ... │
    # │ 1758054666000000000 ┆ S         ┆ 121  ┆ 14.955 ┆ 180955.5 ┆ ... │
    # │ 1758054668000000000 ┆ S         ┆ 5    ┆ 14.955 ┆ 7477.5   ┆ ... │
    # │ 1758054683000000000 ┆ S         ┆ 3    ┆ 14.955 ┆ 4486.5   ┆ ... │
    # │ 1758054712000000000 ┆ B         ┆ 10   ┆ 14.968 ┆ 14968.0  ┆ ... │
    # │ 1758054800000000000 ┆ B         ┆ 134  ┆ 14.965 ┆ 200531.0 ┆ ... │
    # │ 1758054800000000000 ┆ B         ┆ 133  ┆ 14.965 ┆ 199034.5 ┆ ... │
    # │ 1758054800000000000 ┆ B         ┆ 151  ┆ 14.966 ┆ 225986.6 ┆ ... │
    # │ 1758054862000000000 ┆ B         ┆ 10   ┆ 14.974 ┆ 14974.0  ┆ ... │
    # │ 1758054895000000000 ┆ B         ┆ 10   ┆ 14.974 ┆ 14974.0  ┆ ... │
    # └─────────────────────┴───────────┴──────┴────────┴──────────┴─────┘
    cluster = Cluster(tf, tics)
    buy = tics.filter(pl.col("direction") == "B")
    sel = tics.filter(pl.col("direction") == "S")

    assert cluster.ts == tf.prev_ts(1758054666000000000)
    assert cluster.open == 14.956
    assert cluster.high == 14.974
    assert cluster.low == 14.955
    assert cluster.close == 14.974
    assert cluster.pct == 0.12

    assert cluster.vol_b == 10 + 134 + 133 + 151 + 10 + 10
    assert cluster.vol_s == 10 + 121 + 5 + 3
    assert cluster.vol == 10 + 121 + 5 + 3 + 10 + 134 + 133 + 151 + 10 + 10

    assert cluster.val == tics["value"].sum()
    assert cluster.val_b == buy["value"].sum()
    assert cluster.val_s == sel["value"].sum()

    assert cluster.count == 10
    assert cluster.count_b == 6
    assert cluster.count_s == 4

    assert cluster.buy_p == 76.33
    assert cluster.sell_p == 23.67
    assert cluster.disb_p == 52.66

    assert cluster.vwap_b == 14.965805803571428
    assert cluster.vwap_s == 14.955071942446043
    assert cluster.vwap == 14.96326405451448
