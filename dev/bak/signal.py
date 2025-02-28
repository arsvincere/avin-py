#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================
""" Doc """

from __future__ import annotations

class Signal():# {{{
    class Type(enum.Enum):# {{{
        UNDEFINE = 0
        LONG =     1
        SHORT =    2
        KILL =     3
        MANUAL =   4
    # }}}
    class Status(enum.Enum):# {{{
        UNDEFINE = 0
        INITIAL =  1
        NEW =      2
        POST =     3
        OPEN =     4
        CLOSE =    5
        ARCHIVE =  7
        CANCELED = 8
    # }}}
    class Close(enum.Enum):# {{{
        UNDEFINE =      0
        STOP_TAKE =     1
        SIGNAL_KILL =   2
        DATETIME =      3
        ON_CLOSE =      4
    # }}}
    def __init__(# {{{
            self,
            dt:                 datetime,
            strategy:           object,
            signal_type:        Type,
            asset:              Asset,
            # open_price:         float=None,
            # stop_price:         float=None,
            # take_price:         float=None,
            open_order_type:    Order.Type=Order.Type.MARKET,
            close_condition:    Close=Close.SIGNAL_KILL,
            status:             Status=Status.INITIAL,
            ID:                str="",
            ):
        self.asset = asset
        strategy_info = {
            "signal_datetime":  dt,
            "strategy":         strategy,
            "type":             signal_type,
            "asset":            asset,
            "open_price":       open_price,
            "stop_price":       stop_price,
            "take_price":       take_price,
            "open_order_type":  open_order_type,
            "close_condition":  close_condition,
            }
        for k, v in strategy.config.items():
            strategy_info.setdefault(k, v)
        self.__info = {
            "ID":       ID if ID else uuid.uuid4().hex,
            "status":   status,
            "strategy": strategy_info
            }
        self.__position = None
    # }}}
    def __str__(self):# {{{
        dt = self.dt
        dt = dt.strftime("%Y-%m-%d %H:%M")
        string = (
            f"==> SIGNAL {dt} {self.strategy}-{self.version} "
            f"{self.asset.ticker} {self.type.name.lower()}"
            )
        return string
    # }}}
    def __encode_for_JSON(self, obj):# {{{
        for k, v in obj.items():
            if isinstance(v, (enum.Enum, datetime, TimeFrame)):
                obj[k] = str(obj[k])
            elif isinstance(v, Asset):
                obj[k] = Asset.toJSON(obj[k])
            elif isinstance(v, Strategy):
                obj[k] = obj[k].name + "-" + obj[k].version
            elif k == "timeframe_list":
                tmp = list()
                for t in obj["timeframe_list"]:
                    string = str(t)
                    tmp.append(string)
                obj["timeframe_list"] = tmp
                # after transformation it looks like ["1M", "D"]
        return obj
    # }}}
    def __formatInfo(self):# {{{
        i = self.__info
        i["status"] =   str(i["status"])
        i["strategy"] = self.__encode_for_JSON(i["strategy"])
        i["analytic"] = self.__encode_for_JSON(i["analytic"])
        i["market"] =   self.__encode_for_JSON(i["market"])
        i["risk"] =     self.__encode_for_JSON(i["risk"])
        i["ruler"] =    self.__encode_for_JSON(i["ruler"])
        i["adviser"] =  self.__encode_for_JSON(i["adviser"])
        i["position"] = self.__encode_for_JSON(i["position"])
        for n, op in enumerate(i["operation"]):
            i["operation"][n] = Operation.toJSON(op)
        return i
    # }}}
    @staticmethod  # toBIN{{{
    def toBIN(signal):
        assert False, "не написана функция, или в bin?"
    # }}}
    @staticmethod  # fromBIN{{{
    def fromBIN(obj):
        assert False, "не написана функция, или в bin?"
    # }}}
    @staticmethod  # save{{{
    def save(signal):
        assert False, "не написана функция, или в bin?"
    # }}}
    @staticmethod  # load{{{
    def load(path):
        assert False, "не написана функция, или в bin?"
    # }}}
    @property  #ID# {{{
    def ID(self):
        return self.__info["ID"]
    # }}}
    @property  #status# {{{
    def status(self):
        return self.__info["status"]
    @status.setter
    def status(self, status):
        self.__info["status"] = status
    # }}}
    @property  #position# {{{
    def position(self):
        return self.__position
    @position.setter
    def position(self, pos):
        assert isinstance(pos, Position)
        self.__position = pos
    # }}}
    @property  #info# {{{
    def info(self):
        return self.__info
    # }}}
    @property  #strategy# {{{
    def strategy(self):
        return self.__info["strategy"]["strategy"]
    # }}}
    @property  #version# {{{
    def version(self):
        return self.__info["strategy"]["strategy"].version
    # }}}
    @property  #type# {{{
    def type(self):
        return self.__info["strategy"]["type"]
    # }}}
    # @property  #asset{{{
    # def asset(self):
    #     return self.__info["strategy"]["asset"]
    #
    @property  #dt
    def dt(self):
        return self.__info["strategy"]["signal_datetime"]
    # }}}
    @property  #open_price# {{{
    def open_price(self):
        return self.__info["strategy"]["open_price"]
    # }}}
    @property  #stop_price# {{{
    def stop_price(self):
        return self.__info["strategy"]["stop_price"]
    # }}}
    @property  #take_price# {{{
    def take_price(self):
        return self.__info["strategy"]["take_price"]
    # }}}
    @property  #open_order_type# {{{
    def open_order_type(self):
        return self.__info["strategy"]["open_order_type"]
    # }}}
    @property  #close_condition# {{{
    def close_condition(self):
        return self.__info["strategy"]["close_condition"]
    # }}}
    def isShort(self):# {{{
        return self.__info["strategy"]["type"] == Signal.Type.SHORT
    # }}}
    def isLong(self):# {{{
        return self.__info["strategy"]["type"] == Signal.Type.LONG
    # }}}
    def toTrade(self):# {{{
        assert self.__info["status"] == Signal.Status.CLOSE
        dict_obj = self.__formatInfo()
        trade = Trade(dict_obj)
        return trade
    # }}}
# }}}
