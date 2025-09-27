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

from avin.core import Bar, Direction, Tic
from avin.manager import Manager
from avin.utils import AvinError, dt_to_ts


def ti_to_av(obj: Any):
    """Tinkoff objects to avin objects"""

    class_name = obj.__class__.__name__
    match class_name:
        case "Quotation":
            return _tiQuotation_to_avPrice(obj)
        case "Candle":
            return _tiCandle_to_avBar(obj)
        case "Trade":
            return _tiTrade_to_avTic(obj)
        case _:
            raise AvinError(f"Object={class_name}")


def _tiQuotation_to_avPrice(ti_quotation):
    price = float(quotation_to_decimal(ti_quotation))

    return price


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


def _tiTrade_to_avTic(trade: ti.Trade):
    """Trade(
        figi='BBG004730ZJ9',
        direction=<TradeDirection.TRADE_DIRECTION_BUY: 1>,
        price=Quotation(units=90, nano=840000000),
        quantity=11,
        time=datetime.datetime(
            2025, 3, 2, 13, 47, 45, 986916,
            tzinfo=datetime.timezone.utc
        ),
        instrument_uid='8e2b0325-0292-4654-8a18-4f63ed3b0e09',
        trade_source=<TradeSourceType.TRADE_SOURCE_EXCHANGE: 1>
    )
    """

    iid = Manager.find_figi(trade.figi)
    ts = dt_to_ts(trade.time)
    direction = _tiTradeDirection_to_avDirection(trade.direction)
    price = _tiQuotation_to_avPrice(trade.price)
    lots = trade.quantity
    value = iid.lot() * lots * price

    tic = Tic.new(
        ts=ts,
        direction=direction,
        price=price,
        lots=lots,
        value=value,
    )

    return tic


def _tiTradeDirection_to_avDirection(tinkoff_direction):
    td = ti.TradeDirection
    directions = {
        # td.TRADE_DIRECTION_UNSPECIFIED:
        td.TRADE_DIRECTION_BUY: Direction.BUY,
        td.TRADE_DIRECTION_SELL: Direction.SELL,
    }
    avin_direction = directions[tinkoff_direction]

    return avin_direction
