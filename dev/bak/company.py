#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

"""doc
Разбить на два модуля:
    - general
    - tester

Эти модули лежат на ружу, файлами в корне
А все мои более глубокие штуки будут лежать уже в поддиректориях

"""

import asyncio
import logging
import sys

sys.path.append("/home/alex/ya/avin-dev/")
sys.path.append("/usr/lib/python3.12/site-packages")
# sys.path.append("/home/alex/.local/lib/python3.11/site-packages/tinkoff")
# sys.path.append("/home/alex/.local/lib/python3.11/site-packages/tinkoff/invest")
import time as timer
from datetime import date, datetime, time
from decimal import Decimal

import tinkoff.invest

# }}}
from tinkoff.invest import (  # {{{
    AsyncClient,
    CandleInterval,
    Client,
    MoneyValue,
    OrderDirection,
    OrderExecutionReportStatus,
    OrderType,
    PostOrderResponse,
    StopOrderDirection,
    StopOrderType,
    SubscriptionInterval,
)

# }}}
from tinkoff.invest.async_services import (  # {{{
    AsyncMarketDataStreamManager,
)
from tinkoff.invest.constants import (  # {{{
    INVEST_GRPC_API,
    INVEST_GRPC_API_SANDBOX,
)

# }}}
from tinkoff.invest.schemas import (  # {{{
    CandleInstrument,
)

# }}}
# }}}
from tinkoff.invest.utils import (  # {{{
    decimal_to_quotation,
    money_to_decimal,
    quotation_to_decimal,
)

# }}}
from avin.const import (  # {{{
    ASSET_DIR,
    ONE_SECOND,
    UTC,
)

# }}}
from avin.core import (  # {{{
    Asset,
    AssetList,
    Bar,
    Data,
    Event,
    Exchange,
    Message,
    Operation,
    Order,
    Portfolio,
    Position,
    Range,
    Share,
    Signal,
    Strategy,
    Test,
    TimeFrame,
    TinkoffId,
    Type,
)

# }}}
from avin.utils import (  # {{{
    Cmd,
    now,
)

# }}}
logger = logging.getLogger("LOGGER")


class CompanyError(Exception):
    pass


class Analytic:  # {{{
    def __init__(self, general=None):  # {{{
        self.__general = general

    # }}}
    def __loadSizeClassify(asset, element):  # {{{
        path = Cmd.join(asset.analytic_dir, f"{element}.json")
        obj = Cmd.loadJSON(path)
        classify = dict()
        for k, v in obj.items():
            size = eval(f"Range.{k}")
            range_ = eval(v)
            classify.setdefault(size, range_)
        return classify

    # }}}
    @staticmethod  # size# {{{
    def size(range_: Range):
        asset = range_.parent().parent().parent()
        element = range_.type.name.lower()
        classification = Analytic.__loadSizeClassify(asset, element)
        p = range_.percent()
        for size, range_ in classification.items():
            if p in range_:
                return size
        bs = classification[Range.Size.BLACKSWAN_SMALL]
        if p < bs.min:
            return Range.Size.BLACKSWAN_SMALL
        bb = classification[Range.Size.BLACKSWAN_BIG]
        if p > bs.max:
            return Range.Size.BLACKSWAN_BIG

    # }}}
    @property  # general# {{{
    def general(self):
        return self.general

    # }}}
    def start(self):  # {{{
        ...
    # }}}
    def process(self, signal):  # {{{
        self.__info = dict()
        signal.info.setdefault("analytic", self.__info)

    # }}}
    def finish(self):  # {{{
        ...

    # }}}


# }}}
class Market:  # {{{
    def __init__(self, general=None):  # {{{
        self.__general = general

    # }}}
    @property  # general# {{{
    def general(self):
        return self.__general

    # }}}
    def process(self, signal):  # {{{
        self.info = dict()
        signal.info.setdefault("market", self.info)

    # }}}


# }}}
class Risk:  # {{{
    def __init__(self, general=None):  # {{{
        self.__general = general

    # }}}
    def __setMaxShares(self, signal: Signal):  # {{{
        if signal.close_condition == Signal.Close.STOP_TAKE:
            self.__processStopTake(signal)
        else:
            self.__processNoneStop(signal)

    # }}}
    def __processNoneStop(self, signal: Signal):  # {{{
        deposit = signal.info["strategy"]["deposit"]
        max_shares = int(deposit / signal.open_price)
        self.info.setdefault("max shares", max_shares)

    # }}}
    def __processStopTake(self, signal: Signal):  # {{{
        R = signal.info["strategy"]["r"]
        risk = abs(signal.open_price - signal.stop_price)
        max_shares = int(R / risk)
        profit = abs(signal.open_price - signal.take_price)
        pr = round(profit / risk, 2)
        self.info.setdefault("max shares", max_shares)
        self.info.setdefault("p/r", pr)

    # }}}
    def __setMaxLots(self, signal):  # {{{
        max_shares = self.info["max shares"]
        lotX = signal.asset.lot
        amount = signal.open_price * max_shares
        free = 1_000_000
        self.info.setdefault("free", free)
        if amount <= free:
            self.info.setdefault("status", "ALLOW")
        else:
            self.info.setdefault("status", "DEPRICATE")
            max_shares = int(free / signal.open_price)
            self.info.setdefault("change max shares", max_shares)
        max_lots = int(max_shares / lotX)
        self.info.setdefault("max lots", max_lots)

    # }}}
    @property  # general# {{{
    def general(self):
        return self.__general

    # }}}
    def process(self, signal):  # {{{
        self.info = dict()
        self.__setMaxShares(signal)
        self.__setMaxLots(signal)
        signal.info.setdefault("risk", self.info)

    # }}}


# }}}
class Ruler:  # {{{
    def __init__(self, general=None):  # {{{
        self.__general = general

    # }}}
    @property  # general# {{{
    def parent(self):
        return self.__general
        # }}}

    def setPortfolio(self, portfolio):  # {{{
        self.portfolio = portfolio

    # }}}
    def process(self, signal):  # {{{
        self.__info = dict()
        signal.info.setdefault("ruler", self.__info)

    # }}}


# }}}
class Adviser:  # {{{
    def __init__(self, general=None):  # {{{
        self.__general = general

    # }}}
    @property  # general# {{{
    def general(self):
        return self.__general

    # }}}
    def process(self, signal):  # {{{
        self.__info = dict()
        signal.info.setdefault("adviser", self.__info)

    # }}}


# }}}
class Tester:  # {{{
    """const"""  # {{{

    PROGRESS_EMIT_PERIOD = ONE_SECOND * 1
    # }}}
    """ signal """  # {{{
    progress = Message(int)

    # }}}
    def __init__(self):  # {{{
        self.test = None
        self.portfolio = None
        self.strategy = None
        self.time = None
        self.analytic = None
        self.risk = None
        self.ruler = None
        self.signals = list()

    # }}}
    def __openPosition(self, signal: Signal):  # {{{
        if signal.type == Signal.Type.LONG:
            direction = Operation.Direction.BUY
        else:
            direction = Operation.Direction.SELL
        open_price = signal.asset.chart("1M").now.open
        quantity = signal.info["risk"]["max lots"] * signal.asset.lot
        amount = open_price * quantity
        commission = amount * self.test.commission
        op = Operation(
            signal=signal,
            dt=signal.asset.chart("1M").now.dt,
            direction=direction,
            asset=signal.asset,
            lots=signal.info["risk"]["max lots"],
            price=open_price,
            quantity=quantity,
            amount=amount,
            commission=commission,
        )
        pos = Position(signal, op)
        signal.status = Signal.Status.OPEN
        return pos

    # }}}
    def __closePosition(self, pos: Position, close_price: float):  # {{{
        if pos.signal.type == Signal.Type.LONG:
            direction = Operation.Direction.SELL
        else:
            direction = Operation.Direction.BUY
        quantity = abs(pos.quantity())
        amount = close_price * quantity
        commission = amount * self.test.commission
        op = Operation(
            signal=pos.signal,
            dt=pos.asset.chart("1M").now.dt,
            direction=direction,
            asset=pos.asset,
            lots=abs(pos.lots()),
            price=close_price,
            quantity=quantity,
            amount=amount,
            commission=commission,
        )
        pos.add(op)
        assert pos.status == Position.Status.CLOSE
        return pos

    # }}}
    def __checkCloseCondition(self, pos, bar: Bar):  # {{{
        """TODO : тут все надо перелопатить нормально создавать
        ордер операцию и вот это вот все"""
        info = pos.signal.info["strategy"]
        if info["close_condition"] == Signal.Close.ON_CLOSE:
            if bar.dt.time() == time(15, 45):
                close_price = bar.close
                self.__closePosition(pos, close_price)

    # }}}
    def __checkStopLoss(self, pos: Position, bar: Bar):  # {{{
        info = pos.signal.info["strategy"]
        signal = pos.signal
        if info["close_condition"] != Signal.Close.STOP_TAKE:
            return
        stop_price = info["stop_price"]
        if stop_price in bar:
            close_price = stop_price
            self.__closePosition(pos, close_price)
        # проверим возможно гепом перелетели через стоп
        elif (
            signal.isShort()
            and bar.open >= stop_price
            or signal.isLong()
            and bar.open <= stop_price
        ):
            close_price = bar.open
            self.__closePosition(pos, close_price)

    # }}}
    def __checkTakeProfit(self, pos, bar):  # {{{
        info = pos.signal.info["strategy"]
        signal = pos.signal
        if info["close_condition"] != Signal.Close.STOP_TAKE:
            return
        take_price = info["take_price"]
        if take_price in bar:
            close_price = take_price
            self.__closePosition(pos, close_price)
        # проверим возможно гепом перелетели через стоп
        elif (
            signal.isShort()
            and bar.open <= take_price
            or signal.isLong()
            and bar.open >= take_price
        ):
            close_price = bar.open
            self.__closePosition(pos, close_price)

    # }}}
    def __nextTime(self):  # {{{
        self.time += self.test.timeframe
        for timeframe in self.strategy.timeframe_list:
            chart = self.current_asset.chart(timeframe)
            while self.time >= chart.now.dt:
                result = chart._nextHead()
                if result is None:
                    break

    # }}}
    def __emitProgress(self):  # {{{
        passed_time = now() - self.last_emit
        if passed_time > self.PROGRESS_EMIT_PERIOD:
            complete = (self.time - self.test.begin).total_seconds()
            progress = int(complete / self.total_time * 100)
            self.progress.emit(progress)
            self.last_emit = now()

    # }}}
    def __loadStrategy(self):  # {{{
        logger.info(f"Tester load strategy {self.test.strategy}")
        name = self.test.strategy
        ver = self.test.version
        self.strategy = Strategy.load(name, ver, general=self)
        self.strategy.long_list = self.test.alist
        self.strategy.short_list = self.test.alist
        self.strategy.signal.connect(self.__receiveSignal)

    # }}}
    def __loadPortfolio(self):  # {{{
        logger.info("Tester load portfolio")
        self.portfolio = Portfolio(
            cash=list(),
            shares=list(),
            bounds=list(),
            futures=list(),
            options=list(),
        )
        self.portfolio.virtualSetMoney(self.test.deposit)

    # }}}
    def __loadTeam(self):  # {{{
        logger.info("Tester load team")
        self.analytic = Analytic(general=self)
        self.market = Market(general=self)
        self.risk = Risk(general=self)
        self.ruler = Ruler(general=self)
        self.ruler.setPortfolio(self.portfolio)
        self.adviser = Adviser(general=self)

    # }}}
    def __loadChart(self):  # {{{
        for timeframe in self.strategy.timeframe_list:
            logger.info(
                f"Tester load chart {self.current_asset.ticker}-{timeframe}"
            )
            self.current_asset.loadChart(
                timeframe,
                self.test.begin,
                self.test.end,
            )
            self.current_asset.chart(timeframe)._setHeadIndex(0)

    # }}}
    def __setCurrentAsset(self, asset):  # {{{
        self.current_asset = asset

    # }}}
    def __setTime(self):  # {{{
        self.time = self.test.begin
        self.total_time = (self.test.end - self.test.begin).total_seconds()
        self.progress.emit(0)
        self.last_emit = now()

    # }}}
    def __startTest(self):  # {{{
        logger.info(f"Start test {self.current_asset.ticker}")
        self.strategy.start()
        self.__setTime()
        while self.time <= self.test.end:
            self.__processStrategy()
            self.__processSignals()
            self.__processOpenPositions()
            self.__removeClosedPositions()
            self.__emitProgress()
            self.__nextTime()

    # }}}
    def __processStrategy(self):  # {{{
        self.strategy.process(self.current_asset)

    # }}}
    def __processSignals(self):  # {{{
        while len(self.signals) > 0:
            signal = self.signals[0]
            self.analytic.process(signal)
            self.market.process(signal)
            self.risk.process(signal)
            self.ruler.process(signal)
            self.adviser.process(signal)
            pos = self.__openPosition(signal)
            if pos is not None:
                self.portfolio.add(pos)
            self.signals.pop(0)

    # }}}
    def __processOpenPositions(self):  # {{{
        for pos in self.portfolio.positions:
            flag = False
            bar = pos.signal.asset.chart("1M").now
            self.__checkStopLoss(pos, bar)
            self.__checkTakeProfit(pos, bar)
            self.__checkCloseCondition(pos, bar)
            if pos.status == Position.Status.CLOSE:
                pos.signal.status = Signal.Status.CLOSE
                trade = Signal.toTrade(pos.signal)
                self.test.tlist.add(trade)

    # }}}
    def __removeClosedPositions(self):  # {{{
        i = 0
        while i < len(self.portfolio.positions):
            pos = self.portfolio.positions[i]
            if pos.status == Position.Status.CLOSE:
                self.portfolio.positions.pop(i)
            else:
                i += 1

    # }}}
    def __finishTest(self):  # {{{
        logger.info(f"Finish test {self.current_asset.ticker}")
        self.strategy.finish()
        self.portfolio.positions.clear()
        self.current_asset.closeAllChart()
        self.signals.clear()

    # }}}
    def __createReport(self):  # {{{
        self.test.updateReport()

    # }}}
    def __saveTest(self):  # {{{
        Test.save(self.test)
        logger.info("Test saved")

    # }}}
    def __clearAll(self):  # {{{
        self.test = None
        self.strategy = None
        self.portfolio = None
        self.analytic = None
        self.market = None
        self.risk = None
        self.ruler = None
        self.current_asset = None
        self.signals.clear()

    # }}}
    def __receiveSignal(self, signal: Signal):  # {{{
        logger.debug("Tester.__receiveSignal()")
        logger.info(str(signal))
        signal.status = Signal.Status.NEW
        self.signals.append(signal)

    # }}}
    def setTest(self, test):  # {{{
        self.__clearAll()
        self.test = test
        self.test.status = Test.Status.PROCESS

    # }}}
    def runTest(self):  # {{{
        logger.info("Test run")
        self.test.clear()
        self.__loadStrategy()
        self.__loadPortfolio()
        self.__loadTeam()
        for asset in self.test.alist:
            self.__setCurrentAsset(asset)
            self.__loadChart()
            self.__startTest()
            self.__finishTest()
        self.test.status = Test.Status.COMPLETE
        self.__createReport()
        self.__saveTest()
        logger.info(f"Test '{self.test.name}' complete!")
        self.__clearAll()

    # }}}


# }}}
class Broker:  # {{{
    def __init__(self):  # {{{
        ...

    # }}}


# }}}
class Tinkoff(Broker):  # {{{
    TARGET = INVEST_GRPC_API  # {{{
    TOKEN_FULL = Cmd.read(
        "/home/alex/ya/arsvincere/user/broker/Tinkoff/full_access.txt"
    ).strip()

    # }}}
    def __init__(self, general=None):  # {{{
        Broker.__init__(self)
        self._general = general
        self._client = None
        self._connect = False

    # }}}
    @staticmethod  # _CandleIntervalFrom# {{{
    def _CandleIntervalFrom(
        timeframe: TimeFrame,
    ) -> tinkoff.invest.CandleInterval:
        intervals = {
            "1M": CandleInterval.CANDLE_INTERVAL_1_MIN,
            "5M": CandleInterval.CANDLE_INTERVAL_5_MIN,
            "1H": CandleInterval.CANDLE_INTERVAL_HOUR,
            "D": CandleInterval.CANDLE_INTERVAL_DAY,
            "W": CandleInterval.CANDLE_INTERVAL_WEEK,
            "M": CandleInterval.CANDLE_INTERVAL_MONTH,
        }
        return intervals[str(timeframe)]

    # }}}
    @staticmethod  # _SubscriptionIntervalFrom# {{{
    def _SubscriptionIntervalFrom(
        timeframe: TimeFrame,
    ) -> tinkoff.invest.SubscriptionInterval:
        intervals = {
            "1M": SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
            "5M": SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES,
            "1H": SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_HOUR,
            "D": SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_DAY,
            "W": SubscriptionInterval.SUBSCRIPTION_INTERVAL_WEEK,
            "M": SubscriptionInterval.SUBSCRIPTION_INTERVAL_MONTH,
        }
        return intervals[str(timeframe)]

    # }}}
    @staticmethod  # _OrderTypeFrom# {{{
    def _OrderTypeFrom(order: Order):
        ot = tinkoff.invest.OrderType
        sot = tinkoff.invest.StopOrderType
        if order.type == Order.Type.MARKET:
            return ot.ORDER_TYPE_MARKET
        if order.type == Order.Type.LIMIT:
            return ot.ORDER_TYPE_LIMIT
        if order.type == Order.Type.STOP_LOSS:
            return sot.STOP_ORDER_TYPE_STOP_LOSS
        if order.type == Order.Type.TAKE_PROFIT:
            return sot.STOP_ORDER_TYPE_TAKE_PROFIT
        if order.type == Order.Type.STOP:
            current_price = Tinkoff.getLastPrice(order.asset)
            if order.direction == Order.Direction.BUY:
                if current_price >= order.price:
                    return sot.STOP_ORDER_TYPE_TAKE_PROFIT
                if current_price < order.price:
                    return sot.STOP_ORDER_TYPE_STOP_LOSS
            elif order.direction == Order.Direction.SELL:
                if current_price <= order.price:
                    return sot.STOP_ORDER_TYPE_TAKE_PROFIT
                if current_price > order.price:
                    return sot.STOP_ORDER_TYPE_STOP_LOSS

    # }}}
    @staticmethod  # _OrderDirectionFrom# {{{
    def _OrderDirectionFrom(order: Order):
        if order.type in (Order.Type.MARKET, Order.Type.LIMIT):
            if order.direction == Order.Direction.BUY:
                return tinkoff.invest.OrderDirection.ORDER_DIRECTION_BUY
            if order.direction == Order.Direction.SELL:
                return tinkoff.invest.OrderDirection.ORDER_DIRECTION_SELL
            return tinkoff.invest.OrderDirection.ORDER_DIRECTION_UNSPECIFIED
        if order.type in (
            Order.Type.STOP_LOSS,
            Order.Type.TAKE_PROFIT,
            Order.Type.STOP,
            Order.Type.WAIT,
        ):
            if order.direction == Order.Direction.BUY:
                return (
                    tinkoff.invest.StopOrderDirection.STOP_ORDER_DIRECTION_BUY
                )
            if order.direction == Order.Direction.SELL:
                return tinkoff.invest.StopOrderDirection.STOP_ORDER_DIRECTION_SELL
            return StopOrderDirection.STOP_ORDER_DIRECTION_UNSPECIFIED

    # }}}
    @staticmethod  # _QuotationFrom# {{{
    def _QuotationFrom(price: float):
        if price is None:
            return None
        else:
            quotation = decimal_to_quotation(Decimal(price))
            return quotation

    # }}}
    @staticmethod  # _expirationTypeFrom# {{{
    def _expirationTypeFrom(order: Order):
        if order.type == Order.Type.MARKET:
            return None
        if order.type == Order.Type.LIMIT:
            return None
        if order.type == Order.Type.STOP:
            return tinkoff.invest.StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL
        if order.type == Order.Type.TAKE:
            return tinkoff.invest.StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL

    # }}}
    @staticmethod  # _toTimeFrame# {{{
    def _toTimeFrame(tinkoff_interval) -> TimeFrame:
        si = SubscriptionInterval
        ci = CandleInterval
        if isinstance(tinkoff_interval, SubscriptionInterval):
            intervals = {
                si.SUBSCRIPTION_INTERVAL_ONE_MINUTE: "1M",
                si.SUBSCRIPTION_INTERVAL_FIVE_MINUTES: "5M",
                si.SUBSCRIPTION_INTERVAL_ONE_HOUR: "1H",
                si.SUBSCRIPTION_INTERVAL_ONE_DAY: "D",
                si.SUBSCRIPTION_INTERVAL_WEEK: "W",
                si.SUBSCRIPTION_INTERVAL_MONTH: "M",
            }
            string = intervals[tinkoff_interval]
        elif isinstance(tinkoff_interval, CandleInterval):
            intervals = {
                ci.CANDLE_INTERVAL_1_MIN: "1M",
                ci.CANDLE_INTERVAL_5_MIN: "5M",
                ci.CANDLE_INTERVAL_HOUR: "1H",
                ci.CANDLE_INTERVAL_DAY: "D",
                ci.CANDLE_INTERVAL_WEEK: "W",
                ci.CANDLE_INTERVAL_MONTH: "M",
            }
            string = intervals[tinkoff_interval]
        else:
            assert False, "unknow interval type '{type(tinkoff_interval)}'"
        return TimeFrame(string)

    # }}}
    @staticmethod  # _toBar# {{{
    def _toBar(candle, constructor=Bar) -> Bar:
        opn = float(quotation_to_decimal(candle.open))
        cls = float(quotation_to_decimal(candle.close))
        hgh = float(quotation_to_decimal(candle.high))
        low = float(quotation_to_decimal(candle.low))
        vol = candle.volume
        dt = candle.time
        bar = constructor(dt, opn, hgh, low, cls, vol)
        return bar

    # }}}
    @staticmethod  # _getOperationAsset# {{{
    def _getOperationAsset(tinkoff_operation: tinkoff.invest.Operation):
        if tinkoff_operation.instrument_type == "share":
            asset = Asset(
                exchange=Exchange.MOEX,
                asset_type=Type.SHARE,
                uid=tinkoff_operation.instrument_uid,
            )
            return Share(asset.ticker)

    # }}}
    @staticmethod  # _getOperationDirection# {{{
    def _getOperationDirection(tinkoff_operation: tinkoff.invest.Operation):
        if (
            tinkoff_operation.operation_type
            == tinkoff.invest.OperationType.OPERATION_TYPE_BUY
        ):
            return Operation.Direction.BUY
        if (
            tinkoff_operation.operation_type
            == tinkoff.invest.OperationType.OPERATION_TYPE_SELL
        ):
            return Operation.Direction.SELL

    # }}}
    @staticmethod  # _getOperations# {{{
    def _getOperations(response: tinkoff.invest.OperationsResponse):
        operations = list()
        for i in response.operations:
            if i.operation_type in (
                tinkoff.invest.OperationType.OPERATION_TYPE_BUY,
                tinkoff.invest.OperationType.OPERATION_TYPE_SELL,
            ):
                asset = Tinkoff._getOperationAsset(i)
                op = Operation(
                    signal=None,
                    dt=i.date,
                    direction=Tinkoff._getOperationDirection(i),
                    asset=asset,
                    lots=int(i.quantity / asset.lot),
                    quantity=i.quantity,
                    price=float(money_to_decimal(i.price)),
                    amount=abs(float(money_to_decimal(i.payment))),
                    commission=0,
                    broker_info=i,
                )
                operations.append(op)
        return operations

    # }}}
    @staticmethod  # _getMoney# {{{
    def _getMoney(response: tinkoff.invest.PositionsResponse):
        money = list()
        for i in response.money:
            currency = i.currency
            val = float(money_to_decimal(i))
            block = None
            cash = Portfolio.Cash(currency, val, block)
            money.append(cash)
        return money

    # }}}
    @staticmethod  # _getShares# {{{
    def _getShares(response: tinkoff.invest.PositionsResponse):
        shares = list()
        for i in response.securities:
            if i.instrument_type != "share":
                continue
            figi = i.figi
            asset = Asset.assetByFigi(figi)
            balance = i.balance
            block = i.blocked
            ID = i.position_uid
            s = Portfolio.Share(asset, balance, block, ID, i)
            shares.append(s)
        return shares

    # }}}
    @staticmethod  # _getBounds# {{{
    def _getBounds(response: tinkoff.invest.PositionsResponse):
        return list()

    # }}}
    @staticmethod  # _getFutures# {{{
    def _getFutures(response: tinkoff.invest.PositionsResponse):
        return list()

    # }}}
    @staticmethod  # _getOptions# {{{
    def _getOptions(response: tinkoff.invest.PositionsResponse):
        return list()

    # }}}
    @staticmethod  # _getOrderAsset# {{{
    def _getOrderAsset(response: tinkoff.invest.OrderState):
        figi = response.figi
        asset = TinkoffId.assetByFigi(figi)
        return asset

    # }}}
    @staticmethod  # _getOrderType# {{{
    def _getOrderType(response: tinkoff.invest.OrderState):
        ot = OrderType
        sot = StopOrderType
        types = {
            "ORDER_TYPE_UNSPECIFIED": Order.Type.UNDEFINE,
            "ORDER_TYPE_LIMIT": Order.Type.LIMIT,
            "ORDER_TYPE_MARKET": Order.Type.MARKET,
            "ORDER_TYPE_BESTPRICE": Order.Type.MARKET,
            "STOP_ORDER_TYPE_UNSPECIFIED": Order.Type.UNDEFINE,
            "STOP_ORDER_TYPE_TAKE_PROFIT": Order.Type.TAKE_PROFIT,
            "STOP_ORDER_TYPE_STOP_LOSS": Order.Type.STOP_LOSS,
            "STOP_ORDER_TYPE_STOP_LIMIT": Order.Type.STOP,
        }
        tinkoff_order_type = response.order_type.name
        avin_type = types[tinkoff_order_type]
        return avin_type

    # }}}
    @staticmethod  # _getOrderDirection# {{{
    def _getOrderDirection(response: tinkoff.invest.OrderState):
        od = OrderDirection
        sod = StopOrderDirection
        directions = {
            "ORDER_DIRECTION_UNSPECIFIED": Order.Direction.UNDEFINE,
            "ORDER_DIRECTION_BUY": Order.Direction.BUY,
            "ORDER_DIRECTION_SELL": Order.Direction.SELL,
            "STOP_ORDER_DIRECTION_UNSPECIFIED": Order.Direction.UNDEFINE,
            "STOP_ORDER_DIRECTION_BUY": Order.Direction.BUY,
            "STOP_ORDER_DIRECTION_SELL": Order.Direction.SELL,
        }
        tinkoff_order_direction = response.direction.name
        avin_direction = directions[tinkoff_order_direction]
        return avin_direction

    # }}}
    @staticmethod  # _getLimitOrderStatus# {{{
    def _getLimitOrderStatus(response: tinkoff.invest.OrderState):
        oers = OrderExecutionReportStatus
        statuses = {
            oers.EXECUTION_REPORT_STATUS_UNSPECIFIED: Order.Status.UNDEFINE,
            oers.EXECUTION_REPORT_STATUS_FILL: Order.Status.FILL,
            oers.EXECUTION_REPORT_STATUS_REJECTED: Order.Status.REJECT,
            oers.EXECUTION_REPORT_STATUS_CANCELLED: Order.Status.CANCEL,
            oers.EXECUTION_REPORT_STATUS_NEW: Order.Status.POST,
            oers.EXECUTION_REPORT_STATUS_PARTIALLYFILL: Order.Status.PARTIAL,
        }
        tinkoff_status = response.execution_report_status
        avin_status = statuses[tinkoff_status]
        return avin_status

    # }}}
    @staticmethod  # _getLimitOrderPrice# {{{
    def _getLimitOrderPrice(response: tinkoff.invest.OrderState):
        money_value = response.initial_security_price
        price = float(money_to_decimal(money_value))
        return price

    # }}}
    @staticmethod  # _getStopOrderActivationPrice# {{{
    def _getStopOrderActivationPrice(response: tinkoff.invest.StopOrder):
        money_value = response.stop_price
        price = float(money_to_decimal(money_value))
        return price

    # }}}
    @staticmethod  # _getOrderAsset# {{{
    def _getOrderCommission(response: tinkoff.invest.OrderState):
        money_value = response.initial_commission
        commission = float(money_to_decimal(money_value))
        return commission

    # }}}
    @staticmethod  # _getOrderExecPrice# {{{
    def _getOrderExecPrice(response: tinkoff.invest.OrderState):
        money_value = response.executed_order_price
        price = float(money_to_decimal(money_value))
        if price:
            return price
        else:
            return None

    # }}}
    @staticmethod  # _getLimitOrders# {{{
    def _getLimitOrders(response: tinkoff.invest.GetOrdersResponse):
        orders = list()
        for i in response.orders:
            order = Order(
                signal=None,
                type=Tinkoff._getOrderType(i),
                direction=Tinkoff._getOrderDirection(i),
                asset=Tinkoff._getOrderAsset(i),
                lots=i.lots_requested,
                price=Tinkoff._getLimitOrderPrice(i),
                exec_price=Tinkoff._getOrderExecPrice(i),
                timeout=None,
                status=Tinkoff._getLimitOrderStatus(i),
                ID=i.order_id,
                commission=Tinkoff._getOrderCommission(i),
            )
            orders.append(order)
        return orders

    # }}}
    @staticmethod  # _getStopOrders# {{{
    def _getStopOrders(response: tinkoff.invest.GetOrdersResponse):
        orders = list()
        for i in response.stop_orders:
            order = Order(
                signal=None,
                type=Tinkoff._getOrderType(i),
                direction=Tinkoff._getOrderDirection(i),
                asset=Tinkoff._getOrderAsset(i),
                lots=i.lots_requested,
                price=Tinkoff._getStopOrderActivationPrice(i),
                exec_price="unspecified",
                timeout=None,
                status=Order.Status.POST,
                ID=i.stop_order_id,
                commission="unspecified",
            )
            orders.append(order)
        return orders

    # }}}
    @staticmethod  # getHistoricalBars# {{{
    def getHistoricalBars(asset, timeframe, begin, end) -> list[Bar]:
        logger.debug(f"Tinkoff.getHistoricalBars({asset.ticker})")
        new_bars = list()
        with Client(Tinkoff.TOKEN_FULL) as client:
            try:
                candles = client.get_all_candles(
                    figi=asset.figi,
                    from_=begin,
                    to=end,
                    interval=Tinkoff._CandleIntervalFrom(timeframe),
                )
                for candle in candles:
                    if candle.is_complete:
                        bar = Tinkoff._toBar(candle)
                        new_bars.append(bar)
            except tinkoff.invest.exceptions.RequestError as err:
                tracking_id = err.metadata.tracking_id if err.metadata else ""
                logger.error(
                    f"Tracking_id={tracking_id}, "
                    f"code={err.code}"
                    f"RequestError={err}"
                )
                return None
            return new_bars

    # }}}
    @staticmethod  # getLastPrice# {{{
    def getLastPrice(asset) -> float:
        with Client(Tinkoff.TOKEN_FULL) as client:
            try:
                response = client.market_data.get_last_prices(
                    figi=[
                        asset.figi,
                    ]
                )
                last_price = response.last_prices[0].price
                last_price = float(quotation_to_decimal(last_price))
            except tinkoff.invest.exceptions.RequestError as err:
                tracking_id = err.metadata.tracking_id if err.metadata else ""
                logger.error(
                    f"Tracking_id={tracking_id}, "
                    f"code={err.code}, "
                    f"RequestError={errcode}"
                )
                return None
            return last_price

    # }}}
    @property  # general# {{{
    def general(self):
        return self._general

    # }}}
    async def connect(self, token):  # {{{
        logger.debug("Tinkoff.activate()")
        with Client(token, target=INVEST_GRPC_API) as client:
            self._client = client
            self._connect = True
            while self._connect:
                await asyncio.sleep(1)
            print("after close connection!")

    # }}}
    def disconnect(self):  # {{{
        logger.debug("Tinkoff.deactivate()")
        self._connect = False

    # }}}
    def isConnect(self):  # {{{
        return self._connect

    # }}}
    def isMarketOpen(self):  # {{{
        sber_figi = Share("SBER").figi
        status = self._client.market_data.get_trading_status(figi=sber_figi)
        is_open = (
            status.market_order_available_flag
            and status.api_trade_available_flag
        )
        return is_open

    # }}}
    def getAllAccounts(self):  # {{{
        logger.debug("Tinkoff.getAllAccounts()")
        response = self._client.users.get_accounts()
        logger.debug(f"Tinkoff.getAllAccounts: Response='{response}'")
        user_accounts = list()
        for i in response.accounts:
            acc = Account(self, i, self.general)
            user_accounts.append(acc)
        return user_accounts

    # }}}
    def getMoney(self, acc):  # {{{
        logger.debug(f"Tinkoff.getMoney(acc={acc})")
        response = self._client.operations.get_positions(
            account_id=acc.id,
        )
        money = float(quotation_to_decimal(response.money[0]))
        logger.debug(f"Tinkoff.getMoney: Response='{response}'")
        logger.debug(f"Tinkoff.getMoney: UserValue='{money}'")
        return money

    # }}}
    def getLimitOrders(self, acc):  # {{{
        logger.debug(f"Tinkoff.getLimitOrders(acc={acc})")
        response = self._client.orders.get_orders(account_id=acc.id)
        logger.debug(f"Tinkoff.getLimitOrders: Response='{response}'")
        orders = Tinkoff._getLimitOrders(response)
        return orders

    # }}}
    def getStopOrders(self, acc):  # {{{
        logger.debug(f"Tinkoff.getStopOrders(acc={acc})")
        try:
            response = self._client.stop_orders.get_stop_orders(
                account_id=acc.id
            )
        except tinkoff.invest.exceptions.InvestError:
            logger.error("Tinkoff.getStopOrders: Error={err}")
            return None
        logger.debug(f"Tinkoff.getStopOrders: Response='{response}'")
        orders = Tinkoff._getStopOrders(response)
        return orders

    # }}}
    def getOperations(self, acc, from_, to):  # {{{
        logger.debug(
            f"Tinkoff.getOperations(acc={acc}), from_={from_}, to={to}"
        )
        assert isinstance(from_, datetime)
        assert isinstance(to, datetime)
        response = self._client.operations.get_operations(
            account_id=acc.id,
            from_=from_,
            to=to,
        )
        logger.debug(f"Tinkoff.getOperations: Response='{response}'")
        operations = Tinkoff._getOperations(response)
        return operations

    # }}}
    def getPositions(self, acc):  # {{{
        logger.debug(f"Tinkoff.getPositions(acc={acc})")
        response = self._client.operations.get_positions(account_id=acc.id)
        logger.debug(f"Tinkoff.getPositions: Response='{response}'")
        money = Tinkoff._getMoney(response)
        shares = Tinkoff._getShares(response)
        bounds = Tinkoff._getBounds(response)
        futures = Tinkoff._getFutures(response)
        options = Tinkoff._getOptions(response)
        portfolio = Portfolio(money, shares, bounds, futures, options)
        return portfolio

    # }}}
    def getDetailedPortfolio(self, acc):  # {{{
        logger.debug(f"Tinkoff.getDetailedPortfolio(acc={acc})")
        # короче это более подрбная версия get_positions()
        # см документацию
        response = self._client.operations.get_portfolio(account_id=acc.id)
        logger.debug(f"Tinkoff.getDetailedPortfolio: Response='{response}'")
        return response

    # }}}
    def getWithdrawLimits(self, acc):  # {{{
        logger.debug(f"Tinkoff.getWithdrawLimits(acc={acc})")
        response = self._client.operations.get_withdraw_limits(
            account_id=acc.id
        )
        logger.debug(f"Tinkoff.getWithdrawLimits: Response='{response}'")
        return limits

    # }}}
    def postMarketOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.postMarketOrder({order})")
        response: PostOrderResponse = self._client.orders.post_order(
            account_id=acc.id,
            order_type=Tinkoff._OrderTypeFrom(order),
            direction=Tinkoff._OrderDirectionFrom(order),
            instrument_id=order.asset.uid,
            quantity=order.lots,
            # price =  # для market не указываем
            # order_id = order.ID,  # в песочнице с ним не работает
        )
        order.ID = response.order_id
        logger.debug(f"Tinkoff.postMarketOrder: Response='{response}'")
        return response

    # }}}
    def postLimitOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.postLimitOrder({order})")
        response: PortfoliostOrderResponse = self._client.orders.post_order(
            account_id=acc.id,
            order_type=Tinkoff._OrderTypeFrom(order),
            direction=Tinkoff._OrderDirectionFrom(order),
            instrument_id=order.asset.uid,
            quantity=order.lots,
            price=Tinkoff._QuotationFrom(order.price),
            # order_id = order.ID,  # в песочнице с ним не работает
        )
        logger.debug(f"Tinkoff.postLimitOrder: Response='{response}'")
        order.ID = response.order_id
        return response

    # }}}
    def postStopOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.postStopOrder({order})")
        try:
            response = self._client.stop_orders.post_stop_order(
                price=Tinkoff._QuotationFrom(order.exec_price),
                quantity=order.lots,
                direction=Tinkoff._OrderDirectionFrom(order),
                account_id=acc.id,
                stop_price=Tinkoff._QuotationFrom(order.price),
                # expire_date=
                instrument_id=order.asset.uid,
                expiration_type=Tinkoff._expirationTypeFrom(order),
                stop_order_type=Tinkoff._OrderTypeFrom(order),
                # order_id = order.ID,  # в песочнице с ним не работает
            )
            # response = self._client.stop_orders.post_stop_order(
            #     account_id = acc.id,
            #     stop_order_type= Tinkoff._OrderTypeFrom(order),
            #     direction = Tinkoff._OrderDirectionFrom(order),
            #     instrument_id = order.asset.uid,
            #     quantity = order.lots,
            #     stop_price = Tinkoff._QuotationFrom(order.price),  # activate price
            #     # price = Tinkoff._QuotationFrom(order.exec_price), # exec_price market
            #     expiration_type = Tinkoff._expirationTypeFrom(order),
            #     # expire_date =
            # )
        except tinkoff.invest.exceptions.RequestError as err:
            logger.error(f"{err}")
            return False
        order.ID = response.stop_order_id
        logger.debug(f"Tinkoff.postStopOrder: Response='{response}'")
        return response

    # }}}
    # def postTakeProfit(self, order, acc):{{{
    #     response = self._client.stop_orders.post_stop_order(
    #         price = decimal_to_quotation(Decimal(order.exec_price)),
    #         quantity = order.lots,
    #         direction = Tinkoff._OrderDirectionFrom(order),
    #         account_id = acc.id,
    #         stop_price= decimal_to_quotation(Decimal(order.price)),
    #         instrument_id = order.asset.uid,
    #         expiration_type = Tinkoff._expirationTypeFrom(order),
    #         # expire_date =
    #         stop_order_type= Tinkoff._OrderTypeFrom(order),
    #     )
    #     return response
    # }}}
    def cancelLimitOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.cancelLimitOrder(acc={acc}, order={order})")
        response = self._client.orders.cancel_order(
            account_id=acc.id,
            order_id=order.ID,
        )
        logger.debug(f"Tinkoff.cancelLimitOrder: Response='{response}'")
        return response

    # }}}
    def cancelStopOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.cancelStopOrder(acc={acc}, order={order})")
        response = self._client.stop_orders.cancel_stop_order(
            account_id=acc.id,
            stop_order_id=order.ID,
        )
        logger.debug(f"Tinkoff.cancelStopOrder: Response='{response}'")
        return response

    # }}}
    def createDataStream(self):  # {{{
        logger.debug("Tinkoff.getDataStream()")
        stream: AsyncMarketDataStreamManager = (
            self._client.create_market_data_stream()
        )
        return stream

    # }}}
    def addSubscription(self, stream, asset, timeframe):  # {{{
        logger.debug("Tinkoff.createSubscription()")
        figi = asset.figi
        interval = Tinkoff._SubscriptionIntervalFrom(timeframe)
        candle_subscription = CandleInstrument(figi=figi, interval=interval)
        stream.candles.waiting_close().subscribe([candle_subscription])

    # }}}
    def addOrderSubscription(self, stream, asset):  # {{{
        logger.debug("Tinkoff.createOrderSubscription()")

    # }}}
    def checkStream(self, stream: AsyncMarketDataStreamManager):  # {{{
        logger.debug("async Tinkoff.checkStream()")
        it = iter(stream)
        # response = next(stream)
        # logger.debug(f"    - async Tinkoff.checkStream: Response='{response}'")

    # }}}
    def waitEvent(self, stream: AsyncMarketDataStreamManager):  # {{{
        logger.debug("async Tinkoff.waitEvent()")
        response = next(stream)
        logger.debug(f"  Tinkoff.waitEvent: Response='{response}'")
        if response.candle:
            figi = response.candle.figi
            timeframe = Tinkoff._toTimeFrame(response.candle.interval)
            bar = Tinkoff._toBar(response.candle)
            event = Event.NewBar(figi, timeframe, bar)
            return event
        else:
            return None

    # }}}


# }}}
class AsyncTinkoff(Broker):  # {{{
    TARGET = INVEST_GRPC_API  # {{{
    TOKEN_FULL = Cmd.read(
        "/home/alex/ya/arsvincere/user/broker/Tinkoff/full_access.txt"
    ).strip()

    # }}}
    def __init__(self, general=None):  # {{{
        Broker.__init__(self)
        self._general = general
        self._client = None
        self._connect = False

    # }}}
    @staticmethod  # _CandleIntervalFrom# {{{
    def _CandleIntervalFrom(
        timeframe: TimeFrame,
    ) -> tinkoff.invest.CandleInterval:
        intervals = {
            "1M": CandleInterval.CANDLE_INTERVAL_1_MIN,
            "5M": CandleInterval.CANDLE_INTERVAL_5_MIN,
            "1H": CandleInterval.CANDLE_INTERVAL_HOUR,
            "D": CandleInterval.CANDLE_INTERVAL_DAY,
            "W": CandleInterval.CANDLE_INTERVAL_WEEK,
            "M": CandleInterval.CANDLE_INTERVAL_MONTH,
        }
        return intervals[str(timeframe)]

    # }}}
    @staticmethod  # _SubscriptionIntervalFrom# {{{
    def _SubscriptionIntervalFrom(
        timeframe: TimeFrame,
    ) -> tinkoff.invest.SubscriptionInterval:
        intervals = {
            "1M": SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
            "5M": SubscriptionInterval.SUBSCRIPTION_INTERVAL_FIVE_MINUTES,
            "1H": SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_HOUR,
            "D": SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_DAY,
            "W": SubscriptionInterval.SUBSCRIPTION_INTERVAL_WEEK,
            "M": SubscriptionInterval.SUBSCRIPTION_INTERVAL_MONTH,
        }
        return intervals[str(timeframe)]

    # }}}
    @staticmethod  # _OrderTypeFrom# {{{
    def _OrderTypeFrom(order: Order):
        ot = tinkoff.invest.OrderType
        sot = tinkoff.invest.StopOrderType
        if order.type == Order.Type.MARKET:
            return ot.ORDER_TYPE_MARKET
        if order.type == Order.Type.LIMIT:
            return ot.ORDER_TYPE_LIMIT
        if order.type == Order.Type.STOP_LOSS:
            return sot.STOP_ORDER_TYPE_STOP_LOSS
        if order.type == Order.Type.TAKE_PROFIT:
            return sot.STOP_ORDER_TYPE_TAKE_PROFIT
        if order.type == Order.Type.STOP:
            current_price = Tinkoff.getLastPrice(order.asset)
            if order.direction == Order.Direction.BUY:
                if current_price >= order.price:
                    return sot.STOP_ORDER_TYPE_TAKE_PROFIT
                if current_price < order.price:
                    return sot.STOP_ORDER_TYPE_STOP_LOSS
            elif order.direction == Order.Direction.SELL:
                if current_price <= order.price:
                    return sot.STOP_ORDER_TYPE_TAKE_PROFIT
                if current_price > order.price:
                    return sot.STOP_ORDER_TYPE_STOP_LOSS

    # }}}
    @staticmethod  # _OrderDirectionFrom# {{{
    def _OrderDirectionFrom(order: Order):
        if order.type in (Order.Type.MARKET, Order.Type.LIMIT):
            if order.direction == Order.Direction.BUY:
                return tinkoff.invest.OrderDirection.ORDER_DIRECTION_BUY
            if order.direction == Order.Direction.SELL:
                return tinkoff.invest.OrderDirection.ORDER_DIRECTION_SELL
            return tinkoff.invest.OrderDirection.ORDER_DIRECTION_UNSPECIFIED
        if order.type in (
            Order.Type.STOP_LOSS,
            Order.Type.TAKE_PROFIT,
            Order.Type.STOP,
            Order.Type.WAIT,
        ):
            if order.direction == Order.Direction.BUY:
                return (
                    tinkoff.invest.StopOrderDirection.STOP_ORDER_DIRECTION_BUY
                )
            if order.direction == Order.Direction.SELL:
                return tinkoff.invest.StopOrderDirection.STOP_ORDER_DIRECTION_SELL
            return StopOrderDirection.STOP_ORDER_DIRECTION_UNSPECIFIED

    # }}}
    @staticmethod  # _QuotationFrom# {{{
    def _QuotationFrom(price: float):
        if price is None:
            return None
        else:
            quotation = decimal_to_quotation(Decimal(price))
            return quotation

    # }}}
    @staticmethod  # _expirationTypeFrom# {{{
    def _expirationTypeFrom(order: Order):
        if order.type == Order.Type.MARKET:
            return None
        if order.type == Order.Type.LIMIT:
            return None
        if order.type == Order.Type.STOP:
            return tinkoff.invest.StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL
        if order.type == Order.Type.TAKE:
            return tinkoff.invest.StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL

    # }}}
    @staticmethod  # _toTimeFrame# {{{
    def _toTimeFrame(tinkoff_interval) -> TimeFrame:
        si = SubscriptionInterval
        ci = CandleInterval
        if isinstance(tinkoff_interval, SubscriptionInterval):
            intervals = {
                si.SUBSCRIPTION_INTERVAL_ONE_MINUTE: "1M",
                si.SUBSCRIPTION_INTERVAL_FIVE_MINUTES: "5M",
                si.SUBSCRIPTION_INTERVAL_ONE_HOUR: "1H",
                si.SUBSCRIPTION_INTERVAL_ONE_DAY: "D",
                si.SUBSCRIPTION_INTERVAL_WEEK: "W",
                si.SUBSCRIPTION_INTERVAL_MONTH: "M",
            }
            string = intervals[tinkoff_interval]
        elif isinstance(tinkoff_interval, CandleInterval):
            intervals = {
                ci.CANDLE_INTERVAL_1_MIN: "1M",
                ci.CANDLE_INTERVAL_5_MIN: "5M",
                ci.CANDLE_INTERVAL_HOUR: "1H",
                ci.CANDLE_INTERVAL_DAY: "D",
                ci.CANDLE_INTERVAL_WEEK: "W",
                ci.CANDLE_INTERVAL_MONTH: "M",
            }
            string = intervals[tinkoff_interval]
        else:
            assert False, "unknow interval type '{type(tinkoff_interval)}'"
        return TimeFrame(string)

    # }}}
    @staticmethod  # _toBar# {{{
    def _toBar(candle, constructor=Bar) -> Bar:
        opn = float(quotation_to_decimal(candle.open))
        cls = float(quotation_to_decimal(candle.close))
        hgh = float(quotation_to_decimal(candle.high))
        low = float(quotation_to_decimal(candle.low))
        vol = candle.volume
        dt = candle.time
        bar = constructor(dt, opn, hgh, low, cls, vol)
        return bar

    # }}}
    @staticmethod  # _getOperationAsset# {{{
    def _getOperationAsset(tinkoff_operation: tinkoff.invest.Operation):
        if tinkoff_operation.instrument_type == "share":
            asset = Asset(
                exchange=Exchange.MOEX,
                asset_type=Type.SHARE,
                uid=tinkoff_operation.instrument_uid,
            )
            return Share(asset.ticker)

    # }}}
    @staticmethod  # _getOperationDirection# {{{
    def _getOperationDirection(tinkoff_operation: tinkoff.invest.Operation):
        if (
            tinkoff_operation.operation_type
            == tinkoff.invest.OperationType.OPERATION_TYPE_BUY
        ):
            return Operation.Direction.BUY
        if (
            tinkoff_operation.operation_type
            == tinkoff.invest.OperationType.OPERATION_TYPE_SELL
        ):
            return Operation.Direction.SELL

    # }}}
    @staticmethod  # _getOperations# {{{
    def _getOperations(response: tinkoff.invest.OperationsResponse):
        operations = list()
        for i in response.operations:
            if i.operation_type in (
                tinkoff.invest.OperationType.OPERATION_TYPE_BUY,
                tinkoff.invest.OperationType.OPERATION_TYPE_SELL,
            ):
                asset = Tinkoff._getOperationAsset(i)
                op = Operation(
                    signal=None,
                    dt=i.date,
                    direction=Tinkoff._getOperationDirection(i),
                    asset=asset,
                    lots=int(i.quantity / asset.lot),
                    quantity=i.quantity,
                    price=float(money_to_decimal(i.price)),
                    amount=abs(float(money_to_decimal(i.payment))),
                    commission=0,
                    broker_info=i,
                )
                operations.append(op)
        return operations

    # }}}
    @staticmethod  # _getMoney# {{{
    def _getMoney(response: tinkoff.invest.PositionsResponse):
        money = list()
        for i in response.money:
            currency = i.currency
            val = float(money_to_decimal(i))
            block = None
            cash = Portfolio.Cash(currency, val, block)
            money.append(cash)
        return money

    # }}}
    @staticmethod  # _getShares# {{{
    def _getShares(response: tinkoff.invest.PositionsResponse):
        shares = list()
        for i in response.securities:
            if i.instrument_type != "share":
                continue
            figi = i.figi
            asset = Asset.assetByFigi(figi)
            balance = i.balance
            block = i.blocked
            ID = i.position_uid
            s = Portfolio.Share(asset, balance, block, ID, i)
            shares.append(s)
        return shares

    # }}}
    @staticmethod  # _getBounds# {{{
    def _getBounds(response: tinkoff.invest.PositionsResponse):
        return list()

    # }}}
    @staticmethod  # _getFutures# {{{
    def _getFutures(response: tinkoff.invest.PositionsResponse):
        return list()

    # }}}
    @staticmethod  # _getOptions# {{{
    def _getOptions(response: tinkoff.invest.PositionsResponse):
        return list()

    # }}}
    @staticmethod  # _getOrderAsset# {{{
    def _getOrderAsset(response: tinkoff.invest.OrderState):
        figi = response.figi
        asset = TinkoffId.assetByFigi(figi)
        return asset

    # }}}
    @staticmethod  # _getOrderType# {{{
    def _getOrderType(response: tinkoff.invest.OrderState):
        ot = OrderType
        sot = StopOrderType
        types = {
            "ORDER_TYPE_UNSPECIFIED": Order.Type.UNDEFINE,
            "ORDER_TYPE_LIMIT": Order.Type.LIMIT,
            "ORDER_TYPE_MARKET": Order.Type.MARKET,
            "ORDER_TYPE_BESTPRICE": Order.Type.MARKET,
            "STOP_ORDER_TYPE_UNSPECIFIED": Order.Type.UNDEFINE,
            "STOP_ORDER_TYPE_TAKE_PROFIT": Order.Type.TAKE_PROFIT,
            "STOP_ORDER_TYPE_STOP_LOSS": Order.Type.STOP_LOSS,
            "STOP_ORDER_TYPE_STOP_LIMIT": Order.Type.STOP,
        }
        tinkoff_order_type = response.order_type.name
        avin_type = types[tinkoff_order_type]
        return avin_type

    # }}}
    @staticmethod  # _getOrderDirection# {{{
    def _getOrderDirection(response: tinkoff.invest.OrderState):
        od = OrderDirection
        sod = StopOrderDirection
        directions = {
            "ORDER_DIRECTION_UNSPECIFIED": Order.Direction.UNDEFINE,
            "ORDER_DIRECTION_BUY": Order.Direction.BUY,
            "ORDER_DIRECTION_SELL": Order.Direction.SELL,
            "STOP_ORDER_DIRECTION_UNSPECIFIED": Order.Direction.UNDEFINE,
            "STOP_ORDER_DIRECTION_BUY": Order.Direction.BUY,
            "STOP_ORDER_DIRECTION_SELL": Order.Direction.SELL,
        }
        tinkoff_order_direction = response.direction.name
        avin_direction = directions[tinkoff_order_direction]
        return avin_direction

    # }}}
    @staticmethod  # _getLimitOrderStatus# {{{
    def _getLimitOrderStatus(response: tinkoff.invest.OrderState):
        oers = OrderExecutionReportStatus
        statuses = {
            oers.EXECUTION_REPORT_STATUS_UNSPECIFIED: Order.Status.UNDEFINE,
            oers.EXECUTION_REPORT_STATUS_FILL: Order.Status.FILL,
            oers.EXECUTION_REPORT_STATUS_REJECTED: Order.Status.REJECT,
            oers.EXECUTION_REPORT_STATUS_CANCELLED: Order.Status.CANCEL,
            oers.EXECUTION_REPORT_STATUS_NEW: Order.Status.POST,
            oers.EXECUTION_REPORT_STATUS_PARTIALLYFILL: Order.Status.PARTIAL,
        }
        tinkoff_status = response.execution_report_status
        avin_status = statuses[tinkoff_status]
        return avin_status

    # }}}
    @staticmethod  # _getLimitOrderPrice# {{{
    def _getLimitOrderPrice(response: tinkoff.invest.OrderState):
        money_value = response.initial_security_price
        price = float(money_to_decimal(money_value))
        return price

    # }}}
    @staticmethod  # _getStopOrderActivationPrice# {{{
    def _getStopOrderActivationPrice(response: tinkoff.invest.StopOrder):
        money_value = response.stop_price
        price = float(money_to_decimal(money_value))
        return price

    # }}}
    @staticmethod  # _getOrderAsset# {{{
    def _getOrderCommission(response: tinkoff.invest.OrderState):
        money_value = response.initial_commission
        commission = float(money_to_decimal(money_value))
        return commission

    # }}}
    @staticmethod  # _getOrderExecPrice# {{{
    def _getOrderExecPrice(response: tinkoff.invest.OrderState):
        money_value = response.executed_order_price
        price = float(money_to_decimal(money_value))
        if price:
            return price
        else:
            return None

    # }}}
    @staticmethod  # _getLimitOrders# {{{
    def _getLimitOrders(response: tinkoff.invest.GetOrdersResponse):
        orders = list()
        for i in response.orders:
            order = Order(
                signal=None,
                type=Tinkoff._getOrderType(i),
                direction=Tinkoff._getOrderDirection(i),
                asset=Tinkoff._getOrderAsset(i),
                lots=i.lots_requested,
                price=Tinkoff._getLimitOrderPrice(i),
                exec_price=Tinkoff._getOrderExecPrice(i),
                timeout=None,
                status=Tinkoff._getLimitOrderStatus(i),
                ID=i.order_id,
                commission=Tinkoff._getOrderCommission(i),
            )
            orders.append(order)
        return orders

    # }}}
    @staticmethod  # _getStopOrders# {{{
    def _getStopOrders(response: tinkoff.invest.GetOrdersResponse):
        orders = list()
        for i in response.stop_orders:
            order = Order(
                signal=None,
                type=Tinkoff._getOrderType(i),
                direction=Tinkoff._getOrderDirection(i),
                asset=Tinkoff._getOrderAsset(i),
                lots=i.lots_requested,
                price=Tinkoff._getStopOrderActivationPrice(i),
                exec_price="unspecified",
                timeout=None,
                status=Order.Status.POST,
                ID=i.stop_order_id,
                commission="unspecified",
            )
            orders.append(order)
        return orders

    # }}}
    @staticmethod  # getHistoricalBars# {{{
    def getHistoricalBars(asset, timeframe, begin, end) -> list[Bar]:
        logger.debug(f"Tinkoff.getHistoricalBars({asset.ticker})")
        new_bars = list()
        with Client(Tinkoff.TOKEN_FULL) as client:
            try:
                candles = client.get_all_candles(
                    figi=asset.figi,
                    from_=begin,
                    to=end,
                    interval=Tinkoff._CandleIntervalFrom(timeframe),
                )
                for candle in candles:
                    if candle.is_complete:
                        bar = Tinkoff._toBar(candle)
                        new_bars.append(bar)
            except tinkoff.invest.exceptions.RequestError as err:
                tracking_id = err.metadata.tracking_id if err.metadata else ""
                logger.error(
                    f"Tracking_id={tracking_id}, "
                    f"code={err.code}"
                    f"RequestError={err}"
                )
                return None
            return new_bars

    # }}}
    @staticmethod  # getLastPrice# {{{
    def getLastPrice(asset) -> float:
        with Client(Tinkoff.TOKEN_FULL) as client:
            try:
                response = client.market_data.get_last_prices(
                    figi=[
                        asset.figi,
                    ]
                )
                last_price = response.last_prices[0].price
                last_price = float(quotation_to_decimal(last_price))
            except tinkoff.invest.exceptions.RequestError as err:
                tracking_id = err.metadata.tracking_id if err.metadata else ""
                logger.error(
                    f"Tracking_id={tracking_id}, "
                    f"code={err.code}, "
                    f"RequestError={errcode}"
                )
                return None
            return last_price

    # }}}
    @property  # general# {{{
    def general(self):
        return self._general

    # }}}
    async def connect(self, token):  # {{{
        logger.debug("Tinkoff.activate()")
        async with AsyncClient(token, target=INVEST_GRPC_API) as client:
            self._client = client
            self._connect = True
            while self._connect:
                await asyncio.sleep(1)
            # after close connection
            print("after close connection!")
            ...

    # }}}
    def disconnect(self):  # {{{
        logger.debug("Tinkoff.deactivate()")
        self._connect = False

    # }}}
    def isConnect(self):  # {{{
        return self._connect

    # }}}
    async def isMarketOpen(self):  # {{{
        sber_figi = Share("SBER").figi
        status = await self._client.market_data.get_trading_status(
            figi=sber_figi
        )
        is_open = (
            status.market_order_available_flag
            and status.api_trade_available_flag
        )
        return is_open

    # }}}
    async def getAllAccounts(self):  # {{{
        logger.debug("Tinkoff.getAllAccounts()")
        response = await self._client.users.get_accounts()
        logger.debug(f"Tinkoff.getAllAccounts: Response='{response}'")
        user_accounts = list()
        for i in response.accounts:
            acc = Account(self, i, self.general)
            user_accounts.append(acc)
        return user_accounts

    # }}}
    async def getMoney(self, acc):  # {{{
        logger.debug(f"Tinkoff.getMoney(acc={acc})")
        response = await self._client.operations.get_positions(
            account_id=acc.id,
        )
        money = float(quotation_to_decimal(response.money[0]))
        logger.debug(f"Tinkoff.getMoney: Response='{response}'")
        logger.debug(f"Tinkoff.getMoney: UserValue='{money}'")
        return money

    # }}}
    def getLimitOrders(self, acc):  # {{{
        logger.debug(f"Tinkoff.getLimitOrders(acc={acc})")
        response = self._client.orders.get_orders(account_id=acc.id)
        logger.debug(f"Tinkoff.getLimitOrders: Response='{response}'")
        orders = Tinkoff._getLimitOrders(response)
        return orders

    # }}}
    def getStopOrders(self, acc):  # {{{
        logger.debug(f"Tinkoff.getStopOrders(acc={acc})")
        try:
            response = self._client.stop_orders.get_stop_orders(
                account_id=acc.id
            )
        except tinkoff.invest.exceptions.InvestError:
            logger.error("Tinkoff.getStopOrders: Error={err}")
            return None
        logger.debug(f"Tinkoff.getStopOrders: Response='{response}'")
        orders = Tinkoff._getStopOrders(response)
        return orders

    # }}}
    def getOperations(self, acc, from_, to):  # {{{
        logger.debug(
            f"Tinkoff.getOperations(acc={acc}), from_={from_}, to={to}"
        )
        assert isinstance(from_, datetime)
        assert isinstance(to, datetime)
        response = self._client.operations.get_operations(
            account_id=acc.id,
            from_=from_,
            to=to,
        )
        logger.debug(f"Tinkoff.getOperations: Response='{response}'")
        operations = Tinkoff._getOperations(response)
        return operations

    # }}}
    def getPositions(self, acc):  # {{{
        logger.debug(f"Tinkoff.getPositions(acc={acc})")
        response = self._client.operations.get_positions(account_id=acc.id)
        logger.debug(f"Tinkoff.getPositions: Response='{response}'")
        money = Tinkoff._getMoney(response)
        shares = Tinkoff._getShares(response)
        bounds = Tinkoff._getBounds(response)
        futures = Tinkoff._getFutures(response)
        options = Tinkoff._getOptions(response)
        portfolio = Portfolio(money, shares, bounds, futures, options)
        return portfolio

    # }}}
    def getDetailedPortfolio(self, acc):  # {{{
        logger.debug(f"Tinkoff.getDetailedPortfolio(acc={acc})")
        # короче это более подрбная версия get_positions()
        # см документацию
        response = self._client.operations.get_portfolio(account_id=acc.id)
        logger.debug(f"Tinkoff.getDetailedPortfolio: Response='{response}'")
        return response

    # }}}
    def getWithdrawLimits(self, acc):  # {{{
        logger.debug(f"Tinkoff.getWithdrawLimits(acc={acc})")
        response = self._client.operations.get_withdraw_limits(
            account_id=acc.id
        )
        logger.debug(f"Tinkoff.getWithdrawLimits: Response='{response}'")
        return limits

    # }}}
    def postMarketOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.postMarketOrder({order})")
        response: PostOrderResponse = self._client.orders.post_order(
            account_id=acc.id,
            order_type=Tinkoff._OrderTypeFrom(order),
            direction=Tinkoff._OrderDirectionFrom(order),
            instrument_id=order.asset.uid,
            quantity=order.lots,
            # price =  # для market не указываем
            # order_id = order.ID,  # в песочнице с ним не работает
        )
        order.ID = response.order_id
        logger.debug(f"Tinkoff.postMarketOrder: Response='{response}'")
        return response

    # }}}
    def postLimitOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.postLimitOrder({order})")
        response: PortfoliostOrderResponse = self._client.orders.post_order(
            account_id=acc.id,
            order_type=Tinkoff._OrderTypeFrom(order),
            direction=Tinkoff._OrderDirectionFrom(order),
            instrument_id=order.asset.uid,
            quantity=order.lots,
            price=Tinkoff._QuotationFrom(order.price),
            # order_id = order.ID,  # в песочнице с ним не работает
        )
        logger.debug(f"Tinkoff.postLimitOrder: Response='{response}'")
        order.ID = response.order_id
        return response

    # }}}
    def postStopOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.postStopOrder({order})")
        try:
            response = self._client.stop_orders.post_stop_order(
                price=Tinkoff._QuotationFrom(order.exec_price),
                quantity=order.lots,
                direction=Tinkoff._OrderDirectionFrom(order),
                account_id=acc.id,
                stop_price=Tinkoff._QuotationFrom(order.price),
                # expire_date=
                instrument_id=order.asset.uid,
                expiration_type=Tinkoff._expirationTypeFrom(order),
                stop_order_type=Tinkoff._OrderTypeFrom(order),
                # order_id = order.ID,  # в песочнице с ним не работает
            )
            # response = self._client.stop_orders.post_stop_order(
            #     account_id = acc.id,
            #     stop_order_type= Tinkoff._OrderTypeFrom(order),
            #     direction = Tinkoff._OrderDirectionFrom(order),
            #     instrument_id = order.asset.uid,
            #     quantity = order.lots,
            #     stop_price = Tinkoff._QuotationFrom(order.price),  # activate price
            #     # price = Tinkoff._QuotationFrom(order.exec_price), # exec_price market
            #     expiration_type = Tinkoff._expirationTypeFrom(order),
            #     # expire_date =
            # )
        except tinkoff.invest.exceptions.RequestError as err:
            logger.error(f"{err}")
            return False
        order.ID = response.stop_order_id
        logger.debug(f"Tinkoff.postStopOrder: Response='{response}'")
        return response

    # }}}
    # def postTakeProfit(self, order, acc):{{{
    #     response = self._client.stop_orders.post_stop_order(
    #         price = decimal_to_quotation(Decimal(order.exec_price)),
    #         quantity = order.lots,
    #         direction = Tinkoff._OrderDirectionFrom(order),
    #         account_id = acc.id,
    #         stop_price= decimal_to_quotation(Decimal(order.price)),
    #         instrument_id = order.asset.uid,
    #         expiration_type = Tinkoff._expirationTypeFrom(order),
    #         # expire_date =
    #         stop_order_type= Tinkoff._OrderTypeFrom(order),
    #     )
    #     return response
    # }}}
    def cancelLimitOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.cancelLimitOrder(acc={acc}, order={order})")
        response = self._client.orders.cancel_order(
            account_id=acc.id,
            order_id=order.ID,
        )
        logger.debug(f"Tinkoff.cancelLimitOrder: Response='{response}'")
        return response

    # }}}
    def cancelStopOrder(self, order, acc):  # {{{
        logger.debug(f"Tinkoff.cancelStopOrder(acc={acc}, order={order})")
        response = self._client.stop_orders.cancel_stop_order(
            account_id=acc.id,
            stop_order_id=order.ID,
        )
        logger.debug(f"Tinkoff.cancelStopOrder: Response='{response}'")
        return response

    # }}}
    def createDataStream(self):  # {{{
        logger.debug("Tinkoff.getDataStream()")
        stream: AsyncMarketDataStreamManager = (
            self._client.create_market_data_stream()
        )
        return stream

    # }}}
    def addSubscription(self, stream, asset, timeframe):  # {{{
        logger.debug("Tinkoff.createSubscription()")
        figi = asset.figi
        interval = Tinkoff._SubscriptionIntervalFrom(timeframe)
        candle_subscription = CandleInstrument(figi=figi, interval=interval)
        stream.candles.waiting_close().subscribe([candle_subscription])
        # stream.order_book.subscribe([order_subscription])
        # stream.trades.subscribe([trades_subscription])
        # stream.info.subscribe([info_subscription])
        # stream.last_price.subscribe([last_price_subscription])

    # }}}
    def checkStream(self, stream: AsyncMarketDataStreamManager):  # {{{
        logger.debug("async Tinkoff.checkStream()")
        it = aiter(stream)
        response = anext(stream)
        logger.debug(
            f"    - async Tinkoff.checkStream: Response='{response}'"
        )

    # }}}
    async def waitEvent(self, stream: AsyncMarketDataStreamManager):  # {{{
        logger.debug("async Tinkoff.waitEvent()")
        response = await anext(stream)
        logger.debug(f"    async Tinkoff.waitEvent: Response='{response}'")
        new_candle = response.candle
        if new_candle is not None:
            figi = new_candle.figi
            timeframe = Tinkoff._toTimeFrame(new_candle.interval)
            bar = Tinkoff._toBar(new_candle)
            return figi, timeframe, bar
        else:
            return None, None, None

    # }}}


# }}}
class Sandbox(Tinkoff):  # {{{
    TARGET = INVEST_GRPC_API_SANDBOX  # {{{

    # }}}
    def __init__(self, general=None):  # {{{
        Tinkoff.__init__(self, general)
        # }}}

    async def connect(self, token):  # {{{
        logger.debug("Tinkoff.activate()")
        with Client(token, target=INVEST_GRPC_API_SANDBOX) as client:
            self._client = client
            self._connect = True
            while self._connect:
                await asyncio.sleep(1)
            # after close connection
            print("after close connection!")
            ...

    # }}}
    def openAccount(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.openAccount()")
        sandbox_account = self._client.sandbox.open_sandbox_account()
        logger.info("Sandbox add new account 'sandbox_account'")
        return sandbox_account

    # }}}
    def closeAccount(self, acc):  # {{{
        logger.info(f"Sandbox: close account id={acc.id}")
        self._client.sandbox.close_sandbox_account(account_id=acc.id)

    # }}}
    def closeAllSandboxAccounts(self):  # {{{
        logger.info("Sandbox: close all accounts")
        for acc in self.sandbox_accounts.accounts:
            self._client.sandbox.close_sandbox_account(account_id=acc.id)

    # }}}
    def addMoney(self, acc, money, currency="rub"):  # {{{
        logger.info(f"Sandbox: add money '{money} {currency}'")
        money = decimal_to_quotation(Decimal(money))
        amount = MoneyValue(
            units=money.units, nano=money.nano, currency=currency
        )
        self._client.sandbox.sandbox_pay_in(
            account_id=acc.id,
            amount=amount,
        )

    # }}}
    def postMarketOrder(self, order, acc):  # {{{
        logger.debug(f"Sandbox.postMarketOrder({order})")
        d = Tinkoff._OrderDirectionFrom(order)
        response: PostOrderResponse = self._client.orders.post_order(
            account_id=acc.id,
            order_type=Tinkoff._OrderTypeFrom(order),
            direction=Tinkoff._OrderDirectionFrom(order),
            instrument_id=order.asset.uid,
            quantity=order.lots,
            # price =  # для market не указываем
            # order_id = order.uid,  # в песочнице с ним не работает
        )
        logger.debug(f"Sandbox.postMarketOrder: Response='{response}'")
        return response

    # }}}
    def postLimitOrder(self, order, acc):  # {{{
        logger.debug(f"Sandbox.postLimitOrder({order})")
        response: PortfoliostOrderResponse = self._client.orders.post_order(
            account_id=acc.id,
            order_type=Tinkoff._OrderTypeFrom(order),
            direction=Tinkoff._OrderDirectionFrom(order),
            instrument_id=order.asset.uid,
            quantity=order.lots,
            price=Tinkoff._QuotationFrom(order.price),
            # order_id = order.uid,  # в песочнице с ним не работает
        )
        logger.debug(f"Sandbox.postLimitOrder: Response='{response}'")
        return response

    # }}}
    def postStopOrder(self, order, acc):  # {{{
        logger.debug(f"Sandbox.postStopOrder({order})")
        response = self._client.stop_orders.post_stop_order(
            # price = Tinkoff._QuotationFrom(order.exec_price),
            quantity=order.lots,
            direction=Tinkoff._OrderDirectionFrom(order),
            account_id=acc.id,
            stop_price=Tinkoff._QuotationFrom(order.price),
            # expire_date =
            instrument_id=order.asset.uid,
            expiration_type=Tinkoff._expirationTypeFrom(order),
            stop_order_type=Tinkoff._OrderTypeFrom(order),
        )
        logger.debug(f"Sandbox.postStopOrder: Response='{response}'")
        return response

    # }}}
    # def postTakeProfit(self, order, acc):{{{
    #     logger.debug(f"Sandbox.postTakeProfit({order})")
    #     response = self._client.stop_orders.post_stop_order(
    #         price = decimal_to_quotation(Decimal(order.price)),
    #         quantity = order.lots,
    #         direction = Tinkoff._OrderDirectionFrom(order),
    #         account_id = acc.id,
    #         stop_price= decimal_to_quotation(Decimal(order.price)),
    #         instrument_id = order.asset.uid,
    #         expiration_type = Tinkoff._expirationTypeFrom(order),
    #         # expire_date =
    #         stop_order_type= Tinkoff._OrderTypeFrom(order),
    #     )
    #     logger.debug(f"Sandbox.postTakeProfit: Response='{response}'")
    #     return response
    # }}}


# }}}
class Account:  # {{{
    def __init__(self, broker, account, general=None):  # {{{
        logger.debug("Account.__init__(broker, account)")
        self.__broker = broker
        self.__name = account.name if account.name else "unnamed"
        self.__account = account
        self.__general = general

    # }}}
    @property  # broker# {{{
    def broker(self):
        return self.__broker

    # }}}
    @property  # name# {{{
    def name(self):
        return self.__name

    # }}}
    @property  # ID# {{{
    def ID(self):
        return self.__account.id

    # }}}
    @property  # account_info# {{{
    def account_info(self):
        return self.__account

    # }}}
    @property  # general# {{{
    def general(self):
        return self.__general

    # }}}
    def addMoney(self, money):  # {{{
        logger.debug(f"Account.addMoney({money})")
        self.__broker.addMoney(self.__account, money)

    # }}}
    def money(self):  # {{{
        logger.debug("Account.money()")
        return self.__broker.getMoney(self.__account)

    # }}}
    def orders(self):  # {{{
        logger.debug("Account.orders()")
        limit_orders = self.__broker.getLimitOrders(self.__account)
        if self.__broker.TARGET == Sandbox.TARGET:
            stop_orders = list()
        else:
            stop_orders = self.__broker.getStopOrders(self.__account)
        return limit_orders + stop_orders

    # }}}
    def operations(self, begin=None, end=None):  # {{{
        logger.debug("Account.operations()")
        if begin is None:
            end = now()
            begin = datetime.combine(date.today(), time(0, 0), UTC)
        operations = self.__broker.getOperations(self.__account, begin, end)
        return operations

    # }}}
    def portfolio(self) -> Portfolio:  # {{{
        logger.debug("Account.positions()")
        portfolio = self.__broker.getPositions(self.__account)
        return portfolio

    # }}}
    def detailedPortfolio(self) -> Portfolio:  # {{{
        logger.debug("Account.portfolio()")
        p = self.__broker.getDetailedPortfolio(self.__account)
        return p

    # }}}
    def withdrawLimits(self):  # {{{
        logger.debug("Account.withdrawLimits()")
        return self.__broker.getWithdrawLimits(self.__account)

    # }}}
    def post(self, order: Order):  # {{{
        logger.debug(f"Account.post({order})")
        logger.info(
            f"Post order: {order.type.name} "
            f"{order.direction.name} "
            f"{order.asset.ticker} "
            f"{order.lots} x ({order.asset.lot}) x {order.price}, "
            f"exec_price={order.exec_price}"
        )
        if order.type == Order.Type.MARKET:
            response = self.__broker.postMarketOrder(order, self.__account)
        elif order.type == Order.Type.LIMIT:
            response = self.__broker.postLimitOrder(order, self.__account)
        elif order.type in (
            Order.Type.STOP,
            Order.Type.STOP_LOSS,
            Order.Type.TAKE_PROFIT,
        ):
            response = self.__broker.postStopOrder(order, self.__account)
        elif (
            order.type == Order.Type.WAIT or order.type == Order.Type.TRAILING
        ):
            assert False
        logger.info(f"Response='{response}'")
        return response

    # }}}
    def cancel(self, order):  # {{{
        logger.info(
            f"Cancel order: {order.type.name} "
            f"{order.direction.name} "
            f"{order.asset.ticker} "
            f"{order.lots} x ({order.asset.lot}) x {order.price}, "
            f"exec_price={order.exec_price} "
            f"ID={order.ID}"
        )
        if order.type == Order.Type.LIMIT:
            response = self.__broker.cancelLimitOrder(order, self.__account)
        else:
            response = self.__broker.cancelStopOrder(order, self.__account)
        logger.info(f"Cancel order: Response='{response}'")
        return response

    # }}}


# }}}
class Scout:  # {{{
    def __init__(self, general=None):  # {{{
        self.__general = general

    @property  # general
    def general(self):
        return self.__general

    # }}}
    def setBroker(self, broker):  # {{{
        logger.debug("Scout.setBroker()")
        self.__broker = broker

    # }}}
    def updateData(
        self, asset, timeframe, try_count=3, check_interval=10
    ):  # {{{
        data = Data.loadLastData(asset, timeframe)
        begin = data.last_dt + timeframe
        end = now()
        for i in range(try_count):
            new_bars = Tinkoff.getHistoricalBars(asset, timeframe, begin, end)
            if new_bars is not None:
                data.add(new_bars)
                msg = (
                    f"  - update {asset.ticker}-{str(timeframe):<2} -> "
                    f"{data.last_dt}"
                )
                logger.info(msg)
                return True
            else:
                logger.warning(
                    f"  - update {asset.ticker}-{timeframe} fail #{i}!"
                    f"\nTry again after {check_interval} seconds"
                )
                timer.sleep(check_interval)
        logger.error("Scout update failure!")
        return False

    # }}}
    def updateAllData(self, asset):  # {{{
        for timeframe in TimeFrame.ALL:
            result = self.updateData(asset, timeframe)
            if not result:
                return False
        return True

    # }}}
    def makeStream(self, assets, timeframes):  # {{{
        self.stream = self.__broker.createDataStream()
        for asset in assets:
            for timeframe in timeframes:
                self.__broker.addSubscription(self.stream, asset, timeframe)
                logger.info(
                    f"Scout add subscription {asset.ticker}-{timeframe}"
                )
        self.__broker.checkStream(self.stream)

    # }}}
    def observe(self) -> Asset:  # {{{
        event = self.__broker.waitEvent(self.stream)
        return event
        # if event.type == Event.Type.BAR:
        #     asset = self.general.alist.find(figi=event.figi)
        #     asset.chart(timeframe).update(new_bars=[event.bar, ])
        #     last_time = (event.bar.dt + MSK_TIME_DIF).time()
        #     logger.info(
        #         f"Scout new bar {asset.ticker}-{timeframe} {last_time}"
        #         )
        #     event.updated_asset = asset
        #     e = Event.UpdateAsset(asset)
        #     return asset
        #     ...
        #     # тут бы разное выцепать из респонса и отправлять тупо
        #     # новое событие, это может быть свеча, ордер, операция...
        # else:
        #     return None

    # }}}


# }}}
class Trader:  # {{{
    def __init__(self, general=None):  # {{{
        self.general = general

    # }}}
    def parent(self):  # {{{
        return self.general

    # }}}
    def openPosition(self, signal: Signal):  # {{{
        pass

    # }}}
    def increaseX2(self, position: Position):  # {{{
        pass

    # }}}
    def decreaseX2(self, position: Position):  # {{{
        pass

    # }}}
    def reverse(self, position: Position):  # {{{
        pass

    # }}}
    def close(self, pos):  # {{{
        pass

    # }}}


# }}}
class General:  # {{{
    def __init__(self):  # {{{
        logger.debug("Genera.__init__()")
        self.work = False
        self.event = None

    # }}}
    def __loadConfig(self):  # {{{
        logger.info(":: General load config")
        self.cfg = {
            "broker": Tinkoff,
            # "broker":           Sandbox,
            # "broker":           AsyncTinkoff,
            "token": Tinkoff.TOKEN_FULL,
            "account": 0,
            "strategyes": "One,Two,Three,Four,Five",
            "timeframe_list": [TimeFrame("1M")],
        }

    # }}}
    def __loadTimeTable(self):  # {{{
        logger.info(":: General load timetable")
        self.timetable = None

    # }}}
    def __loadStrategyes(self):  # {{{
        logger.info(":: General load strategyes")
        self.strategyes = list()

    # }}}
    def __loadTeam(self):  # {{{
        logger.info(":: General load team")
        self.broker = self.cfg["broker"](general=self)
        self.analytic = Analytic(general=self)
        self.market = Market(general=self)
        self.risk = Risk(general=self)
        self.ruler = Ruler(general=self)
        self.adviser = Adviser(general=self)
        self.trader = Trader(general=self)
        self.scout = Scout(general=self)

    # }}}
    def __makeGeneralAssetList(self):  # {{{
        logger.info(":: General make asset list")
        # self.alist = AssetList.load(Cmd.join(ASSET_DIR, "afks"), parent=self)
        self.alist = AssetList.load(
            Cmd.join(ASSET_DIR, "Trio.al"), parent=self
        )

    # }}}
    async def __updateData(self):  # {{{
        logger.info(":: General update historical data")
        for asset in self.alist:
            self.scout.updateAllData(asset)

    # }}}
    async def __loadCharts(self):  # {{{
        logger.info(":: General load all chart")
        for asset in self.alist:
            logger.info(f"  loading chart {asset.ticker}")
            asset.loadAllChart()

    # }}}
    async def __updateAnalytic(self):  # {{{
        logger.info(":: General update data analytic")
        # for asset in self.alist:
        #     self.analytic.updateAll(asset)

    # }}}
    async def __processStrategy(self, asset):  # {{{
        logger.info(f":: General process {asset.ticker}")
        for s in self.strategyes:
            s.process(asset)

    # }}}
    async def __processSignals(self):  # {{{
        logger.info(":: General process signals")

    # }}}
    async def __processPositions(self):  # {{{
        logger.info(":: General process positions")

    # }}}
    async def __finishWork(self):  # {{{
        ...
        # strategy.finish()
        # keeper.saveAll
        #     saveSignals()
        #     saveOrders()
        #     saveOperations()
        #     savePositions()   (Portfolio snap shot)
        # keeper.createReport()
        # sendTelegram()
        # closeConnection()
        # updateGUI
        self.work = False

    # }}}
    async def __attemptConnect(self):  # {{{
        logger.debug("General.__attemptConnect()")
        asyncio.create_task(self.broker.connect(self.cfg["token"]))
        for n in range(5):
            if self.broker.isConnect():
                logger.info("  successfully connected!")
                return True
            else:
                logger.info(f"  waiting connection... ({n})")
                await asyncio.sleep(1)
        else:
            logger.error("  fail to connect!")
            return False

    # }}}
    async def __ensureConnection(self):  # {{{
        logger.info(":: General ensure connection")
        result = await self.__attemptConnect()
        while not result:
            logger.info("  sleep 1 minute...")
            await asyncio.sleep(60)
            logger.info("  try again:")
            result = await self.__attemptConnect()
        self.scout.setBroker(self.broker)
        accounts = self.broker.getAllAccounts()
        self.account = accounts[0]

    # }}}
    async def __makeDataStream(self):  # {{{
        logger.info(":: General make data stream")
        self.scout.makeStream(self.alist, self.cfg["timeframe_list"])

    # }}}
    async def __ensureMarketOpen(self):  # {{{
        logger.debug(":: General ensure market open")
        """
        Loop until the market is openly.
        :return: when market is available for trading
        """
        status = self.broker.isMarketOpen()
        while not status:
            logger.info("  waiting to open market, sleep 1 minute")
            await asyncio.sleep(60)
            status = self.broker.isMarketOpen()
        logger.info("  market is open!")

    # }}}
    async def __waitMarketEvent(self):  # {{{
        logger.debug("  wait market event")
        self.event = self.scout.observe()

    # }}}
    async def __processEvent(self):  # {{{
        if self.event is None:
            return
        elif self.event.type == Event.Type.NEW_BAR:
            logger.info(f"-> receive event {self.event.type}")
            updated_asset = self.alist.receive(self.event)
        await self.__processSignals()
        await self.__processPositions()
        self.event = None

    # }}}
    async def __mainCycle(self):  # {{{
        logger.info(":: General run main cycle")
        self.work = True
        while self.work:
            await self.__ensureMarketOpen()
            await self.__waitMarketEvent()
            await self.__processEvent()
            # print(self.account)
            # print(type(self.account))
            # print(self.account.money())
            # p = self.account.portfolio()
            # for i in p.money:
            #     print(i)

        await self.__finishWork()

    # }}}
    async def initialize(self):  # {{{
        logger.info(":: General start initialization")
        self.__loadConfig()
        self.__loadTimeTable()
        self.__loadStrategyes()
        self.__loadTeam()
        self.__makeGeneralAssetList()

    # }}}
    async def start(self):  # {{{
        logger.info(":: General start")
        await self.__ensureConnection()
        await self.__updateData()
        await self.__loadCharts()
        await self.__updateAnalytic()
        await self.__makeDataStream()
        await self.__mainCycle()

    # }}}
    def stop(self):  # {{{
        if self.work:
            logger.info(":: General shuting down")
            self.work = False
        else:
            logger.warning("General.stop() called, but now he is not work")

    # }}}


# }}}
class Keeper:  # {{{
    pass


# }}}

if __name__ == "__main__":
    ...
