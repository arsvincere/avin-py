# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import polars as pl

TINKOFF_BAR_CSV_SCHEMA = pl.Schema(
    {
        "uid": pl.String,
        "datetime": pl.String,
        "open": pl.Float64,
        "close": pl.Float64,
        "high": pl.Float64,
        "low": pl.Float64,
        "volume": pl.Int64,
        "x": pl.String,
    }
)

TINKOFF_TIC_CSV_SCHEMA = pl.Schema(
    {
        "datetime": pl.String,
        "ticker": pl.String,
        "direction": pl.String,
        "price": pl.Float64,
        "lots": pl.Int64,
        "source": pl.String,
        "uid": pl.String,
        "x": pl.String,
    }
)
