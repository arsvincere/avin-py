#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import asyncio
from datetime import datetime

import polars as pl
from PyQt6 import QtCore

from avin.analytic import VolumeAnalytic
from avin.core import Asset, Chart, TimeFrame
from avin.data import Data
from avin.utils import logger
from gui.custom import awaitQThread


class Thread:  # {{{
    """Fasade class"""

    @classmethod  # loadBars  # {{{
    def loadBars(cls, asset, timeframe, begin, end) -> pl.DataFrame:
        logger.debug(f"{cls.__name__}.loadChart()")

        thread = _TLoadBars(asset, timeframe, begin, end)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # loadChart  # {{{
    def loadChart(cls, asset, timeframe, begin=None, end=None) -> Chart:
        logger.debug(f"{cls.__name__}.loadChart()")

        thread = _TLoadChart(asset, timeframe, begin, end)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # addMark  # {{{
    def addMark(cls, gchart: GChart, mark: Mark) -> None:
        logger.debug(f"{cls.__name__}.addGMarker()")

        thread = _TAddMarker(gchart, mark)
        thread.start()
        awaitQThread(thread)

    # }}}
    @classmethod  # getMaxVol  # {{{
    def getMaxVol(cls, asset, timeframe) -> int:
        logger.debug(f"{cls.__name__}.getMaxVol()")

        thread = _TGetMaxVol(asset, timeframe)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}
    @classmethod  # getVolSizes  # {{{
    def getVolSizes(cls, asset, timeframe) -> int:
        logger.debug(f"{cls.__name__}.getVolSizes()")

        thread = _TGetVolSizes(asset, timeframe)
        thread.start()
        awaitQThread(thread)

        return thread.result

    # }}}


# }}}
class _TLoadBars(QtCore.QThread):  # {{{
    def __init__(
        self,
        asset: Asset,
        timeframe: TimeFrame,
        begin: datetime,
        end: datetime,
        parent=None,
    ):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__asset = asset
        self.__timeframe = timeframe
        self.__begin = begin
        self.__end = end

        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        records = await Data.request(
            instrument=self.__asset,
            data_type=self.__timeframe.toDataType(),
            begin=self.__begin,
            end=self.__end,
        )
        self.result = pl.DataFrame([dict(r) for r in records])

    # }}}


# }}}
class _TLoadChart(QtCore.QThread):  # {{{
    def __init__(
        self,
        asset: Asset,
        timeframe: TimeFrame,
        begin: datetime,
        end: datetime,
        parent=None,
    ):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__asset = Asset
        self.__timeframe = timeframe
        self.__begin = begin
        self.__end = end

        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await self.__asset.loadChart(
            self.__timeframe,
            self.__begin,
            self.__end,
        )

    # }}}


# }}}
class _TAddMarker(QtCore.QThread):  # {{{
    def __init__(self, gchart: GChart, mark: Mark, parent=None):  # {{{
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__gchart = gchart
        self.__mark = mark

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        gchart = self.__gchart
        mark = self.__mark
        chart = self.__gchart.chart
        f = self.__mark.filter

        chart.setHeadIndex(0)
        while chart.nextHead():
            result = await f.acheck(chart)

            if result:
                dt = chart.now.dt
                gbar = gchart.gbarFromDatetime(dt)
                gbar.addGShape(mark.shape)

    # }}}


# }}}
class _TGetMaxVol(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self,
        asset: Asset,
        timeframe: TimeFrame,
        parent=None,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__asset = Asset
        self.__timeframe = timeframe

        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await VolumeAnalytic.maxVol(
            self.__asset, self.__timeframe
        )

    # }}}


# }}}
class _TGetVolSizes(QtCore.QThread):  # {{{
    def __init__(  # {{{
        self,
        asset: Asset,
        timeframe: TimeFrame,
        parent=None,
    ):
        logger.debug(f"{self.__class__.__name__}.__init__()")
        QtCore.QThread.__init__(self, parent)

        self.__asset = Asset
        self.__timeframe = timeframe

        self.result = None

    # }}}
    def run(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.run()")

        asyncio.run(self.__arun())

    # }}}
    async def __arun(self):  # {{{
        logger.debug(f"{self.__class__.__name__}.__arun()")

        self.result = await VolumeAnalytic.sizes(
            self.__asset, self.__timeframe
        )

    # }}}


# }}}


if __name__ == "__main__":
    ...
