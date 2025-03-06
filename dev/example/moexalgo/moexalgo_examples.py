#!/usr/bin/env  python3

import asyncio

import moexalgo

from avin import *

login, password = Cmd.loadText(Usr.MOEX_ACCOUNT)
login, password = login.strip(), password.strip()
moexalgo.session.authorize(login, password)

# INFO: исходные примеры тут
# https://github.com/moexalgo/moexalgo/blob/main/samples/quick_start.ipynb
# и ссылки на описание параметров там есть, а то в SuperCandles например
# с ходу не разберешься. Или вот там все сразу:
# https://moexalgo.github.io/


async def main():
    sber = moexalgo.Ticker("SBER")
    stocks = moexalgo.Market("shares")  # FUT - фьючерсы, FX - валюта

    # список акций на сегодня
    # r = stocks.tickers(use_dataframe=False)
    # print(r)

    # торговая статистика за сегодня
    # r = stocks.marketdata()
    # print(r)

    # торговая статистика за сегодня
    # stocks.marketdata().head()

    # свечки, periods: '1min', '10min', '1h', '1d', '1w', '1m'
    # r = sber.candles(start="2025-01-01", end="2025-01-30", period="1d")
    # print(r)

    # стакан котировок
    # r = sber.orderbook()
    # print(r)

    # TODO: вот это надо каждый день сохранять
    # сделки за сегодня
    # r = sber.trades()
    # print(r)
    # r.to_csv("sber 2025-03-02", sep=";")
    # r.to_parquet("sber 2025-03-02.parquet")

    # INFO: а это уже SuperCandles пошли
    # SuperCandles - расширенные 5 мин. свечи

    # статистика по сделкам
    r = sber.tradestats(start="2025-01-25", end="2025-01-30")
    print(r)

    # статистика по заявкам
    # r = sber.orderstats(start="2025-01-25", end="2025-01-30")
    # print(r)

    # статистика по стакану
    # r = sber.obstats(start="2025-01-25", end="2025-01-30")
    # print(r)

    # INFO: FUTOI
    # Si = moexalgo.Ticker("SiH5")
    # r = Si.futoi(start="2025-01-30", end="2025-01-30")
    # print(r)

    # INFO: Market Concentration (HI2)
    # r = sber.hi2(start="2025-01-01", end="2025-03-01")
    # print(r)

    # INFO: Alerts
    # r = sber.alerts(start="2025-02-25", end="2025-03-03")
    # print(r)


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
