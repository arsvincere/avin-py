# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

import polars as pl


def bar_schema() -> dict:
    """Polars dataframe schema for bars

    # ru
    Возвращает polars схему датафрейма для баров
    """

    schema = {
        "ts_nanos": pl.Int32,
        "open": pl.Float64,
        "high": pl.Float64,
        "low": pl.Float64,
        "close": pl.Float64,
        "volume": pl.Int32,
        "value": pl.Int32,
    }

    return schema


def tic_schema() -> dict:
    """Polars dataframe schema for tics

    # ru
    Возвращает polars схему датафрейма для тиков
    """
    schema = {
        "ts_nanos": pl.Int64,
        "direction": pl.String,
        "lots": pl.Int64,
        "price": pl.Float64,
        "value": pl.Float64,
        "session": pl.Int8,
        "tradeno": pl.Int64,
    }

    return schema


def trades_schema() -> dict:
    """Polars dataframe schema for trades stat (SuperCandle)

    # ru
    Возвращает polars схему датафрейма для trades stat (SuperCandle)
    """

    schema = {
        "ts_nanos": pl.Int64,
        "open": pl.Float64,
        "high": pl.Float64,
        "low": pl.Float64,
        "close": pl.Float64,
        "std": pl.Float64,
        "vol": pl.Int64,
        "val": pl.Float64,
        "trades": pl.Int64,
        "vwap": pl.Float64,
        "change": pl.Float64,
        "trades_b": pl.Int64,
        "trades_s": pl.Int64,
        "val_b": pl.Float64,
        "val_s": pl.Float64,
        "vol_b": pl.Int64,
        "vol_s": pl.Int64,
        "disb": pl.Float64,
        "vwap_b": pl.Float64,
        "vwap_s": pl.Float64,
    }
    return schema


def orders_schema() -> dict:
    """Polars dataframe schema for orders stat (SuperCandle)

    # ru
    Возвращает polars схему датафрейма для orders stat (SuperCandle)
    """
    schema = {
        "ts_nanos": pl.Int64,
        "put_orders_b": pl.Int64,
        "put_orders_s": pl.Int64,
        "put_val_b": pl.Float64,
        "put_val_s": pl.Float64,
        "put_vol_b": pl.Int64,
        "put_vol_s": pl.Int64,
        "put_vwap_b": pl.Float64,
        "put_vwap_s": pl.Float64,
        "put_vol": pl.Int64,
        "put_val": pl.Float64,
        "put_orders": pl.Int64,
        "cancel_orders_b": pl.Int64,
        "cancel_orders_s": pl.Int64,
        "cancel_val_b": pl.Float64,
        "cancel_val_s": pl.Float64,
        "cancel_vol_b": pl.Int64,
        "cancel_vol_s": pl.Int64,
        "cancel_vwap_b": pl.Float64,
        "cancel_vwap_s": pl.Float64,
        "cancel_vol": pl.Int64,
        "cancel_val": pl.Float64,
        "cancel_orders": pl.Int64,
    }

    return schema


def ob_schema() -> dict:
    """Polars dataframe schema for order book stat (SuperCandle)

    # ru
    Возвращает polars схему датафрейма для order book stat (SuperCandle)
    """

    schema = {
        "ts_nanos": pl.Int64,
        "spread_bbo": pl.Float64,
        "spread_lv10": pl.Float64,
        "spread_1mio": pl.Float64,
        "levels_b": pl.Int64,
        "levels_s": pl.Int64,
        "vol_b": pl.Int64,
        "vol_s": pl.Int64,
        "val_b": pl.Int64,
        "val_s": pl.Int64,
        "imbalance_vol_bbo": pl.Float64,
        "imbalance_val_bbo": pl.Float64,
        "imbalance_vol": pl.Float64,
        "imbalance_val": pl.Float64,
        "vwap_b": pl.Float64,
        "vwap_s": pl.Float64,
        "vwap_b_1mio": pl.Float64,
        "vwap_s_1mio": pl.Float64,
    }

    return schema
