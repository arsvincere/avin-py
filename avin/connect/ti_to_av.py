# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

from typing import Any

import tinkoff.invest as ti
from tinkoff.invest.utils import quotation_to_decimal

from avin.core import Bar
from avin.utils import AvinError, dt_to_ts


def ti_to_av(obj: Any):
    """Tinkoff objects to avin objects"""

    class_name = obj.__class__.__name__
    match class_name:
        case "Candle":
            return _tiCandle_to_avBar(obj)
        case _:
            raise AvinError(f"Object={class_name}")


def _tiCandle_to_avBar(candle: ti.Candle) -> Bar:
    """Candle(
        figi='BBG004730N88',
        interval=<SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE: 1>,
        open=Quotation(units=295, nano=690000000),
        high=Quotation(units=295, nano=690000000),
        low=Quotation(units=295, nano=460000000),
        close=Quotation(units=295, nano=460000000),
        volume=14,
        time=datetime.datetime(
            2025, 9, 21, 7, 33, tzinfo=datetime.timezone.utc
        ),
        last_trade_ts=datetime.datetime(
            2025, 9, 21, 7, 33, 30, 882150, tzinfo=datetime.timezone.utc
        ),
        instrument_uid='e6123145-9665-43e0-8413-cd61b8aa9b13',
        candle_source_type=<CandleSource.CANDLE_SOURCE_DEALER_WEEKEND: 2>
    )
    """

    o = float(quotation_to_decimal(candle.open))
    h = float(quotation_to_decimal(candle.high))
    l = float(quotation_to_decimal(candle.low))
    c = float(quotation_to_decimal(candle.close))
    v = candle.volume
    dt = candle.time
    ts = dt_to_ts(dt)

    bar = Bar.from_ohlcv(ts, o, h, l, c, v)

    return bar
