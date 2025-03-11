#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import asyncio
import enum

import pandas as pd

from avin.analytic._analytic import Analytic
from avin.core import Asset, TimeFrame
from avin.data import Data
from avin.extra.size import Size
from avin.utils import configureLogger, logger, now

__all__ = ("TrendAnalytic",)


class TrendAnalytic(Analytic):  # {{{
    name = "Trend"

    class Analyse(enum.Enum):  # {{{
        TREND = 1
        SIZE = 2

        def __str__(self):
            return self.name.lower()

    # }}}
    class Trait(enum.Enum):  # {{{
        PERIOD = 1
        DELTA = 2
        SPEED = 3
        VOLUME = 4

    # }}}

    @classmethod  # load  # {{{
    def load(
        cls,
        asset: Asset,
        tf: TimeFrame,
        term: Term,
        analyse: TrendAnalytic.Analyse,
    ) -> pd.DataFrame | None:
        name = f"{cls.name} {tf} {term} {analyse}"
        df = super().load(asset, name)
        return df

    # }}}
    @classmethod  # analyse  #  {{{
    async def analyse(cls, asset: Asset, tf: TimeFrame, term: Term):
        logger.info(f":: {cls.name} analyse {asset.ticker}-{tf} {term}")

        await cls.__collectTrends(asset, tf, term)
        cls.__defineTrendSizes(asset, tf, term)
        cls.__identifyTrendSizes(asset, tf, term)

    # }}}
    @classmethod  # updateAll  #  {{{
    async def updateAll(cls):
        logger.info(f":: {cls.name} update all")

        assets = await Asset.requestAll()
        timeframes = [
            TimeFrame("W"),
            TimeFrame("D"),
            TimeFrame("1H"),
            TimeFrame("5M"),
            TimeFrame("1M"),
        ]

        for asset in assets:
            for tf in timeframes:
                for term in Term:
                    await TrendAnalytic.analyse(asset, tf, term)

    # }}}

    @classmethod  # periodSize  # {{{
    def periodSize(cls, trend: Trend) -> Size:
        size = cls.__getSize(trend, cls.Trait.PERIOD, trend.period())
        return size

    # }}}
    @classmethod  # deltaSize  # {{{
    def deltaSize(cls, trend: Trend) -> Size:
        size = cls.__getSize(trend, cls.Trait.DELTA, trend.deltaPercent())
        return size

    # }}}
    @classmethod  # speedSize  # {{{
    def speedSize(cls, trend: Trend) -> Size:
        size = cls.__getSize(trend, cls.Trait.SPEED, trend.speedPercent())
        return size

    # }}}
    @classmethod  # volumeSize  # {{{
    def volumeSize(cls, trend: Trend) -> Size:
        size = cls.__getSize(trend, cls.Trait.VOLUME, trend.volume())
        return size

    # }}}

    @classmethod  # __collectTrends  # {{{
    async def __collectTrends(
        cls,
        asset: Asset,
        tf: TimeFrame,
        term: Term,
    ):
        logger.info("   Collect trends")

        chart = await cls.__loadChart(asset, tf)
        elist = ExtremumList(chart)
        trends = elist.getAllTrends(term)

        df = cls.__createDataFrame(trends)
        name = f"{cls.name} {tf} {term} {cls.Analyse.TREND}"
        super().save(
            asset=asset,
            analyse_name=name,
            data_frame=df,
        )

    # }}}
    @classmethod  # __loadChart  # {{{
    async def __loadChart(cls, asset, tf):
        match str(tf):
            case "1M":
                begin = now() - ONE_YEAR * 1
            case "5M":
                begin = now() - ONE_YEAR * 5
            case "1H":
                info = await Data.info(asset, tf.toDataType())
                begin = info.first_dt
            case "D":
                info = await Data.info(asset, tf.toDataType())
                begin = info.first_dt
            case "W":
                info = await Data.info(asset, tf.toDataType())
                begin = info.first_dt

        chart = await asset.loadChart(tf, begin, end=now())
        return chart

    # }}}
    @classmethod  # __createDataFrame  # {{{
    def __createDataFrame(cls, trends: list[Trend]):
        begin = list()
        end = list()
        begin_price = list()
        end_price = list()
        typ = list()
        volume = list()
        period = list()
        delta = list()
        speed = list()

        for trend in trends:
            begin.append(trend.begin.dt)
            end.append(trend.end.dt)
            begin_price.append(trend.begin.price)
            end_price.append(trend.end.price)
            typ.append(trend.type.name)
            volume.append(trend.volume())
            period.append(trend.period())
            delta.append(trend.deltaPercent())
            speed.append(trend.speedPercent())

        df = pd.DataFrame()
        df["begin"] = begin
        df["end"] = end
        df["begin_price"] = begin_price
        df["end_price"] = end_price
        df["type"] = typ
        df["period"] = period
        df["delta"] = delta
        df["speed"] = speed
        df["volume"] = volume

        return df

    # }}}
    @classmethod  # __defineTrendSizes  # {{{
    def __defineTrendSizes(cls, asset: Asset, tf: TimeFrame, term: Term):
        logger.info("   Define trend sizes")

        # load trends
        name = f"{cls.name} {tf} {term} {cls.Analyse.TREND}"
        trend = super().load(asset, name)

        # skip if the amount is small
        if len(trend) < 200:
            return

        period_size = super()._classifySizes(trend["period"].to_list())
        delta_size = super()._classifySizes(trend["delta"].to_list())
        speed_size = super()._classifySizes(trend["speed"].to_list())
        volume_size = super()._classifySizes(trend["volume"].to_list())
        trend_size = pd.concat(
            [period_size, delta_size, speed_size, volume_size],
            keys=("period", "delta", "speed", "volume"),
        )

        name = f"{cls.name} {tf} {term} {cls.Analyse.SIZE}"
        super().save(asset, name, trend_size)

    # }}}
    @classmethod  # __identifyTrendSizes  # {{{
    def __identifyTrendSizes(cls, asset: Asset, tf: TimeFrame, term: Term):
        logger.info("   Identify trend sizes")

        # load trends & sizes
        trend = super().load(asset, f"Trend {tf} {term} {cls.Analyse.TREND}")
        size = super().load(asset, f"Trend {tf} {term} {cls.Analyse.SIZE}")
        if trend is None or size is None:
            return

        size = size.sort_index()

        # select trait sizes
        p_size = size.xs("period")
        d_size = size.xs("delta")
        s_size = size.xs("speed")
        v_size = size.xs("volume")

        # identify sizes
        p = trend["period"].apply(lambda x: cls._identifySize(x, p_size))
        d = trend["delta"].apply(lambda x: cls._identifySize(x, d_size))
        s = trend["speed"].apply(lambda x: cls._identifySize(x, s_size))
        v = trend["volume"].apply(lambda x: cls._identifySize(x, v_size))

        # add sizes to df
        trend["period_size"] = p.apply(lambda x: str(x))
        trend["delta_size"] = d.apply(lambda x: str(x))
        trend["speed_size"] = s.apply(lambda x: str(x))
        trend["volume_size"] = v.apply(lambda x: str(x))

        # add simple sizes to df
        trend["period_ssize"] = p.apply(lambda x: str(x.toSimpleSize()))
        trend["delta_ssize"] = d.apply(lambda x: str(x.toSimpleSize()))
        trend["speed_ssize"] = s.apply(lambda x: str(x.toSimpleSize()))
        trend["volume_ssize"] = v.apply(lambda x: str(x.toSimpleSize()))

        # save alalysed trends
        name = f"{cls.name} {tf} {term} {cls.Analyse.TREND}"
        super().save(asset, name, trend)

    # }}}
    @classmethod  # __getSizes  # {{{
    def __getSize(cls, trend: Trend, trait: Trait, value) -> pd.DataFrame:
        sizes = cls.load(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            analyse=cls.Analyse.SIZE,
        )
        trait_sizes = sizes.xs(trait.name.lower())

        row = trait_sizes.query(f"begin <= {value} < end")
        if not row.empty:
            size = Size.fromStr(row.index.values[0])
            return size

        if value < trait_sizes.begin["GREATEST_SMALL"]:
            return Size.BLACKSWAN_SMALL

        if value > trait_sizes.end["GREATEST_BIG"]:
            return Size.BLACKSWAN_BIG

    # }}}


# }}}


async def main():  # {{{
    await TrendAnalytic.updateAll()
    return

    asset = await Asset.fromStr("MOEX SHARE AFKS")
    tf = TimeFrame("5M")
    term = Term.STERM
    analyse = TrendAnalytic.Analyse.SIZE

    sizes = TrendAnalytic.load(asset, tf, term, analyse)
    print(sizes.xs("delta"))


# }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
