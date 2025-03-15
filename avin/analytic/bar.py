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
from avin.core import Asset, Chart, Range, TimeFrame
from avin.data import Data
from avin.extra.size import Size
from avin.utils import Tree, configureLogger, logger, now


class BarAnalytic(Analytic):
    name = "bar"
    cache = Tree()

    class Analyse(enum.Enum):  # {{{
        SIZE = 1

        def __str__(self):
            return self.name.lower()

    # }}}

    @classmethod  # getSizes  # {{{
    def getSizes(
        cls, asset: Asset, tf: TimeFrame, element: Range.Type
    ) -> pl.DataFrame | None:
        # # try find sizes in cache
        # sizes = cls.cache[asset][tf][typ]
        # if sizes:
        #     return sizes

        # load
        all_sizes = cls.load(asset, tf, cls.Analyse.SIZE)
        sizes = all_sizes.filter(pl.col("element") == element.name.lower())

        return sizes

    # }}}
    @classmethod  # size  # {{{
    def size(cls, r: Range) -> Size:
        assert isinstance(r, Range)

        # get sizes
        asset = r.bar.chart.asset
        tf = r.bar.chart.timeframe
        element = r.type
        sizes = cls.getSizes(asset, tf, element)

        value = r.percent()
        size = super()._identifySize(value, sizes)

        return size

    # }}}

    @classmethod  # analyse  #  {{{
    async def analyse(
        cls, asset: Asset, tf: TimeFrame, analyse: BarAnalytic.Analyse
    ) -> None:
        logger.info(f":: {cls.name} analyse {asset.ticker}-{tf}")

        chart = await cls.__loadChart(asset, tf)
        cls.__analyseBar(chart)

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
                for a in cls.Analyse:
                    await cls.analyse(asset, tf, a)

    # }}}
    @classmethod  # load  # {{{
    def load(
        cls,
        asset: Asset,
        tf: TimeFrame,
        analyse: BarAnalytic.Analyse,
    ) -> pl.DataFrame | None:
        logger.debug(f"{cls.__name__}.load()")

        name = f"{cls.name} {tf} {analyse}"
        df = super().load(asset, name)

        return df

    # }}}

    @classmethod  # __loadChart  # {{{
    async def __loadChart(cls, asset: Asset, tf: TimeFrame) -> Chart:
        logger.info("   loading chart")
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
            case _:
                logger.critical(f"Not supported timeframe={tf}")
                assert False, "TODO_ME"

        chart = await asset.loadChart(tf, begin, end=now())
        return chart

    # }}}
    @classmethod  # __analyseBar  # {{{
    def __analyseBar(cls, chart: Chart):
        # skip if not enought bars
        min_bars = 200
        n = len(chart)
        if n < min_bars:
            logger.warning(
                f"Skip {chart} - not enought bars [{n}/{min_bars}]"
            )
            return

        # collect elements
        logger.info("   collect elements")
        full = cls.__collectFull(chart)
        body = cls.__collectBody(chart)
        uppr = cls.__collectUpper(chart)
        lowr = cls.__collectLower(chart)

        # classify
        logger.info("   classify sizes")
        full_sizes = super()._classifySizes(full)
        body_sizes = super()._classifySizes(body)
        uppr_sizes = super()._classifySizes(uppr)
        lowr_sizes = super()._classifySizes(lowr)

        # add column with element name
        full_sizes = full_sizes.with_columns(element=pl.lit("full"))
        body_sizes = full_sizes.with_columns(element=pl.lit("body"))
        uppr_sizes = full_sizes.with_columns(element=pl.lit("upper"))
        lowr_sizes = full_sizes.with_columns(element=pl.lit("lower"))

        # create total df
        sizes = pl.DataFrame(
            schema=[
                ("size", pl.String),
                ("begin", pl.Float64),
                ("end", pl.Float64),
                ("element", pl.String),
            ]
        )
        sizes.extend(full_sizes)
        sizes.extend(body_sizes)
        sizes.extend(uppr_sizes)
        sizes.extend(lowr_sizes)

        # save
        logger.info("   save analyse")
        name = f"{cls.name} {chart.timeframe} {cls.Analyse.SIZE}"
        super().save(chart.asset, name, sizes)

    # }}}
    @classmethod  # __collectFull  # {{{
    def __collectFull(cls, chart: Chart) -> pl.Series:
        logger.info("   - collect full")

        df = chart.data_frame
        df = df.with_columns((pl.col("high") - pl.col("low")).alias("delta"))

        # bull bars
        df = df.with_columns(
            (pl.col("delta") / pl.col("high") * 100).alias("percent")
        )

        total = df["percent"]
        return total

    # }}}
    @classmethod  # __collectBody  # {{{
    def __collectBody(cls, chart: Chart) -> pl.Series:
        logger.info("   - collect body")

        df = chart.data_frame
        df = df.with_columns(
            (pl.col("open") - pl.col("close")).alias("delta")
        )

        # bull bars
        bull = df.filter(pl.col("delta") > 0).with_columns(
            (pl.col("delta") / pl.col("close") * 100).alias("percent")
        )
        # bear bars
        bear = df.filter(pl.col("delta") < 0).with_columns(
            (-pl.col("delta") / pl.col("open") * 100).alias("percent")
        )

        total = bull["percent"].extend(bear["percent"])
        return total

    # }}}
    @classmethod  # __collectUpper  # {{{
    def __collectUpper(cls, chart: Chart) -> pl.Series:
        logger.info("   - collect upper")

        df = chart.data_frame
        df = df.with_columns(
            (pl.col("open") - pl.col("close")).alias("delta")
        )

        # bull bars
        bull = df.filter(pl.col("delta") > 0)
        bull = bull.with_columns(
            (pl.col("high") - pl.col("close")).alias("upper")
        )
        bull = bull.with_columns(
            (pl.col("upper") / pl.col("high") * 100).alias("percent")
        )

        # bear bars
        bear = df.filter(pl.col("delta") < 0)
        bear = bear.with_columns(
            (pl.col("high") - pl.col("open")).alias("upper")
        )
        bear = bear.with_columns(
            (pl.col("upper") / pl.col("high") * 100).alias("percent")
        )

        total = bull["percent"].extend(bear["percent"])
        return total

    # }}}
    @classmethod  # __collectLower  # {{{
    def __collectLower(cls, chart: Chart) -> pl.Series:
        logger.info("   - collect lower")

        df = chart.data_frame
        df = df.with_columns(
            (pl.col("open") - pl.col("close")).alias("delta")
        )

        # bull bars
        bull = df.filter(pl.col("delta") > 0)
        bull = bull.with_columns(
            (pl.col("open") - pl.col("low")).alias("lower")
        )
        bull = bull.with_columns(
            (pl.col("lower") / pl.col("open") * 100).alias("percent")
        )

        # bear bars
        bear = df.filter(pl.col("delta") < 0)
        bear = bear.with_columns(
            (pl.col("close") - pl.col("low")).alias("lower")
        )
        bear = bear.with_columns(
            (pl.col("lower") / pl.col("close") * 100).alias("percent")
        )

        total = bull["percent"].extend(bear["percent"])
        return total

    # }}}


async def main():  # {{{
    await BarAnalytic.analyseAll()
    return

    # pl.Config.set_tbl_rows(100)
    # asset = await Asset.fromStr("MOEX SHARE SBER")
    # tf = TimeFrame("D")
    # analyse = BarAnalytic.Analyse.SIZE

    # await BarAnalytic.analyse(asset, tf, analyse)

    # df = BarAnalytic.load(asset, tf, analyse)
    # print(df)

    # sizes = BarAnalytic.getSizes(asset, tf, Range.Type.FULL)
    # pl.Config.set_tbl_rows(20)
    # print(sizes)
    # with pl.Config():

    # chart = await asset.loadChart(tf)
    # bar = chart.last
    # size = BarAnalytic.size(bar.full)
    # print(size)


# }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
