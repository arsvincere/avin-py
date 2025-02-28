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

from avin.analytic._analytic import Analytic
from avin.analytic.size import Size
from avin.core import Asset, Range, TimeFrame
from avin.utils import Tree

__all__ = ("BarAnalytic",)

# TODO: ???
# сюда можно заебенить как раз стандартные фильтры, типо:
# SizeAnalytic.filter(b1, body, BIG)
# SizeAnalytic.filter(b1, body, [NORMAL, BIG, BIGGER])
# SizeAnalytic.filter(b1.body, [NORMAL, BIG, BIGGER])


class BarAnalytic(Analytic):
    name = "bar"
    cache = Tree()

    @classmethod  # getSizes  # {{{
    async def getSizes(
        cls, asset: Asset, tf: TimeFrame, typ: Range.Type
    ) -> Size:
        # try find sizes in cache
        sizes_dict = cls.cache[asset][tf][typ]
        if sizes_dict:
            return sizes_dict

        # load
        analyse_name = f"{tf}-{typ}"
        data = await AnalyticData.load(cls.name, analyse_name, asset)
        sizes_dict = cls.decoderJson(data.json_str)

        # save cache
        cls.cache[asset][tf] = sizes_dict

        return sizes_dict

    # }}}
    @classmethod  # rangeSize  # {{{
    async def rangeSize(cls, r: Range) -> Size:
        bar = r.bar
        chart = bar.chart
        instrument = chart.instrument
        asset = Asset.fromInstrument(instrument)
        typ = r.type.name.lower()

        sizes_dict = await cls.getSizes(asset, tf, typ)

        # for example:
        # sizes_dict = {
        #     ...,
        #     Size.SMALL: <class Range>,
        #     Size.NORMAL: <class Range>,
        #     Size.BIG: <class Range>,
        #     ...,
        #     }

        percent = r.percent()
        size = cls.__identifySize(percent, sizes_dict)
        return size

    # }}}

    @classmethod  # update  # {{{
    async def update(cls):
        logger.info(":: Analytic=range start update")

        await Analytic.save(cls)

        assets = await Asset.requestAll()
        for asset in assets:
            logger.info(f"   Analyse bar ranges {asset.ticker}")
            await cls.__analyseBar(asset)

        logger.info(f"Analytic={cls.name} update complete!")

    # }}}

    @classmethod  # __analyseBar  # {{{
    async def __analyseBar(cls, asset):
        timeframes = [
            TimeFrame("D"),
            TimeFrame("1H"),
            TimeFrame("5M"),
            TimeFrame("1M"),
        ]

        for timeframe in timeframes:
            logger.info(f"   - {timeframe}")

            datainfo_list = await Data.info(instrument=asset)
            info = datainfo_list.info(asset, timeframe.toDataType())
            chart = await asset.loadChart(timeframe, info.first_dt, now())

            await cls.__analyseBarTimeFrame(chart)

    # }}}
    @classmethod  # __analyseBarTimeFrame  # {{{
    async def __analyseBarTimeFrame(cls, chart):
        # elements - части бара: весь диапазон, тело, нижняя/верхняя тень
        for element in Range.Type:
            logger.info(f"   -- {element.name}")
            await cls.__researchElement(chart, element)

    # }}}
    @classmethod  # __researchElement  # {{{
    async def __researchElement(cls, chart, element: Range.Type):
        ranges_list = list()
        for bar in chart:
            # command looks like:  bar.body.percent()
            command = f"bar.{element.name.lower()}.percent()"
            r = eval(command)
            r = round(r, 2)
            ranges_list.append(r)

        if len(ranges_list) < 200:
            return

        classify = cls.__classifySizes(ranges_list)
        await cls.__saveAnalyticData(chart, element, classify)

    # }}}
    @classmethod  # __classifySizes  # {{{
    def __classifySizes(cls, ranges_list: list) -> dict:
        # create DataFrame
        days_count = len(ranges_list)
        counter = collections.Counter(ranges_list)
        sorted_rlist = list()
        count_list = list()
        for i in sorted(counter):
            sorted_rlist.append(i)
            count_list.append(counter[i])
        df = pd.DataFrame(
            {
                "range": sorted_rlist,
                "count": count_list,
            }
        )
        df["percent"] = df["count"] / days_count * 100

        # create classify
        classify = dict()
        percent = df["percent"]
        minimum = df.iloc[0]["range"]
        last = 1
        for size in Size:
            if size in (
                Size.BLACKSWAN_SMALL,  # не существующие еще черные лебеди
                Size.BLACKSWAN_BIG,  # не существующие еще черные лебеди
                Size.GREATEST_BIG,  # last range set up after cycle
            ):
                continue

            while percent[0:last].sum() < size.value:
                last += 1
            maximum = df.iloc[last]["range"]
            classify[size] = Range(minimum, maximum)
            minimum = maximum

        # set last range GREATEST_BIG
        maximum = df["range"].max()
        classify[Size.GREATEST_BIG] = Range(minimum, maximum)

        return classify

        # # create classify
        # percent = df["percent"]
        # i = 1
        # while percent[0:i].sum() < 1:
        #     i += 1
        # greatest_small = Range(df.iloc[0]["range"], df.iloc[i]["range"])
        # while percent[0:i].sum() < 3:
        #     i += 1
        # anomal_small = Range(greatest_small.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 5:
        #     i += 1
        # extra_small = Range(anomal_small.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 10:
        #     i += 1
        # very_small = Range(extra_small.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 20:
        #     i += 1
        # smallest = Range(very_small.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 30:
        #     i += 1
        # smaller = Range(smallest.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 40:
        #     i += 1
        # small = Range(smaller.max, df.iloc[i]["range"])
        # # while percent[0:i].sum() < 50:
        # #     i += 1
        # # center = df.iloc[i]["range"]
        # while percent[0:i].sum() < 60:
        #     i += 1
        # normal = Range(small.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 70:
        #     i += 1
        # big = Range(normal.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 80:
        #     i += 1
        # bigger = Range(big.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 90:
        #     i += 1
        # biggest = Range(bigger.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 95:
        #     i += 1
        # very_big = Range(biggest.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 97:
        #     i += 1
        # extra_big = Range(very_big.max, df.iloc[i]["range"])
        # while percent[0:i].sum() < 99:
        #     i += 1
        # anomal_big = Range(extra_big.max, df.iloc[i]["range"])
        # greatest_big = Range(anomal_big.max, df["range"].max())
        #
        # # save classify
        # classify[Size.GREATEST_SMALL] = greatest_small
        # classify[Size.ANOMAL_SMALL] = anomal_small
        # classify[Size.EXTRA_SMALL] = extra_small
        # classify[Size.VERY_SMALL] = very_small
        # classify[Size.SMALLEST] = smallest
        # classify[Size.SMALLER] = smaller
        # classify[Size.SMALL] = small
        # classify[Size.NORMAL] = normal
        # classify[Size.BIG] = big
        # classify[Size.BIGGER] = bigger
        # classify[Size.BIGGEST] = biggest
        # classify[Size.VERY_BIG] = very_big
        # classify[Size.EXTRA_BIG] = extra_big
        # classify[Size.ANOMAL_BIG] = anomal_big
        # classify[Size.GREATEST_BIG] = greatest_big
        #
        # return classify

    # }}}
    @classmethod  # __saveAnalyticData  # {{{
    async def __saveAnalyticData(cls, chart, element, classify):
        asset = chart.instrument
        tf = chart.timeframe
        analyse_name = f"{tf}-{element}"

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

        # если значение < чем существующий GREATEST_SMALL ->  BLACKSWAN_SMALL
        range_ = sizes_dict[Size.GREATEST_SMALL]
        if value < range_.min:
            return Size.BLACKSWAN_SMALL

        # если значение > чем существующий GREATEST_BIG ->  BLACKSWAN_BIG
        range_ = sizes_dict[Size.GREATEST_BIG]
        if value > range_.max:
            return Size.BLACKSWAN_BIG

    # }}}

    @staticmethod  # encoderJson  # {{{
    def encoderJson(data) -> str:
        logger.debug("UAnalytic=range: encoderJson")

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


#     def printSortedAverageRanges():  # {{{
#         ALL = Cmd.loadJSON("/home/alex/AVIN/research/range.json")
#         AVG = dict()
#         for ticker in ALL:
#             ranges = ALL[ticker]
#             avg = dict()
#             for type_ in ranges:
#                 avg[type_] = ranges[type_]["avg"]
#             AVG[ticker] = avg
#         df = pd.DataFrame(AVG)
#         data = pd.DataFrame()
#         data["range"] = df.loc["range"]
#         data["body"] = df.loc["body"]
#         data["upper_shadow"] = df.loc["upper_shadow"]
#         data["lower_shadow"] = df.loc["lower_shadow"]
#         data = data.sort_values("lower_shadow")
#         print()
#         print("Average values sorted by 'lower_shadow':")
#         print("-------------------------------------------")
#         print(data)
#         print()
#
#
# # }}}


if __name__ == "__main__":
    assert False, "ну это ничайно второй раз запустил, чтобы не затерло БД..."
    exit(100500)
    configureLogger(debug=True, info=True)
    asyncio.run(BarAnalytic.update())
