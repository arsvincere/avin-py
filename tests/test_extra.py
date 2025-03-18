#!/usr/bin/env python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import pytest
from avin import *


def test_Size():  # {{{
    b = Size.BIG
    m = Size.M
    s = Size.SMALL

    assert s < b
    assert m <= b
    assert b > s
    assert b >= m
    assert m == Size.M


# }}}
def test_SimpleSize():  # {{{
    assert BlackSwan.BLACKSWAN_SMALL == BlackSwan.XXS

    assert Size.GREATEST_SMALL == SimpleSize.XS
    assert Size.ANOMAL_SMALL == SimpleSize.XS
    assert Size.EXTRA_SMALL == SimpleSize.XS
    assert Size.VERY_SMALL == SimpleSize.XS

    assert Size.SMALLEST == SimpleSize.S
    assert Size.SMALLER == SimpleSize.S

    assert Size.SMALL == SimpleSize.M
    assert Size.M == SimpleSize.M
    assert Size.BIG == SimpleSize.M

    assert Size.BIGGER == SimpleSize.L
    assert Size.BIGGEST == SimpleSize.L

    assert Size.VERY_BIG == SimpleSize.XL
    assert Size.EXTRA_BIG == SimpleSize.XL
    assert Size.ANOMAL_BIG == SimpleSize.XL
    assert Size.GREATEST_BIG == SimpleSize.XL

    assert BlackSwan.BLACKSWAN_BIG == BlackSwan.XXL


# }}}
@pytest.mark.asyncio  # Extremum  # {{{
async def test_Extremum(event_loop):
    asset = await Asset.fromStr("moex share sber")
    tf = TimeFrame("D")
    chart = await asset.loadChart(tf)
    elist = ExtremumList(chart)

    e = elist.extr(Term.T1, 501)
    print(e.dt)
    print(e.term)
    print(e.type)
    print(e.price)
    print(e.elist)
    print(e.asset)
    print(e.chart)
    print(e.timeframe)

    print(e.isMin())
    print(e.isMax())
    print(e.isT1())
    print(e.isT2())
    print(e.isT3())


# }}}
@pytest.mark.asyncio  # Trend  # {{{
async def test_Trend(event_loop):
    asset = await Asset.fromStr("moex share sber")
    tf = TimeFrame("D")
    chart = await asset.loadChart(tf)
    elist = ExtremumList(chart)

    t = elist.trend(Term.T1, 8)
    print(t)
    print(t.begin)
    print(t.end)
    print(t.asset)
    print(t.chart)
    print(t.timeframe)
    print(t.term)
    print(t.type)
    print(t.strength)

    print(t.isBull())
    print(t.isBear())
    print(t.period())
    print(t.deltaPrice())
    print(t.deltaPercent())
    print(t.speedPrice())
    print(t.speedPercent())
    print(t.volumeBear())
    print(t.volumeBull())
    print(t.volumeTotal())
    print(t.bars())

    print(t.isStrong())
    print(t.isWeak())


# }}}


@pytest.mark.asyncio  # TrendAnalytic  # {{{
async def test_Trend(event_loop):
    asset = await Asset.fromStr("moex share afks")
    chart = await asset.loadChart(TimeFrame("5M"))
    elist = ExtremumList(chart)
    term = Term.T1

    trend = elist.trend(term, 2)

    p = TrendAnalytic.posteriorSize(trend)
    print(p)
    p = TrendAnalytic.posteriorSimpleSize(trend)
    print(p)
    p = TrendAnalytic.posteriorStep(trend)
    print(p)


# }}}
