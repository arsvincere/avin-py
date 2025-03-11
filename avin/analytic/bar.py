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

__all__ = ("BarAnalytic",)


class BarAnalytic(Analytic):
    name = "Bar"
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

        # try find size
        value = r.percent()
        result = sizes.filter(
            (value >= pl.col("begin")),
            (value < pl.col("end")),
        )

        # ok - return size
        if len(result) == 1:
            size = Size.fromStr(result.item(0, "size"))
            return size

        # else - BLACKSWAN
        if value < sizes.item(0, "begin"):
            return Size.BLACKSWAN_SMALL
        if value > sizes.item(-1, "begin"):
            return Size.BLACKSWAN_BIG

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
        body = cls.__collectBarElement(chart, Range.Type.BODY)
        full = cls.__collectBarElement(chart, Range.Type.FULL)
        uppr = cls.__collectBarElement(chart, Range.Type.UPPER)
        lowr = cls.__collectBarElement(chart, Range.Type.LOWER)

        # classify
        logger.info("   classify sizes")
        body_sizes = super()._classifySizes(body)
        full_sizes = super()._classifySizes(full)
        uppr_sizes = super()._classifySizes(uppr)
        lowr_sizes = super()._classifySizes(lowr)

        # insert column with element name
        b = pl.Series("element", ["body"] * len(body_sizes))
        f = pl.Series("element", ["full"] * len(full_sizes))
        u = pl.Series("element", ["upper"] * len(uppr_sizes))
        l = pl.Series("element", ["lower"] * len(lowr_sizes))
        body_sizes.insert_column(0, b)
        full_sizes.insert_column(0, f)
        uppr_sizes.insert_column(0, u)
        lowr_sizes.insert_column(0, l)

        # create total df
        sizes = pl.DataFrame(
            schema=[
                ("element", pl.String),
                ("size", pl.String),
                ("begin", pl.Float64),
                ("end", pl.Float64),
            ]
        )
        sizes.extend(body_sizes)
        sizes.extend(full_sizes)
        sizes.extend(uppr_sizes)
        sizes.extend(lowr_sizes)

        # save
        logger.info("   save analyse")
        name = f"{cls.name} {chart.timeframe} {cls.Analyse.SIZE}"
        super().save(chart.asset, name, sizes)

    # }}}
    @classmethod  # __collectBarElement  # {{{
    def __collectBarElement(cls, chart, element: Range.Type):
        ranges_list = list()
        for bar in chart:
            # command looks like:  bar.body.percent()
            command = f"bar.{element.name.lower()}.percent()"
            value = eval(command)
            value = round(value, 2)
            ranges_list.append(value)

        return ranges_list

    # }}}


async def main():  # {{{
    await BarAnalytic.analyseAll()
    return

    asset = await Asset.fromStr("MOEX SHARE AFKS")
    tf = TimeFrame("D")
    analyse = BarAnalytic.Analyse.SIZE

    # await BarAnalytic.analyse(asset, tf, analyse)

    # df = BarAnalytic.load(asset, tf, analyse)
    # print(df)

    # sizes = BarAnalytic.getSizes(asset, tf, Range.Type.FULL)
    # print(sizes)

    # chart = await asset.loadChart(tf)
    # bar = chart.last
    # size = BarAnalytic.size(bar.full)
    # print(size)


# }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
