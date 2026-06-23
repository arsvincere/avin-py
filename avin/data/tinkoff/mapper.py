# ============================================================================
# URL:          http://arsvincjre.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import t_tech.invest as ti

from avin.core.category import Category
from avin.utils import dt_to_ts

TINKOFF_CATEGORY_MAP = {
    "shares": Category.SHARE,
    "bonds": Category.BOND,
    "futures": Category.FUTURE,
    "currencies": Category.CURRENCY,
}


def exchange_to_avin_exchange(name: str) -> str:
    name = name.upper()

    # values as "MOEX_PLUS", "MOEX_WEEKEND".. set "echange"="MOEX"
    if "MOEX" in name:
        return "MOEX"

    # values as "SPB_RU_MORNING"... set "echange"="SPB"
    if "SPB" in name:
        return "SPB"

    # FUTURE - у них биржа указана FORTS_EVENING, но похеру
    # пока для простоты ставлю им тоже биржу MOEX
    if "FORTS" in name:
        return "MOEX"

    # CURRENCY - у них биржа указана FX, но похеру
    # пока для простоты ставлю им тоже биржу MOEX
    if name == "FX":
        return "MOEX"

    # Там всякая странная хуйня еще есть в биржах
    # "otc_ncc", "LSE_MORNING", "moex_close", "Issuance",
    # "unknown"...
    # Часть из них по факту американские биржи, по которым сейчас
    # один хрен торги не доступны, другие хз, внебирживые еще, я всем
    # этим не торгую, поэтому сейчас ставим всем непонятным активам
    # биржу "", а потом перед сохранением делаем фильтр
    # если биржа "" - отбрасываем этот ассет из кэша
    return ""


def category_to_avin_category(name: str) -> Category:
    return TINKOFF_CATEGORY_MAP[name]


def extract_info(i: ti.Instrument) -> dict[str, str]:
    # define short alias
    dec = ti.utils.quotation_to_decimal

    info = {
        "exchange": exchange_to_avin_exchange(i.exchange),
        "exchange_specific": i.exchange,  # original exchange name
        "category": "",  # seting below
        "ticker": i.ticker,
        "figi": i.figi,
        "country": i.country_of_risk,
        "currency": i.currency,
        "sector": "",  # seting below
        "class_code": i.class_code,
        "isin": "",  # seting below
        "uid": i.uid,
        "name": i.name,
        "lot": str(i.lot),
        "step": str(float(dec(i.min_price_increment))),
        "long": str(float(dec(i.dlong))),
        "short": str(float(dec(i.dshort))),
        "long_qual": str(float(dec(i.dlong_min))),
        "short_qual": str(float(dec(i.dshort_min))),
        "first_1m": str(dt_to_ts(i.first_1min_candle_date)),
        "first_d": str(dt_to_ts(i.first_1day_candle_date)),
    }

    # save attributes "isin" & "sector", if availible
    if hasattr(i, "isin"):
        info["isin"] = i.isin
    if hasattr(i, "sector"):
        info["sector"] = i.sector

    # # set standart instrument category
    if isinstance(i, ti.Share):
        info["category"] = Category.SHARE.name
    elif isinstance(i, ti.Bond):
        info["category"] = Category.BOND.name
    elif isinstance(i, ti.Future):
        info["category"] = Category.FUTURE.name
    elif isinstance(i, ti.Currency):
        info["category"] = Category.CURRENCY.name
    else:
        raise ValueError(f"Unknown instrument category: {i}")

    return info
