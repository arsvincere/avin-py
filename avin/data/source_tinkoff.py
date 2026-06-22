# ============================================================================
# URL:          http://arsvincjre.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from __future__ import annotations

import time

import polars as pl
import requests
import t_tech.invest as ti

from avin.core.category import Category
from avin.core.iid import Iid
from avin.core.market_data import MarketData
from avin.core.source import Source
from avin.data.bar_storge import BarStorage
from avin.data.iid_storage import IidStorage
from avin.data.tic_storage import TicStorage
from avin.utils import Cmd, Date, DateTime, TimeDelta, cfg, dt_to_ts, log
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
    def availible_market_data(cls) -> list[MarketData]:
        return [MarketData.BAR_1M]

    @classmethod
    def cache(cls) -> None:
        log.info("Caching instruments info from Tinkoff")

        # Without authorization - not work
        cls.__ensure_auth()

        # favorite list with short info (ti.FavoriteInstrument)
        f_shares = cls.__get_favorite_shares()
        # df with full info about shares
        df_shares_info = cls.__get_shares_info(f_shares)

        cache = IidStorage(SOURCE, Category.SHARE, df_shares_info)
        IidStorage.save(cache)

    @classmethod
    def download(cls, iid: Iid, md: MarketData, year: int) -> None:
        match md:
            case MarketData.BAR_1M:
                _download_tinkoff_bar_1m(iid, md, year)
            case MarketData.TIC:
                _download_tinkoff_tic(iid, md, year)
            case _:
                raise ValueError(f"Tinkoff not provide: {md}")

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


def _download_tinkoff_bar_1m(iid: Iid, md: MarketData, year: int) -> None:
    # create clear tmp dir
    tmp_dir = cfg.tmp / "tinkoff"
    if tmp_dir.exists():
        Cmd.delete_dir(tmp_dir)
        Cmd.make_dirs(tmp_dir)

    # create archive path
    e = iid.exchange.name
    c = iid.category.name
    t = iid.ticker
    archive_name = f"{e}-{c}-{t}-{md}-{year}.zip"
    archive_path = tmp_dir / "download" / archive_name
    Cmd.make_dirs_for_file(archive_path)

    # create clear dir path for extract files
    extract_dir_name = f"{e}-{c}-{t}-{md}-{year}"
    extract_path = tmp_dir / "extract" / extract_dir_name
    Cmd.make_dirs_for_file(extract_path)
    if extract_path.exists():
        Cmd.delete_dir(tmp_dir)
        Cmd.make_dirs(tmp_dir)

    # download archive
    uid = iid.dump_raw_info()["uid"]
    url = "https://invest-public-api.tinkoff.ru/history-data?"
    url += f"instrumentId={uid}&"
    url += f"year={year}"
    with open(archive_path, "wb") as f:
        f.write(requests.get(url).content)

    # check archive not empty
    if Cmd.size(archive_path) == 0:
        raise ValueError(f"Market data for {iid}-{year} unavailable")

    # extract archive
    Cmd.extract_zip(archive_path, extract_path)

    # read extracted tinkoff csv files
    schema = pl.Schema(
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
    tinkoff_df = pl.DataFrame(schema=schema)
    files = sorted(Cmd.get_files(extract_path, full_path=True))
    for file in files:
        file_df = pl.read_csv(
            file,
            has_header=False,
            separator=";",
            schema=schema,
        )
        tinkoff_df.extend(file_df)

    # format tinkoff bars data:
    # input df
    # ┌─────┬───────────┬───────┬───────┬───────┬───────┬────────┬──────┐
    # │ uid ┆ datetime  ┆ open  ┆ close ┆ high  ┆ low   ┆ volume ┆ x    │
    # │ --- ┆ ---       ┆ ---   ┆ ---   ┆ ---   ┆ ---   ┆ ---    ┆ ---  │
    # │ str ┆ str       ┆ f64   ┆ f64   ┆ f64   ┆ f64   ┆ i64    ┆ str  │
    # ╞═════╪═══════════╪═══════╪═══════╪═══════╪═══════╪════════╪══════╡
    # │ c.. ┆ 2025-01.. ┆ 83.2  ┆ 83.4  ┆ 83.4  ┆ 83.2  ┆ 4      ┆ null │
    # │ c.. ┆ 2025-01.. ┆ 82.68 ┆ 82.68 ┆ 82.68 ┆ 82.68 ┆ 1      ┆ null │
    # │ c.. ┆ 2025-01.. ┆ 82.64 ┆ 82.64 ┆ 82.64 ┆ 82.64 ┆ 1      ┆ null │
    # │ c.. ┆ 2025-01.. ┆ 82.66 ┆ 82.64 ┆ 82.68 ┆ 82.64 ┆ 15     ┆ null │
    # │ c.. ┆ 2025-01.. ┆ 82.68 ┆ 82.8  ┆ 82.8  ┆ 82.68 ┆ 30     ┆ null │
    # │ …   ┆ …         ┆ …     ┆ …     ┆ …     ┆ …     ┆ …      ┆ …    │
    #
    # output df
    # ┌───────────┬───────┬───────┬───────┬───────┬────────┬──────┐
    # │ datetime  ┆ open  ┆ close ┆ high  ┆ low   ┆ volume ┆ ts   │
    # │ ---       ┆ ---   ┆ ---   ┆ ---   ┆ ---   ┆ ---    ┆ ---  │
    # │ str       ┆ f64   ┆ f64   ┆ f64   ┆ f64   ┆ i64    ┆ i64  │
    # ╞═══════════╪═══════╪═══════╪═══════╪═══════╪════════╪══════╡
    # │ 2025-01.. ┆ 83.2  ┆ 83.4  ┆ 83.4  ┆ 83.2  ┆ 4      ┆ 1234 │
    # │ 2025-01.. ┆ 82.68 ┆ 82.68 ┆ 82.68 ┆ 82.68 ┆ 1      ┆ 1235 │
    # │ 2025-01.. ┆ 82.64 ┆ 82.64 ┆ 82.64 ┆ 82.64 ┆ 1      ┆ 1236 │
    # │ 2025-01.. ┆ 82.66 ┆ 82.64 ┆ 82.68 ┆ 82.64 ┆ 15     ┆ 1237 │
    # │ 2025-01.. ┆ 82.68 ┆ 82.8  ┆ 82.8  ┆ 82.68 ┆ 30     ┆ 1238 │
    # │ …         ┆ …     ┆ …     ┆ …     ┆ …     ┆ …      ┆ …    │
    timestamps = list()
    datetimes = tinkoff_df.get_column("datetime")
    for str_dt in datetimes:
        dt = DateTime.fromisoformat(str_dt)
        ts = dt_to_ts(dt)
        timestamps.append(ts)

    df = tinkoff_df.select(
        ["datetime", "open", "high", "low", "close", "volume"]
    )
    df = df.with_columns(pl.Series("ts", timestamps))

    # save parquet
    BarStorage.save(iid, SOURCE, md, df)

    # clear tmp dir
    Cmd.delete_dir(tmp_dir)


def _download_tinkoff_tic(iid: Iid, md: MarketData, year: int) -> None:
    # create clear tmp dir
    tmp_dir = cfg.tmp / "tinkoff"
    if tmp_dir.exists():
        Cmd.delete_dir(tmp_dir)
        Cmd.make_dirs(tmp_dir)

    # download archive day by day
    ticker = iid.ticker
    day = Date(year, 1, 1)
    end = Date(year + 1, 1, 1)
    while day < end:
        # HTTP ERROR 429 (Too Many Requests)... 30 per minute is max
        time.sleep(1)

        # create archive path
        e = iid.exchange.name
        c = iid.category.name
        t = iid.ticker
        archive_name = f"{e}-{c}-{t}-{md}-{day}.csv.gz"
        archive_path = tmp_dir / "download" / archive_name
        Cmd.make_dirs_for_file(archive_path)

        # create clear dir path for extract files
        extract_dir_name = f"{e}-{c}-{t}-{md}-{day}"
        extract_path = tmp_dir / "extract" / extract_dir_name
        Cmd.make_dirs_for_file(extract_path)
        if extract_path.exists():
            Cmd.delete_dir(tmp_dir)
            Cmd.make_dirs(tmp_dir)

        url = "https://invest-public-api.tinkoff.ru/history-trades/"
        url += f"{day}?"
        url += f"instrumentId={ticker}_TQBR"
        with open(archive_path, "wb") as f:
            f.write(requests.get(url).content)

        # check archive not empty: skip / extract
        if Cmd.size(archive_path) == 0:
            log.info(f"{day} - no tic data")
            Cmd.delete(archive_path)
            day += TimeDelta(days=1)
            continue
        else:
            Cmd.extract_gz(archive_path, extract_path)
            log.info(f"{day} - tic data extracted")

        # read extracted tinkoff csv files
        schema = pl.Schema(
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
        tinkoff_df = pl.read_csv(
            extract_path,
            has_header=True,
            separator=",",
            schema=schema,
        )

        # format tinkoff bars data:
        # input df
        # ┌─────────┬───────┬──────────┬───────┬─────┬───────┬─────┬─────┐
        # │ datetime┆ ticker┆ direction┆ price ┆ lots┆ source┆ uid ┆ x   │
        # │ ---     ┆ ---   ┆ ---      ┆ ---   ┆ --- ┆ ---   ┆ --- ┆ --- │
        # │ str     ┆ str   ┆ str      ┆ f64   ┆ f64 ┆ str   ┆ str ┆ str │
        # ╞═════════╪═══════╪══════════╪═══════╪═════╪═══════╪═════╪═════╡
        # │ 2026-01-┆ SBER_T┆ BUY      ┆ 300.53┆ 1.0 ┆ DEALER┆ e612┆ null│
        #
        # output df
        # ┌──────────┬───────────┬────────┬──────┬──────────┬────────┬───────┐
        # │ datetime ┆ direction ┆ price  ┆ lots ┆ quantity ┆ value  ┆ ts    │
        # │ ---      ┆ ---       ┆ ---    ┆ ---  ┆ ---      ┆ ---    ┆ ---   │
        # │ str      ┆ str       ┆ f64    ┆ i64  ┆ i64      ┆ f64    ┆ i64   │
        # ╞══════════╪═══════════╪════════╪══════╪══════════╪════════╪═══════╡
        # │ 2026-..  ┆ BUY       ┆ 300.26 ┆ 1    ┆ 10       ┆ 3002.6 ┆ 176.. │

        df = tinkoff_df.select(["datetime", "direction", "price", "lots"])
        df = df.with_columns(quantity=pl.col("lots") * iid.lot)
        df = df.with_columns(value=pl.col("quantity") * pl.col("price"))
        df = df.with_columns(pl.col("direction").str.replace_all("BUY", "B"))
        df = df.with_columns(pl.col("direction").str.replace_all("SELL", "S"))

        timestamps = list()
        datetimes = tinkoff_df.get_column("datetime")
        for str_dt in datetimes:
            dt = DateTime.fromisoformat(str_dt)
            ts = dt_to_ts(dt)
            timestamps.append(ts)
        df = df.with_columns(pl.Series("ts", timestamps))

        # save parquet
        TicStorage.save(iid, SOURCE, md, df)

        # next day
        day += TimeDelta(days=1)

    # clear tmp dir
    Cmd.delete_dir(tmp_dir)


if __name__ == "__main__":
    ...
