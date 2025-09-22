# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import polars as pl

from avin.core.quantum import Quantum
from avin.core.timeframe import TimeFrame


class Cluster:
    def __init__(self, tf: TimeFrame, tics: pl.DataFrame):
        self.ts = _calc_ts(tf, tics)
        self.open = _calc_open(tics)
        self.high = _calc_high(tics)
        self.low = _calc_low(tics)
        self.close = _calc_close(tics)
        self.pct = round(((self.close - self.open) / self.open * 100.0), 2)

        self.vol_b = _calc_vol_b(tics)
        self.vol_s = _calc_vol_s(tics)
        self.vol = self.vol_b + self.vol_s

        self.val_b = _calc_val_b(tics)
        self.val_s = _calc_val_s(tics)
        self.val = self.val_b + self.val_s

        self.count_b = _calc_count_b(tics)
        self.count_s = _calc_count_s(tics)
        self.count = self.count_b + self.count_s

        self.buy_p = round((self.val_b / self.val * 100.0), 2)
        self.sell_p = round((self.val_s / self.val * 100.0), 2)
        self.disb_p = round((self.buy_p - self.sell_p), 2)

        self.vwap_b = _calc_vwap_b(tics)
        self.vwap_s = _calc_vwap_s(tics)
        self.vwap = _calc_vwap(tics)

        self.quantum = Quantum(tics)


def _calc_ts(tf: TimeFrame, tics: pl.DataFrame):
    ts = tics.item(0, "ts_nanos")
    ts = tf.prev_ts(ts)

    return ts


def _calc_open(tics: pl.DataFrame) -> float:
    return tics.item(0, "price")


def _calc_high(tics: pl.DataFrame) -> float:
    return tics["price"].max()  # type: ignore


def _calc_low(tics: pl.DataFrame) -> float:
    return tics["price"].min()  # type: ignore


def _calc_close(tics: pl.DataFrame) -> float:
    return tics.item(-1, "price")


def _calc_vol_b(tics: pl.DataFrame) -> int:
    buy = tics.filter(pl.col("direction") == "B")
    vol_b = buy["lots"].sum()

    return vol_b  # type: ignore


def _calc_vol_s(tics: pl.DataFrame) -> int:
    sell = tics.filter(pl.col("direction") == "S")
    vol_s = sell["lots"].sum()

    return vol_s  # type: ignore


def _calc_val_b(tics: pl.DataFrame) -> float:
    buy = tics.filter(pl.col("direction") == "B")
    val_b = buy["value"].sum()

    return val_b


def _calc_val_s(tics: pl.DataFrame) -> float:
    sell = tics.filter(pl.col("direction") == "S")
    val_s = sell["value"].sum()

    return val_s


def _calc_count_b(tics: pl.DataFrame) -> int:
    buy = tics.filter(pl.col("direction") == "B")
    count_b = len(buy)

    return count_b


def _calc_count_s(tics: pl.DataFrame) -> int:
    sell = tics.filter(pl.col("direction") == "S")
    count_s = len(sell)

    return count_s


def _calc_vwap(tics: pl.DataFrame) -> float:
    # Средневзвешенная цена — средняя цена сделок с учетом объема
    sum = (tics["lots"] * tics["price"]).sum()
    vol = tics["lots"].sum()

    return sum / vol


def _calc_vwap_b(tics: pl.DataFrame) -> float:
    # Средневзвешенная цена покупки — это средняя цена покупки,
    # весом которых является объем соответствующих сделок
    buy = tics.filter(pl.col("direction") == "B")

    sum = (buy["lots"] * buy["price"]).sum()
    vol = buy["lots"].sum()

    return sum / vol


def _calc_vwap_s(tics: pl.DataFrame) -> float:
    # Средневзвешенная цена покупки — это средняя цена покупки,
    # весом которых является объем соответствующих сделок
    sell = tics.filter(pl.col("direction") == "S")

    sum = (sell["lots"] * sell["price"]).sum()
    vol = sell["lots"].sum()

    return sum / vol


# Rust
# fn calc_var(tics: &[Tic]) -> f64 {
#     // Дисперсия цены — мера разброса значений цены относительно
#     // её средневзвешенной цены
#     // Дисперсией называют среднее квадрата отклонения величины
#     // от её средней.
#
#     // за среднюю в данном случае принимаем vwap
#     let _e = vwap();
#     for _tic in tics.iter() {
#         // let delta = tic.price - e;
#         todo!()
#     }
#     todo!()
# }
# fn calc_std(tics: &[Tic]) -> f64 {
#     // Стандартное отклонение цены
#     // — это мера волатильности, показывающая, насколько сильно цена
#     // акции отклоняется от средневзвешенной.
#     todo!()
# }


if __name__ == "__main__":
    ...
