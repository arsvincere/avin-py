#!/usr/bin/env  python3
# ============================================================================
# URL:          http://arsvincere.com
# AUTHOR:       Alex Avin
# E-MAIL:       mr.alexavin@gmail.com
# LICENSE:      GNU GPLv3
# ============================================================================

from __future__ import annotations

import asyncio
import collections
import enum

import pandas as pd

from avin.analytic._analytic import Analytic
from avin.extremum import *
from avin.utils import Tree

__all__ = ("VaweAnalytic",)


class VaweAnalytic(Analytic):
    class Analyse(enum.Enum):  # {{{
        TYPE = 0
        PERIOD = 1
        DELTA = 2
        SPEED = 3
        VOLUME = 4

    # }}}

    name = "vawe"
    cache = Tree()

    @classmethod  # getSizes  # {{{
    async def getSizes(cls, vawe: Vawe, analyse: Analyse) -> dict:
        # cls.cache = {
        #     asset: {
        #         tf: {
        #             type: {
        #                 analyse: {
        #                     Size: Range(min, max),
        #                     ...
        #                 }
        #             }
        #         }
        #     }
        # }
        assert analyse != cls.Analyse.Type

        asset = vawe.asset
        tf = vawe.timeframe
        term = vawe.term
        bear_bull = "BULL" if vawe.isBull() else "BEAR"

        sizes_dict = cls.cache[asset][tf][term][analyse][bear_bull]
        if sizes_dict:
            return sizes_dict

        # load
        analyse_name = f"{tf}-{term.name}-{analyse.name}-{bear_bull}"
        data = await AnalyticData.load(cls.name, analyse_name, asset)
        sizes_dict = cls.decoderJson(data.json_str)

        # save cache
        cls.cache[asset][tf][term][analyse][bear_bull] = sizes_dict

        return sizes_dict

    # }}}
    @classmethod  # speedSize  # {{{
    async def speedSize(cls, vawe: Vawe) -> Size:
        # for example:
        # sizes_dict = {
        #     ...,
        #     Size.SMALL: Range(min, max),
        #     Size.NORMAL: Range(min, max),
        #     Size.BIG: Range(min, max),
        #     ...,
        #     }

        # NOTE:
        # в базе данных размеры диапазонов хранятся по модулю (положительные)
        # из за траблов с классификацией размеров, функция
        # __classifySizes лажает на отрицательных значения, переделывать
        # влом, а так эта функция для положительных значений нормально
        # работает
        # trent.speedPercent()
        # trent.speedPrice()
        # возвращают отрицательные значения если тренд медвежий.
        # поэтому берем модуль скорости а потом ищем ее размер
        sizes_dict = await cls.getSizes(vawe, cls.Analyse.SPEED)
        speed = abs(vawe.speedPercent())

        size = cls.__identifySize(speed, sizes_dict)
        return size

    # }}}
    @classmethod  # deltaSize  # {{{
    async def deltaSize(cls, vawe: Vawe):
        # for example:
        # sizes_dict = {
        #     ...,
        #     Size.SMALL: Range(min, max),
        #     Size.NORMAL: Range(min, max),
        #     Size.BIG: Range(min, max),
        #     ...,
        #     }

        # NOTE:
        # с delta, таже тема что и с speed, размеры в БД хранятся по модулю,
        # в то время как функции
        # trent.deltaPercent()
        # trent.deltaPrice()
        # возвращают отрицательные значения для медвежьего тренда
        # поэтому берем модуль чтобы корректно определить размер
        sizes_dict = await cls.getSizes(vawe, cls.Analyse.DELTA)
        delta = abs(vawe.deltaPercent())

        size = cls.__identifySize(delta, sizes_dict)
        return size

    # }}}
    @classmethod  # periodSize  # {{{
    async def periodSize(cls, vawe: Vawe):
        sizes_dict = await cls.getSizes(vawe, cls.Analyse.PERIOD)
        period = vawe.period()

        size = cls.__identifySize(period, sizes_dict)
        return size

    # }}}
    @classmethod  # volumeSize  # {{{
    async def volumeSize(cls, vawe: Vawe):
        sizes_dict = await cls.getSizes(vawe, cls.Analyse.VOLUME)
        volume = vawe.volume()

        size = cls.__identifySize(volume, sizes_dict)
        return size

    # }}}

    @classmethod  # filtering
    async def filtering(test: Test, term, analyse):
        pass

    @classmethod  # update  # {{{
    async def update(cls):
        logger.info(f":: Analytic={cls.name}: start update")

        await Analytic.save(cls)

        assets = await AssetList.load("XX5")
        # asset = await Asset.fromStr("MOEX-SHARE-LSRG")
        # assets = [asset]
        for asset in assets:
            await cls.__analyseVawe(asset)

        logger.info(f"Analytic={cls.name}: update complete!")

    # }}}

    @classmethod  # __analyseVawe  # {{{
    async def __analyseVawe(cls, asset):
        timeframes = TimeFrameList(
            [
                TimeFrame("D"),
                TimeFrame("1H"),
                TimeFrame("5M"),
            ]
        )

        for timeframe in timeframes:
            logger.info(f"   Analyse {cls.name} {asset}-{timeframe}")

            if timeframe == TimeFrame("1M"):
                first_dt = DateTime(2024, 1, 1, tzinfo=UTC)
            elif timeframe == TimeFrame("5M"):
                first_dt = DateTime(2023, 1, 1, tzinfo=UTC)
            else:
                info = await Data.info(asset, timeframe.toDataType())
                first_dt = info.first_dt

            # info = await Data.info(asset, timeframe.toDataType())
            # first_dt = info.first_dt
            chart = await asset.loadChart(timeframe, first_dt, now())
            elist = ExtremumList(chart)

            svawes = elist.getAllVawes(Term.STERM)
            mvawes = elist.getAllVawes(Term.MTERM)
            lvawes = elist.getAllVawes(Term.LTERM)
            await cls.__analyseVawesSizes(svawes)
            await cls.__analyseVawesSizes(mvawes)
            await cls.__analyseVawesSizes(lvawes)

    # }}}
    @classmethod  # __analyseVawesSizes  # {{{
    async def __analyseVawesSizes(cls, vawes: list[Vawe]):
        # NOTE:
        # логика такая если их меньше 300 то будет в притык к 100шт
        # бычьих и медвежьих, и классифицировать тут нечего еще.
        # Главное потом в стратегиях не забыть всегда проверять
        # а есть ли вообще в БД классификация по этому
        # активу по этому таймфрейму по s/m/l-term
        # Пока там ассерт стоит в Keeper стоит потом решу где его
        # лучше обрабатывать и как.
        if len(vawes) < 300:
            return

        term_name = vawes[0].term.name
        timeframe = vawes[0].timeframe
        asset = vawes[0].asset
        logger.info(f"   - analyse {term_name}")

        period_bull_list = list()
        period_bear_list = list()
        delta_bull_list = list()
        delta_bear_list = list()
        speed_bull_list = list()
        speed_bear_list = list()
        volume_bull_list = list()
        volume_bear_list = list()

        for vawe in vawes:
            period = vawe.period()
            delta = vawe.deltaPercent()
            speed = vawe.speedPercent()
            volume = vawe.volume()

            if vawe.isBull():
                period_bull_list.append(period)
                delta_bull_list.append(delta)
                speed_bull_list.append(speed)
                volume_bull_list.append(volume)
            elif vawe.isBear():
                period_bear_list.append(period)
                delta_bear_list.append(abs(delta))
                speed_bear_list.append(abs(speed))
                volume_bear_list.append(volume)

        # period bull
        name = f"{timeframe}-{term_name}-PERIOD-BULL"
        classify = cls.__classifySizes(period_bull_list)
        await cls.__saveAnalyticData(name, asset, classify)
        # period bear
        name = f"{timeframe}-{term_name}-PERIOD-BEAR"
        classify = cls.__classifySizes(period_bear_list)
        await cls.__saveAnalyticData(name, asset, classify)

        # volume bull
        name = f"{timeframe}-{term_name}-VOLUME-BULL"
        classify = cls.__classifySizes(volume_bull_list)
        await cls.__saveAnalyticData(name, asset, classify)
        # volume bear
        name = f"{timeframe}-{term_name}-VOLUME-BEAR"
        classify = cls.__classifySizes(volume_bear_list)
        await cls.__saveAnalyticData(name, asset, classify)

        # delta bull
        name = f"{timeframe}-{term_name}-DELTA-BULL"
        classify = cls.__classifySizes(delta_bull_list)
        await cls.__saveAnalyticData(name, asset, classify)
        # delta bear
        name = f"{timeframe}-{term_name}-DELTA-BEAR"
        classify = cls.__classifySizes(delta_bear_list)
        await cls.__saveAnalyticData(name, asset, classify)

        # speed bull
        name = f"{timeframe}-{term_name}-SPEED-BULL"
        classify = cls.__classifySizes(speed_bull_list)
        await cls.__saveAnalyticData(name, asset, classify)
        # speed bear
        classify = cls.__classifySizes(speed_bear_list)
        name = f"{timeframe}-{term_name}-SPEED-BEAR"
        await cls.__saveAnalyticData(name, asset, classify)

    # }}}
    @classmethod  # __classifySizes  # {{{
    def __classifySizes(cls, value_list: list) -> dict:
        assert len(value_list) > 100

        # create DataFrame
        classify = dict()
        trends_count = len(value_list)
        counter = collections.Counter(value_list)
        sorted_values_list = list()
        count_list = list()
        for i in sorted(counter):
            sorted_values_list.append(i)
            count_list.append(counter[i])
        df = pd.DataFrame(
            {
                "value": sorted_values_list,
                "count": count_list,
            }
        )
        df["percent"] = df["count"] / trends_count * 100

        # ####
        # df.to_csv("vawe", sep=";")
        # input(1)
        # fig = px.scatter(x=df["value"], y=df["percent"])
        # fig.show()
        # print(df)
        # exit(0)
        # ####

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

            # иногда когда значений мало - заглючивает в последней
            # категории, не охота разбираться, просто возьму 1 значение
            # из предыдущей и запихаю его в GREATEST_BIG
            if last == len(percent):
                last -= 1

            maximum = df.iloc[last]["value"]
            classify[size] = Range(minimum, maximum)
            minimum = maximum

        # set last value GREATEST_BIG
        maximum = df["value"].max()
        classify[Size.GREATEST_BIG] = Range(minimum, maximum)

        return classify

    # }}}
    @classmethod  # __saveAnalyticData  # {{{
    async def __saveAnalyticData(cls, name, asset, classify):
        logger.info(f"   -- save {asset.ticker} {name}")

        analytic_data = AnalyticData(
            analytic_name=cls.name,
            analyse_name=name,
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
        # to dict_sizes = {Size.NORMAL: <class Range>, ...}
        dict_sizes = dict()
        for size_str, range_repr in obj.items():
            size = Size.fromStr(size_str)
            r = eval(range_repr)
            dict_sizes[size] = r

        return dict_sizes

    # }}}


if __name__ == "__main__":
    configureLogger(debug=True, info=True)
    asyncio.run(VaweAnalytic.update())
