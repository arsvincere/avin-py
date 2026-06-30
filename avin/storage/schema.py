# ────────────────────────────────────────────────────────────────────────────
#  AVIN
#  Understand the market before trading it.
#
#  https://avin.info
# ────────────────────────────────────────────────────────────────────────────

import polars as pl


class Schema:
    """
    Storage dataframe schemas.

    Schema defines canonical column names and Polars types used by local
    storage. These schemas are the low-level storage contract for parquet
    files and dataframes.

    Storage, codecs and source adapters use these constants to create,
    validate and convert dataframes. This class does not load, save, convert,
    validate business meaning, or know anything about API/service/domain
    behavior.

    -- ru
    Схемы storage dataframes.

    Schema определяет канонические имена колонок и Polars-типы, которые
    используются локальным storage. Эти схемы являются низкоуровневым
    storage-контрактом для parquet-файлов и dataframes.

    Storage, codecs и source adapters используют эти константы для создания,
    проверки и конвертации dataframes. Этот класс не загружает, не сохраняет,
    не конвертирует, не валидирует бизнес-смысл и ничего не знает про
    API/service/domain поведение.
    """

    IID = pl.Schema(
        {
            "exchange": pl.String,
            "exchange_specific": pl.String,
            "category": pl.String,
            "ticker": pl.String,
            "figi": pl.String,
            "country": pl.String,
            "currency": pl.String,
            "sector": pl.String,
            "class_code": pl.String,
            "isin": pl.String,
            "uid": pl.String,
            "name": pl.String,
            "lot": pl.String,
            "step": pl.String,
            "long": pl.String,
            "short": pl.String,
            "long_qual": pl.String,
            "short_qual": pl.String,
            "first_1m": pl.String,
            "first_d": pl.String,
        }
    )

    BAR = pl.Schema(
        {
            "datetime": pl.String,
            "open": pl.Float64,
            "high": pl.Float64,
            "low": pl.Float64,
            "close": pl.Float64,
            "volume": pl.Int64,
            "ts": pl.Int64,
        }
    )

    TICK = pl.Schema(
        {
            "datetime": pl.String,
            "direction": pl.String,
            "price": pl.Float64,
            "lots": pl.Int64,
            "quantity": pl.Int64,
            "value": pl.Float64,
            "ts": pl.Int64,
        }
    )
