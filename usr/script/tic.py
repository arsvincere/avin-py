#!/usr/bin/env  python3

import asyncio

import moexalgo

from avin import *
from avin.data.source_moex import _MoexData

"""Первая версия скрипта который качает тиковые данные с Мос.биржи"""

login, password = Cmd.loadText(Usr.MOEX_ACCOUNT)
login, password = login.strip(), password.strip()
result = moexalgo.session.authorize(login, password)
print("Authorize", result)

tickers = [  # {{{
    "GAZP",
    "LKOH",
    "ROSN",
    "SBER",
    "VTBR",
    "YDEX",
]  # }}}


async def main():
    for ticker in tickers:
        trades = download_trades(ticker)
        if trades.empty:
            continue

        tics = format_tics(trades)
        save_tics(ticker, tics)

        save_last_tic_id(trades)


def download_trades(ticker: str):  # {{{
    logger.info(f":: Download {ticker}")
    ticker = moexalgo.Ticker(ticker)
    all_trades = pd.DataFrame()

    logger.info("   - from 07:00:00")
    trades = ticker.trades()
    all_trades = pd.concat([all_trades, trades], ignore_index=True)

    # INFO: Мос.Биржа отдает по 10.000 тиков за раз максимум.
    # соответственно если пришло 10.000 значит есть еще.
    # В последней партии будет например 2545 тиков...
    while len(trades) == 10_000:
        last = trades.loc[len(trades) - 1]
        last_tic_id = last["tradeno"]

        logger.info(f"   - from {last['tradetime']}")
        trades = ticker.trades(tradeno=last_tic_id)
        all_trades = pd.concat([all_trades, trades], ignore_index=True)

    return all_trades


# }}}
def format_tics(trades: pd.DataFrame):  # {{{
    logger.info("   Formatting...")
    # create df for formatted tics
    df = pd.DataFrame()

    # format dt
    times = trades["tradetime"].tolist()
    d = Date.today()
    dts = list()
    for t in times:
        dt = DateTime.combine(d, t, tzinfo=UTC) - _MoexData.MSK_TIME_DIF
        dts.append(dt)
    df["dt"] = dts

    # format direction
    df["direction"] = trades["buysell"]

    # other columns
    df["price"] = trades["price"]
    df["lots"] = trades["quantity"]
    df["amount"] = trades["value"]

    return df


# }}}
def save_tics(ticker: str, tics: pd.DataFrame):  # {{{
    logger.info("   Saving...")
    dir_path = Cmd.path(Usr.DATA, "MOEX", "SHARE", ticker, "TIC")
    Cmd.makeDirs(dir_path)

    date = tics.loc[0]["dt"].date()
    file_name = f"{date} tic.parquet"
    file_path = Cmd.path(dir_path, file_name)
    tics.to_parquet(file_path)

    dt = Usr.localTime(tics.iloc[-1]["dt"])
    logger.info(f"   Last tic={dt}")


# }}}
def save_last_tic_id(trades: pd.DataFrame):  # {{{
    logger.warning("TODO: save last tic id!!!")
    pass


# }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
