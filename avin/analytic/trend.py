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

import polars as pl

from avin.analytic._analytic import Analytic
from avin.const import ONE_YEAR
from avin.core import Asset, TimeFrame
from avin.data import Data
from avin.extra import ExtremumList, Term
from avin.extra.size import Size
from avin.utils import configureLogger, logger, now

__all__ = ("TrendAnalytic",)


class TrendAnalytic(Analytic):
    name = "trend"

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
        VOL_BULL = 4
        VOL_BEAR = 5
        VOL_TOTAL = 6

        def __str__(self):
            return self.name.lower()

    # }}}

    @classmethod  # getSizes  # {{{
    def getSizes(
        cls,
        asset: Asset,
        tf: TimeFrame,
        term: Term,
        trait: TrendAnalytic.Trait,
    ) -> pl.DataFrame:
        sizes = cls.load(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            analyse=cls.Analyse.SIZE,
        )
        trait_sizes = sizes.filter(pl.col(str(trait) == "trait"))

        return trait_sizes

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

    @classmethod  # analyse  #  {{{
    async def analyse(cls, asset: Asset, tf: TimeFrame, term: Term) -> None:
        logger.info(f":: {cls.name} analyse {asset.ticker}-{tf} {term}")

        await cls.__collectTrends(asset, tf, term)
        cls.__defineTrendSizes(asset, tf, term)
        cls.__setTrendSizes(asset, tf, term)

    # }}}
    @classmethod  # analyseAll  #  {{{
    async def analyseAll(cls) -> None:
        logger.info(f":: Analytic-{cls.name} analyse all")

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
                # for term in Term:
                term = Term.T1
                await TrendAnalytic.analyse(asset, tf, term)

    # }}}
    @classmethod  # load  # {{{
    def load(
        cls,
        asset: Asset,
        tf: TimeFrame,
        term: Term,
        analyse: TrendAnalytic.Analyse,
    ) -> pl.DataFrame | None:
        logger.debug(f"{cls.__name__}.load()")

        name = f"{cls.name} {tf} {term} {analyse}"
        df = super().load(asset, name)

        return df

    # }}}

    @classmethod  # __loadChart  # {{{
    async def __loadChart(cls, asset, tf):
        match str(tf):
            case "1M":
                begin = now() - ONE_YEAR * 5
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
    @classmethod  # __createDataFrame  # {{{
    def __createDataFrame(cls, trends: list[Trend]):
        begin = list()
        end = list()
        begin_price = list()
        end_price = list()
        typ = list()
        period = list()
        delta = list()
        speed = list()
        vol_bear = list()
        vol_bull = list()
        vol_total = list()

        for trend in trends:
            begin.append(trend.begin.dt)
            end.append(trend.end.dt)
            begin_price.append(trend.begin.price)
            end_price.append(trend.end.price)
            typ.append(trend.type.name)
            period.append(trend.period())
            delta.append(trend.deltaPercent())
            speed.append(trend.speedPercent())
            vol_bear.append(trend.volumeBear())
            vol_bull.append(trend.volumeBull())
            vol_total.append(trend.volumeTotal())

        df = pl.DataFrame(
            {
                "begin": begin,
                "end": end,
                "begin_price": begin_price,
                "end_price": end_price,
                "type": typ,
                "period": period,
                "delta": delta,
                "speed": speed,
                "vol_bear": vol_total,
                "vol_bull": vol_total,
                "vol_total": vol_total,
            }
        )

        return df

    # }}}
    @classmethod  # __defineTrendSizes  # {{{
    def __defineTrendSizes(cls, asset: Asset, tf: TimeFrame, term: Term):
        logger.info("   Define trend sizes")

        # load trends
        name = f"{cls.name} {tf} {term} {cls.Analyse.TREND}"
        trend = super().load(asset, name)

        # skip if the amount is small
        min_trends = 200
        if len(trend) < 200:
            logger.warning(
                f"Skip {asset.ticker}-{tf}{term} "
                f"- not enought trends [{n}/{min_trends}]"
            )
            return

        # classify
        period = super()._classifySizes(trend["period"])
        delta = super()._classifySizes(trend["delta"])
        speed = super()._classifySizes(trend["speed"])
        vol_bear = super()._classifySizes(trend["vol_bear"])
        vol_bull = super()._classifySizes(trend["vol_bull"])
        vol_total = super()._classifySizes(trend["vol_total"])

        # add column with trait name
        period = period.with_columns(trait=pl.lit("period"))
        delta = delta.with_columns(trait=pl.lit("delta"))
        speed = speed.with_columns(trait=pl.lit("speed"))
        vol_bear = vol_bear.with_columns(trait=pl.lit("vol_bear"))
        vol_bull = vol_bear.with_columns(trait=pl.lit("vol_bull"))
        vol_total = vol_bear.with_columns(trait=pl.lit("vol_total"))

        # cast int -> float
        period = period.cast({"begin": pl.Float64, "end": pl.Float64})
        vol_bear = vol_bear.cast({"begin": pl.Float64, "end": pl.Float64})
        vol_bull = vol_bull.cast({"begin": pl.Float64, "end": pl.Float64})
        vol_total = vol_total.cast({"begin": pl.Float64, "end": pl.Float64})

        # total df
        sizes = period
        sizes.extend(delta)
        sizes.extend(speed)
        sizes.extend(vol_bear)
        sizes.extend(vol_bull)
        sizes.extend(vol_total)

        name = f"{cls.name} {tf} {term} {cls.Analyse.SIZE}"
        super().save(asset, name, sizes)
        return

        # name = f"{cls.name} {tf} {term} period_{cls.Analyse.SIZE}"
        # super().save(asset, name, period)
        #
        # name = f"{cls.name} {tf} {term} delta_{cls.Analyse.SIZE}"
        # super().save(asset, name, delta)
        #
        # name = f"{cls.name} {tf} {term} speed_{cls.Analyse.SIZE}"
        # super().save(asset, name, speed)
        #
        # name = f"{cls.name} {tf} {term} vol_bear_{cls.Analyse.SIZE}"
        # super().save(asset, name, vol_bear)
        #
        # name = f"{cls.name} {tf} {term} vol_bull_{cls.Analyse.SIZE}"
        # super().save(asset, name, vol_bull)
        #
        # name = f"{cls.name} {tf} {term} vol_total_{cls.Analyse.SIZE}"
        # super().save(asset, name, vol_total)

    # }}}
    @classmethod  # __setTrendSizes  # {{{
    def __setTrendSizes(cls, asset: Asset, tf: TimeFrame, term: Term):
        logger.info("   Set trend sizes")

        # load trends & table sizes
        df = super().load(asset, f"{cls.name} {tf} {term} trend")
        sz = super().load(asset, f"{cls.name} {tf} {term} size")
        if df is None or sz is None:
            return

        # set trait sizes
        for trait in cls.Trait:
            trait_sz_table = sz.filter(pl.col("trait") == str(trait))
            trait_values = df.get_column(str(trait))
            sizes = trait_values.map_elements(
                lambda x: cls._identifySize(x, trait_sz_table),
                return_dtype=pl.Object,  # type = avin.Size
            )
            df = df.with_columns(
                sizes.map_elements(
                    lambda x: x.name, return_dtype=pl.String
                ).alias(f"{trait}_size"),
                sizes.map_elements(
                    lambda x: x.simple().name, return_dtype=pl.String
                ).alias(f"{trait}_ssize"),
            )

        # save all trends with setted trait sizes
        name = f"{cls.name} {tf} {term} {cls.Analyse.TREND}"
        super().save(asset, name, df)

    # }}}


async def main():  # {{{
    # pl.Config.set_tbl_rows(1000)
    await TrendAnalytic.analyseAll()
    return

    asset = await Asset.fromStr("MOEX SHARE AFKS")
    tf = TimeFrame("D")
    term = Term.T1

    await TrendAnalytic.analyse(asset, tf, term)

    # analyse = TrendAnalytic.Analyse.TREND
    # df = TrendAnalytic.load(asset, tf, term, analyse)
    # print(df)
    # print(df.columns)


# }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
