# ============================================================================
# URL:          http://avin.info
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      MIT
# ============================================================================

from pathlib import Path

from avin import *


def test_asset():
    # тест базового класса Asset
    # Share - наследует Asset

    sber = Share.from_str("moex_share_sber")

    assert sber.exchange() == Exchange.MOEX
    assert sber.category() == Category.SHARE
    assert sber.ticker() == Ticker("SBER")
    assert sber.figi() == "BBG004730N88"
    assert sber.name() == "Сбер Банк"
    assert sber.lot() == 1
    assert sber.step() == 0.01
    assert sber.path() == Path("/home/alex/avin/usr/data/MOEX/SHARE/SBER")


def test_from_csv():
    sber = Share.from_csv("moex;share;sber")
    assert sber.figi() == "BBG004730N88"

    sber = Share.from_csv("moex;share;sber;")
    assert sber.figi() == "BBG004730N88"

    sber = Share.from_csv("MOEX;SHARE;SBER;")
    assert sber.figi() == "BBG004730N88"


def test_all():
    all = Share.all()
    assert len(all) == 20


def test_chart():
    tf = TimeFrame.DAY
    sber = Share.from_str("moex_share_sber")
    assert sber.chart(tf) is None

    sber.load_chart(tf)
    assert sber.chart(tf) is not None
    assert not sber.chart(tf).bars().is_empty()

    sber.load_chart_empty(tf)
    assert sber.chart(tf) is not None
    assert sber.chart(tf).bars().is_empty()


def test_tics():
    sber = Share.from_str("moex_share_sber")
    assert sber.tics() is None

    sber.load_tics()
    assert sber.tics() is not None


def test_bar_event():
    tf = TimeFrame.M1
    sber = Share.from_str("moex_share_sber")
    sber.load_chart_empty(tf)
    assert sber.chart(tf).now() is None

    figi = "BBG004730N88"
    tf = TimeFrame.M1
    bar = Bar.from_ohlcv(100500, 10, 20, 5, 15, 100)
    e = BarEvent(figi, tf, bar)

    sber.bar_event(e)
    assert sber.chart(tf).now() is not None
    assert sber.chart(tf).now().ts == 100500
    assert sber.chart(tf).now().o == 10
    assert sber.chart(tf).now().h == 20
    assert sber.chart(tf).now().l == 5
    assert sber.chart(tf).now().c == 15
    assert sber.chart(tf).now().v == 100


def test_tic_event():
    sber = Share.from_str("moex_share_sber")
    assert sber.tics() is None

    ts = 100500
    direction = Direction.BUY
    lots = 10
    price = 320.5
    value = 3205.0
    figi = "BBG004730N88"
    tic = Tic.new(ts, direction, lots, price, value)
    e = TicEvent(figi, tic)

    sber.tic_event(e)
    assert sber.tics() is not None
