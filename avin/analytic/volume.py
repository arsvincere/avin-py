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
from avin.core import Asset, Bar, Chart, TimeFrame
from avin.data import Data
from avin.extra.size import Size
from avin.utils import Tree, configureLogger, logger, now


class VolumeAnalytic(Analytic):
    name = "volume"
    cache = Tree()

    class Analyse(enum.Enum):  # {{{
        SIZE = 1

        def __str__(self):
            return self.name.lower()

    # }}}

    @classmethod  # getSizes  # {{{
    def getSizes(cls, asset: Asset, tf: TimeFrame) -> pl.DataFrame | None:
        # # try find sizes in cache
        # sizes = cls.cache[asset][tf][typ]
        # if sizes:
        #     return sizes

        # load
        sizes = cls.load(asset, tf, cls.Analyse.SIZE)
        return sizes

    # }}}
    @classmethod  # size  # {{{
    def size(cls, bar: Bar) -> Size:
        assert isinstance(bar, Bar)

        # get sizes
        asset = bar.chart.asset
        tf = bar.chart.timeframe
        sizes = cls.getSizes(asset, tf)

        value = bar.volume
        size = super()._identifySize(value, sizes)

        return size

    # }}}
    @classmethod  # maxVol  # {{{
    def maxVol(cls, asset: Asset, tf: TimeFrame) -> int:
        sizes = cls.getSizes(asset, tf)
        vol = sizes.item(-1, "end")

        return vol

    # }}}
    @classmethod  # minVol  # {{{
    def minVol(cls, asset: Asset, tf: TimeFrame) -> int:
        sizes = cls.getSizes(asset, tf)
        vol = sizes.item(0, "begin")

        return vol

    # }}}

    @classmethod  # analyse  #  {{{
    async def analyse(
        cls, asset: Asset, tf: TimeFrame, analyse: VolumeAnalytic.Analyse
    ) -> None:
        logger.info(f":: {cls.name} analyse {asset.ticker}-{tf}")

        chart = await cls.__loadChart(asset, tf)
        cls.__analyseVolume(chart)

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
        analyse: VolumeAnalytic.Analyse,
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
    @classmethod  # __analyseVolume  # {{{
    def __analyseVolume(cls, chart: Chart):
        # skip if not enought bars
        min_bars = 200
        n = len(chart)
        if n < min_bars:
            logger.warning(
                f"Skip {chart} - not enought bars [{n}/{min_bars}]"
            )
            return

        logger.info("   collect elements")
        df = chart.data_frame
        volumes = df["volume"]

        logger.info("   classify sizes")
        sizes = super()._classifySizes(volumes)

        logger.info("   save analyse")
        name = f"{cls.name} {chart.timeframe} {cls.Analyse.SIZE}"
        super().save(chart.asset, name, sizes)

    # }}}


async def main():  # {{{
    pl.Config.set_tbl_rows(100)
    await VolumeAnalytic.analyseAll()
    return

    asset = await Asset.fromStr("MOEX SHARE AFKS")
    tf = TimeFrame("1M")
    analyse = VolumeAnalytic.Analyse.SIZE

    await VolumeAnalytic.analyse(asset, tf, analyse)

    # df = VolumeAnalytic.load(asset, tf, analyse)
    # print(df)

    # sizes = VolumeAnalytic.getSizes(asset, tf)
    # print(sizes)

    # chart = await asset.loadChart(tf)
    # bar = chart.last
    # size = VolumeAnalytic.size(bar)

    # min_vol = VolumeAnalytic.minVol(asset, tf)
    # max_vol = VolumeAnalytic.maxVol(asset, tf)
    # print(min_vol, max_vol)


# }}}

if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(main())
