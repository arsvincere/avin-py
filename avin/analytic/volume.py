#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

import asyncio
import collections

import pandas as pd

# import plotly
# import plotly.graph_objs as go
from avin.analytic._analytic import Analytic
from avin.analytic.size import Size
from avin.core import Asset, Bar, TimeFrame
from avin.utils import Tree, logger

__all__ = ("VolumeAnalytic",)


class VolumeAnalytic(Analytic):
    name = "volume"
    cache = Tree()

    @classmethod  # getSizes  # {{{
    async def getSizes(cls, asset: Asset, tf: TimeFrame) -> Size:
        # try find sizes in cache
        sizes_dict = cls.cache[asset][tf]
        if sizes_dict:
            return sizes_dict

        # load
        analyse_name = f"{tf}"
        data = await AnalyticData.load(cls.name, analyse_name, asset)
        sizes_dict = cls.decoderJson(data.json_str)

        # save cache
        cls.cache[asset][tf] = sizes_dict

        return sizes_dict

    # }}}
    @classmethod  # volumeSize  # {{{
    async def volumeSize(cls, bar: Bar) -> Size:
        volume = bar.vol
        chart = bar.chart
        timeframe = chart.timeframe
        instrument = chart.instrument
        asset = Asset.fromInstrument(instrument)

        sizes_dict = cls.getSizes(asset, timeframe)

        # for example:
        # sizes_dict = {
        #     ...,
        #     Size.SMALL: <class Range>,
        #     Size.NORMAL: <class Range>,
        #     Size.BIG: <class Range>,
        #     ...,
        #     }

        size = cls.__identifySize(volume, sizes_dict)
        return size

    # }}}
    @classmethod  # maxVol  # {{{
    async def maxVol(cls, asset: Asset, timeframe: TimeFrame) -> int:
        sizes_dict = await cls.getSizes(asset, timeframe)

        # for example:
        # sizes_dict = {
        #     ...,
        #     Size.SMALL: <class Range(float, float)>,
        #     Size.NORMAL: <class Range(float, float)>,
        #     Size.BIG: <class Range(float, float)>,
        #     ...,
        #     }

        r = sizes_dict[Size.GREATEST_BIG]
        max_vol = int(r.max)

        return max_vol

    # }}}
    @classmethod  # minVol  # {{{
    async def minVol(cls, asset: Asset, timeframe: TimeFrame) -> int:
        sizes_dict = await cls.getSizes(asset, timeframe)

        # for example:
        # sizes_dict = {
        #     ...,
        #     Size.SMALL: <class Range(float, float)>,
        #     Size.NORMAL: <class Range(float, float)>,
        #     Size.BIG: <class Range(float, float)>,
        #     ...,
        #     }

        # BLACKSWAN_SMALL диапазон идет от минимального исторического объема
        # до крошечных объемов которые встречаются в 1% случаев
        # Range хранит min-max во float, поэтому преобразуем в int
        r = sizes_dict[Size.BLACKSWAN_SMALL]
        min_vol = int(r.min)

        return min_vol

    # }}}

    @classmethod  # update  # {{{
    async def update(cls):
        logger.info(f":: Analytic={cls.name}: start update")

        await Analytic.save(cls)

        assets = await Asset.requestAll()
        for asset in assets:
            await cls.__analyseVolume(asset)

        logger.info(f"Analytic={cls.name}: update complete!")

    # }}}

    @classmethod  # __analyseVolume  # {{{
    async def __analyseVolume(cls, asset):
        timeframes = [
            TimeFrame("D"),
            TimeFrame("1H"),
            TimeFrame("5M"),
            TimeFrame("1M"),
        ]

        logger.info(f"   analyse volumes {asset}")
        for timeframe in timeframes:
            logger.info(f"   - {timeframe}")

            info = await Data.info(asset, timeframe.toDataType())
            chart = await asset.loadChart(timeframe, info.first_dt, now())

            await cls.__analyseVolumeTimeFrame(chart)

    # }}}
    @classmethod  # __analyseVolumeTimeFrame  # {{{
    async def __analyseVolumeTimeFrame(cls, chart):
        volumes_list = list()
        for bar in chart:
            v = bar.vol
            volumes_list.append(v)

        if len(volumes_list) < 200:
            return

        classify = cls.__classifySizes(volumes_list)
        await cls.__saveAnalyticData(chart, classify)

    # }}}
    @classmethod  # __classifySizes  # {{{
    def __classifySizes(cls, volumes_list: list) -> dict:
        # create DataFrame
        classify = dict()
        days_count = len(volumes_list)
        counter = collections.Counter(volumes_list)
        sorted_volumes_list = list()
        count_list = list()
        for i in sorted(counter):
            sorted_volumes_list.append(i)
            count_list.append(counter[i])
        df = pd.DataFrame(
            {
                "value": sorted_volumes_list,
                "count": count_list,
            }
        )
        df["percent"] = df["count"] / days_count * 100

        ####
        # df.to_csv("vcp", sep=";")
        # fig = px.scatter(x=df["value"], y=df["percent"])
        # fig.show()
        # exit(0)
        ####

        # create classify
        classify = dict()
        percent = df["percent"]
        minimum = df.iloc[0]["value"]
        last = 1
        for size in Size:
            if size in (
                Size.BLACKSWAN_SMALL,  # не существующие еще черные лебеди
                Size.BLACKSWAN_BIG,  # не существующие еще черные лебеди
                Size.GREATEST_BIG,  # last value set up after cycle
            ):
                continue

            while percent[0:last].sum() < size.value:
                last += 1
            maximum = df.iloc[last]["value"]
            classify[size] = Range(minimum, maximum)
            minimum = maximum

        # set last value GREATEST_BIG
        maximum = df["value"].max()
        classify[Size.GREATEST_BIG] = Range(minimum, maximum)

        return classify

    # }}}
    @classmethod  # __saveAnalyticData  # {{{
    async def __saveAnalyticData(cls, chart, classify):
        asset = chart.instrument
        tf = chart.timeframe
        analyse_name = f"{tf}"

        analytic_data = AnalyticData(
            analytic_name=cls.name,
            analyse_name=analyse_name,
            asset=asset,
            json_str=cls.encoderJson(classify),
        )
        await AnalyticData.save(analytic_data)

    # }}}
    @classmethod  # __identifySize  #{{{
    def __identifySize(cls, value, sizes_dict):
        # смотрим диапазоны, если value в нем, возвращаем этот размер
        for size, range_ in sizes_dict.items():
            if value in range_:
                return size

        # если значение < чем существующий черный лебедь ->  BLACKSWAN_SMALL
        range_ = sizes_dict[Size.BLACKSWAN_SMALL]
        if value < range_.min:
            return Size.BLACKSWAN_SMALL

        # если значение > чем существующий черный лебедь ->  BLACKSWAN_BIG
        range_ = sizes_dict[Size.BLACKSWAN_BIG]
        if value > range_.max:
            return Size.BLACKSWAN_BIG

    # }}}

    @staticmethod  # encoderJson  # {{{
    def encoderJson(data) -> str:
        logger.debug("UAnalytic=volume: encoderJson")

        # from data = {Size.NORMAL: <class Range>, ...}
        # to obj = {"NORMAL": "Range(1.1, 1.5), ..."}
        obj = dict()
        for size, range_ in data.items():
            obj[size.name] = repr(range_)

        # from obj = {"NORMAL": "Range(1.1, 1.5)", ...}
        # to str = '{"NORMAL": "Range(1.1, 1.5)", ...}'
        json_string = Cmd.toJson(obj)

        return json_string

    # }}}
    @staticmethod  # decoderJson  # {{{
    def decoderJson(pg_json_str) -> dict:
        logger.debug("UAnalytic=range: decoderJson")

        # from str = '{"NORMAL": "Range(1.1, 1.5)", ...}'
        # to obj = {"NORMAL": "Range(1.1, 1.5)", ...}
        obj = Cmd.fromJson(pg_json_str)

        # from obj = {"NORMAL": "Range(1.1, 1.5)", ...}
        # to sizes_dict = {Size.NORMAL: <class Range>, ...}
        sizes_dict = dict()
        for size_str, range_repr in obj.items():
            size = Size.fromStr(size_str)
            r = eval(range_repr)
            sizes_dict[size] = r

        return sizes_dict

    # }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(VolumeAnalytic.update())
