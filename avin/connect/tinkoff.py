# ============================================================================
# URL:          http://arsvincjre.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import polars as pl
import t_tech.invest as ti

from avin.core.category import Category
from avin.core.source import Source
from avin.data.iid_cache import IidCache
from avin.utils import Cmd, cfg, dt_to_ts, log
from avin.utils.exceptions import InvalidToken

SOURCE = Source.TINKOFF
TARGET = ti.constants.INVEST_GRPC_API
TOKEN_PATH = cfg.tinkoff_token
SCHEMA = pl.Schema(
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


class SourceTinkoff:
    TOKEN = None

    @classmethod
    def cache_instruments_info(cls) -> None:
        log.info("Caching instruments info from Tinkoff")

        # Without authorization - not work
        cls.__ensure_auth()

        # favorite list with short info (ti.FavoriteInstrument)
        f_shares = cls.__get_favorite_shares()
        # df with full info about shares
        df_shares_info = cls.__get_shares_info(f_shares)

        cache = IidCache(SOURCE, Category.SHARE, df_shares_info)
        IidCache.save(cache)

        print(df_shares_info)

    @classmethod
    def __ensure_auth(cls) -> None:
        if cls.TOKEN is None:
            token = _read_token()

        if _try_token(token):
            cls.TOKEN = token

    @classmethod
    def __get_favorite_shares(cls) -> list:
        shares = list()

        with ti.Client(cls.TOKEN) as client:
            # get favorite instruments & select shares
            response = client.instruments.get_favorites()
            for i in response.favorite_instruments:
                if i.instrument_type == "share":
                    shares.append(i)

        return shares

    @classmethod
    def __get_shares_info(
        cls,
        shares: list[ti.FavoriteInstrument],
    ) -> pl.DataFrame:
        df_shares = pl.DataFrame(schema=SCHEMA)

        with ti.Client(cls.TOKEN) as client:
            for i in shares:
                response = client.instruments.share_by(
                    id_type=ti.InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI,
                    id=i.figi,
                )
                info = _extract_info(response.instrument)
                row = pl.DataFrame(info)
                df_shares.extend(row)

        return df_shares


def _read_token() -> str:
    if not Cmd.is_exist(TOKEN_PATH):
        log.error(
            "Tinkoff not exist token file, operations with market data "
            "and orders unavailible. Make a token and put it in a "
            f"'{TOKEN_PATH}'. Read more about token: "
            "https://developer.tinkoff.ru/docs/intro/"
            "manuals/self-service-auth"
        )
        raise FileNotFoundError("Tinkoff token not found")

    token = Cmd.read(TOKEN_PATH).strip()

    return token


def _try_token(token: str) -> bool:
    try:
        with ti.Client(token) as client:
            response = client.users.get_accounts()
            if response:
                log.info("Tinkoff Authorization successful")
                return True
    except ti.exceptions.UnauthenticatedError as err:
        log.error(
            "Tinkoff authorization fault, check your token. "
            "Operations with market data unavailible. "
        )
        raise InvalidToken(token) from err

    return False


def _exchange_to_avin_exchange(name: str) -> str:
    if "MOEX" in name.upper():
        # values as "MOEX_PLUS", "MOEX_WEEKEND".. set "echange"="MOEX"
        standart_exchange_name = "MOEX"
    elif "SPB" in name.upper():
        # values as "SPB_RU_MORNING"... set "echange"="SPB"
        standart_exchange_name = "SPB"
    elif "FORTS" in name.upper():
        # NOTE:
        # FUTURE - у них биржа указана FORTS_EVENING, но похеру
        # пока для простоты ставлю им тоже биржу MOEX
        standart_exchange_name = "MOEX"
    elif name == "FX":
        # NOTE:
        # CURRENCY - у них биржа указана FX, но похеру
        # пока для простоты ставлю им тоже биржу MOEX
        standart_exchange_name = "MOEX"
    else:
        # NOTE:
        # там всякая странная хуйня еще есть в биржах
        # "otc_ncc", "LSE_MORNING", "moex_close", "Issuance",
        # "unknown"...
        # Часть из них по факту американские биржи, по которым сейчас
        # один хрен торги не доступны, другие хз, внебирживые еще, я всем
        # этим не торгую, поэтому сейчас ставим всем непонятным активам
        # биржу "", а потом перед сохранением делаем фильтр
        # если биржа "" - отбрасываем этот ассет из кэша
        standart_exchange_name = ""

    return standart_exchange_name


def _category_to_avin_category(name: str) -> Category:
    names = {
        "shares": Category.SHARE,
        "bonds": Category.BOND,
        "futures": Category.FUTURE,
        "currencies": Category.CURRENCY,
    }

    return names[name]


def _extract_info(i: ti.Instrument) -> dict:
    # define short alias
    dec = ti.utils.quotation_to_decimal

    info = {
        "exchange": _exchange_to_avin_exchange(i.exchange),
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
        log.error(f"Unknown instrument category: {i}")
        exit(1)

    return info


if __name__ == "__main__":
    ...
