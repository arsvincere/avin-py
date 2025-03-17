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
from avin.core import Asset, Chart, TimeFrame
from avin.data import Data
from avin.extra.extremum_list import ExtremumList
from avin.extra.size import SimpleSize, Size
from avin.extra.term import Term
from avin.extra.trend import Trend
from avin.utils import configureLogger, logger, now


class TrendAnalytic(Analytic):
    name = "trend"

    class Analyse(enum.Enum):  # {{{
        TREND = 1
        SIZE = 2
        SIMPLE_SIZE = 3

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
            asset=asset,
            tf=tf,
            term=term,
            analyse=cls.Analyse.SIZE,
        )
        if sizes is None:
            return None

        trait_sizes = sizes.filter(pl.col("trait") == str(trait))
        return trait_sizes

    # }}}
    @classmethod  # getSimpleSizes  # {{{
    def getSimpleSizes(
        cls,
        asset: Asset,
        tf: TimeFrame,
        term: Term,
        trait: TrendAnalytic.Trait,
    ) -> pl.DataFrame:
        sizes = cls.load(
            asset=asset,
            tf=tf,
            term=term,
            analyse=cls.Analyse.SIMPLE_SIZE,
        )
        trait_sizes = sizes.filter(pl.col("trait") == str(trait))

        return trait_sizes

    # }}}
    @classmethod  # periodSize  # {{{
    def periodSize(cls, trend: Trend) -> Size:
        sizes = cls.getSizes(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            trait=cls.Trait.PERIOD,
        )

        value = trend.period()
        size = super()._identifySize(value, sizes)
        return size

    # }}}
    @classmethod  # deltaSize  # {{{
    def deltaSize(cls, trend: Trend) -> Size | None:
        sizes = cls.getSizes(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            trait=cls.Trait.DELTA,
        )
        if sizes is None:
            return None

        value = trend.deltaPercent()
        size = super()._identifySize(value, sizes)
        return size

    # }}}
    @classmethod  # speedSize  # {{{
    def speedSize(cls, trend: Trend) -> Size:
        sizes = cls.getSizes(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            trait=cls.Trait.SPEED,
        )

        value = trend.speedPercent()
        size = super()._identifySize(value, sizes)
        return size

    # }}}
    @classmethod  # volumeBearSize  # {{{
    def volumeBearSize(cls, trend: Trend) -> Size:
        sizes = cls.getSizes(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            trait=cls.Trait.VOL_TOTAL,
        )

        value = trend.volumeBear()
        size = super()._identifySize(value, sizes)
        return size

    # }}}
    @classmethod  # volumeBullSize  # {{{
    def volumeBullSize(cls, trend: Trend) -> Size:
        sizes = cls.getSizes(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            trait=cls.Trait.VOL_TOTAL,
        )

        value = trend.volumeBull()
        size = super()._identifySize(value, sizes)
        return size

    # }}}
    @classmethod  # volumeTotalSize  # {{{
    def volumeTotalSize(cls, trend: Trend) -> Size:
        sizes = cls.getSizes(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            trait=cls.Trait.VOL_TOTAL,
        )

        value = trend.volumeTotal()
        size = super()._identifySize(value, sizes)
        return size

    # }}}

    @classmethod  # posterior  # {{{
    def posterior(cls, trend: Trend) -> pl.DataFrame | None:
        assert isinstance(trend, Trend)

        # try get trend delta size
        size = TrendAnalytic.deltaSize(trend)
        if size is None:
            return None

        # get df with cumulative probability
        trait = "delta_ssize"
        H = [str(i) for i in SimpleSize]
        obs = str(size.simple())
        trends = cls.load(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            analyse=cls.Analyse.TREND,
        )
        posterior = cls.__posteriorSimple(obs, H, trait, trends)

        # load sizes table
        ssizes = cls.load(
            asset=trend.asset,
            tf=trend.timeframe,
            term=trend.term,
            analyse=cls.Analyse.SIMPLE_SIZE,
        )
        trait_ssizes = ssizes.filter(pl.col("trait") == "delta")

        # Если тренд бычий, значит следующий медвежий.
        # а дельты все по модулю посчитаны, так что
        # для определения цен текущего медвежьего тренда, надо
        # дельты умножить на -1
        if trend.isBull():
            trait_ssizes = trait_ssizes.with_columns(
                begin=-pl.col("begin"),
                end=-pl.col("end"),
            )

        # calc prices
        price = trend.end.price
        posterior = posterior.with_columns(
            # begin_price=price,  # + trait_ssizes["begin"] * price / 100,
            begin_price=price + trait_ssizes["begin"] * price / 100,
            end_price=price + trait_ssizes["end"] * price / 100,
        )

        return posterior

    # }}}

    @classmethod  # analyse  #  {{{
    async def analyse(cls, asset: Asset, tf: TimeFrame, term: Term) -> None:
        logger.info(f":: {cls.name} analyse {asset.ticker}-{tf} {term}")

        chart = await cls.__loadChart(asset, tf)
        elist = cls.__defineExtremum(chart)
        cls.__getAllTrends(elist, term)
        cls.__defineTrendSizes(asset, tf, term)
        cls.__defineTrendSimpleSizes(asset, tf, term)
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
            # TimeFrame("1M"),
        ]

        for asset in assets:
            for tf in timeframes:
                logger.info(f":: {cls.name} analyse {asset.ticker}-{tf}")
                chart = await cls.__loadChart(asset, tf)
                elist = cls.__defineExtremum(chart)
                for term in Term:
                    cls.__getAllTrends(elist, term)
                    cls.__defineTrendSizes(asset, tf, term)
                    cls.__defineTrendSimpleSizes(asset, tf, term)
                    cls.__setTrendSizes(asset, tf, term)

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
        logger.info("   Loading chart")

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
    @classmethod  # __defineExtremum  # {{{
    def __defineExtremum(cls, chart: Chart):
        logger.info("   Define extremums")

        elist = ExtremumList(chart)

        return elist

    # }}}
    @classmethod  # __getAllTrends  # {{{
    def __getAllTrends(
        cls,
        elist: ExtremumList,
        term: Term,
    ):
        logger.info(f"   Get all trends {term}")

        trends = elist.getAllTrends(term)
        df = cls.__createDataFrame(trends)

        name = f"{cls.name} {elist.timeframe} {term} {cls.Analyse.TREND}"
        super().save(
            asset=elist.asset,
            analyse_name=name,
            data_frame=df,
        )

    # }}}
    @classmethod  # __createDataFrame  # {{{
    def __createDataFrame(cls, trends: list[Trend]):
        logger.info("   - create dataframe")

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
                "vol_bear": vol_bear,
                "vol_bull": vol_bull,
                "vol_total": vol_total,
            }
        )

        return df

    # }}}
    @classmethod  # __defineTrendSizes  # {{{
    def __defineTrendSizes(cls, asset: Asset, tf: TimeFrame, term: Term):
        logger.info("   - define trend sizes")

        # load trends
        name = f"{cls.name} {tf} {term} {cls.Analyse.TREND}"
        trend = super().load(asset, name)

        # skip if the amount is small
        min_trends = 200
        n = len(trend)
        if n < min_trends:
            logger.warning(
                f"Skip {asset.ticker}-{tf} {term} "
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
        vol_bull = vol_bull.with_columns(trait=pl.lit("vol_bull"))
        vol_total = vol_total.with_columns(trait=pl.lit("vol_total"))

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

    # }}}
    @classmethod  # __defineTrendSimpleSizes  # {{{
    def __defineTrendSimpleSizes(
        cls, asset: Asset, tf: TimeFrame, term: Term
    ):
        logger.info("   - define trend simple sizes")

        # load trends
        name = f"{cls.name} {tf} {term} {cls.Analyse.TREND}"
        trend = super().load(asset, name)

        # skip if the amount is small
        min_trends = 200
        n = len(trend)
        if n < min_trends:
            logger.warning(
                f"Skip {asset.ticker}-{tf} {term} "
                f"- not enought trends [{n}/{min_trends}]"
            )
            return

        # classify
        period = super()._classifySimpleSizes(trend["period"])
        delta = super()._classifySimpleSizes(trend["delta"])
        speed = super()._classifySimpleSizes(trend["speed"])
        vol_bear = super()._classifySimpleSizes(trend["vol_bear"])
        vol_bull = super()._classifySimpleSizes(trend["vol_bull"])
        vol_total = super()._classifySimpleSizes(trend["vol_total"])

        # add column with trait name
        period = period.with_columns(trait=pl.lit("period"))
        delta = delta.with_columns(trait=pl.lit("delta"))
        speed = speed.with_columns(trait=pl.lit("speed"))
        vol_bear = vol_bear.with_columns(trait=pl.lit("vol_bear"))
        vol_bull = vol_bull.with_columns(trait=pl.lit("vol_bull"))
        vol_total = vol_total.with_columns(trait=pl.lit("vol_total"))

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

        name = f"{cls.name} {tf} {term} {cls.Analyse.SIMPLE_SIZE}"
        super().save(asset, name, sizes)
        return

    # }}}
    @classmethod  # __setTrendSizes  # {{{
    def __setTrendSizes(cls, asset: Asset, tf: TimeFrame, term: Term):
        logger.info("   - set trend sizes")

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

            size_col_name = f"{trait}_size"
            ssize_col_name = f"{trait}_ssize"
            df = df.with_columns(
                sizes.map_elements(
                    lambda x: x.name, return_dtype=pl.String
                ).alias(size_col_name),
                sizes.map_elements(
                    lambda x: x.simple().name, return_dtype=pl.String
                ).alias(ssize_col_name),
            )

            # INFO: из за того что я классифицию размеры
            # по формуле (begin <= x < end)
            # то у меня полюбому в получается один BLACKSWAN_BIG / XXL
            # а так не должно быть, в истории он должен быть с размером
            # GREATEST_BIG  /  XL   соответственно. Replace it.
            df = df.with_columns(
                pl.when(pl.col(size_col_name) == "BLACKSWAN_BIG")
                .then(pl.lit("GREATEST_BIG"))
                .otherwise(pl.col(size_col_name))
                .alias(size_col_name),
                pl.when(pl.col(ssize_col_name) == "XXL")
                .then(pl.lit("XL"))
                .otherwise(pl.col(ssize_col_name))
                .alias(ssize_col_name),
            )

        # save all trends with setted trait sizes
        name = f"{cls.name} {tf} {term} {cls.Analyse.TREND}"
        super().save(asset, name, df)

    # }}}

    @classmethod  # __posteriorSimple  # {{{
    def __posteriorSimple(
        cls, obs: str, H: list[str], trait: str, trends: pl.DataFrame
    ) -> pl.DataFrame:
        df = trends.with_row_index()
        obs_trends = df.filter(pl.col(trait) == obs)
        obs_index = obs_trends["index"]
        h_index = obs_index + 1

        posterior = list()
        for h in H:
            pair_trends = df.filter(
                pl.col("index").is_in(h_index),
                pl.col(trait) == h,
            )
            p = len(pair_trends) / len(obs_trends)
            posterior.append(p)

        result = pl.DataFrame(
            {
                trait: H,
                "probability": posterior,
            }
        )
        result = result.with_columns(
            cumulative=pl.col("probability").reverse().cum_sum().reverse()
            * 100
        )
        return result

    # }}}


async def main():  # {{{
    # pl.Config.set_tbl_rows(50)
    # await TrendAnalytic.analyseAll()
    # return

    asset = await Asset.fromStr("MOEX SHARE AFKS")
    tf = TimeFrame("D")
    term = Term.T1
    trait = TrendAnalytic.Trait.DELTA

    await TrendAnalytic.analyse(asset, tf, term)

    # analyse = TrendAnalytic.Analyse.TREND
    # df = TrendAnalytic.load(asset, tf, term, analyse)
    # print(df[["delta", "vol_total", "delta_size", "vol_total_size"]])

    # analyse = TrendAnalytic.Analyse.SIMPLE_SIZE
    # df = TrendAnalytic.load(asset, tf, term, analyse)
    # print(df)

    df = TrendAnalytic.getSimpleSizes(asset, tf, term, trait)
    print(df)

    # df = TrendAnalytic.getSizes(asset, tf, term, trait)
    # print(df)


# }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
